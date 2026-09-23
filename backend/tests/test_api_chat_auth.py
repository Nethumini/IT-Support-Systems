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
