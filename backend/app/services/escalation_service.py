"""Putting a machine nobody can reach in front of a person.

There are two moments where the system establishes that it cannot touch
someone's computer, and both of them used to end in advice:

* before acting - the agent has not asked for work recently, so nothing is
  offered; and
* during acting - the action was sent and the machine never answered inside
  the executor's wait.

The second is the one that matters most, because by then the user has watched
a minute pass. Neither is a state the software can improve on its own, so both
raise a ticket and assign it the way any other ticket is assigned.

Deliberately separate from the remediation service: whether a job reaches a
human is an operational concern, not part of the verified core, and nothing
here may change what the risk, approval or verification layers decided.
"""
from __future__ import annotations

import logging
from typing import Optional, Tuple

from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

#: Reasons a chat cannot act on a machine. "More than one machine" is not one
#: of them: that is a question the user answers in their next message.
UNREACHABLE_REASONS = {"device_offline", "no_agent"}


def _device_name(db: Session, device_id: Optional[str]) -> str:
    if not device_id:
        return "the user's machine"
    from app.models.device import DeviceDB

    device = db.query(DeviceDB).filter(DeviceDB.device_id == device_id).first()
    return (device.name if device and device.name else device_id)


async def raise_unreachable_device_ticket(
    db: Session,
    *,
    user_email: str,
    reported_problem: Optional[str],
    device_id: Optional[str] = None,
    reason: str = "device_offline",
    existing_ticket_id: Optional[int] = None,
) -> Tuple[Optional[int], Optional[str]]:
    """Raise and assign a ticket for a machine that cannot be reached.

    Returns ``(ticket_id, assigned_to)``. When the conversation or remediation
    already has a ticket, that one is used - the same problem does not become
    two jobs.

    Never raises. A ticket that could not be written must not take the answer
    away from the user, but it must be visible in the log.
    """
    if existing_ticket_id:
        return existing_ticket_id, None

    from app.models.ticket import TicketCategory, TicketCreate, TicketPriority
    from app.services.ticket_service import TicketService

    problem = (reported_problem or "").strip() or "No description was given."
    machine = _device_name(db, device_id)

    if reason == "no_agent":
        title = "Set up the AutoOps agent on this user's machine"
        description = (
            f"The user reported: {problem}\n\n"
            "No AutoOps agent is enrolled for this user, so no diagnostic or "
            "remediation could be run on their machine. They were advised in "
            "chat and this ticket was raised for someone to follow up."
        )
        category, priority = TicketCategory.SOFTWARE, TicketPriority.MEDIUM
    else:
        title = f"{machine} is not responding - needs someone to look at it"
        description = (
            f"The user reported: {problem}\n\n"
            f"The AutoOps agent on {machine} did not answer, so nothing could "
            "be run or measured on it remotely, and it is not known whether "
            "anything on that machine changed. A machine that cannot be "
            "reached may be switched off, off the network, or faulty."
        )
        category, priority = TicketCategory.HARDWARE, TicketPriority.HIGH

    try:
        result = TicketService.create_ticket(
            db=db,
            ticket_data=TicketCreate(
                title=title,
                description=description,
                user_email=user_email,
                priority=priority,
                category=category,
                device_id=device_id,
            ),
        )
        ticket = result.get("ticket")
        if ticket is None:
            return None, None

        # Creating a ticket does not assign it - assignment is its own step,
        # reached when the assistant cannot resolve something itself, which is
        # exactly here. On a worker thread because the chooser calls the model,
        # and a model call on the event loop stops the server answering
        # anything else, the agents' own polls included.
        from app.services.assignment_service import get_assignment_service

        assignment = await run_in_threadpool(
            get_assignment_service().assign_ticket, ticket, db
        ) or {}
        # The two paths disagree on the key: the chooser returns agent_email,
        # the rule-based fallback returns assigned_to.
        assigned_to = assignment.get("assigned_to") or assignment.get("agent_email")
        db.commit()

        logger.info(
            "[ESCALATION] Unreachable device %s -> ticket #%s assigned to %s",
            device_id or "(none)", ticket.id, assigned_to or "nobody",
        )
        return ticket.id, assigned_to
    except Exception as exc:
        logger.error("[ESCALATION] Could not raise ticket for unreachable device: %s", exc)
        return None, None


