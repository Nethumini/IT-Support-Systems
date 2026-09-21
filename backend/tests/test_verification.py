"""Tests for pre-action and post-action verification.

The central claim under test: a command completing is not the same as a problem
being solved (thesis 8, TC08). Several tests below deliberately make an action
report success while changing nothing, and assert the system refuses to call
that a resolution.
"""
import pytest

from app.services.execution import SimulatedDriver, SimulatedSystem
from app.services.execution.base import ExecutionResult
from app.services.verification import (
    CONTRACTS,
    PostCheckStatus,
    PreCheckStatus,
    VerificationService,
)


@pytest.fixture
def driver():
    return SimulatedDriver(SimulatedSystem())


@pytest.fixture
def verifier():
    return VerificationService()


# --------------------------------------------------------------------------
# Pre-action checks
# --------------------------------------------------------------------------

def test_unregistered_action_fails_pre_check(verifier, driver):
    result = verifier.verify_before("delete_everything", {}, driver)
    assert result.status is PreCheckStatus.FAILED
    assert any(c.name == "action_supported" for c in result.failures)


def test_clean_action_passes_all_pre_checks(verifier, driver):
    result = verifier.verify_before("clear_temp_files", {}, driver)
    assert result.passed is True
    assert result.failures == []


def test_missing_required_parameter_blocks_execution(verifier, driver):
    result = verifier.verify_before("kill_process_by_id", {}, driver)
    assert result.passed is False
    assert any(c.name == "parameters_valid" for c in result.failures)


def test_unknown_target_blocks_execution(verifier, driver):
    """TC06: the executor must not be called when the target is wrong."""
    result = verifier.verify_before("kill_process_by_id", {"pid": 999999}, driver)
    assert result.passed is False
    assert any(c.name == "target_identified" for c in result.failures)


def test_known_target_passes(verifier, driver):
    pid = driver.system.processes[0].pid
    result = verifier.verify_before("kill_process_by_id", {"pid": pid}, driver)
    assert result.passed is True


def test_missing_approval_blocks_execution(verifier, driver):
    result = verifier.verify_before("clear_temp_files", {}, driver, approval_granted=False)
    assert result.passed is False
    assert any(c.name == "approval_granted" for c in result.failures)


def test_insufficient_evidence_blocks_execution(verifier, driver):
    """TC04: a plausible suggestion with no evidence must not execute."""
    result = verifier.verify_before("clear_temp_files", {}, driver, evidence_sufficient=False)
    assert result.passed is False
    assert any(c.name == "evidence_sufficient" for c in result.failures)


def test_stale_risk_assessment_blocks_execution(verifier, driver):
    """TC07: altered action or parameters return it for reassessment."""
    result = verifier.verify_before("clear_temp_files", {}, driver, risk_assessment_current=False)
    assert result.passed is False
    assert any(c.name == "risk_current" for c in result.failures)


def test_inappropriate_action_is_blocked(verifier, driver):
    """Do not run a disk cleanup on a machine with plenty of free space."""
    driver.system.disk_free_gb = 180.0
    result = verifier.verify_before("clear_temp_files", {}, driver)
    assert result.passed is False
    assert any(c.name == "action_appropriate" for c in result.failures)


def test_unknown_service_is_blocked(verifier, driver):
    result = verifier.verify_before("restart_service", {"service_name": "NotAService"}, driver)
    assert result.passed is False


def test_known_service_passes(verifier, driver):
    result = verifier.verify_before("restart_service", {"service_name": "Spooler"}, driver)
    assert result.passed is True


def test_failure_reasons_are_readable(verifier, driver):
    result = verifier.verify_before("clear_temp_files", {}, driver, approval_granted=False)
    assert any("approval" in reason.lower() for reason in result.failure_reasons)


def test_pre_check_is_serialisable(verifier, driver):
    import json

    payload = json.dumps(verifier.verify_before("clear_temp_files", {}, driver).to_dict())
    assert json.loads(payload)["status"] in {"passed", "failed"}


def test_rollback_availability_is_recorded(verifier, driver):
    result = verifier.verify_before("clear_temp_files", {}, driver)
    rollback_check = next(c for c in result.checks if c.name == "rollback_known")
    assert "No rollback defined" in rollback_check.reason


# --------------------------------------------------------------------------
# Post-action checks: the contribution
# --------------------------------------------------------------------------

def test_real_fix_is_verified_as_success(verifier, driver):
    result = driver.execute("clear_temp_files")
    verdict = verifier.verify_after("clear_temp_files", result)
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS
    assert verdict.is_resolved is True


