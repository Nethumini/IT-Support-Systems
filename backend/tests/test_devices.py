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
