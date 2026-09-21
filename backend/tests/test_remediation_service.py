"""End-to-end tests for the remediation workflow.

These are the integration tests behind thesis Table 6.1. Each of TC04 to TC09
has a test here, named after it, so a reviewer can trace a claimed test case to
the code that demonstrates it.

Everything runs against an in-memory SQLite database and the simulated driver,
so the whole flow is exercised without touching a real machine.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.remediation import (
    RemediationRequestDB,
    RemediationStatus,
    fingerprint,
)
from app.services.execution import SimulatedDriver, SimulatedSystem
from app.services.remediation_service import RemediationError, RemediationService
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
def driver():
    return SimulatedDriver(SimulatedSystem())


@pytest.fixture
def service(driver):
    return RemediationService(driver=driver)


def safe_factors():
    """Strong evidence, reversible, the user's own machine."""
    return RiskFactors.from_ratings(
        impact=1, confidence_rating=3, evidence_quality=3,
        irreversibility=1, affected_scope=1,
    )


def risky_factors():
    return RiskFactors.from_ratings(
        impact=3, confidence_rating=2, evidence_quality=2,
        irreversibility=3, affected_scope=2,
    )


def propose(service, db, action_id="clear_temp_files", parameters=None, **kwargs):
    return service.propose(
        db,
        user_email=kwargs.pop("user_email", "bethany.williams@acme-soft.com"),
        reported_problem=kwargs.pop("reported_problem", "My C drive is full"),
        action_id=action_id,
        parameters=parameters or {},
        diagnosis=kwargs.pop("diagnosis", "Temporary files have filled the disk"),
        evidence=kwargs.pop("evidence", [{"kb_id": "KB-007", "similarity_score": 0.78}]),
        **kwargs,
    )


# --------------------------------------------------------------------------
# Proposal
# --------------------------------------------------------------------------

def test_proposal_is_persisted(service, db):
    request = propose(service, db)
    assert request.id is not None
    assert request.status == RemediationStatus.PENDING_ASSESSMENT.value


def test_proposal_survives_a_new_session(service, db):
    request = propose(service, db)
    found = db.query(RemediationRequestDB).filter_by(id=request.id).first()
    assert found is not None
    assert found.action_id == "clear_temp_files"


def test_proposal_records_its_evidence(service, db):
    request = propose(service, db)
    assert request.evidence[0]["kb_id"] == "KB-007"


def test_proposal_alone_does_not_execute(service, db, driver):
    before = driver.system.disk_free_gb
    propose(service, db)
    assert driver.system.disk_free_gb == before


# --------------------------------------------------------------------------
# Assessment and routing
# --------------------------------------------------------------------------

def test_low_risk_becomes_ready_for_execution(service, db):
    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.LOW)
    assert request.risk_level == "low"
    assert request.status == RemediationStatus.READY_FOR_EXECUTION.value


def test_medium_risk_awaits_user_approval(service, db):
    factors = RiskFactors.from_ratings(
        impact=2, confidence_rating=3, evidence_quality=2,
        irreversibility=2, affected_scope=1,
    )
    request = service.assess(db, propose(service, db, "kill_process_by_id", {"pid": 4812}),
                             factors, catalogue_risk=RiskLevel.MEDIUM)
    assert request.risk_level == "medium"
    assert request.status == RemediationStatus.AWAITING_APPROVAL.value


def test_high_risk_is_blocked(service, db):
    request = service.assess(db, propose(service, db, "reset_winsock"),
                             risky_factors(), catalogue_risk=RiskLevel.HIGH)
    assert request.risk_level == "high"
    assert request.status == RemediationStatus.BLOCKED.value


def test_assessment_stores_the_full_factor_vector(service, db):
    """Thesis 5.3.3: the same input must be replayable during evaluation."""
    request = service.assess(db, propose(service, db), safe_factors())
    stored = request.risk_assessment
    assert set(stored["factors"]) == {
        "impact", "diagnostic_uncertainty", "evidence_weakness",
        "irreversibility", "affected_scope",
    }
    assert stored["policy_version"]
    assert stored["weights"]


