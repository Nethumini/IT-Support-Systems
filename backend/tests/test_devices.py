"""Security tests for endpoint device registration and authentication.

A device credential lets a machine collect approved remediation work and run it.
That makes these the tests that matter most in the agent path: they check that a
device can only ever be what it claims with the right secret, that the secret is
never readable back, and that a device credential buys nothing on a user route.

Everything runs against an in-memory database. No agent and no Windows host is
needed, so these run in CI on any platform.
"""
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import (
    DEVICE_ID_HEADER,
    DEVICE_SECRET_HEADER,
    get_current_device,
    get_db,
)
from app.core.database import Base
from app.models.device import DeviceDB, new_device_id


@pytest.fixture
def db():
    # StaticPool keeps every thread on the same connection. TestClient runs the
    # endpoint in a worker thread, and without this an in-memory SQLite database
    # hands that thread a second, empty database instead.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def device(db):
    """A registered device, with its plaintext secret kept for the test only."""
    d = DeviceDB(
        device_id=new_device_id(),
        name="WIN-LAB-01",
        owner_email="admin@acme.com",
        os_name="Windows",
        os_version="11",
        is_active=True,
    )
    secret = d.issue_secret()
    db.add(d)
    db.commit()
    db.refresh(d)
    return d, secret


@pytest.fixture
def client(db):
    """A minimal app exposing one device-authenticated route.

    Mounting a single route keeps the test about the credential itself rather
    than about whichever endpoint happens to use it.
    """
    app = FastAPI()

    @app.get("/agent/ping")
    def ping(current_device=Depends(get_current_device)):
        return {"device_id": current_device.device_id}

    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app, raise_server_exceptions=False)


def headers(device_id, secret):
    return {DEVICE_ID_HEADER: device_id, DEVICE_SECRET_HEADER: secret}


# --- the secret ------------------------------------------------------------

def test_secret_is_not_stored_in_plaintext(device):
    """The database must never hold a usable copy of the credential."""
    d, secret = device
    assert d.secret_hash != secret
    assert secret not in d.secret_hash


def test_secret_never_appears_in_the_public_view(device):
    """``to_dict`` feeds API responses, so it must not carry the secret."""
    d, secret = device
    payload = d.to_dict()
    assert secret not in str(payload)
    assert "secret_hash" not in payload
    assert "secret" not in payload


def test_each_device_gets_a_different_secret(db):
    first = DeviceDB(device_id=new_device_id(), name="a", owner_email="x@y.z")
    second = DeviceDB(device_id=new_device_id(), name="b", owner_email="x@y.z")
    assert first.issue_secret() != second.issue_secret()


# --- authentication --------------------------------------------------------

def test_correct_credential_is_accepted(client, device):
    d, secret = device
    response = client.get("/agent/ping", headers=headers(d.device_id, secret))
    assert response.status_code == 200
    assert response.json()["device_id"] == d.device_id


def test_wrong_secret_is_refused(client, device):
    d, _ = device
    response = client.get("/agent/ping", headers=headers(d.device_id, "not-the-secret"))
    assert response.status_code == 401


def test_unknown_device_is_refused(client, device):
    _, secret = device
    response = client.get("/agent/ping", headers=headers("dev_does_not_exist", secret))
    assert response.status_code == 401


def test_missing_headers_are_refused(client):
    assert client.get("/agent/ping").status_code == 401


def test_failures_are_indistinguishable(client, device):
    """An attacker must not be able to tell a real device id from a fake one.

    If a wrong secret and an unknown device gave different answers, the endpoint
    would confirm which machines exist - enough to enumerate the fleet before
    attacking one.
    """
    d, secret = device
    wrong_secret = client.get("/agent/ping", headers=headers(d.device_id, "wrong"))
    unknown_device = client.get("/agent/ping", headers=headers("dev_nope", secret))

    assert wrong_secret.status_code == unknown_device.status_code
    assert wrong_secret.json() == unknown_device.json()


# --- revocation ------------------------------------------------------------

def test_revoked_device_is_refused_even_with_the_right_secret(client, db, device):
    """Revocation is the only way to stop a leaked credential, so it must bite
    before the secret is even considered."""
    d, secret = device
    assert client.get("/agent/ping", headers=headers(d.device_id, secret)).status_code == 200

    d.revoke()
    db.commit()

    assert client.get("/agent/ping", headers=headers(d.device_id, secret)).status_code == 401


def test_revocation_records_when_it_happened(db, device):
    d, _ = device
    d.revoke()
    db.commit()
    assert d.is_active is False
    assert d.revoked_at is not None


# --- liveness --------------------------------------------------------------

def test_successful_call_records_last_seen(client, db, device):
    """An administrator needs to see which machines are still reporting in."""
    d, secret = device
    assert d.last_seen_at is None

    client.get("/agent/ping", headers=headers(d.device_id, secret))
    db.refresh(d)

    assert d.last_seen_at is not None


def test_refused_call_does_not_record_last_seen(client, db, device):
    """A wrong secret must not let an attacker fake activity on a device."""
    d, _ = device
    client.get("/agent/ping", headers=headers(d.device_id, "wrong"))
    db.refresh(d)
    assert d.last_seen_at is None


# --- which machine does a chat action run on? ------------------------------
#
# This is what joins a logged-in person to their computer. Before it existed,
# an action from the chat ran on whatever host the backend was on - harmless on
# a developer laptop, wrong on a server, where it would read the server's disk
# and report it to the user as their own.