def test_command_succeeds_but_problem_remains_is_a_failure(verifier, driver):
    """TC08, and the whole point of the research. The command reports success,
    disk space did not change, and this must NOT be reported as resolved."""
    driver.inject_fault("clear_temp_files")
    result = driver.execute("clear_temp_files")

    assert result.success is True  # the command "worked"

    verdict = verifier.verify_after("clear_temp_files", result)
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE
    assert verdict.is_resolved is False


def test_failed_command_is_a_verified_failure(verifier, driver):
    result = driver.execute("kill_process_by_id", {"pid": 999999})
    verdict = verifier.verify_after("kill_process_by_id", result)
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE
    assert verdict.is_resolved is False


def test_killed_process_is_verified_gone(verifier, driver):
    pid = driver.system.processes[0].pid
    result = driver.execute("kill_process_by_id", {"pid": pid})
    verdict = verifier.verify_after("kill_process_by_id", result)
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS


def test_process_still_running_is_verified_failure(verifier, driver):
    pid = driver.system.processes[0].pid
    driver.inject_fault("kill_process_by_id")
    result = driver.execute("kill_process_by_id", {"pid": pid})
    verdict = verifier.verify_after("kill_process_by_id", result)
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE
    assert str(pid) in verdict.reason


def test_restarted_service_is_verified_running(verifier, driver):
    result = driver.execute("restart_service", {"service_name": "Spooler"})
    verdict = verifier.verify_after("restart_service", result)
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS


def test_service_still_stopped_is_verified_failure(verifier, driver):
    driver.inject_fault("restart_service")
    result = driver.execute("restart_service", {"service_name": "Spooler"})
    verdict = verifier.verify_after("restart_service", result)
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE


def test_flush_dns_is_verified_by_cache_being_empty(verifier, driver):
    result = driver.execute("flush_dns")
    verdict = verifier.verify_after("flush_dns", result)
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS


def test_winsock_reset_is_verified_by_stack_health(verifier, driver):
    result = driver.execute("reset_winsock")
    verdict = verifier.verify_after("reset_winsock", result)
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS


def test_disable_startup_item_is_verified(verifier, driver):
    result = driver.execute("disable_startup_item", {"item_name": "Spotify"})
    verdict = verifier.verify_after("disable_startup_item", result)
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS


# --------------------------------------------------------------------------
# Inconclusive is its own answer, never success
# --------------------------------------------------------------------------

def test_unverifiable_action_is_inconclusive_not_success(verifier, driver):
    result = driver.execute("restart_explorer")
    verdict = verifier.verify_after("restart_explorer", result)
    assert verdict.status is PostCheckStatus.INCONCLUSIVE
    assert verdict.is_resolved is False


def test_missing_state_field_is_inconclusive(verifier, driver):
    """If the evidence needed is absent, say so rather than guessing."""
    result = driver.execute("clear_temp_files")
    result.state_after = {}
    verdict = verifier.verify_after("clear_temp_files", result)
    assert verdict.status is PostCheckStatus.INCONCLUSIVE
    assert verdict.is_resolved is False


def test_missing_pid_parameter_is_inconclusive(verifier, driver):
    pid = driver.system.processes[0].pid
    result = driver.execute("kill_process_by_id", {"pid": pid})
    result.parameters = {}
    verdict = verifier.verify_after("kill_process_by_id", result)
    assert verdict.status is PostCheckStatus.INCONCLUSIVE


def test_unregistered_action_is_inconclusive(verifier, driver):
    result = driver.execute("clear_temp_files")
    verdict = verifier.verify_after("not_registered", result)
    assert verdict.status is PostCheckStatus.INCONCLUSIVE


def test_inconclusive_never_counts_as_resolved(verifier, driver):
    result = driver.execute("restart_explorer")
    verdict = verifier.verify_after("restart_explorer", result)
    assert verdict.status is PostCheckStatus.INCONCLUSIVE
    assert verdict.is_resolved is False


# --------------------------------------------------------------------------
# Read-only actions
# --------------------------------------------------------------------------

def test_diagnostic_action_is_verified_by_nothing_changing(verifier, driver):
    result = driver.execute("check_disk_space")
    verdict = verifier.verify_after("check_disk_space", result)
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS


def test_read_only_action_that_changed_state_is_a_failure(verifier, driver):
    result = driver.execute("check_disk_space")
    result.state_after = dict(result.state_after)
    result.state_after["disk_free_gb"] = 999
    verdict = verifier.verify_after("check_disk_space", result)
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE


# --------------------------------------------------------------------------
# Contract registry
# --------------------------------------------------------------------------

def test_every_contract_names_a_state_scope():
    for action_id, contract in CONTRACTS.items():
        assert contract.state_scope, f"{action_id} has no state scope"


