"""Who the chat believes you are, and whose conversations you may read.

The chat can enumerate the machines registered to a person and raise
remediation requests in their name. Until 23 September 2026 it took that
person's address from the request body and required no token at all, so any
caller could be anybody - and the approval record the contribution rests on
would have proved nothing.

These tests hold the boundary. None of them reaches a language model:
authentication is decided before any agent is called, so the suite costs no
quota and needs no API key.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.main import app

PASSWORD = "test-password-123"
OWNER = "bethany.williams@acme-soft.com"
STRANGER = "olu.adeyemi@acme-soft.com"
SUPPORT = "ravi.patel@acme-soft.com"


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)


@pytest.fixture
def client(session_factory):
    from app.models.chat_history import ChatMessageDB
    from app.models.ticket import TicketDB
    from app.models.user import UserDB

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    db = session_factory()
    for email, role in ((OWNER, "staff"), (STRANGER, "staff"), (SUPPORT, "support_l2")):
        db.add(UserDB(
            email=email,
            name=email.split("@")[0],
            hashed_password=get_password_hash(PASSWORD),
            role=role,
            is_active=True,
        ))
    db.add(TicketDB(id=1, title="Disk full", description="C drive is full", user_email=OWNER))
    db.add(ChatMessageDB(
        session_id="session-owned-by-bethany",
        user_email=OWNER,
        role="user",
        content="My disk is full",
        ticket_id=1,
    ))
    db.commit()
    db.close()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def auth(client, email):
    response = client.post("/api/v1/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


# --------------------------------------------------------------------------
# No token, no conversation
# --------------------------------------------------------------------------

@pytest.mark.parametrize("method,path,kwargs", [
    ("post", "/api/v1/chat", {"json": {"message": "hello", "user_email": OWNER}}),
    ("post", "/api/v1/chat/reset", {"json": {"user_email": OWNER}}),
    ("get", "/api/v1/chat/history/1", {}),
    ("get", f"/api/v1/chat/sessions/{OWNER}", {}),
    ("post", "/api/v1/chat/resume/session-owned-by-bethany", {}),
    ("post", "/api/v1/chat/image", {"files": {"image": ("x.png", b"not-an-image", "image/png")}}),
])
def test_chat_routes_refuse_an_unauthenticated_caller(client, method, path, kwargs):
    response = getattr(client, method)(path, **kwargs)
    assert response.status_code in (401, 403), f"{path} answered {response.status_code}"


def test_a_forged_token_does_not_open_the_chat(client):
    response = client.post(
        "/api/v1/chat",
        json={"message": "hello"},
        headers={"Authorization": "Bearer not.a.real.token"},
    )
    assert response.status_code in (401, 403)


# --------------------------------------------------------------------------
# Whose conversations you may read
# --------------------------------------------------------------------------

def test_a_stranger_cannot_list_someone_elses_sessions(client):
    """The address is in the path, so without this check it is an invitation."""
    response = client.get(f"/api/v1/chat/sessions/{OWNER}", headers=auth(client, STRANGER))
    assert response.status_code == 403


def test_you_can_list_your_own_sessions(client):
    response = client.get(f"/api/v1/chat/sessions/{OWNER}", headers=auth(client, OWNER))
    assert response.status_code == 200


def test_support_staff_can_list_the_sessions_they_answer(client):
    response = client.get(f"/api/v1/chat/sessions/{OWNER}", headers=auth(client, SUPPORT))
    assert response.status_code == 200


def test_a_stranger_cannot_resume_someone_elses_session(client):
    """A session id is hard to guess, but unguessable is not a rule."""
    response = client.post(
        "/api/v1/chat/resume/session-owned-by-bethany",
        headers=auth(client, STRANGER),
    )
    assert response.status_code == 403


def test_a_stranger_cannot_read_the_chat_behind_someone_elses_ticket(client):
    response = client.get("/api/v1/chat/history/1", headers=auth(client, STRANGER))
    assert response.status_code == 403


def test_the_ticket_owner_can_read_their_own_chat(client):
    response = client.get("/api/v1/chat/history/1", headers=auth(client, OWNER))
    assert response.status_code == 200


def test_support_staff_can_read_the_chat_behind_a_ticket(client):
    response = client.get("/api/v1/chat/history/1", headers=auth(client, SUPPORT))
    assert response.status_code == 200


def test_a_missing_ticket_is_a_404_not_a_leak(client):
    response = client.get("/api/v1/chat/history/424242", headers=auth(client, OWNER))
    assert response.status_code == 404


# --------------------------------------------------------------------------
# The body cannot name someone else
# --------------------------------------------------------------------------

def test_reset_acts_on_the_caller_not_on_the_address_in_the_body(client):
    """Sending another person's address must not reset their conversation."""
    response = client.post(
        "/api/v1/chat/reset",
        json={"user_email": STRANGER},
        headers=auth(client, OWNER),
    )
    assert response.status_code == 200
    assert response.json()["user_email"] == OWNER


