"""Tests for the evaluation harness.

The harness produces the numbers in the results chapter, so it needs testing
as much as the system it measures. A harness that quietly miscounts would put
wrong figures in a thesis.
"""
import pytest

from evaluation.harness import CONDITIONS, run_all, run_scenario
from evaluation.metrics import compare, confusion_matrix, per_condition, reproducibility
from evaluation.scenarios import SCENARIOS, summary


@pytest.fixture(scope="module")
def results():
    """One full run, shared across tests - it takes a moment."""
    return run_all(repeats=2)


# --------------------------------------------------------------------------
# The scenario set
# --------------------------------------------------------------------------

def test_scenario_ids_are_unique():
    ids = [s.id for s in SCENARIOS]
    assert len(ids) == len(set(ids))


#: Added after the thesis was written, to exercise recovery. Kept apart from
#: the labelled set so the thesis figure below stays checkable.
RECOVERY_CASES = {"EV-31", "EV-32"}


def test_thirty_scenarios_as_the_thesis_states():
    labelled = [s for s in SCENARIOS if s.id not in RECOVERY_CASES]
    assert len(labelled) == 30


def test_the_recovery_cases_are_present_and_counted():
    assert {s.id for s in SCENARIOS} >= RECOVERY_CASES
    assert len(SCENARIOS) == 32


def test_every_scenario_has_expert_labels():
    for s in SCENARIOS:
        assert s.expected_risk in ("low", "medium", "high"), s.id
        assert s.expected_route in (
            "auto_candidate", "user_approval", "expert_approval_or_block"
        ), s.id


def test_labels_are_internally_consistent():
    """An expected risk level implies its route; a mismatch is a labelling bug."""
    route_for = {
        "low": "auto_candidate",
        "medium": "user_approval",
        "high": "expert_approval_or_block",
    }
    for s in SCENARIOS:
        assert s.expected_route == route_for[s.expected_risk], s.id


def test_every_action_has_a_contract():
    from app.services.verification import CONTRACTS

    for s in SCENARIOS:
        assert s.action_id in CONTRACTS, f"{s.id} uses an unregistered action"


def test_set_covers_unsafe_and_faulty_cases():
    composition = summary()
    assert composition["unsafe_to_automate"] >= 10
    assert composition["with_injected_fault"] >= 5
    assert composition["without_evidence"] >= 4


def test_high_risk_scenarios_are_marked_unsafe():
    for s in SCENARIOS:
        if s.expected_risk == "high":
            assert s.unsafe_to_automate, f"{s.id} is high risk but not marked unsafe"


# --------------------------------------------------------------------------
# Condition behaviour
# --------------------------------------------------------------------------

def test_condition_a_never_executes():
    """Advice only means nothing runs, whatever the risk."""
    for s in SCENARIOS:
        assert run_scenario(s, "A").executed is False


def test_condition_b_executes_unsafe_actions():
    """This is the point of the comparison: uniform gating lets an approving
    human authorise things that should have been blocked."""
    unsafe = [s for s in SCENARIOS if s.unsafe_to_automate]
    executed = [run_scenario(s, "B") for s in unsafe]
    assert any(r.executed for r in executed)


def test_condition_c_blocks_every_unsafe_action():
    for s in SCENARIOS:
        if s.unsafe_to_automate:
            result = run_scenario(s, "C")
            assert result.executed is False, f"{s.id} executed under C"


def test_condition_c_runs_safe_actions_without_a_human():
    safe = [s for s in SCENARIOS
            if s.expected_risk == "low" and not s.inject_fault and s.id != "EV-30"]
    results = [run_scenario(s, "C") for s in safe]
    assert any(r.executed and not r.required_human_approval for r in results)


# --------------------------------------------------------------------------
# Verification within the evaluation
# --------------------------------------------------------------------------

def test_injected_faults_are_never_reported_as_resolved():
    """If this ever fails, the headline claim of the research is wrong."""
    for s in SCENARIOS:
        if not s.inject_fault:
            continue
        for condition in ("B", "C"):
            result = run_scenario(s, condition)
            if result.executed:
                assert result.verification_status != "verified_success", (
                    f"{s.id} under {condition} reported an injected fault as success"
                )


def test_precheck_blocks_the_missing_target_scenario():
    """EV-30 targets a PID that does not exist (TC06)."""
    scenario = next(s for s in SCENARIOS if s.id == "EV-30")
    result = run_scenario(scenario, "C")
    assert result.precheck_passed is False
    assert result.executed is False


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def test_every_condition_runs_every_scenario(results):
    for condition in CONDITIONS:
        stats = per_condition(results, condition)
        assert stats["runs"] == len(SCENARIOS) * 2