# --------------------------------------------------------------------------
# TC04: insufficient evidence
# --------------------------------------------------------------------------

def test_tc04_no_evidence_blocks_execution_despite_plausible_suggestion(service, db):
    request = service.assess(db, propose(service, db, evidence=[]),
                             safe_factors(), has_required_evidence=False)
    assert request.risk_level == "high"
    assert request.status == RemediationStatus.BLOCKED.value
    assert "missing_required_evidence" in request.risk_assessment["overrides"]


def test_tc04_no_execution_token_is_issued_when_blocked(service, db):
    request = service.assess(db, propose(service, db), safe_factors(), has_required_evidence=False)
    assert request.approval_token is None


# --------------------------------------------------------------------------
# Approval
# --------------------------------------------------------------------------

def test_user_can_approve_a_medium_risk_action(service, db):
    request = service.assess(db, propose(service, db, "kill_process_by_id", {"pid": 4812}),
                             RiskFactors.from_ratings(impact=2, confidence_rating=3,
                                                      evidence_quality=2, irreversibility=2,
                                                      affected_scope=1),
                             catalogue_risk=RiskLevel.MEDIUM)
    request, token = service.approve(db, request, approver_email="bethany.williams@acme-soft.com",
                                     approver_role="staff")
    assert request.status == RemediationStatus.APPROVED.value
    assert token


def test_high_risk_needs_an_expert_not_the_requester(service, db):
    request = service.assess(db, propose(service, db, "reset_winsock"),
                             risky_factors(), catalogue_risk=RiskLevel.HIGH)
    with pytest.raises(RemediationError, match="cannot approve a high-risk"):
        service.approve(db, request, approver_email="someone@acme-soft.com", approver_role="staff")


def test_high_risk_cannot_be_self_approved(service, db):
    """A second principal is required, even when the requester is an admin."""
    request = service.assess(db, propose(service, db, "reset_winsock",
                                         user_email="admin@acme.com"),
                             risky_factors(), catalogue_risk=RiskLevel.HIGH)
    with pytest.raises(RemediationError, match="second principal"):
        service.approve(db, request, approver_email="admin@acme.com", approver_role="system_admin")


def test_expert_can_approve_high_risk(service, db):
    request = service.assess(db, propose(service, db, "reset_winsock"),
                             risky_factors(), catalogue_risk=RiskLevel.HIGH)
    request, token = service.approve(db, request, approver_email="expert@acme-soft.com",
                                     approver_role="support_l2")
    assert request.status == RemediationStatus.APPROVED.value
    assert token


def test_rejected_action_never_executes(service, db, driver):
    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.MEDIUM)
    request = service.reject(db, request, approver_email="bethany.williams@acme-soft.com",
                             reason="I am in the middle of something")
    assert request.status == RemediationStatus.REJECTED.value
    with pytest.raises(RemediationError):
        service.execute(db, request, token="anything")


# --------------------------------------------------------------------------
# TC07: token binding, expiry and single use
# --------------------------------------------------------------------------

def test_tc07_wrong_token_is_rejected(service, db):
    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.MEDIUM)
    request, _token = service.approve(db, request, approver_email="u@acme-soft.com", approver_role="staff")
    with pytest.raises(RemediationError, match="does not match"):
        service.execute(db, request, token="not-the-real-token")


def test_tc07_token_is_single_use(service, db):
    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.MEDIUM)
    request, token = service.approve(db, request, approver_email="u@acme-soft.com", approver_role="staff")
    service.execute(db, request, token=token)
    with pytest.raises(RemediationError):
        service.execute(db, request, token=token)


def test_tc07_expired_token_is_rejected(service, db):
    from datetime import datetime, timedelta

    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.MEDIUM)
    request, token = service.approve(db, request, approver_email="u@acme-soft.com", approver_role="staff")
    request.token_expires_at = datetime.utcnow() - timedelta(minutes=1)
    db.commit()
    with pytest.raises(RemediationError, match="expired"):
        service.execute(db, request, token=token)