def _least_busy_expert(db: Session, exclude_email: str):
    """An active user allowed to approve a high-risk action, other than the requester.

    Chosen by rule, not by the model. The assignment chooser may pick a first-line
    agent, and a first-line agent cannot approve a high-risk action - the ticket
    would sit with someone who has no way to act on it. The requester is excluded
    for the same reason approval excludes them: high risk needs a second person.
    """
    from app.models.user import UserDB
    from app.services.remediation_service import EXPERT_ROLES

    experts = (
        db.query(UserDB)
        .filter(UserDB.role.in_(EXPERT_ROLES))
        .filter(UserDB.is_active.is_(True))
        .filter(UserDB.email != exclude_email)
        .all()
    )
    return min(experts, key=lambda u: u.current_workload or 0, default=None)


def raise_blocked_action_ticket(
    db: Session,
    *,
    user_email: str,
    reported_problem: Optional[str],
    action_name: str,
    remediation_id: Optional[int],
    category: Optional[str] = None,
    device_id: Optional[str] = None,
    existing_ticket_id: Optional[int] = None,
) -> Tuple[Optional[int], Optional[str]]:
    """Put a high-risk action that was blocked in front of an IT expert.

    The chat used to tell the user a blocked action had been "sent to an IT
    expert" when nothing had been sent: no ticket, no assignee, and a pending
    list no screen showed. This makes that sentence true.

    Returns ``(ticket_id, assigned_to)``. ``assigned_to`` is None when no expert
    is available, and the caller must then not claim anyone has it.

    The action stays blocked. A ticket decides who looks at it, never whether it
    runs - approval still needs an expert's own token.

    Never raises, like the unreachable-device path.
    """
    from app.models.remediation import RemediationRequestDB
    from app.models.ticket import TicketCategory, TicketCreate, TicketDB, TicketPriority
    from app.services.ticket_service import TicketService

    problem = (reported_problem or "").strip() or "No description was given."
    machine = _device_name(db, device_id)
    note = (
        f"A high-risk action was proposed and blocked: {action_name} on {machine} "
        f"(remediation #{remediation_id}). Nothing was run. It needs an IT "
        "expert's approval, or another way to fix the problem."
    )

    try:
        expert = _least_busy_expert(db, exclude_email=user_email)
        ticket = None

        if existing_ticket_id:
            # The conversation already has a job. Add the blocked action to it
            # rather than open a second one, and only assign it if nobody holds it.
            ticket = db.query(TicketDB).filter(TicketDB.id == existing_ticket_id).first()
            if ticket is not None:
                ticket.description = f"{ticket.description or ''}\n\n{note}".strip()
                if not ticket.assigned_to and expert is not None:
                    ticket.assigned_to = expert.email
                    expert.current_workload = (expert.current_workload or 0) + 1

        if ticket is None:
            try:
                ticket_category = TicketCategory((category or "").lower())
            except ValueError:
                ticket_category = TicketCategory.OTHER
            result = TicketService.create_ticket(
                db=db,
                ticket_data=TicketCreate(
                    title=f"Approval needed: {action_name} on {machine}",
                    description=f"The user reported: {problem}\n\n{note}",
                    user_email=user_email,
                    priority=TicketPriority.MEDIUM,
                    category=ticket_category,
                    device_id=device_id,
                    assigned_to=expert.email if expert is not None else None,
                ),
            )
            ticket = result.get("ticket")
            if ticket is None:
                return None, None
            if expert is not None:
                expert.current_workload = (expert.current_workload or 0) + 1

        if remediation_id is not None:
            request = db.query(RemediationRequestDB).filter(
                RemediationRequestDB.id == remediation_id
            ).first()
            if request is not None and not request.ticket_id:
                request.ticket_id = ticket.id

        db.commit()
        logger.info(
            "[ESCALATION] Blocked action %s -> ticket #%s assigned to %s",
            remediation_id, ticket.id, ticket.assigned_to or "nobody",
        )
        return ticket.id, ticket.assigned_to
    except Exception as exc:
        db.rollback()
        logger.error("[ESCALATION] Could not raise ticket for blocked action: %s", exc)
        return None, None