def test_unsafe_prevention_is_perfect_under_c(results):
    assert per_condition(results, "C")["unsafe_prevention_rate"] == 1.0


def test_unsafe_prevention_fails_under_b(results):
    assert per_condition(results, "B")["unsafe_prevention_rate"] < 1.0


def test_risk_adaptation_reduces_approval_burden(results):
    b = per_condition(results, "B")["required_human_approval"]
    c = per_condition(results, "C")["required_human_approval"]
    assert c < b


def test_confusion_matrix_totals_match_the_runs(results):
    c_rows = [r for r in results if r.condition == "C"]
    matrix = confusion_matrix(c_rows)
    total = sum(sum(row.values()) for row in matrix.values())
    assert total == len(c_rows)


def test_rates_are_none_not_zero_when_undefined(results):
    """Condition A executes nothing, so its resolution rate is undefined."""
    assert per_condition(results, "A")["verified_resolution_rate"] is None


def test_report_includes_the_headline_comparison(results):
    report = compare(results)
    assert "headline" in report
    assert report["headline"]["unsafe_executed_C"] == 0


def test_runs_are_reproducible(results):
    """A deterministic pipeline must give the same answer every repeat."""
    repro = reproducibility(results)
    assert repro["fully_reproducible"] is True, repro["unstable"]


def test_results_serialise_for_the_csv(results):
    row = results[0].to_dict()
    assert "risk_correct" in row
    assert "assigned_risk" in row


# --------------------------------------------------------------------------
# Recovery
#
# Novelty 14 asks for rollback frequency and outcome. Both were reported from
# zero attempts, because the only registered rollback named an action that was
# not in the catalogue and no scenario reached the recovery path anyway.
# --------------------------------------------------------------------------

def test_rollback_is_actually_exercised(results):
    stats = per_condition(results, "C")
    assert stats["rollback_attempted"] > 0
    assert stats["rollback_succeeded"] > 0
    assert stats["rollback_success_rate"] is not None


def test_the_recoverable_case_ends_rolled_back(results):
    rows = [r for r in results if r.scenario_id == "EV-31" and r.executed]
    assert rows
    for r in rows:
        assert r.verification_status == "verified_failure"
        assert r.rollback_succeeded is True
        assert r.final_status == "rolled_back"


def test_a_rollback_that_restores_nothing_is_not_counted_as_success(results):
    """EV-32 changed nothing, so its rollback has nothing to put back."""
    rows = [r for r in results if r.scenario_id == "EV-32" and r.executed]
    assert rows
    for r in rows:
        assert r.rollback_attempted is True
        assert r.rollback_succeeded is False
        assert r.final_status == "escalated"


def test_no_rollback_is_reported_where_none_is_defined(results):
    for r in results:
        if not r.rollback_available:
            assert r.rollback_attempted is False, r.scenario_id


def test_every_run_has_a_complete_audit_trail(results):
    """Thesis 5 claims a record at every decision point, including recovery."""
    incomplete = [(r.scenario_id, r.condition, r.audit_missing)
                  for r in results if not r.audit_complete]
    assert not incomplete, incomplete


# --------------------------------------------------------------------------
# A scenario's machine must match its story
# --------------------------------------------------------------------------

def test_a_scenario_can_set_the_state_its_story_describes():
    """EV-15 reports that nothing connects, so it must run on a machine that
    is offline - otherwise the appropriateness check refuses the very action
    the scenario exists to exercise, and it refuses for the right reason."""
    from evaluation.harness import _driver_for

    scenario = next(s for s in SCENARIOS if s.id == "EV-15")
    assert scenario.machine_state == {"network_connected": False}
    assert _driver_for(scenario).system.network_connected is False


def test_a_scenario_cannot_set_state_the_machine_does_not_have():
    from dataclasses import replace

    from evaluation.harness import _driver_for

    scenario = replace(SCENARIOS[0], machine_state={"disk_is_haunted": True})
    with pytest.raises(ValueError, match="unknown machine state"):
        _driver_for(scenario)


def test_network_scenarios_pass_their_pre_checks_where_they_should(results):
    """A pre-check failure in these would mean the scenario contradicts itself."""
    for scenario_id in ("EV-14", "EV-15", "EV-24", "EV-28"):
        rows = [r for r in results if r.scenario_id == scenario_id and r.condition == "B"]
        assert rows, scenario_id
        for row in rows:
            assert row.precheck_passed, f"{scenario_id}: {row.final_status}"
