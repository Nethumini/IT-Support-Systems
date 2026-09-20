"""Orchestrates one remediation from proposal to verified outcome.

The flow, as thesis 12 sets it out:

    propose -> assess risk -> route for approval -> pre-check
            -> execute -> post-check -> resolve, roll back or escalate

Each stage is a separate method so a request can pause between them - a medium
risk action waits for a person, and that wait may outlive the process. State
lives in the database, not in memory.

Two rules hold throughout:

* **Reasoning is separated from authority.** An agent may propose an action.
  Only this service, the risk engine and a human may authorise one. Nothing
  here accepts a command string.
* **Completion is not resolution.** Execution returning success moves the
  request to post-check, never straight to completed. Only observed state
  decides whether the problem is solved.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.audit_log import AuditAction
from app.models.remediation import (
    RemediationRequestDB,
    RemediationStatus,
    fingerprint,
)
from app.services.execution import ExecutionError, get_driver
from app.services.risk_engine import (
    ApprovalRoute,
    RiskEngine,
    RiskFactors,
    RiskLevel,
)
from app.services.verification import (
    PostCheckStatus,
    PreCheckStatus,
    VerificationService,
)

logger = logging.getLogger(__name__)

#: Roles permitted to approve a HIGH-risk action. A second principal is always
#: required: the proposer may not approve their own request.
EXPERT_ROLES = {"support_l2", "support_l3", "it_admin", "system_admin"}


class RemediationError(Exception):
    """Raised when a caller asks for something the workflow forbids."""


class RemediationService:
    """Drives a remediation request through its lifecycle."""

    def __init__(
        self,
        risk_engine: Optional[RiskEngine] = None,
        verifier: Optional[VerificationService] = None,
        driver=None,
    ) -> None:
        self.risk_engine = risk_engine or RiskEngine()
        self.verifier = verifier or VerificationService()
        self._driver = driver

    @property
    def driver(self):
        return self._driver if self._driver is not None else get_driver()

    # -- audit ---------------------------------------------------------------

    def _audit(
        self,
        db: Session,
        request: RemediationRequestDB,
        action: AuditAction,
        success: str,
        details: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record one step. Never raises - a failed audit write must not abort
        a remediation, but it must be visible in the logs."""
        try:
            from app.services.audit_service import AuditService

            metadata = {
                "remediation_id": request.id,
                "action_id": request.action_id,
                "status": request.status,
                "risk_level": request.risk_level,
            }
            if extra:
                metadata.update(extra)

            AuditService.log_action(
                db=db,
                action=action,
                success=success,
                user_email=request.user_email,
                resource_type="remediation",
                resource_id=str(request.id),
                details=details,
                action_metadata=metadata,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("[REMEDIATION] Audit write failed: %s", exc)

    # -- 1. propose ----------------------------------------------------------

    def propose(
        self,
        db: Session,
        *,
        user_email: str,
        reported_problem: str,
        action_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        diagnosis: Optional[str] = None,
        evidence: Optional[List[Dict[str, Any]]] = None,
        ticket_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> RemediationRequestDB:
        """Record a proposed action. Nothing is assessed or run yet."""
        parameters = parameters or {}
        request = RemediationRequestDB(
            user_email=user_email,
            ticket_id=ticket_id,
            session_id=session_id,
            reported_problem=reported_problem,
            diagnosis=diagnosis,
            evidence=evidence or [],
            action_id=action_id,
            parameters=parameters,
            action_fingerprint=fingerprint(action_id, parameters),
            status=RemediationStatus.PENDING_ASSESSMENT.value,
        )
        db.add(request)
        db.commit()
        db.refresh(request)

        self._audit(
            db, request, AuditAction.REMEDIATION_PROPOSED, "success",
            f"Proposed {action_id} for: {reported_problem[:120]}",
            {"evidence_ids": [e.get("kb_id") for e in (evidence or [])]},
        )
        return request

    # -- 2. assess -----------------------------------------------------------

    def assess(
        self,
        db: Session,
        request: RemediationRequestDB,
        factors: RiskFactors,
        *,
        catalogue_risk: Optional[RiskLevel] = None,
        is_privileged_security_action: bool = False,
        has_required_evidence: bool = True,
        rollback_available: Optional[bool] = None,
    ) -> RemediationRequestDB:
        """Score the risk and decide who, if anyone, may approve it."""
        if rollback_available is None:
            contract = self.verifier.get_contract(request.action_id)
            rollback_available = bool(contract and contract.has_rollback)

        assessment = self.risk_engine.assess(
            factors,
            catalogue_risk=catalogue_risk,
            is_privileged_security_action=is_privileged_security_action,
            has_required_evidence=has_required_evidence,
            rollback_available=rollback_available,
        )

        request.risk_level = assessment.level.value
        request.risk_score = assessment.weighted_score
        request.risk_assessment = assessment.to_dict()
        request.approval_route = assessment.route.value

        if assessment.route is ApprovalRoute.AUTO_CANDIDATE:
            # Classification is not permission: pre-checks still gate execution.
            request.status = RemediationStatus.READY_FOR_EXECUTION.value
        elif assessment.route is ApprovalRoute.USER_APPROVAL:
            request.status = RemediationStatus.AWAITING_APPROVAL.value
        else:
            request.status = RemediationStatus.BLOCKED.value

        db.commit()
        db.refresh(request)

        self._audit(
            db, request, AuditAction.REMEDIATION_ASSESSED, "success",
            f"Risk {assessment.level.value.upper()} (score {assessment.weighted_score:.3f}) "
            f"-> {assessment.route.value}",
            {
                "risk_factors": assessment.factors.as_dict(),
                "overrides": assessment.overrides,
                "policy_version": assessment.policy_version,
            },
        )
        return request

    # -- 3. approve or reject ------------------------------------------------

    def approve(
        self,
        db: Session,
        request: RemediationRequestDB,
        *,
        approver_email: str,
        approver_role: str,
    ) -> Tuple[RemediationRequestDB, str]:
        """Approve a request and issue its single-use token.

        Returns the request and the token. The token is the only thing that
        authorises execution, and it authorises exactly this action with
        exactly these parameters.
        """
        status = RemediationStatus(request.status)

        if status is RemediationStatus.BLOCKED:
            # High risk: needs an expert, and never the person who proposed it.
            if approver_role.lower() not in EXPERT_ROLES:
                raise RemediationError(
                    f"Role {approver_role!r} cannot approve a high-risk action. "
                    f"Requires one of: {', '.join(sorted(EXPERT_ROLES))}."
                )
            if approver_email.lower() == (request.user_email or "").lower():
                raise RemediationError(
                    "A high-risk action cannot be approved by the person who requested it. "
                    "A second principal is required."
                )
        elif status is not RemediationStatus.AWAITING_APPROVAL:
            raise RemediationError(
                f"Request is {request.status}, which does not accept approval."
            )

        request.approver_email = approver_email
        request.approver_role = approver_role
        request.approved_at = datetime.utcnow()
        request.status = RemediationStatus.APPROVED.value
        token = request.issue_token()
        db.commit()
        db.refresh(request)

        self._audit(
            db, request, AuditAction.REMEDIATION_APPROVED, "success",
            f"Approved by {approver_email} ({approver_role})",
            {"approver_role": approver_role, "token_expires_at": str(request.token_expires_at)},
        )
        return request, token

    def reject(
        self,
        db: Session,
        request: RemediationRequestDB,
        *,
        approver_email: str,
        reason: str,
    ) -> RemediationRequestDB:
        """Reject a request. A rejected action can never execute."""
        request.status = RemediationStatus.REJECTED.value
        request.approver_email = approver_email
        request.rejection_reason = reason
        request.approval_token = None
        request.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(request)

        self._audit(
            db, request, AuditAction.REMEDIATION_REJECTED, "denied",
            f"Rejected by {approver_email}: {reason}",
        )
        return request

    # -- 4. execute ----------------------------------------------------------

    def execute(
        self,
        db: Session,
        request: RemediationRequestDB,
        *,
        token: Optional[str] = None,
        evidence_sufficient: bool = True,
    ) -> RemediationRequestDB:
        """Run the action, then verify whether the problem actually went away.

        Refuses when the request is not executable, when the token is invalid,
        or when any pre-check fails. Never marks a request completed on the
        strength of the command's own exit status.
        """
        status = RemediationStatus(request.status)

        if status is RemediationStatus.APPROVED:
            error = request.token_error(token or "", request.action_id, request.parameters)
            if error:
                self._audit(db, request, AuditAction.REMEDIATION_PRECHECK_FAILED, "denied",
                            f"Execution refused: {error}")
                raise RemediationError(error)
            approval_granted = True
        elif status is RemediationStatus.READY_FOR_EXECUTION:
            # Low risk under policy: no human token, but every other gate applies.
            approval_granted = True
        else:
            raise RemediationError(
                f"Request is {request.status} and cannot be executed. "
                "Only approved or auto-eligible requests may run."
            )

        if request.token_used_at is not None and status is RemediationStatus.APPROVED:
            raise RemediationError("This approval has already been used.")

        # --- pre-checks ---
        pre = self.verifier.verify_before(
            request.action_id,
            request.parameters or {},
            self.driver,
            approval_granted=approval_granted,
            evidence_sufficient=evidence_sufficient,
            risk_assessment_current=(
                fingerprint(request.action_id, request.parameters) == request.action_fingerprint
            ),
        )
        request.pre_check = pre.to_dict()

        if pre.status is PreCheckStatus.FAILED:
            request.status = RemediationStatus.FAILED.value
            request.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(request)
            self._audit(
                db, request, AuditAction.REMEDIATION_PRECHECK_FAILED, "denied",
                "Pre-check failed; executor not called: " + "; ".join(pre.failure_reasons),
                {"pre_check_failures": pre.failure_reasons},
            )
            return request

        # --- execute ---
        if status is RemediationStatus.APPROVED:
            request.consume_token()
        request.status = RemediationStatus.EXECUTING.value
        request.executed_at = datetime.utcnow()
        db.commit()

        try:
            result = self.driver.execute(request.action_id, request.parameters or {})
        except ExecutionError as exc:
            request.status = RemediationStatus.FAILED.value
            request.completed_at = datetime.utcnow()
            request.escalation_reason = str(exc)
            db.commit()
            db.refresh(request)
            self._audit(db, request, AuditAction.REMEDIATION_FAILED, "failure",
                        f"Execution refused by driver: {exc}")
            return request

        request.execution_result = result.to_dict()

        # --- post-checks: did the problem actually go away? ---
        post = self.verifier.verify_after(request.action_id, result)
        request.post_check = post.to_dict()
        request.verification_status = post.status.value

        if post.status is PostCheckStatus.VERIFIED_SUCCESS:
            request.status = RemediationStatus.COMPLETED.value
            request.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(request)
            self._audit(db, request, AuditAction.REMEDIATION_VERIFIED, "success",
                        f"Verified resolved: {post.reason}",
                        {"verification": post.status.value})
            self._propose_knowledge(db, request)
            return request

        # Failure or inconclusive: recover, never silently succeed.
        return self._recover(db, request, post_reason=post.reason, post_status=post.status)

    # -- 5. recover ----------------------------------------------------------

    def _recover(
        self,
        db: Session,
        request: RemediationRequestDB,
        *,
        post_reason: str,
        post_status: PostCheckStatus,
    ) -> RemediationRequestDB:
        """Roll back where a rollback is defined and safe, otherwise escalate.

        Rollback is never improvised. An action without a registered rollback
        escalates with its evidence, which thesis 9 requires.
        """
        contract = self.verifier.get_contract(request.action_id)

        if contract is not None and contract.has_rollback:
            request.rollback_attempted = True
            try:
                rollback = self.driver.execute(contract.rollback_action_id, request.parameters or {})
                request.rollback_result = rollback.to_dict()
                request.status = RemediationStatus.ROLLED_BACK.value
                request.completed_at = datetime.utcnow()
                db.commit()
                db.refresh(request)
                self._audit(
                    db, request, AuditAction.REMEDIATION_ROLLED_BACK, "failure",
                    f"Remediation not verified ({post_status.value}); rolled back via "
                    f"{contract.rollback_action_id}. {post_reason}",
                    {"rollback_action_id": contract.rollback_action_id},
                )
                return request
            except Exception as exc:
                request.rollback_result = {"error": str(exc)}
                logger.error("[REMEDIATION] Rollback failed for %s: %s", request.id, exc)

        request.status = RemediationStatus.ESCALATED.value
        request.escalation_reason = (
            f"Remediation {post_status.value}: {post_reason} "
            f"No safe rollback is defined for {request.action_id}."
        )
        request.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(request)

        self._audit(
            db, request, AuditAction.REMEDIATION_ESCALATED, "failure",
            request.escalation_reason,
            {"verification": post_status.value, "rollback_attempted": request.rollback_attempted},
        )
        return request

    # -- learning ------------------------------------------------------------

    @staticmethod
    def _propose_knowledge(db: Session, request: RemediationRequestDB) -> None:
        """Offer a draft article when a verified fix had no existing procedure.

        A draft only. It is not searchable and cannot be cited until a reviewer
        approves it - otherwise the system would start grounding answers on its
        own unreviewed guesses.

        Never raises: failing to propose an article must not undo a remediation
        that actually worked.
        """
        try:
            from app.services.knowledge_service import knowledge_service

            knowledge_service.propose_from_remediation(db, request)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("[REMEDIATION] Could not propose knowledge draft: %s", exc)

    # -- queries -------------------------------------------------------------

    def get(self, db: Session, remediation_id: int) -> Optional[RemediationRequestDB]:
        return db.query(RemediationRequestDB).filter(
            RemediationRequestDB.id == remediation_id
        ).first()

    def pending_approvals(
        self, db: Session, *, user_email: Optional[str] = None
    ) -> List[RemediationRequestDB]:
        """Requests waiting on a person, newest first."""
        query = db.query(RemediationRequestDB).filter(
            RemediationRequestDB.status.in_([
                RemediationStatus.AWAITING_APPROVAL.value,
                RemediationStatus.BLOCKED.value,
            ])
        )
        if user_email:
            query = query.filter(RemediationRequestDB.user_email == user_email)
        return query.order_by(RemediationRequestDB.created_at.desc()).all()

    def history(
        self, db: Session, *, user_email: Optional[str] = None, limit: int = 50
    ) -> List[RemediationRequestDB]:
        query = db.query(RemediationRequestDB)
        if user_email:
            query = query.filter(RemediationRequestDB.user_email == user_email)
        return query.order_by(RemediationRequestDB.created_at.desc()).limit(limit).all()
