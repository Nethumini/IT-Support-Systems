"""Runs the labelled scenarios under the three comparison conditions.

Thesis 6.4.3 defines them:

* **A - advice only.** Evidence is retrieved and a fix is proposed, but nothing
  executes. The baseline: what a grounded chatbot alone achieves.
* **B - uniform gating.** Actions may run, but every case takes the same
  approval route regardless of risk. Models the common design where a human
  confirms everything, and approval fatigue means they confirm.
* **C - risk-adaptive.** The contribution: the route depends on impact,
  confidence, evidence, reversibility and scope.

Comparing B with C isolates what risk adaptation buys. B has a human in the
loop for every action, so it looks safe; the measures show whether uniform
gating actually prevents the unsafe cases, and what it costs in approvals.

No chat model is called. Every signal is fixed in the scenario, so a run is
deterministic, repeats identically, and spends no API quota.
"""
from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.services.execution import SimulatedDriver, SimulatedSystem
from app.services.remediation_service import RemediationError, RemediationService
from app.services.risk_engine import RiskFactors, RiskLevel
from app.services.risk_signals import factors_for_action, has_required_evidence
from app.services.verification import CONTRACTS

from .scenarios import SCENARIOS, Scenario

logger = logging.getLogger(__name__)

CONDITIONS = ("A", "B", "C")

CONDITION_NAMES = {
    "A": "Advice only (no execution)",
    "B": "Uniform gating (same approval for every action)",
    "C": "Risk-adaptive (five-factor routing)",
}


@dataclass
class RunResult:
    """What happened to one scenario under one condition."""

    scenario_id: str
    condition: str
    problem: str
    action_id: str

    expected_risk: str
    expected_route: str
    unsafe_to_automate: bool

    assigned_risk: Optional[str] = None
    assigned_route: Optional[str] = None
    risk_score: Optional[float] = None
    overrides: List[str] = field(default_factory=list)

    executed: bool = False
    required_human_approval: bool = False
    precheck_passed: Optional[bool] = None
    verification_status: Optional[str] = None
    final_status: Optional[str] = None
    escalated: bool = False
    fault_injected: bool = False
    duration_ms: int = 0
    error: Optional[str] = None

    @property
    def risk_correct(self) -> bool:
        return self.assigned_risk == self.expected_risk

    @property
    def route_correct(self) -> bool:
        return self.assigned_route == self.expected_route

    @property
    def unsafe_prevented(self) -> bool:
        """Thesis 6.4.3: an unsafe case counts as prevented when it was
        correctly blocked or escalated - that is, when it did not execute."""
        if not self.unsafe_to_automate:
            return True
        return not self.executed

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["risk_correct"] = self.risk_correct
        data["route_correct"] = self.route_correct
        return data


def _fresh_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def _driver_for(scenario: Scenario) -> SimulatedDriver:
    """A fresh machine per scenario, so runs cannot contaminate each other."""
    driver = SimulatedDriver(SimulatedSystem())
    if scenario.inject_fault:
        driver.inject_fault(scenario.action_id)
    return driver


def _factors(scenario: Scenario) -> RiskFactors:
    return factors_for_action(
        {"action_id": scenario.action_id, "risk_level": scenario.catalogue_risk},
        citations=scenario.citations,
        classifier_confidence=scenario.classifier_confidence,
    )


def run_scenario(scenario: Scenario, condition: str) -> RunResult:
    """Run one scenario under one condition."""
    result = RunResult(
        scenario_id=scenario.id,
        condition=condition,
        problem=scenario.problem,
        action_id=scenario.action_id,
        expected_risk=scenario.expected_risk,
        expected_route=scenario.expected_route,
        unsafe_to_automate=scenario.unsafe_to_automate,
        fault_injected=scenario.inject_fault,
    )

    db = _fresh_db()
    driver = _driver_for(scenario)
    service = RemediationService(driver=driver)
    started = time.perf_counter()

    try:
        request = service.propose(
            db,
            user_email="evaluation@acme-soft.com",
            reported_problem=scenario.problem,
            action_id=scenario.action_id,
            parameters=scenario.parameters,
            diagnosis=f"Proposed {scenario.action_id}",
            evidence=scenario.citations,
        )

        # Every condition assesses risk, so the measured classification is the
        # same in all three. Only what happens next differs.
        request = service.assess(
            db,
            request,
            _factors(scenario),
            catalogue_risk=RiskLevel(scenario.catalogue_risk),
            has_required_evidence=has_required_evidence(scenario.action_id, scenario.citations),
        )

        result.assigned_risk = request.risk_level
        result.risk_score = request.risk_score
        result.assigned_route = request.approval_route
        result.overrides = list((request.risk_assessment or {}).get("overrides", []))

        if condition == "A":
            # Advice only: the proposal is recorded and nothing runs.
            result.final_status = request.status
            return result

        if condition == "B":
            # Uniform gating: every action takes the same route, and the human
            # approves. Risk plays no part in who decides or whether it runs.
            result.required_human_approval = True
            request.status = "awaiting_approval"
            db.commit()
            request, token = service.approve(
                db, request,
                approver_email="evaluation@acme-soft.com",
                approver_role="staff",
            )
            request = service.execute(db, request, token=token)

        else:  # condition C
            route = request.approval_route
            if route == "auto_candidate":
                request = service.execute(db, request)
            elif route == "user_approval":
                result.required_human_approval = True
                request, token = service.approve(
                    db, request,
                    approver_email="evaluation@acme-soft.com",
                    approver_role="staff",
                )
                request = service.execute(db, request, token=token)
            else:
                # Blocked: an expert is required and none is available in an
                # unattended run, so it stays blocked. That is the point.
                result.required_human_approval = True
                result.final_status = request.status
                return result

        result.executed = request.execution_result is not None
        result.precheck_passed = (request.pre_check or {}).get("status") == "passed"
        result.verification_status = request.verification_status
        result.final_status = request.status
        result.escalated = request.status == "escalated"

    except RemediationError as exc:
        result.error = str(exc)
        result.final_status = "refused"
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Scenario %s failed under condition %s", scenario.id, condition)
        result.error = str(exc)
        result.final_status = "error"
    finally:
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        db.close()

    return result


def run_all(
    conditions: Optional[List[str]] = None,
    repeats: int = 3,
    scenarios: Optional[List[Scenario]] = None,
) -> List[RunResult]:
    """Run every scenario under every condition, ``repeats`` times each.

    Thesis 6.4.3 specifies three repeats. The pipeline is deterministic, so
    repeats confirm that rather than averaging noise - a differing result
    between repeats is itself a finding worth reporting.
    """
    conditions = conditions or list(CONDITIONS)
    scenarios = scenarios if scenarios is not None else SCENARIOS

    results: List[RunResult] = []
    for condition in conditions:
        for _ in range(repeats):
            for scenario in scenarios:
                results.append(run_scenario(scenario, condition))
    return results
