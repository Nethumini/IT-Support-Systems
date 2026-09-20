"""Tests for learning knowledge from solved problems.

The rule these protect: a fix the system worked out on its own does not become
company knowledge until a person approves it. If a draft were ever retrievable,
the system would ground future answers on its own unreviewed guesses.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.knowledge import DraftStatus, KnowledgeDraftDB
from app.services.execution import SimulatedDriver, SimulatedSystem
from app.services.knowledge_service import KnowledgeError, KnowledgeService
from app.services.remediation_service import RemediationService
from app.services.risk_engine import RiskFactors, RiskLevel


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def service():
    return KnowledgeService()


@pytest.fixture
def driver():
    return SimulatedDriver(SimulatedSystem())


def safe_factors():
    return RiskFactors.from_ratings(
        impact=1, confidence_rating=3, evidence_quality=3,
        irreversibility=1, affected_scope=1,
    )


def solved_remediation(db, driver, *, evidence=None):
    """Run a remediation through to a verified success."""
    remediation = RemediationService(driver=driver)
    request = remediation.propose(
        db,
        user_email="user@acme-soft.com",
        reported_problem="My temp folder filled the disk",
        action_id="clear_temp_files",
        diagnosis="Temporary files filled the disk",
        evidence=evidence if evidence is not None else [],
    )
    request = remediation.assess(
        db, request, safe_factors(), catalogue_risk=RiskLevel.LOW,
        has_required_evidence=True,
    )
    return remediation.execute(db, request)


# --------------------------------------------------------------------------
# Proposing
# --------------------------------------------------------------------------

def test_verified_fix_with_no_article_proposes_a_draft(db, driver, service):
    request = solved_remediation(db, driver)
    assert request.verification_status == "verified_success"

    draft = db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first()
    assert draft is not None
    assert draft.status == DraftStatus.PENDING.value


def test_draft_records_where_it_came_from(db, driver):
    request = solved_remediation(db, driver)
    draft = db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first()
    assert draft.source_problem == "My temp folder filled the disk"
    assert draft.verification_status == "verified_success"
    assert draft.machine_generated is True


def test_no_draft_when_an_article_already_covered_it(db, driver, service):
    """Retrieval found something, so this is not new knowledge."""
    request = solved_remediation(db, driver, evidence=[{"kb_id": "KB-007"}])
    assert db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first() is None


def test_no_draft_from_an_unverified_fix(db, driver, service):
    """A command that ran but did not fix anything teaches nothing."""
    driver.inject_fault("clear_temp_files")
    request = solved_remediation(db, driver)
    assert request.verification_status != "verified_success"
    assert db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first() is None


def test_proposing_twice_reuses_the_same_draft(db, driver, service):
    request = solved_remediation(db, driver)
    first = service.propose_from_remediation(db, request)
    second = service.propose_from_remediation(db, request)
    assert first.id == second.id


def test_draft_has_usable_steps(db, driver):
    request = solved_remediation(db, driver)
    draft = db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first()
    assert len(draft.resolution_steps) >= 3


# --------------------------------------------------------------------------
# The gate: a draft is never searchable
# --------------------------------------------------------------------------

def test_pending_draft_is_not_in_approved_articles(db, driver, service):
    solved_remediation(db, driver)
    assert service.approved_articles(db) == []


def test_rejected_draft_is_not_in_approved_articles(db, driver, service):
    request = solved_remediation(db, driver)
    draft = db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first()
    service.reject(db, draft, reviewer_email="expert@acme-soft.com", reason="Too specific")
    assert service.approved_articles(db) == []


def test_pending_draft_has_no_article_id(db, driver, service):
    """No id means it cannot be cited, even by accident."""
    request = solved_remediation(db, driver)
    draft = db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first()
    assert draft.article_id is None


def test_approved_draft_becomes_searchable(db, driver, service):
    request = solved_remediation(db, driver)
    draft = db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first()
    service.approve(db, draft, reviewer_email="expert@acme-soft.com")

    articles = service.approved_articles(db)
    assert len(articles) == 1
    assert articles[0]["id"].startswith("KB-")
    assert articles[0]["resolution_steps"]


# --------------------------------------------------------------------------
# Review decisions
# --------------------------------------------------------------------------

def test_approval_assigns_the_next_article_id(db, driver, service):
    request = solved_remediation(db, driver)
    draft = db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first()
    draft = service.approve(db, draft, reviewer_email="expert@acme-soft.com")
    assert draft.article_id is not None
    assert draft.article_id.startswith("KB-")


def test_article_ids_do_not_collide(db, service):
    first = service.propose_manual(
        db, title="First", category="network", resolution_steps=["a"], proposed_by="x")
    second = service.propose_manual(
        db, title="Second", category="network", resolution_steps=["b"], proposed_by="x")
    a = service.approve(db, first, reviewer_email="e@acme-soft.com").article_id
    b = service.approve(db, second, reviewer_email="e@acme-soft.com").article_id
    assert a != b


def test_reviewer_can_edit_before_approving(db, driver, service):
    """Machine-written drafts usually need correcting."""
    request = solved_remediation(db, driver)
    draft = db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first()
    draft = service.approve(
        db, draft, reviewer_email="expert@acme-soft.com",
        edited={"title": "Disk fills with temporary files",
                "resolution_steps": ["Check free space", "Clear temp files", "Verify"]},
    )
    assert draft.title == "Disk fills with temporary files"
    assert len(draft.resolution_steps) == 3


def test_approving_twice_is_refused(db, driver, service):
    request = solved_remediation(db, driver)
    draft = db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first()
    service.approve(db, draft, reviewer_email="expert@acme-soft.com")
    with pytest.raises(KnowledgeError):
        service.approve(db, draft, reviewer_email="expert@acme-soft.com")


def test_rejected_draft_cannot_be_approved_later(db, driver, service):
    request = solved_remediation(db, driver)
    draft = db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first()
    service.reject(db, draft, reviewer_email="e@acme-soft.com", reason="Wrong")
    with pytest.raises(KnowledgeError):
        service.approve(db, draft, reviewer_email="e@acme-soft.com")


def test_approval_records_who_decided(db, driver, service):
    request = solved_remediation(db, driver)
    draft = db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first()
    draft = service.approve(db, draft, reviewer_email="expert@acme-soft.com", note="Checked")
    assert draft.reviewed_by == "expert@acme-soft.com"
    assert draft.reviewed_at is not None
    assert draft.review_note == "Checked"


def test_cannot_approve_an_article_with_no_steps(db, service):
    draft = service.propose_manual(
        db, title="Empty", category="other", resolution_steps=["placeholder"], proposed_by="x")
    draft.resolution_steps = []
    db.commit()
    with pytest.raises(KnowledgeError):
        service.approve(db, draft, reviewer_email="e@acme-soft.com")


def test_manual_draft_needs_steps(db, service):
    with pytest.raises(KnowledgeError):
        service.propose_manual(db, title="X", category="other",
                               resolution_steps=[], proposed_by="x")


def test_manual_draft_is_marked_as_human_written(db, service):
    draft = service.propose_manual(
        db, title="Written by a person", category="network",
        resolution_steps=["step"], proposed_by="tech@acme-soft.com")
    assert draft.machine_generated is False


# --------------------------------------------------------------------------
# Listing
# --------------------------------------------------------------------------

def test_pending_lists_only_unreviewed(db, driver, service):
    solved_remediation(db, driver)
    assert len(service.pending(db)) == 1
    draft = service.pending(db)[0]
    service.approve(db, draft, reviewer_email="e@acme-soft.com")
    assert service.pending(db) == []


def test_history_keeps_rejected_drafts(db, service):
    draft = service.propose_manual(
        db, title="Bad idea", category="other", resolution_steps=["x"], proposed_by="y")
    service.reject(db, draft, reviewer_email="e@acme-soft.com", reason="Not useful")
    assert len(service.history(db)) == 1


# --------------------------------------------------------------------------
# The full loop
# --------------------------------------------------------------------------

def test_learned_article_is_retrievable_after_approval(db, driver, service):
    """Solve -> draft -> approve -> the retriever can now find it."""
    from app.services.dataset_analyzer import DatasetAnalyzer

    request = solved_remediation(db, driver)
    draft = db.query(KnowledgeDraftDB).filter_by(remediation_id=request.id).first()

    analyzer = DatasetAnalyzer()
    before = len(analyzer.knowledge_base)
    analyzer.load_approved_articles(db)
    assert len(analyzer.knowledge_base) == before, "a pending draft must not be loaded"

    service.approve(db, draft, reviewer_email="expert@acme-soft.com")

    analyzer = DatasetAnalyzer()
    analyzer.load_approved_articles(db)
    assert len(analyzer.knowledge_base) == before + 1
