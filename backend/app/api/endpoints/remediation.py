"""Remediation API: propose, approve, execute, verify, review.

Every endpoint here requires authentication. The older ``/actions/*`` routes
accept a ``user_email`` string and trust it, which means anyone reaching the API
can approve anything for anyone. Nothing in this module does that: the approver
is taken from the verified JWT, never from the request body, because otherwise
the approval record proves nothing.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.remediation import RemediationStatus
from app.services.remediation_service import RemediationError, RemediationService
from app.services.risk_engine import RiskFactors
from app.services.risk_signals import has_required_evidence
from app.services.verification import CONTRACTS

logger = logging.getLogger(__name__)
router = APIRouter()
service = RemediationService()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RiskFactorInput(BaseModel):
    """Factors as a human states them: 3 = best for confidence and evidence.

    The engine inverts the two positive ratings itself, so a caller never has
    to remember which direction each field runs in.
    """

    impact: int = Field(..., ge=1, le=3, description="1 local, 2 contained, 3 organisation-wide")
    confidence_rating: int = Field(..., ge=1, le=3, description="3 = confident diagnosis")
    evidence_quality: int = Field(..., ge=1, le=3, description="3 = approved and corroborated")
    irreversibility: int = Field(..., ge=1, le=3, description="1 = tested rollback exists")
    affected_scope: int = Field(..., ge=1, le=3, description="1 = the user's own device")


class ProposeRequest(BaseModel):
    reported_problem: str
    action_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    diagnosis: Optional[str] = None
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    ticket_id: Optional[int] = None
    session_id: Optional[str] = None
    device_id: Optional[str] = Field(
        None,
        description=(
            "Machine to act on. Omit to use the host running the backend, "
            "which is the original behaviour."
        ),
    )
    factors: RiskFactorInput
    is_privileged_security_action: bool = False
    catalogue_risk: Optional[str] = Field(None, description="low, medium or high")


class ApproveRequest(BaseModel):
    remediation_id: int


class RejectRequest(BaseModel):
    remediation_id: int
    reason: str = Field(..., min_length=1)


class ExecuteRequest(BaseModel):
    remediation_id: int
    token: Optional[str] = Field(None, description="Required for approved requests")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _catalogue_risk(value: Optional[str]):
    if not value:
        return None
    from app.services.risk_engine import RiskLevel

    try:
        return RiskLevel(value.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown risk level: {value!r}")


def _resolve_device(db: Session, device_id: Optional[str], user) -> Optional[str]:
    """Check the caller may act on this machine, and that it can still be used.

    A user may target their own device. Anyone else needs the admin permission,
    because running a remediation on somebody else's laptop is a different act
    from running one on your own.
    """
    if device_id is None:
        return None

    from app.models.device import DeviceDB
    from app.models.role import Permission, Role, has_permission

    device = db.query(DeviceDB).filter(DeviceDB.device_id == device_id).first()
    if device is None or not device.is_active:
        raise HTTPException(
            status_code=404,
            detail="Device not found or has been revoked.",
        )

    is_owner = device.owner_email == user.email
    is_admin = has_permission(Role(user.role), Permission.SYSTEM_ADMIN)
    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=403,
            detail="You may only run remediations on your own device.",
        )

    return device.device_id


def _load(db: Session, remediation_id: int):
    request = service.get(db, remediation_id)
    if request is None:
        raise HTTPException(status_code=404, detail=f"Remediation {remediation_id} not found")
    return request


def _may_view(request, user) -> bool:
    """Owners see their own; support roles see everything."""
    from app.models.role import Role

    privileged = {
        Role.SUPPORT_L1.value, Role.SUPPORT_L2.value, Role.SUPPORT_L3.value,
        Role.IT_ADMIN.value, Role.SYSTEM_ADMIN.value,
    }
    role = getattr(user.role, "value", user.role)
    return request.user_email == user.email or role in privileged


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/actions")
async def list_available_actions(current_user=Depends(get_current_active_user)):
    """Actions that can be run through the verified path.

    An action absent here cannot be executed however it is requested - the
    catalogue is the allow-list.
    """
    return {
        "actions": [
            {
                "action_id": contract.action_id,
                "description": contract.description,
                "read_only": contract.read_only,
                "requires": list(contract.required_parameters),
                "has_rollback": contract.has_rollback,
                "verifiable": contract.postcondition is not None or contract.read_only,
            }
            for contract in sorted(CONTRACTS.values(), key=lambda c: c.action_id)
        ]
    }


@router.post("/propose", status_code=status.HTTP_201_CREATED)
async def propose_remediation(
    payload: ProposeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Propose an action and assess its risk in one step.

    Returns the request with its risk level and the route it must take. Nothing
    has been executed: a low-risk action is only *eligible* to run.
    """
    if payload.action_id not in CONTRACTS:
        raise HTTPException(
            status_code=400,
            detail=f"Action {payload.action_id!r} has no verification contract and cannot be run.",
        )

    request = service.propose(
        db,
        user_email=current_user.email,
        reported_problem=payload.reported_problem,
        action_id=payload.action_id,
        parameters=payload.parameters,
        diagnosis=payload.diagnosis,
        evidence=payload.evidence,
        ticket_id=payload.ticket_id,
        session_id=payload.session_id,
        device_id=_resolve_device(db, payload.device_id, current_user),
    )

    factors = RiskFactors.from_ratings(**payload.factors.model_dump())
    request = service.assess(
        db,
        request,
        factors,
        catalogue_risk=_catalogue_risk(payload.catalogue_risk),
        is_privileged_security_action=payload.is_privileged_security_action,
        has_required_evidence=has_required_evidence(payload.action_id, payload.evidence),
    )
    return request.to_dict()