def test_an_authenticated_caller_gets_past_the_gate(client):
    """An empty message is rejected after authentication and before any agent
    runs, so this proves the token is accepted without spending chat quota."""
    response = client.post(
        "/api/v1/chat",
        json={"message": "   "},
        headers=auth(client, OWNER),
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


# --------------------------------------------------------------------------
# A ticket can say which machine it is about
#
# Until 24 September 2026 it could not: a technician opened a ticket and had
# no way to know which computer to go to, including the tickets raised
# automatically for machines that had stopped answering.
# --------------------------------------------------------------------------

def _enrol(session_factory, owner, name="WIN-LAB-01"):
    from app.models.device import DeviceDB, new_device_id

    db = session_factory()
    device = DeviceDB(device_id=new_device_id(), name=name, owner_email=owner, is_active=True)
    device.issue_secret()
    db.add(device)
    db.commit()
    device_id = device.device_id
    db.close()
    return device_id


def _raise_ticket(client, headers, **fields):
    payload = {
        "title": "Laptop will not wake from sleep",
        "description": "Pressing the power button does nothing until I hold it down.",
        "priority": "medium",
        "category": "hardware",
    }
    payload.update(fields)
    return client.post("/api/v1/tickets", json=payload, headers=headers)


def test_a_ticket_can_name_the_users_own_machine(client, session_factory):
    device_id = _enrol(session_factory, OWNER)

    response = _raise_ticket(client, auth(client, OWNER), device_id=device_id)

    assert response.status_code == 201, response.text
    assert response.json()["device_id"] == device_id


def test_a_ticket_about_no_machine_is_still_allowed(client):
    """Most tickets are not about one: a password reset, a VPN question."""
    response = _raise_ticket(client, auth(client, OWNER), device_id=None)

    assert response.status_code == 201
    assert response.json()["device_id"] is None


def test_a_ticket_cannot_name_someone_elses_machine(client, session_factory):
    device_id = _enrol(session_factory, STRANGER, name="NOT-YOURS")

    response = _raise_ticket(client, auth(client, OWNER), device_id=device_id)

    assert response.status_code == 403
    assert "not registered" in response.json()["detail"]


def test_a_ticket_cannot_name_a_machine_that_does_not_exist(client):
    response = _raise_ticket(client, auth(client, OWNER), device_id="dev_invented")

    assert response.status_code == 404


def test_a_revoked_machine_cannot_be_named(client, session_factory):
    """A revoked credential means that machine is no longer ours to point at."""
    from app.models.device import DeviceDB

    device_id = _enrol(session_factory, OWNER, name="RETIRED")
    db = session_factory()
    db.query(DeviceDB).filter(DeviceDB.device_id == device_id).first().is_active = False
    db.commit()
    db.close()

    assert _raise_ticket(client, auth(client, OWNER), device_id=device_id).status_code == 404


def test_you_cannot_raise_a_ticket_in_someone_elses_name(client):
    response = _raise_ticket(client, auth(client, OWNER), user_email=STRANGER)

    assert response.status_code == 403


def test_support_staff_may_raise_a_ticket_for_someone(client, session_factory):
    """Someone phones the service desk: the ticket is theirs, not the agent's."""
    device_id = _enrol(session_factory, OWNER)

    response = _raise_ticket(
        client, auth(client, SUPPORT), user_email=OWNER, device_id=device_id
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user_email"] == OWNER
    assert body["device_id"] == device_id


def test_the_device_list_says_which_machines_are_answering(client, session_factory):
    _enrol(session_factory, OWNER)

    rows = client.get("/api/v1/devices/mine", headers=auth(client, OWNER)).json()

    assert rows
    assert rows[0]["online"] is False  # enrolled, but its agent never called in
