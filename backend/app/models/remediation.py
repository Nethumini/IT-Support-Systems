"""Persistence for remediation requests.

One row per proposed remediation, carrying the whole trail: the diagnosis and
the evidence behind it, the risk factors and the score they produced, who
approved it, what the pre-checks said, what execution did, and whether the
problem was actually solved afterwards.

Replacing the previous in-memory dictionary matters for two reasons. Pending
approvals used to vanish on restart, and nothing could be measured afterwards -
thesis chapter 6 needs every one of these fields to compute its results.

Approval is bound to a **single-use token** (thesis 5.3.4, TC07). The token
carries a fingerprint of the exact action and parameters that were approved, so
changing either one invalidates it and sends the request back for reassessment.
Approving "restart the print spooler" must never authorise "restart the domain
controller".
"""
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.core.database import Base

#: How long an approval stays valid. Short by design: an approval granted on a
#: stale view of the system should not be usable an hour later.
APPROVAL_TTL_MINUTES = 15


class RemediationStatus(str, Enum):
    """Lifecycle of a remediation request (novelty.md section 5)."""

    PENDING_ASSESSMENT = "pending_assessment"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    READY_FOR_EXECUTION = "ready_for_execution"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    ESCALATED = "escalated"

    @property
    def is_terminal(self) -> bool:
        return self in {
            RemediationStatus.COMPLETED,
            RemediationStatus.FAILED,
            RemediationStatus.REJECTED,
            RemediationStatus.ROLLED_BACK,
            RemediationStatus.ESCALATED,
        }


def fingerprint(
    action_id: str,
    parameters: Optional[Dict[str, Any]],
    device_id: Optional[str] = None,
) -> str:
    """Stable hash of exactly what was approved.

    Parameters are sorted so key order cannot change the fingerprint, and
    values are stringified so ``{"pid": 4812}`` and ``{"pid": "4812"}`` agree -
    they name the same process, and an approval should survive that difference.

    ``device_id`` is part of the hash because novelty.md section 5 binds
    approval to the *target resources*, not only to the action. Approving a
    service restart on one laptop must not authorise the same restart on
    somebody else's machine. ``None`` means the host running the backend, which
    is a distinct target from any enrolled device and hashes differently.
    """
    payload = {
        "action_id": action_id,
        "parameters": {str(k): str(v) for k, v in sorted((parameters or {}).items())},
        "device_id": device_id,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class RemediationRequestDB(Base):
    """A proposed remediation and everything that happened to it."""

    __tablename__ = "remediation_requests"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # --- who and what --------------------------------------------------------
    user_email = Column(String, index=True, nullable=False)
    ticket_id = Column(Integer, index=True, nullable=True)
    session_id = Column(String, index=True, nullable=True)

    reported_problem = Column(Text, nullable=False)
    diagnosis = Column(Text, nullable=True)
    #: KB article ids the diagnosis rests on, as returned to the user.
    evidence = Column(JSON, nullable=True)

    action_id = Column(String, index=True, nullable=False)
    parameters = Column(JSON, nullable=True)

    #: Which machine this runs on. NULL means the host running the backend,
    #: which is the behaviour every existing row was written under. A value
    #: names an enrolled device, and the agent on that device runs the action.
    device_id = Column(String, index=True, nullable=True)
    #: Hash of action + parameters, used to bind the approval to this exact act.
    action_fingerprint = Column(String, index=True, nullable=False)

    # --- risk ----------------------------------------------------------------
    risk_level = Column(String, index=True, nullable=True)
    risk_score = Column(Float, nullable=True)
    #: Full factor vector, weights, overrides and policy version, so the same
    #: input can be re-scored during evaluation (thesis 5.3.3).
    risk_assessment = Column(JSON, nullable=True)
    approval_route = Column(String, nullable=True)

    # --- approval ------------------------------------------------------------
    status = Column(String, index=True, nullable=False, default=RemediationStatus.PENDING_ASSESSMENT.value)
    approver_email = Column(String, nullable=True)
    approver_role = Column(String, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    approval_token = Column(String, index=True, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    token_used_at = Column(DateTime(timezone=True), nullable=True)

    # --- verification and execution -----------------------------------------
    pre_check = Column(JSON, nullable=True)
    execution_result = Column(JSON, nullable=True)
    post_check = Column(JSON, nullable=True)
    verification_status = Column(String, index=True, nullable=True)

    rollback_attempted = Column(Boolean, default=False)
    rollback_result = Column(JSON, nullable=True)
    escalation_reason = Column(Text, nullable=True)

    executed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # --- token handling ------------------------------------------------------

    def issue_token(self, ttl_minutes: int = APPROVAL_TTL_MINUTES) -> str:
        """Mint a single-use approval token bound to this request."""
        token = secrets.token_urlsafe(32)
        self.approval_token = token
        self.token_expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        self.token_used_at = None
        return token

    def token_error(
        self,
        token: str,
        action_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Why this token cannot be used, or ``None`` if it is valid.

        Checks identity, expiry, single use, and that the action and parameters
        still match what was approved.
        """
        if not self.approval_token:
            return "No approval token has been issued for this request."
        if not token or not secrets.compare_digest(token, self.approval_token):
            return "Approval token does not match this request."
        if self.token_used_at is not None:
            return "Approval token has already been used. Approvals are single-use."

        expires = self.token_expires_at
        if expires is not None:
            if expires.tzinfo is not None:
                expires = expires.replace(tzinfo=None)
            if datetime.utcnow() > expires:
                return "Approval token has expired. Re-assess and request approval again."

        if action_id is not None:
            current = fingerprint(action_id, parameters, self.device_id)
            if current != self.action_fingerprint:
                return (
                    "The action or its parameters changed since approval. "
                    "The request must be re-assessed before it can run."
                )
        return None

    def consume_token(self) -> None:
        """Mark the token used. Called once, immediately before execution."""
        self.token_used_at = datetime.utcnow()

    # --- serialisation -------------------------------------------------------

    def to_dict(self, include_token: bool = False) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_email": self.user_email,
            "ticket_id": self.ticket_id,
            "session_id": self.session_id,
            "reported_problem": self.reported_problem,
            "diagnosis": self.diagnosis,
            "evidence": self.evidence,
            "action_id": self.action_id,
            "parameters": self.parameters,
            "device_id": self.device_id,
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "risk_assessment": self.risk_assessment,
            "approval_route": self.approval_route,
            "status": self.status,
            "approver_email": self.approver_email,
            "approver_role": self.approver_role,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "rejection_reason": self.rejection_reason,
            "pre_check": self.pre_check,
            "execution_result": self.execution_result,
            "post_check": self.post_check,
            "verification_status": self.verification_status,
            "rollback_attempted": self.rollback_attempted,
            "rollback_result": self.rollback_result,
            "escalation_reason": self.escalation_reason,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
        if include_token:
            data["approval_token"] = self.approval_token
            data["token_expires_at"] = self.token_expires_at.isoformat() if self.token_expires_at else None
        return data