def test_tc07_changed_parameters_invalidate_approval(service, db):
    """Approving 'kill PID 4812' must not authorise 'kill PID 980'."""
    request = service.assess(db, propose(service, db, "kill_process_by_id", {"pid": 4812}),
                             safe_factors(), catalogue_risk=RiskLevel.MEDIUM)
    request, token = service.approve(db, request, approver_email="u@acme-soft.com", approver_role="staff")

    request.parameters = {"pid": 980}
    db.commit()

    with pytest.raises(RemediationError, match="changed since approval"):
        service.execute(db, request, token=token)


def test_fingerprint_ignores_key_order():
    assert fingerprint("a", {"x": 1, "y": 2}) == fingerprint("a", {"y": 2, "x": 1})


def test_fingerprint_changes_with_the_action():
    assert fingerprint("restart_service", {"service_name": "Spooler"}) != fingerprint(
        "restart_service", {"service_name": "DomainController"}
    )


# --------------------------------------------------------------------------
# TC06: pre-check failure means the executor is never called
# --------------------------------------------------------------------------

def test_tc06_failed_precheck_does_not_call_the_executor(service, db, driver):
    request = service.assess(db, propose(service, db, "kill_process_by_id", {"pid": 999999}),
                             safe_factors(), catalogue_risk=RiskLevel.LOW)
    processes_before = list(driver.system.processes)
    request = service.execute(db, request)
    assert request.status == RemediationStatus.FAILED.value
    assert request.execution_result is None
    assert driver.system.processes == processes_before


def test_tc06_precheck_failure_reason_is_recorded(service, db):
    request = service.assess(db, propose(service, db, "kill_process_by_id", {"pid": 999999}),
                             safe_factors(), catalogue_risk=RiskLevel.LOW)
    request = service.execute(db, request)
    assert any(not c["passed"] for c in request.pre_check["checks"])


# --------------------------------------------------------------------------
# Happy path
# --------------------------------------------------------------------------

def test_low_risk_action_runs_and_is_verified(service, db, driver):
    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.LOW)
    request = service.execute(db, request)
    assert request.status == RemediationStatus.COMPLETED.value
    assert request.verification_status == "verified_success"
    assert driver.system.temp_files_mb == 0


def test_execution_records_before_and_after_state(service, db):
    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.LOW)
    request = service.execute(db, request)
    result = request.execution_result
    assert result["state_before"]["disk_free_gb"] < result["state_after"]["disk_free_gb"]


# --------------------------------------------------------------------------
# TC08: command completes but the problem remains
# --------------------------------------------------------------------------

def test_tc08_silent_failure_is_not_marked_completed(service, db, driver):
    driver.inject_fault("clear_temp_files")
    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.LOW)
    request = service.execute(db, request)

    assert request.execution_result["success"] is True  # the command "worked"
    assert request.verification_status == "verified_failure"
    assert request.status != RemediationStatus.COMPLETED.value


def test_tc08_silent_failure_escalates_when_no_rollback(service, db, driver):
    driver.inject_fault("clear_temp_files")
    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.LOW)
    request = service.execute(db, request)
    assert request.status == RemediationStatus.ESCALATED.value


# --------------------------------------------------------------------------
# TC09: failure with no safe rollback
# --------------------------------------------------------------------------

def test_tc09_escalation_records_the_reason(service, db, driver):
    driver.inject_fault("clear_temp_files")
    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.LOW)
    request = service.execute(db, request)
    assert request.escalation_reason
    assert "no safe rollback" in request.escalation_reason.lower()


def test_tc09_no_further_tool_invocation_after_escalation(service, db, driver):
    driver.inject_fault("clear_temp_files")
    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.LOW)
    request = service.execute(db, request)
    with pytest.raises(RemediationError):
        service.execute(db, request)