@router.get("/pending")
async def list_pending(
    mine_only: bool = Query(False, description="Only requests I raised"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Requests waiting on a human decision."""
    requests = service.pending_approvals(
        db, user_email=current_user.email if mine_only else None
    )
    visible = [r for r in requests if _may_view(r, current_user)]
    return {"count": len(visible), "requests": [r.to_dict() for r in visible]}


@router.get("/history")
async def list_history(
    limit: int = Query(50, ge=1, le=200),
    mine_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Past remediations with their verification outcomes."""
    requests = service.history(
        db, user_email=current_user.email if mine_only else None, limit=limit
    )
    visible = [r for r in requests if _may_view(r, current_user)]
    return {"count": len(visible), "requests": [r.to_dict() for r in visible]}


@router.get("/{remediation_id}")
async def get_remediation(
    remediation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Full trail for one request: risk, evidence, checks, outcome."""
    request = _load(db, remediation_id)
    if not _may_view(request, current_user):
        raise HTTPException(status_code=403, detail="Not permitted to view this remediation")
    return request.to_dict()


@router.post("/approve")
async def approve_remediation(
    payload: ApproveRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Approve a request and receive its single-use execution token.

    The approver is the authenticated user. The token authorises exactly this
    action with exactly these parameters, once, within its expiry.
    """
    request = _load(db, payload.remediation_id)
    role = getattr(current_user.role, "value", current_user.role)

    try:
        request, token = service.approve(
            db, request, approver_email=current_user.email, approver_role=role
        )
    except RemediationError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    data = request.to_dict()
    data["approval_token"] = token
    return data


@router.post("/reject")
async def reject_remediation(
    payload: RejectRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Reject a request. It can never execute afterwards."""
    request = _load(db, payload.remediation_id)
    if not _may_view(request, current_user):
        raise HTTPException(status_code=403, detail="Not permitted to decide on this remediation")
    request = service.reject(
        db, request, approver_email=current_user.email, reason=payload.reason
    )
    return request.to_dict()


@router.post("/execute")
async def execute_remediation(
    payload: ExecuteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Run an approved or auto-eligible request, then verify the outcome.

    Returns the request with its post-check verdict. A ``completed`` status
    means the problem was observed to be solved; anything else means it was
    not, whatever the command reported.
    """
    request = _load(db, payload.remediation_id)
    if not _may_view(request, current_user):
        raise HTTPException(status_code=403, detail="Not permitted to execute this remediation")

    runner = service
    if request.device_id:
        # Bound to this request's machine. The driver is built per request
        # rather than read from configuration, because the target is a property
        # of the remediation, not of the server.
        from app.services.execution import AgentDriver

        runner = RemediationService(driver=AgentDriver(request.device_id))

    def _run():
        return runner.execute(
            db, request, token=payload.token, evidence_sufficient=bool(request.evidence)
        )

    try:
        if request.device_id:
            # The driver blocks waiting for the agent, and the agent collects
            # its work over this same API. Running that wait on the event loop
            # would stop the request it is waiting for from ever being served.
            result = await run_in_threadpool(_run)
        else:
            result = _run()
    except RemediationError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    return result.to_dict()


@router.get("/stats/summary")
async def remediation_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Counts for the evaluation chapter: outcomes, risk mix, approval load."""
    from app.models.remediation import RemediationRequestDB

    rows = db.query(RemediationRequestDB).all()
    total = len(rows)

    def count(predicate):
        return sum(1 for r in rows if predicate(r))

    executed = count(lambda r: r.execution_result is not None)
    verified = count(lambda r: r.verification_status == "verified_success")

    return {
        "total_requests": total,
        "by_risk_level": {
            level: count(lambda r, lv=level: r.risk_level == lv)
            for level in ("low", "medium", "high")
        },
        "by_status": {
            s.value: count(lambda r, sv=s.value: r.status == sv)
            for s in RemediationStatus
        },
        "executed": executed,
        "verified_resolved": verified,
        "verified_resolution_rate": round(verified / executed, 3) if executed else None,
        "blocked_or_escalated": count(
            lambda r: r.status in (RemediationStatus.BLOCKED.value, RemediationStatus.ESCALATED.value)
        ),
        "precheck_failures": count(
            lambda r: r.pre_check is not None and r.pre_check.get("status") == "failed"
        ),
        "required_human_approval": count(lambda r: r.approver_email is not None),
    }
