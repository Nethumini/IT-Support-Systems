"""Turning solved problems into approved knowledge.

The loop: a remediation is verified as having actually fixed something, no
existing article covered it, so a draft is proposed. A reviewer reads the
draft. Only on approval does it become searchable and citable.

Two rules hold the loop together, and both exist to stop the system learning
from itself:

1. **A draft is never retrievable.** Until a person approves it, it cannot be
   found, cited, or used to ground an answer.
2. **Only verified fixes are proposed.** A remediation that merely ran, or that
   ended inconclusive, teaches nothing worth keeping.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditAction
from app.models.knowledge import DraftStatus, KnowledgeDraftDB

logger = logging.getLogger(__name__)

#: Article ids continue the existing KB-NNN sequence.
ARTICLE_PREFIX = "KB-"


class KnowledgeError(Exception):
    """Raised when a review action is not allowed."""


class KnowledgeService:
    """Proposes, reviews and serves learned knowledge articles."""

    # -- proposing ------------------------------------------------------------

    def propose_from_remediation(
        self,
        db: Session,
        remediation,
        *,
        category: str = "other",
        steps: Optional[List[str]] = None,
        proposed_by: str = "system",
    ) -> Optional[KnowledgeDraftDB]:
        """Draft an article from a remediation that verifiably worked.

        Returns ``None`` when the remediation does not qualify: an unverified
        fix is not knowledge, and a problem an article already covered does not
        need a second one.
        """
        if remediation.verification_status != "verified_success":
            logger.debug(
                "[KNOWLEDGE] Not proposing from remediation %s: verification is %s",
                remediation.id, remediation.verification_status,
            )
            return None

        if remediation.evidence:
            # An article already covered this. Improving it is a separate,
            # human decision - silently adding a near-duplicate would make
            # retrieval worse, not better.
            return None

        existing = db.query(KnowledgeDraftDB).filter(
            KnowledgeDraftDB.remediation_id == remediation.id
        ).first()
        if existing is not None:
            return existing

        contract_steps = steps or self._steps_from_remediation(remediation)
        if not contract_steps:
            return None

        draft = KnowledgeDraftDB(
            title=self._title_from_problem(remediation.reported_problem),
            category=category,
            issue_pattern=remediation.reported_problem,
            summary=(
                f"Resolved by {remediation.action_id}, confirmed by post-action "
                f"verification. Proposed automatically from a verified fix."
            ),
            resolution_steps=contract_steps,
            source_problem=remediation.reported_problem,
            remediation_id=remediation.id,
            ticket_id=remediation.ticket_id,
            proposed_by=proposed_by,
            machine_generated=True,
            verification_status=remediation.verification_status,
            status=DraftStatus.PENDING.value,
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)

        self._audit(db, draft, AuditAction.KB_UPDATE, "success",
                    f"Draft proposed from remediation {remediation.id} (pending review)")
        logger.info("[KNOWLEDGE] Draft %s proposed from remediation %s",
                    draft.id, remediation.id)
        return draft

    @staticmethod
    def _steps_from_remediation(remediation) -> List[str]:
        """Describe what was actually done, in order, from the record."""
        from app.services.verification import CONTRACTS

        contract = CONTRACTS.get(remediation.action_id)
        description = contract.description if contract else remediation.action_id
        steps = [f"Confirm the reported symptom: {remediation.reported_problem}."]
        if remediation.diagnosis:
            steps.append(f"Check the diagnosis: {remediation.diagnosis[:200]}")
        steps.append(f"Apply the approved action: {description}.")
        post = (remediation.post_check or {}).get("expected")
        if post:
            steps.append(f"Verify the outcome: {post}.")
        steps.append("If the check fails, escalate with the before and after state.")
        return steps

    @staticmethod
    def _title_from_problem(problem: str) -> str:
        text = re.sub(r"\s+", " ", (problem or "").strip())
        if not text:
            return "Untitled issue"
        title = text[0].upper() + text[1:]
        return title[:117] + "..." if len(title) > 120 else title

    def propose_manual(
        self,
        db: Session,
        *,
        title: str,
        category: str,
        resolution_steps: List[str],
        issue_pattern: Optional[str] = None,
        summary: Optional[str] = None,
        proposed_by: str = "unknown",
    ) -> KnowledgeDraftDB:
        """A person writes a draft directly. Still requires review."""
        if not resolution_steps:
            raise KnowledgeError("An article needs at least one resolution step.")

        draft = KnowledgeDraftDB(
            title=title,
            category=category,
            issue_pattern=issue_pattern or title,
            summary=summary or "",
            resolution_steps=list(resolution_steps),
            proposed_by=proposed_by,
            machine_generated=False,
            status=DraftStatus.PENDING.value,
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)
        self._audit(db, draft, AuditAction.KB_UPDATE, "success",
                    f"Draft written by {proposed_by} (pending review)")
        return draft

    # -- reviewing ------------------------------------------------------------

    def approve(
        self,
        db: Session,
        draft: KnowledgeDraftDB,
        *,
        reviewer_email: str,
        note: Optional[str] = None,
        edited: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeDraftDB:
        """Approve a draft, giving it an article id and making it searchable.

        ``edited`` lets the reviewer correct the text before approving, which is
        the normal case for a machine-written draft.
        """
        if draft.status != DraftStatus.PENDING.value:
            raise KnowledgeError(
                f"Draft {draft.id} is {draft.status} and cannot be approved again."
            )

        if edited:
            for field in ("title", "category", "issue_pattern", "summary", "resolution_steps"):
                if field in edited and edited[field]:
                    setattr(draft, field, edited[field])

        if not draft.resolution_steps:
            raise KnowledgeError("Cannot approve an article with no resolution steps.")

        draft.article_id = self._next_article_id(db)
        draft.status = DraftStatus.APPROVED.value
        draft.reviewed_by = reviewer_email
        draft.reviewed_at = datetime.utcnow()
        draft.review_note = note
        db.commit()
        db.refresh(draft)

        self._audit(db, draft, AuditAction.KB_UPDATE, "success",
                    f"Article {draft.article_id} approved by {reviewer_email}")
        logger.info("[KNOWLEDGE] Draft %s approved as %s by %s",
                    draft.id, draft.article_id, reviewer_email)
        return draft

    def reject(
        self,
        db: Session,
        draft: KnowledgeDraftDB,
        *,
        reviewer_email: str,
        reason: str,
    ) -> KnowledgeDraftDB:
        """Decline a draft. It stays on record and never becomes searchable."""
        if draft.status != DraftStatus.PENDING.value:
            raise KnowledgeError(f"Draft {draft.id} is already {draft.status}.")

        draft.status = DraftStatus.REJECTED.value
        draft.reviewed_by = reviewer_email
        draft.reviewed_at = datetime.utcnow()
        draft.review_note = reason
        db.commit()
        db.refresh(draft)

        self._audit(db, draft, AuditAction.KB_UPDATE, "denied",
                    f"Draft rejected by {reviewer_email}: {reason}")
        return draft

    @staticmethod
    def _next_article_id(db: Session) -> str:
        """Continue the KB-NNN sequence past both the file and the database.

        Raises rather than guessing if the existing articles cannot be read. A
        colliding id would silently shadow a real article in the retriever,
        which is far worse than refusing to approve.
        """
        from app.services.dataset_analyzer import get_analyzer

        highest = 0
        for article_id in get_analyzer().knowledge_base:
            match = re.fullmatch(r"KB-(\d+)", str(article_id))
            if match:
                highest = max(highest, int(match.group(1)))

        for (article_id,) in db.query(KnowledgeDraftDB.article_id).filter(
            KnowledgeDraftDB.article_id.isnot(None)
        ):
            match = re.fullmatch(r"KB-(\d+)", str(article_id))
            if match:
                highest = max(highest, int(match.group(1)))

        if highest == 0:
            raise KnowledgeError(
                "Could not read the existing knowledge base to allocate an "
                "article id. Approving now risks colliding with a real article."
            )

        return f"{ARTICLE_PREFIX}{highest + 1:03d}"

    # -- reading --------------------------------------------------------------

    def pending(self, db: Session, limit: int = 100) -> List[KnowledgeDraftDB]:
        return (
            db.query(KnowledgeDraftDB)
            .filter(KnowledgeDraftDB.status == DraftStatus.PENDING.value)
            .order_by(KnowledgeDraftDB.created_at.desc())
            .limit(limit)
            .all()
        )

    def approved_articles(self, db: Session) -> List[Dict[str, Any]]:
        """Approved articles, in the shape the retriever expects.

        Drafts and rejections are excluded here, which is the single place that
        guarantee lives.
        """
        rows = (
            db.query(KnowledgeDraftDB)
            .filter(KnowledgeDraftDB.status == DraftStatus.APPROVED.value)
            .all()
        )
        return [row.as_article() for row in rows if row.article_id]

    def get(self, db: Session, draft_id: int) -> Optional[KnowledgeDraftDB]:
        return db.query(KnowledgeDraftDB).filter(KnowledgeDraftDB.id == draft_id).first()

    def history(self, db: Session, limit: int = 100) -> List[KnowledgeDraftDB]:
        return (
            db.query(KnowledgeDraftDB)
            .order_by(KnowledgeDraftDB.created_at.desc())
            .limit(limit)
            .all()
        )

    # -- audit ----------------------------------------------------------------

    @staticmethod
    def _audit(db: Session, draft, action, success: str, details: str) -> None:
        try:
            from app.services.audit_service import AuditService

            AuditService.log_action(
                db=db,
                action=action,
                success=success,
                user_email=draft.reviewed_by or draft.proposed_by,
                resource_type="knowledge_draft",
                resource_id=str(draft.id),
                details=details,
                action_metadata={
                    "draft_id": draft.id,
                    "article_id": draft.article_id,
                    "status": draft.status,
                    "machine_generated": draft.machine_generated,
                },
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("[KNOWLEDGE] Audit write failed: %s", exc)


knowledge_service = KnowledgeService()
