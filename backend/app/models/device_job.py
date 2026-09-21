"""One unit of work handed to an endpoint agent.

The server never calls out to an agent. The agent asks "is there anything for
me?", takes one job, runs it, and posts back what happened. That direction
matters practically - a user's laptop is behind a router with no open port - and
it matters for safety, because nothing the agent sends can start work.

**A job carries an action id, never a command string.** This is the same rule
the driver interface enforces locally (thesis 5.3.4): if an agent could be sent
arbitrary text to run, the allow-list would mean nothing, and a compromised
server would become remote code execution on every enrolled machine. The agent
looks the id up in its own copy of the catalogue and refuses anything it does
not recognise.

A job is also the audit record of the remote half: who it was for, what was
asked, when it was taken, and what came back.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, Integer, JSON, String
from sqlalchemy.sql import func

from app.core.database import Base

#: How long a job may sit unclaimed before it is abandoned. Short, because the
#: user is waiting: a machine that is asleep should fail the remediation
#: honestly rather than run it minutes later against changed state.
JOB_TTL_SECONDS = 90


class JobKind(str, Enum):
    """What the agent is being asked to do."""

    #: Run a registered remediation action.
    EXECUTE = "execute"
    #: Read observable state for the before/after snapshots. Changes nothing.
    CAPTURE_STATE = "capture_state"


class JobStatus(str, Enum):
    QUEUED = "queued"
    TAKEN = "taken"
    DONE = "done"
    FAILED = "failed"
    #: Nobody collected it in time, or the agent took it and never answered.
    EXPIRED = "expired"


class DeviceJobDB(Base):
    """A single request from the server to one device."""

    __tablename__ = "device_jobs"

    id = Column(Integer, primary_key=True, index=True)

    #: Opaque public id. The agent addresses a job by this, never by row id.
    job_id = Column(String, unique=True, index=True, nullable=False)

    #: The device this is for. Set by the server from the remediation's target,
    #: and matched against the agent's own credential before handing it over.
    device_id = Column(String, index=True, nullable=False)

    #: The remediation this belongs to, when there is one. State captures taken
    #: before a request exists have none.
    remediation_id = Column(Integer, index=True, nullable=True)

    kind = Column(String, nullable=False, default=JobKind.EXECUTE.value)

    #: For EXECUTE: the registered action id. For CAPTURE_STATE: unused.
    action_id = Column(String, nullable=True)
    #: For CAPTURE_STATE: which scope to read, e.g. "disk".
    scope = Column(String, nullable=True)
    parameters = Column(JSON, nullable=True)

    status = Column(String, index=True, nullable=False, default=JobStatus.QUEUED.value)

    #: Whatever the agent sent back: an ExecutionResult for EXECUTE, a state
    #: mapping for CAPTURE_STATE, or an error description on failure.
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    taken_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # --- lifecycle -----------------------------------------------------------

    def mark_taken(self) -> None:
        self.status = JobStatus.TAKEN.value
        self.taken_at = datetime.utcnow()

    def mark_done(self, result: Dict[str, Any]) -> None:
        self.status = JobStatus.DONE.value
        self.result = result
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error: str, result: Optional[Dict[str, Any]] = None) -> None:
        self.status = JobStatus.FAILED.value
        self.error = error
        self.result = result
        self.completed_at = datetime.utcnow()

    def mark_expired(self) -> None:
        self.status = JobStatus.EXPIRED.value
        self.error = "The device did not respond in time."
        self.completed_at = datetime.utcnow()

    @property
    def is_finished(self) -> bool:
        return self.status in (
            JobStatus.DONE.value,
            JobStatus.FAILED.value,
            JobStatus.EXPIRED.value,
        )

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        """Whether the deadline has passed. Naive UTC throughout, as elsewhere."""
        if self.expires_at is None:
            return False
        deadline = self.expires_at
        if deadline.tzinfo is not None:
            deadline = deadline.replace(tzinfo=None)
        return (now or datetime.utcnow()) > deadline

    # --- serialisation -------------------------------------------------------

    def to_agent_dict(self) -> Dict[str, Any]:
        """What the agent is told. Only what it needs to do the work."""
        return {
            "job_id": self.job_id,
            "kind": self.kind,
            "action_id": self.action_id,
            "scope": self.scope,
            "parameters": self.parameters or {},
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "device_id": self.device_id,
            "remediation_id": self.remediation_id,
            "kind": self.kind,
            "action_id": self.action_id,
            "scope": self.scope,
            "parameters": self.parameters,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "taken_at": self.taken_at.isoformat() if self.taken_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


def new_job_id() -> str:
    return f"job_{secrets.token_urlsafe(16)}"


def deadline(ttl_seconds: int = JOB_TTL_SECONDS) -> datetime:
    return datetime.utcnow() + timedelta(seconds=ttl_seconds)