def test_state_changing_contracts_declare_verification_intent():
    """Either a postcondition, or an explicit acknowledgement that there is
    none. Silence would let an unverifiable action look verified."""
    for action_id, contract in CONTRACTS.items():
        if contract.read_only:
            continue
        assert contract.postcondition is not None or contract.rollback_action_id is None, (
            f"{action_id} has a rollback but no postcondition to trigger it"
        )


def test_irreversible_actions_declare_no_rollback():
    """A killed process and a deleted temp file cannot be restored. Claiming a
    rollback for them would be worse than having none."""
    for action_id in ("kill_process_by_id", "clear_temp_files", "empty_recycle_bin"):
        assert CONTRACTS[action_id].has_rollback is False


def test_every_simulated_action_can_be_verified(driver):
    """No action should be runnable through the driver but unverifiable."""
    verifier = VerificationService()
    unverifiable = [
        action_id for action_id in driver._handlers
        if verifier.get_contract(action_id) is None
    ]
    assert unverifiable == [], f"actions without contracts: {unverifiable}"


def test_post_check_is_serialisable(verifier, driver):
    import json

    result = driver.execute("clear_temp_files")
    payload = json.dumps(verifier.verify_after("clear_temp_files", result).to_dict())
    restored = json.loads(payload)
    assert restored["status"] in {"verified_success", "verified_failure", "inconclusive"}
    assert restored["expected"]


# ---------------------------------------------------------------------------
# Regression: a read-only check must survive a busy machine.
#
# Found on real Windows hardware, not in simulation. A diagnostic reported
# verified_failure because the process list differed between the before and
# after snapshots - 285 processes became 286 while the command ran. Nothing had
# been changed by the action; the machine simply carried on being a machine.
# ---------------------------------------------------------------------------

def test_read_only_passes_when_only_the_process_list_drifted():
    """Processes starting by themselves is not the action changing state."""
    result = ExecutionResult(
        action_id="check_disk_space",
        success=True,
        driver="agent",
        state_before={
            "disk": {"disk_free_gb": 17.1, "disk_used_percent": 95.5},
            "processes": {"process_count": 285, "pids": [1, 2, 3]},
            "network": {"connected": True},
        },
        state_after={
            "disk": {"disk_free_gb": 17.1, "disk_used_percent": 95.5},
            "processes": {"process_count": 286, "pids": [1, 2, 3, 4]},
            "network": {"connected": True},
        },
    )

    verdict = VerificationService().verify_after("check_disk_space", result)
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS


def test_read_only_still_fails_when_real_state_changed():
    """The relaxation must not blunt the check it exists to make.

    Free disk space moving is the action having done something, and a read-only
    action must not do anything.
    """
    result = ExecutionResult(
        action_id="check_disk_space",
        success=True,
        driver="agent",
        state_before={
            "disk": {"disk_free_gb": 17.1},
            "processes": {"process_count": 285, "pids": [1, 2]},
        },
        state_after={
            "disk": {"disk_free_gb": 22.9},
            "processes": {"process_count": 285, "pids": [1, 2]},
        },
    )

    verdict = VerificationService().verify_after("check_disk_space", result)
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE


def test_every_driver_snapshots_what_its_contract_will_compare():
    """One source of truth for the state scope.

    Three drivers each kept a private copy of this map, and they had drifted:
    PowerShell snapshotted everything regardless of the action, so a read-only
    check compared state the action never touched.
    """
    from app.services.execution.base import scope_for

    for action_id, contract in CONTRACTS.items():
        assert scope_for(action_id) == contract.state_scope, action_id


def test_read_only_tolerates_the_disk_drifting_under_it():
    """Second half of the same real-hardware finding.

    With the snapshot narrowed to the disk, the check still failed: free space
    moved 10 MB while the command ran, because Windows was writing logs. A
    read-only action did not do that, and must not be blamed for it.
    """
    result = ExecutionResult(
        action_id="check_disk_space",
        success=True,
        driver="agent",
        state_before={"disk_free_gb": 17.07, "disk_used_percent": 95.5},
        state_after={"disk_free_gb": 17.08, "disk_used_percent": 95.5},
    )
    verdict = VerificationService().verify_after("check_disk_space", result)
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS


def test_the_drift_allowance_does_not_hide_a_real_change():
    """The allowance is far below what a state-changing action does.

    Freeing half a gigabyte is not drift, and an action claiming to be
    read-only that does it must still be caught.
    """
    result = ExecutionResult(
        action_id="check_disk_space",
        success=True,
        driver="agent",
        state_before={"disk_free_gb": 17.07, "disk_used_percent": 95.5},
        state_after={"disk_free_gb": 17.60, "disk_used_percent": 94.9},
    )
    verdict = VerificationService().verify_after("check_disk_space", result)
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE
