"""The device work loop: queue a job, let an agent answer, return a result.

These stand in for the Windows machine. A fake agent takes jobs over the real
API with a real device credential and posts real results, so the loop under test
is the one that will run in production - only the thing at the far end is
substituted.

The behaviour that matters most here is what happens when the device does *not*
answer. A silent machine means the outcome is unknown, and an unknown outcome
must never be reported as a success.
"""
import threading

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import DEVICE_ID_HEADER, DEVICE_SECRET_HEADER, get_db
from app.api.endpoints import agent_work
from app.core.database import Base
from app.models.device import DeviceDB, new_device_id
from app.models.device_job import DeviceJobDB, JobStatus
from app.services.execution import AgentDriver
from app.services.execution.base import ExecutionError

#: A read-only action that exists in the catalogue.
ACTION = "check_disk_space"


@pytest.fixture
def engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def Session(engine):
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)


@pytest.fixture
def db(Session):
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def device(db):
    d = DeviceDB(
        device_id=new_device_id(),
        name="WIN-LAB-01",
        owner_email="admin@acme.com",
        os_name="Windows",
        is_active=True,
    )
    secret = d.issue_secret()
    db.add(d)
    db.commit()
    db.refresh(d)
    return d, secret


@pytest.fixture
def other_device(db):
    d = DeviceDB(device_id=new_device_id(), name="WIN-LAB-02", owner_email="someone@acme.com")
    secret = d.issue_secret()
    db.add(d)
    db.commit()
    db.refresh(d)
    return d, secret


@pytest.fixture
def client(Session):
    """The real agent routes, with their real device authentication."""
    app = FastAPI()
    app.include_router(agent_work.router, prefix="/api/v1/devices")

    def _get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _get_db
    return TestClient(app, raise_server_exceptions=False)


def agent_headers(device_id, secret):
    return {DEVICE_ID_HEADER: device_id, DEVICE_SECRET_HEADER: secret}


def run_in_background(driver, action=None):
    """Start a driver call in a thread, swallowing the expected timeout.

    Some tests deliberately leave a job unanswered. The driver then raises, and
    an unhandled exception in a thread is only noise here - the assertion is
    about what the *other* device can see, not about this call.
    """
    def _call():
        try:
            driver.execute(action or ACTION, {})
        except ExecutionError:
            pass

    thread = threading.Thread(target=_call, daemon=True)
    thread.start()
    return thread


def driver_for(device, Session, **kwargs):
    d, _ = device
    kwargs.setdefault("timeout_seconds", 5)
    kwargs.setdefault("poll_interval", 0.05)
    return AgentDriver(d.device_id, session_factory=Session, **kwargs)


def answer_next_job(client, device, payload, timeout=5.0):
    """Act as the agent: take a job and report the given result."""
    d, secret = device
    headers = agent_headers(d.device_id, secret)
    deadline = threading.Event()

    for _ in range(int(timeout / 0.05)):
        job = client.get("/api/v1/devices/work", headers=headers).json()["job"]
        if job:
            client.post(
                f"/api/v1/devices/work/{job['job_id']}/result",
                json=payload,
                headers=headers,
            )
            return job
        deadline.wait(0.05)
    raise AssertionError("no job was offered to the agent")


# --- the happy path --------------------------------------------------------

def test_action_runs_on_the_device_and_the_result_comes_back(client, Session, device):
    """The full round trip, which is what the Windows agent will do."""
    result = {}

    def run_driver():
        result["value"] = driver_for(device, Session).execute(ACTION, {})

    worker = threading.Thread(target=run_driver)
    worker.start()

    job = answer_next_job(client, device, {
        "success": True,
        "output": "94.2 GB free of 512 GB",
        "duration_ms": 120,
        "state_before": {"disk_free_gb": 94.0},
        "state_after": {"disk_free_gb": 94.2},
    })
    worker.join(timeout=10)

    assert job["action_id"] == ACTION
    outcome = result["value"]
    assert outcome.success is True
    assert outcome.driver == "agent"
    assert "94.2 GB free" in outcome.output
    assert outcome.state_before == {"disk_free_gb": 94.0}
    assert outcome.state_after == {"disk_free_gb": 94.2}


def test_a_failure_on_the_device_is_reported_as_a_failed_result(client, Session, device):
    """An action that ran and failed is a result, not an error - the difference
    decides whether verification runs or the request is refused outright."""
    result = {}

    def run_driver():
        result["value"] = driver_for(device, Session).execute(ACTION, {})

    worker = threading.Thread(target=run_driver)
    worker.start()
    answer_next_job(client, device, {"success": False, "error": "Access is denied."})
    worker.join(timeout=10)

    outcome = result["value"]
    assert outcome.success is False
    assert "Access is denied." in (outcome.error or "")


def test_state_capture_returns_what_the_device_read(client, Session, device):
    captured = {}

    def run_driver():
        captured["value"] = driver_for(device, Session).capture_state("disk")

    worker = threading.Thread(target=run_driver)
    worker.start()
    job = answer_next_job(client, device, {"success": True, "state": {"disk_free_gb": 12.5}})
    worker.join(timeout=10)

    assert job["kind"] == "capture_state"
    assert job["scope"] == "disk"
    assert captured["value"] == {"disk_free_gb": 12.5}


# --- the silent machine ----------------------------------------------------

def test_a_device_that_never_answers_is_an_error_not_a_result(Session, device):
    """The core safety property of this driver.

    Nobody knows whether the action ran, so the driver refuses. An
    ``ExecutionResult`` - even with ``success=False`` - would claim knowledge
    the server does not have.
    """
    driver = driver_for(device, Session, timeout_seconds=0.3)

    with pytest.raises(ExecutionError) as exc:
        driver.execute(ACTION, {})

    assert "did not respond" in str(exc.value)
    assert "unknown" in str(exc.value).lower()


def test_an_unanswered_job_is_marked_expired(Session, device):
    driver = driver_for(device, Session, timeout_seconds=0.3)
    with pytest.raises(ExecutionError):
        driver.execute(ACTION, {})

    session = Session()
    try:
        job = session.query(DeviceJobDB).one()
        assert job.status == JobStatus.EXPIRED.value
    finally:
        session.close()


def test_state_capture_degrades_instead_of_raising(Session, device):
    """A missing snapshot weakens verification; it must not abort the run."""
    driver = driver_for(device, Session, timeout_seconds=0.3)
    assert driver.capture_state("disk") == {}


# --- refusals --------------------------------------------------------------

def test_an_action_outside_the_catalogue_is_never_sent(Session, device):
    """The allow-list applies to remote execution exactly as it does locally."""
    driver = driver_for(device, Session)

    with pytest.raises(ExecutionError) as exc:
        driver.execute("rm -rf /", {})

    assert "catalogue" in str(exc.value)

    session = Session()
    try:
        assert session.query(DeviceJobDB).count() == 0, "nothing should be queued"
    finally:
        session.close()


def test_a_revoked_device_gets_no_work(Session, db, device):
    d, _ = device
    d.revoke()
    db.commit()

    with pytest.raises(ExecutionError) as exc:
        driver_for(device, Session).execute(ACTION, {})
    assert "revoked" in str(exc.value)


# --- one device cannot reach another's work --------------------------------

def test_an_agent_is_not_offered_another_devices_job(client, Session, device, other_device):
    run_in_background(driver_for(device, Session, timeout_seconds=0.3))

    o, o_secret = other_device
    # The other device polls; the queued job is not its own, so it gets nothing.
    for _ in range(5):
        body = client.get("/api/v1/devices/work", headers=agent_headers(o.device_id, o_secret)).json()
        assert body["job"] is None


def test_an_agent_cannot_post_a_result_for_another_devices_job(
    client, Session, device, other_device
):
    run_in_background(driver_for(device, Session, timeout_seconds=1))

    session = Session()
    try:
        for _ in range(40):
            job = session.query(DeviceJobDB).first()
            if job:
                break
            threading.Event().wait(0.05)
            session.expire_all()
        assert job is not None
        job_id = job.job_id
    finally:
        session.close()

    o, o_secret = other_device
    response = client.post(
        f"/api/v1/devices/work/{job_id}/result",
        json={"success": True, "output": "pwned"},
        headers=agent_headers(o.device_id, o_secret),
    )
    assert response.status_code == 404


def test_a_result_cannot_be_submitted_twice(client, Session, device):
    """A replayed submission must not overwrite an outcome already verified."""
    result = {}

    def run_driver():
        result["value"] = driver_for(device, Session).execute(ACTION, {})

    worker = threading.Thread(target=run_driver)
    worker.start()
    job = answer_next_job(client, device, {"success": True, "output": "first"})
    worker.join(timeout=10)

    d, secret = device
    second = client.post(
        f"/api/v1/devices/work/{job['job_id']}/result",
        json={"success": True, "output": "second"},
        headers=agent_headers(d.device_id, secret),
    )
    assert second.status_code == 409
    assert "first" in result["value"].output


def test_work_requires_a_device_credential(client):
    assert client.get("/api/v1/devices/work").status_code == 401