from app.api.endpoints.chat_enhanced import _resolve_target_device  # noqa: E402


def make_device(db, email, name, active=True, silent_for_seconds=0):
    """An enrolled machine whose agent last asked for work ``silent_for_seconds`` ago.

    The default is a machine that is answering right now. A device that has
    never polled, or stopped polling, cannot run anything - see the offline
    tests below.
    """
    from datetime import datetime, timedelta

    d = DeviceDB(device_id=new_device_id(), name=name, owner_email=email, is_active=active)
    d.issue_secret()
    if silent_for_seconds is not None:
        d.last_seen_at = datetime.utcnow() - timedelta(seconds=silent_for_seconds)
    db.add(d)
    db.commit()
    return d


def test_no_agent_means_the_action_is_refused(db):
    """Fail closed: never silently run on a machine nobody asked for."""
    target, prompt = _resolve_target_device(db, "nobody@acme.com", None)

    assert target is None
    assert prompt["reason"] == "no_agent"


def test_one_machine_is_chosen_without_asking(db):
    d = make_device(db, "malith@acme.com", "WIN-LAB-01")
    target, prompt = _resolve_target_device(db, "malith@acme.com", None)

    assert target == d.device_id
    assert prompt is None


def test_two_machines_must_be_disambiguated_by_the_user(db):
    """Guessing could fix the laptop while they sit at the desktop."""
    make_device(db, "malith@acme.com", "LAPTOP")
    make_device(db, "malith@acme.com", "DESKTOP")

    target, prompt = _resolve_target_device(db, "malith@acme.com", None)

    assert target is None
    assert prompt["reason"] == "choose_device"
    assert {d["name"] for d in prompt["devices"]} == {"LAPTOP", "DESKTOP"}


def test_a_chosen_machine_is_honoured(db):
    make_device(db, "malith@acme.com", "LAPTOP")
    desktop = make_device(db, "malith@acme.com", "DESKTOP")

    target, prompt = _resolve_target_device(db, "malith@acme.com", desktop.device_id)

    assert target == desktop.device_id
    assert prompt is None


def test_you_cannot_target_someone_elses_machine(db):
    """The device id comes from the browser, so it is not trusted."""
    theirs = make_device(db, "someone@acme.com", "THEIR-PC")
    make_device(db, "malith@acme.com", "MY-PC")

    target, prompt = _resolve_target_device(db, "malith@acme.com", theirs.device_id)

    assert target is None
    assert prompt["reason"] == "unknown_device"


def test_a_revoked_machine_is_not_offered(db):
    make_device(db, "malith@acme.com", "OLD-PC", active=False)

    target, prompt = _resolve_target_device(db, "malith@acme.com", None)

    assert target is None
    assert prompt["reason"] == "no_agent"


def test_a_device_cannot_be_registered_to_a_stranger(db):
    """An owner who is not a user makes a machine nobody can ever reach.

    The chat matches a machine to its owner's sign-in address, so a device owned
    by an address nobody logs in with is silently unusable.
    """
    from fastapi import HTTPException
    from app.api.endpoints.devices import require_real_owner

    with pytest.raises(HTTPException) as exc:
        require_real_owner(db, "ghost@acme.com")

    assert exc.value.status_code == 400
    assert "No user with the email" in exc.value.detail


def test_a_device_may_be_registered_to_a_real_user(db):
    from app.api.endpoints.devices import require_real_owner
    from app.models.user import UserDB

    db.add(UserDB(email="real@acme.com", name="Real", hashed_password="x", role="end_user"))
    db.commit()

    assert require_real_owner(db, "real@acme.com").email == "real@acme.com"


# --------------------------------------------------------------------------
# A machine nobody has heard from
#
# The agent asks for work every two seconds. Offering an action to a machine
# that stopped answering spends the executor's full 60-second wait to arrive
# at "the outcome is unknown", and tells the user nothing they could not have
# been told immediately.
# --------------------------------------------------------------------------

def test_a_silent_machine_is_not_offered_for_actions(db):
    make_device(db, "malith@acme.com", "WIN-LAB-01", silent_for_seconds=600)

    target, prompt = _resolve_target_device(db, "malith@acme.com", None)

    assert target is None
    assert prompt["reason"] == "device_offline"
    assert "WIN-LAB-01" in prompt["message"]


def test_a_machine_that_never_asked_for_work_is_offline(db):
    """Enrolled is not the same as running."""
    d = make_device(db, "malith@acme.com", "NEVER-STARTED", silent_for_seconds=None)
    assert d.last_seen_at is None

    target, prompt = _resolve_target_device(db, "malith@acme.com", None)

    assert target is None
    assert prompt["reason"] == "device_offline"


def test_choosing_a_silent_machine_is_refused_too(db):
    make_device(db, "malith@acme.com", "LAPTOP")
    desktop = make_device(db, "malith@acme.com", "DESKTOP", silent_for_seconds=600)

    target, prompt = _resolve_target_device(db, "malith@acme.com", desktop.device_id)

    assert target is None
    assert prompt["reason"] == "device_offline"


def test_a_brief_gap_between_polls_is_not_offline(db):
    """Two seconds is the poll interval; a machine is not offline between polls."""
    d = make_device(db, "malith@acme.com", "WIN-LAB-01", silent_for_seconds=5)

    target, prompt = _resolve_target_device(db, "malith@acme.com", None)

    assert target == d.device_id
    assert prompt is None