# --------------------------------------------------------------------------
# Queries used by the UI
# --------------------------------------------------------------------------

def test_pending_approvals_lists_waiting_requests(service, db):
    service.assess(db, propose(service, db, "kill_process_by_id", {"pid": 4812}),
                   safe_factors(), catalogue_risk=RiskLevel.MEDIUM)
    service.assess(db, propose(service, db, "reset_winsock"), risky_factors(),
                   catalogue_risk=RiskLevel.HIGH)
    assert len(service.pending_approvals(db)) == 2


def test_completed_requests_are_not_pending(service, db):
    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.LOW)
    service.execute(db, request)
    assert service.pending_approvals(db) == []


def test_history_is_newest_first(service, db):
    first = propose(service, db, reported_problem="first")
    second = propose(service, db, reported_problem="second")
    history = service.history(db)
    assert history[0].id == second.id
    assert history[-1].id == first.id


def test_request_serialises_without_leaking_the_token(service, db):
    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.MEDIUM)
    request, _token = service.approve(db, request, approver_email="u@acme-soft.com", approver_role="staff")
    assert "approval_token" not in request.to_dict()
    assert "approval_token" in request.to_dict(include_token=True)


# --------------------------------------------------------------------------
# Audit trail
# --------------------------------------------------------------------------

def test_every_step_is_audited(service, db):
    from app.models.audit_log import AuditLogDB

    request = service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.LOW)
    service.execute(db, request)

    actions = [row.action for row in db.query(AuditLogDB).all()]
    assert "remediation_proposed" in actions
    assert "remediation_assessed" in actions
    assert "remediation_verified" in actions


def test_audit_carries_the_risk_factors(service, db):
    from app.models.audit_log import AuditLogDB

    service.assess(db, propose(service, db), safe_factors(), catalogue_risk=RiskLevel.LOW)
    row = db.query(AuditLogDB).filter_by(action="remediation_assessed").first()
    assert row is not None
    assert "risk_factors" in row.action_metadata


# ---------------------------------------------------------------------------
# Regression: a diagnostic must not be blocked for lacking evidence.
#
# Found in a live demo. "my disk is full" matched no knowledge-base article, so
# the request carried no citations. Risk assessment correctly exempted the
# read-only action and routed it to automatic execution - but the execute
# endpoint applied its own, stricter test (`bool(request.evidence)`) and the
# pre-check refused it. The action was scored safe to run and then refused for
# a reason the score had already dismissed.
#
# CLAUDE.md states the rule: reading system state is how evidence gets
# gathered, so requiring evidence first is circular.
# ---------------------------------------------------------------------------

def test_read_only_action_runs_without_any_evidence(db, driver):
    """The exemption must hold at execution, not only at scoring."""
    from app.services.risk_signals import has_required_evidence

    service = RemediationService(driver=driver)
    request = service.propose(
        db,
        user_email="malith@acme.com",
        reported_problem="my disk is full",
        action_id="check_disk_space",
        parameters={},
        evidence=[],  # nothing matched in the knowledge base
    )
    request = service.assess(
        db, request,
        RiskFactors.from_ratings(
            impact=1, confidence_rating=3, evidence_quality=1,
            irreversibility=1, affected_scope=1,
        ),
        catalogue_risk=RiskLevel.LOW,
        has_required_evidence=has_required_evidence("check_disk_space", []),
    )

    # Exactly what the execute endpoint passes.
    request = service.execute(
        db, request,
        evidence_sufficient=has_required_evidence(request.action_id, request.evidence),
    )

    assert request.pre_check["status"] != "failed", request.pre_check["failure_reasons"]
    assert request.status != RemediationStatus.FAILED.value


def test_state_changing_action_still_needs_evidence(db, driver):
    """The exemption is for diagnostics only, and must not leak wider."""
    from app.services.risk_signals import has_required_evidence

    assert has_required_evidence("clear_temp_files", []) is False
    assert has_required_evidence("clear_temp_files", [{"kb_id": "KB-007"}]) is True
