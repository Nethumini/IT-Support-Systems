"""Knowledge articles learned from solved problems.

When the system resolves a problem it had no procedure for, that solution is
worth keeping. But an answer the AI worked out on its own is not organisational
knowledge yet - it is a proposal.

So a solved problem becomes a **draft**, and only a person can turn a draft
into an approved article. Without that gate the system would ground its future
answers on its own past guesses: one wrong fix would become cited policy and
then be repeated with confidence. Thesis 5.3.2 retrieves approved sources only,
and this is what keeps that true as the knowledge base grows.

The same human-in-the-loop principle as risky remediation, applied to what the
system is allowed to learn.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class DraftStatus(str, Enum):
    """Where a proposed article stands."""

    #: Waiting for a reviewer. Never searchable.
    PENDING = "pending"
    #: Reviewed and accepted. Searchable, and citable as company knowledge.
    APPROVED = "approved"
    #: Reviewed and declined. Kept for the record, never searchable.
    REJECTED = "rejected"


class KnowledgeDraftDB(Base):
    """A proposed knowledge-base article, and its review decision."""

    __tablename__ = "knowledge_drafts"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    #: Article id once approved, e.g. "KB-031". Assigned at approval, not before,
    #: so an unapproved draft can never be cited by id.
    article_id = Column(String, unique=True, index=True, nullable=True)

    status = Column(String, index=True, nullable=False, default=DraftStatus.PENDING.value)

    # --- the proposed article ------------------------------------------------
    title = Column(String, nullable=False)
    category = Column(String, index=True, nullable=False)
    issue_pattern = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    resolution_steps = Column(JSON, nullable=False)

    # --- where it came from --------------------------------------------------
    source_problem = Column(Text, nullable=True)
    remediation_id = Column(Integer, index=True, nullable=True)
    ticket_id = Column(Integer, index=True, nullable=True)
    proposed_by = Column(String, nullable=True)
    #: True when the system proposed it from a verified fix rather than a person
    #: writing it. Reviewers should look harder at these.
    machine_generated = Column(Boolean, default=True)
    #: Evidence the original fix was actually verified, not just attempted.
    verification_status = Column(String, nullable=True)

    # --- review --------------------------------------------------------------
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_note = Column(Text, nullable=True)

    @property
    def is_approved(self) -> bool:
        return self.status == DraftStatus.APPROVED.value

    def as_article(self) -> Dict[str, Any]:
        """The shape ``DatasetAnalyzer`` expects of a knowledge-base article."""
        return {
            "id": self.article_id,
            "title": self.title,
            "category": self.category,
            "issue_pattern": self.issue_pattern or self.title,
            "summary": self.summary or "",
            "resolution_steps": list(self.resolution_steps or []),
            "used_in_tickets": [],
            "source": "learned",
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "article_id": self.article_id,
            "status": self.status,
            "title": self.title,
            "category": self.category,
            "issue_pattern": self.issue_pattern,
            "summary": self.summary,
            "resolution_steps": list(self.resolution_steps or []),
            "source_problem": self.source_problem,
            "remediation_id": self.remediation_id,
            "ticket_id": self.ticket_id,
            "proposed_by": self.proposed_by,
            "machine_generated": self.machine_generated,
            "verification_status": self.verification_status,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "review_note": self.review_note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
