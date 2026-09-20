"""Knowledge review API: read drafts, approve or reject them.

Approving a draft changes what the system will cite as company procedure to
every future user, so it is restricted to support and admin roles. A reviewer
may edit the text before approving - a machine-written draft usually needs it.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.knowledge import DraftStatus
from app.models.role import Role
from app.services.knowledge_service import KnowledgeError, knowledge_service

logger = logging.getLogger(__name__)
router = APIRouter()

#: Roles that may decide what becomes organisational knowledge.
REVIEWER_ROLES = {
    Role.SUPPORT_L2.value,
    Role.SUPPORT_L3.value,
    Role.IT_ADMIN.value,
    Role.SYSTEM_ADMIN.value,
}


class DraftEdits(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    issue_pattern: Optional[str] = None
    summary: Optional[str] = None
    resolution_steps: Optional[List[str]] = None


class ApproveRequest(BaseModel):
    draft_id: int
    note: Optional[str] = None
    edits: Optional[DraftEdits] = None


class RejectRequest(BaseModel):
    draft_id: int
    reason: str = Field(..., min_length=1)


class ManualDraft(BaseModel):
    title: str = Field(..., min_length=3)
    category: str
    resolution_steps: List[str] = Field(..., min_length=1)
    issue_pattern: Optional[str] = None
    summary: Optional[str] = None


def _require_reviewer(user) -> str:
    role = getattr(user.role, "value", user.role)
    if role not in REVIEWER_ROLES:
        raise HTTPException(
            status_code=403,
            detail=(
                "Approving knowledge changes what the system tells every user. "
                f"Requires one of: {', '.join(sorted(REVIEWER_ROLES))}."
            ),
        )
    return role


def _load(db: Session, draft_id: int):
    draft = knowledge_service.get(db, draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail=f"Draft {draft_id} not found")
    return draft


@router.get("/drafts")
async def list_drafts(
    pending_only: bool = Query(True),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Proposed articles. By default, only those still awaiting review."""
    drafts = (
        knowledge_service.pending(db, limit=limit)
        if pending_only
        else knowledge_service.history(db, limit=limit)
    )
    return {"count": len(drafts), "drafts": [d.to_dict() for d in drafts]}


@router.get("/drafts/{draft_id}")
async def get_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return _load(db, draft_id).to_dict()


@router.post("/drafts", status_code=status.HTTP_201_CREATED)
async def create_draft(
    payload: ManualDraft,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Write a draft by hand. Still needs review before it is searchable."""
    try:
        draft = knowledge_service.propose_manual(
            db,
            title=payload.title,
            category=payload.category,
            resolution_steps=payload.resolution_steps,
            issue_pattern=payload.issue_pattern,
            summary=payload.summary,
            proposed_by=current_user.email,
        )
    except KnowledgeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return draft.to_dict()


@router.post("/drafts/approve")
async def approve_draft(
    payload: ApproveRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Approve a draft, giving it an article id and making it searchable."""
    _require_reviewer(current_user)
    draft = _load(db, payload.draft_id)

    edits = payload.edits.model_dump(exclude_none=True) if payload.edits else None
    try:
        draft = knowledge_service.approve(
            db, draft,
            reviewer_email=current_user.email,
            note=payload.note,
            edited=edits,
        )
    except KnowledgeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return draft.to_dict()


@router.post("/drafts/reject")
async def reject_draft(
    payload: RejectRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Decline a draft. It stays on record and never becomes searchable."""
    _require_reviewer(current_user)
    draft = _load(db, payload.draft_id)
    try:
        draft = knowledge_service.reject(
            db, draft, reviewer_email=current_user.email, reason=payload.reason
        )
    except KnowledgeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return draft.to_dict()


@router.get("/learned")
async def list_learned_articles(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Approved articles the system learned from solved problems."""
    articles = knowledge_service.approved_articles(db)
    return {"count": len(articles), "articles": articles}


@router.get("/stats")
async def knowledge_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """How much knowledge was proposed, and how much a human accepted."""
    from app.models.knowledge import KnowledgeDraftDB

    rows = db.query(KnowledgeDraftDB).all()

    def count(predicate):
        return sum(1 for r in rows if predicate(r))

    approved = count(lambda r: r.status == DraftStatus.APPROVED.value)
    rejected = count(lambda r: r.status == DraftStatus.REJECTED.value)
    reviewed = approved + rejected

    return {
        "total_drafts": len(rows),
        "pending": count(lambda r: r.status == DraftStatus.PENDING.value),
        "approved": approved,
        "rejected": rejected,
        "machine_generated": count(lambda r: r.machine_generated),
        "written_by_people": count(lambda r: not r.machine_generated),
        # How often a reviewer accepted what the system proposed. A useful
        # measure of whether machine-drafted knowledge is worth the review time.
        "approval_rate": round(approved / reviewed, 3) if reviewed else None,
    }
