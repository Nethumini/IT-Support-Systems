"""A blocked high-risk action must reach a person, and stay blocked.

The chat told users a blocked action had been "sent to an IT expert" when no
ticket existed and nobody was assigned. These tests hold the fix to three
things: a ticket really exists, it goes to someone who is allowed to approve a
high-risk action, and raising it changes nothing about the action itself.

In-memory database, no model calls.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.remediation import RemediationRequestDB, RemediationStatus, fingerprint
from app.models.ticket import TicketDB, TicketPriority
from app.models.user import UserDB
from app.services.escalation_service import raise_blocked_action_ticket

REQUESTER = "staff@acme.com"


@pytest.fixture
def db():
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


def _user(db, email, role, workload=0, active=True):
    user = UserDB(
        email=email, name=email.split("@")[0], hashed_password="x",
        role=role, is_active=active, current_workload=workload,
    )
    db.add(user)
    db.commit()
    return user


def _blocked_request(db):
    request = RemediationRequestDB(
        user_email=REQUESTER,
        reported_problem="Nothing prints",
        action_id="restart_service",
        parameters={},
        action_fingerprint=fingerprint("restart_service", {}, None),
        status=RemediationStatus.BLOCKED.value,
        risk_level="high",
        approval_route="expert_approval_or_block",
    )
    db.add(request)
    db.commit()
    return request


def _raise(db, request, existing=None):
    return raise_blocked_action_ticket(
        db,
        user_email=REQUESTER,
        reported_problem="Nothing prints",
        action_name="Restart Service",
        remediation_id=request.id,
        category="hardware",
        existing_ticket_id=existing,
    )


def test_a_blocked_action_becomes_a_ticket(db):
    request = _blocked_request(db)

    ticket_id, _ = _raise(db, request)

    ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
    assert ticket is not None
    assert "Restart Service" in ticket.title
    assert "Nothing prints" in ticket.description
    assert f"remediation #{request.id}" in ticket.description


def test_it_goes_to_someone_who_can_approve_high_risk(db):
    _user(db, "l1@acme.com", "support_l1")
    _user(db, "l2@acme.com", "support_l2")
    request = _blocked_request(db)

    _, assigned = _raise(db, request)

    assert assigned == "l2@acme.com"


def test_the_least_busy_expert_is_chosen(db):
    _user(db, "busy@acme.com", "support_l3", workload=5)
    _user(db, "free@acme.com", "it_admin", workload=1)
    request = _blocked_request(db)

    _, assigned = _raise(db, request)

    assert assigned == "free@acme.com"
    expert = db.query(UserDB).filter(UserDB.email == "free@acme.com").first()
    assert expert.current_workload == 2


def test_the_requester_is_never_their_own_expert(db):
    """High risk needs a second person, for the ticket as for the approval."""
    _user(db, REQUESTER, "system_admin")
    request = _blocked_request(db)

    ticket_id, assigned = _raise(db, request)

    assert ticket_id is not None
    assert assigned is None


def test_with_no_expert_the_ticket_exists_but_claims_no_assignee(db):
    _user(db, "l1@acme.com", "support_l1")
    _user(db, "gone@acme.com", "support_l2", active=False)
    request = _blocked_request(db)

    ticket_id, assigned = _raise(db, request)

    assert ticket_id is not None
    assert assigned is None


def test_the_action_stays_blocked(db):
    """A ticket decides who looks at it, never whether it runs."""
    _user(db, "l2@acme.com", "support_l2")
    request = _blocked_request(db)

    ticket_id, _ = _raise(db, request)

    db.refresh(request)
    assert request.status == RemediationStatus.BLOCKED.value
    assert request.approval_token is None
    assert request.ticket_id == ticket_id


def test_the_conversation_ticket_is_reused_not_duplicated(db):
    _user(db, "l2@acme.com", "support_l2")
    existing = TicketDB(title="Printer", description="Nothing prints",
                        user_email=REQUESTER, priority=TicketPriority.LOW)
    db.add(existing)
    db.commit()
    request = _blocked_request(db)

    ticket_id, assigned = _raise(db, request, existing=existing.id)

    assert ticket_id == existing.id
    assert db.query(TicketDB).count() == 1
    assert assigned == "l2@acme.com"
    db.refresh(existing)
    assert "Restart Service" in existing.description


def test_someone_already_holding_the_ticket_keeps_it(db):
    _user(db, "l2@acme.com", "support_l2")
    existing = TicketDB(title="Printer", description="x", user_email=REQUESTER,
                        assigned_to="l3@acme.com")
    db.add(existing)
    db.commit()
    request = _blocked_request(db)

    _, assigned = _raise(db, request, existing=existing.id)

    assert assigned == "l3@acme.com"
