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
