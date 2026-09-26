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


# --------------------------------------------------------------------------
# Registered rollbacks
#
# A rollback named in a contract has to exist everywhere it will be looked for.
# It was named in one place and missing from the other two for as long as the
# recovery path went unexercised: every attempt raised, and the request was
# escalated with the message "no safe rollback is defined", which was not what
# had happened.
# --------------------------------------------------------------------------

def _actions_with_rollback():
    return [c for c in CONTRACTS.values() if c.has_rollback]


def test_at_least_one_action_has_a_rollback():
    assert _actions_with_rollback()


def test_every_rollback_action_has_its_own_contract():
    for contract in _actions_with_rollback():
        assert contract.rollback_action_id in CONTRACTS, contract.action_id


def test_every_rollback_action_is_in_the_catalogue():
    from app.services.agents.action_executor_agent import ActionExecutorAgent

    catalogue = ActionExecutorAgent().actions
    for contract in _actions_with_rollback():
        assert contract.rollback_action_id in catalogue, contract.action_id


def test_every_rollback_action_can_be_run_by_the_driver(driver):
    for contract in _actions_with_rollback():
        assert driver.supports(contract.rollback_action_id), contract.action_id


def test_a_rollback_is_verified_like_any_other_action():
    """Recovery is not exempt from post-checks, or it would be the one step
    taken on trust - at the point where the machine is already in a state
    nobody asked for."""
    for contract in _actions_with_rollback():
        rollback = CONTRACTS[contract.rollback_action_id]
        assert rollback.postcondition is not None or rollback.read_only, contract.action_id


def test_rollback_of_a_rollback_returns_to_the_original_action():
    """Undoing an undo is the action itself; anything else is a chain that
    does not terminate."""
    for contract in _actions_with_rollback():
        rollback = CONTRACTS[contract.rollback_action_id]
        if rollback.has_rollback:
            assert rollback.rollback_action_id == contract.action_id


def test_enable_startup_item_verifies_the_item_came_back(verifier, driver):
    driver.execute("disable_startup_item", {"item_name": "Spotify"})
    result = driver.execute("enable_startup_item", {"item_name": "Spotify"})
    verdict = verifier.verify_after("enable_startup_item", result)
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS


def test_a_rollback_that_changes_nothing_is_not_verified(verifier, driver):
    driver.execute("disable_startup_item", {"item_name": "Spotify"})
    driver.inject_fault("enable_startup_item")
    result = driver.execute("enable_startup_item", {"item_name": "Spotify"})

    assert result.success is True          # the command "worked"
    verdict = verifier.verify_after("enable_startup_item", result)
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE


# --------------------------------------------------------------------------
# Is this action even appropriate?
#
# Until 24 September 2026 only the disk cleanups asked. The network actions -
# the ones that interrupt a connection or cost the user a restart - would run
# on a machine whose network was working, because nobody had checked. A user
# reporting slow internet could be handed a Winsock reset and a reboot for a
# problem that was somewhere else entirely.
# --------------------------------------------------------------------------

def _machine(**fields):
    system = SimulatedSystem()
    for name, value in fields.items():
        setattr(system, name, value)
    return SimulatedDriver(system)


def _refusal(result):
    return " ".join(c.reason for c in result.failures)


def test_flushing_an_empty_dns_cache_is_refused(verifier):
    result = verifier.verify_before("flush_dns", {}, _machine(dns_cache_entries=0))

    assert result.status is PreCheckStatus.FAILED
    assert "already empty" in _refusal(result)


def test_flushing_a_populated_dns_cache_is_allowed(verifier):
    result = verifier.verify_before("flush_dns", {}, _machine(dns_cache_entries=412))
    assert result.status is PreCheckStatus.PASSED


def test_resetting_the_adapter_on_a_working_connection_is_refused(verifier):
    """The user would lose a connection that was doing nothing wrong."""
    result = verifier.verify_before("reset_network_adapter", {}, _machine(network_connected=True))

    assert result.status is PreCheckStatus.FAILED
    assert "interrupt a working connection" in _refusal(result)


def test_resetting_the_adapter_when_nothing_connects_is_allowed(verifier):
    result = verifier.verify_before("reset_network_adapter", {}, _machine(network_connected=False))
    assert result.status is PreCheckStatus.PASSED


def test_renewing_an_address_that_works_is_refused(verifier):
    result = verifier.verify_before("release_renew_ip", {}, _machine(network_connected=True))
    assert result.status is PreCheckStatus.FAILED


def test_a_winsock_reset_on_a_healthy_stack_is_refused(verifier):
    """It costs a restart, so it needs evidence that it is needed."""
    result = verifier.verify_before("reset_winsock", {}, _machine(winsock_healthy=True))

    assert result.status is PreCheckStatus.FAILED
    assert "cost a restart for nothing" in _refusal(result)


def test_a_winsock_reset_on_a_degraded_stack_is_allowed(verifier):
    result = verifier.verify_before("reset_winsock", {}, _machine(winsock_healthy=False))
    assert result.status is PreCheckStatus.PASSED


def test_a_winsock_reset_is_refused_where_the_stack_cannot_be_read(verifier):
    """Real Windows, today: stack integrity is not readable, so this refuses.

    An unverifiable justification for a destructive action is not a
    justification. The expert can still act outside the system.
    """
    class BlindDriver(SimulatedDriver):
        def capture_state(self, scope):
            state = super().capture_state(scope)
            state.pop("winsock_healthy", None)
            return state

    result = verifier.verify_before("reset_winsock", {}, BlindDriver(SimulatedSystem()))

    assert result.status is PreCheckStatus.FAILED
    assert "cannot confirm" in _refusal(result).lower()


def test_every_disruptive_network_action_asks_whether_it_is_needed():
    """The gap that started this: disk had the check, network did not."""
    for action_id in ("flush_dns", "release_renew_ip", "reset_winsock", "reset_network_adapter"):
        assert CONTRACTS[action_id].preconditions, action_id


def test_a_large_disk_at_95_percent_is_still_worth_cleaning(verifier):
    """20 GB free sounds ample until it is 5% of the disk.

    The machine that prompted this had 20.06 GB free and 94.7% used: fine to
    an absolute threshold, and plainly not fine to the person using it.
    """
    result = verifier.verify_before(
        "clear_temp_files", {}, _machine(disk_total_gb=380.0, disk_free_gb=20.06)
    )
    assert result.status is PreCheckStatus.PASSED


def test_a_roomy_disk_still_refuses_a_cleanup(verifier):
    result = verifier.verify_before(
        "clear_temp_files", {}, _machine(disk_total_gb=512.0, disk_free_gb=300.0)
    )

    assert result.status is PreCheckStatus.FAILED
    assert "would not address a real problem" in _refusal(result)


def test_a_small_disk_with_little_left_is_caught_by_free_space(verifier):
    result = verifier.verify_before(
        "clear_temp_files", {}, _machine(disk_total_gb=128.0, disk_free_gb=4.2)
    )
    assert result.status is PreCheckStatus.PASSED


# --------------------------------------------------------------------------
# Startup items: judged by the command, not by "enabled"
#
# Until 26 September 2026 the snapshot recorded only True/False per item, and
# the rollback check passed whenever the item was enabled afterwards. After a
# program re-registers itself - the reason a disable fails - it is enabled
# before the rollback runs, so a rollback that did nothing passed. Remediation
# #31 on the Windows test machine recorded exactly that: before true, after
# true, verified. The checks below read the saved command's fingerprint and
# whether the saved copy was consumed.
# --------------------------------------------------------------------------

import json

from app.services.startup_state import startup_record

ORIGINAL = r'"C:\Users\someone\AppData\Local\Microsoft\Teams\Update.exe" --processStart "Teams.exe"'
IMPOSTOR = r'"C:\Users\someone\AppData\Local\Temp\not-teams.exe"'


def _startup(action_id, before, after, success=True, item="Teams"):
    """A result as a driver would return it, with ``None`` meaning not captured."""
    return ExecutionResult(
        action_id=action_id,
        success=success,
        driver="test",
        parameters={"item_name": item},
        state_before={} if before is None else {item: before},
        state_after={} if after is None else {item: after},
    )


def _check(verifier, action_id, before, after):
    return verifier.verify_after(action_id, _startup(action_id, before, after))


# -- disable ------------------------------------------------------------------

def test_a_disable_with_the_original_command_saved_is_verified(verifier):
    verdict = _check(
        verifier, "disable_startup_item",
        startup_record(ORIGINAL, None), startup_record(None, ORIGINAL),
    )
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS
    assert verdict.evidence["before"]["enabled_command_sha256"] == (
        verdict.evidence["after"]["backup_command_sha256"]
    )


def test_a_disable_that_saved_nothing_is_not_verified(verifier):
    """Off, but with no copy the registered rollback cannot restore it."""
    verdict = _check(
        verifier, "disable_startup_item",
        startup_record(ORIGINAL, None), startup_record(None, None),
    )
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE
    assert "no copy" in verdict.reason


def test_a_disable_whose_item_vanished_is_inconclusive(verifier):
    """Removed from the Run key and not saved: neither key lists it, which the
    snapshot cannot tell apart from an unreadable one."""
    verdict = _check(verifier, "disable_startup_item", startup_record(ORIGINAL, None), None)
    assert verdict.status is PostCheckStatus.INCONCLUSIVE


def test_a_disable_that_saved_a_different_command_is_not_verified(verifier):
    verdict = _check(
        verifier, "disable_startup_item",
        startup_record(ORIGINAL, None), startup_record(None, IMPOSTOR),
    )
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE
    assert "not the one that was registered" in verdict.reason


def test_a_disable_with_no_before_state_is_inconclusive(verifier):
    """A saved copy with nothing to compare it against proves only that
    something was saved, not that it was the command that was removed."""
    verdict = _check(verifier, "disable_startup_item", None, startup_record(None, ORIGINAL))

    assert verdict.status is PostCheckStatus.INCONCLUSIVE
    assert verdict.is_resolved is False


def test_a_disable_with_an_unreadable_before_state_is_inconclusive(verifier):
    malformed = startup_record(ORIGINAL, None)
    malformed["enabled_command_sha256"] = None

    for before in (True, {"enabled": "yes"}, malformed):
        verdict = _check(verifier, "disable_startup_item", before, startup_record(None, ORIGINAL))
        assert verdict.status is PostCheckStatus.INCONCLUSIVE, before


def test_a_disable_whose_before_state_shows_it_off_is_inconclusive(verifier):
    """No enabled original was observed, so there is nothing the saved copy
    could be shown to match."""
    verdict = _check(
        verifier, "disable_startup_item",
        startup_record(None, ORIGINAL), startup_record(None, ORIGINAL),
    )
    assert verdict.status is PostCheckStatus.INCONCLUSIVE
    assert "does not show" in verdict.reason


def test_the_after_state_still_decides_an_observed_failure(verifier):
    """Without a before-state, an item that is still enabled - or off with
    nothing saved - is still a demonstrated failure, not an unknown."""
    still_on = _check(verifier, "disable_startup_item", None, startup_record(ORIGINAL, None))
    nothing_saved = _check(verifier, "disable_startup_item", None, startup_record(None, None))

    assert still_on.status is PostCheckStatus.VERIFIED_FAILURE
    assert nothing_saved.status is PostCheckStatus.VERIFIED_FAILURE


def test_a_disable_never_verifies_without_comparing_the_original(verifier):
    """Every success names a before-state whose enabled fingerprint equals the
    saved one. There is no other way to reach success."""
    befores = [None, True, startup_record(None, ORIGINAL), startup_record(ORIGINAL, None)]
    for before in befores:
        verdict = _check(verifier, "disable_startup_item", before, startup_record(None, ORIGINAL))
        if verdict.status is PostCheckStatus.VERIFIED_SUCCESS:
            assert verdict.evidence["before"]["enabled"] is True
            assert verdict.evidence["before"]["enabled_command_sha256"] == (
                verdict.evidence["after"]["backup_command_sha256"]
            )


def test_a_disable_with_a_backup_flag_but_no_fingerprint_is_inconclusive(verifier):
    after = startup_record(None, ORIGINAL)
    after["backup_command_sha256"] = None
    verdict = _check(verifier, "disable_startup_item", startup_record(ORIGINAL, None), after)
    assert verdict.status is PostCheckStatus.INCONCLUSIVE


# -- enable, the rollback ----------------------------------------------------

def test_a_rollback_that_restored_the_saved_command_is_verified(verifier):
    verdict = _check(
        verifier, "enable_startup_item",
        startup_record(None, ORIGINAL), startup_record(ORIGINAL, None),
    )
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS


def test_after_re_registration_a_rollback_must_consume_the_saved_copy(verifier):
    """The #31 case. The item was enabled before the rollback ran, so only the
    saved copy being used up shows that the rollback did anything."""
    before = startup_record(ORIGINAL, ORIGINAL)

    restored = _check(verifier, "enable_startup_item", before, startup_record(ORIGINAL, None))
    did_nothing = _check(verifier, "enable_startup_item", before, startup_record(ORIGINAL, ORIGINAL))

    assert restored.status is PostCheckStatus.VERIFIED_SUCCESS
    assert did_nothing.status is PostCheckStatus.VERIFIED_FAILURE
    assert "still in place" in did_nothing.reason


def test_an_item_enabled_with_another_command_is_not_restored(verifier):
    before = startup_record(IMPOSTOR, ORIGINAL)

    unchanged = _check(verifier, "enable_startup_item", before, startup_record(IMPOSTOR, ORIGINAL))
    copy_gone = _check(verifier, "enable_startup_item", before, startup_record(IMPOSTOR, None))

    assert unchanged.status is PostCheckStatus.VERIFIED_FAILURE
    assert copy_gone.status is PostCheckStatus.VERIFIED_FAILURE
    assert "different command" in copy_gone.reason


def test_a_rollback_with_nothing_saved_beforehand_restored_nothing(verifier):
    verdict = _check(
        verifier, "enable_startup_item",
        startup_record(ORIGINAL, None), startup_record(ORIGINAL, None),
    )
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE
    assert "nothing to restore" in verdict.reason


def test_a_rollback_that_left_the_item_off_is_not_verified(verifier):
    verdict = _check(
        verifier, "enable_startup_item",
        startup_record(None, ORIGINAL), startup_record(None, ORIGINAL),
    )
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE


def test_enabled_true_alone_is_not_evidence_of_restoration(verifier):
    """The old snapshot form. It cannot say which command came back."""
    verdict = verifier.verify_after(
        "enable_startup_item",
        ExecutionResult(
            action_id="enable_startup_item", success=True, driver="test",
            parameters={"item_name": "Teams"},
            state_before={"Teams": True}, state_after={"Teams": True},
        ),
    )
    assert verdict.status is PostCheckStatus.INCONCLUSIVE
    assert verdict.is_resolved is False


def test_a_rollback_with_missing_state_is_inconclusive(verifier):
    no_before = _check(verifier, "enable_startup_item", None, startup_record(ORIGINAL, None))
    no_after = _check(verifier, "enable_startup_item", startup_record(None, ORIGINAL), None)

    assert no_before.status is PostCheckStatus.INCONCLUSIVE
    assert no_after.status is PostCheckStatus.INCONCLUSIVE


def test_startup_verdicts_carry_fingerprints_never_commands(verifier):
    cases = [
        ("disable_startup_item", startup_record(ORIGINAL, None), startup_record(None, ORIGINAL)),
        ("disable_startup_item", startup_record(ORIGINAL, None), startup_record(None, IMPOSTOR)),
        ("enable_startup_item", startup_record(None, ORIGINAL), startup_record(ORIGINAL, None)),
        ("enable_startup_item", startup_record(IMPOSTOR, ORIGINAL), startup_record(IMPOSTOR, None)),
    ]
    for action_id, before, after in cases:
        text = json.dumps(_check(verifier, action_id, before, after).to_dict())
        assert "Update.exe" not in text and "not-teams" not in text, action_id


# -- the same rules against the simulated machine ----------------------------

def test_a_simulated_rollback_that_did_nothing_is_not_verified(verifier, driver):
    """Teams re-registers, so the rollback starts from an enabled item. The
    old check passed this; the command reports success and changes nothing."""
    driver.execute("disable_startup_item", {"item_name": "Teams"})
    driver.inject_fault("enable_startup_item")
    result = driver.execute("enable_startup_item", {"item_name": "Teams"})

    assert result.success is True
    verdict = verifier.verify_after("enable_startup_item", result)
    assert verdict.status is PostCheckStatus.VERIFIED_FAILURE


def test_a_simulated_rollback_after_re_registration_is_verified(verifier, driver):
    driver.execute("disable_startup_item", {"item_name": "Teams"})
    result = driver.execute("enable_startup_item", {"item_name": "Teams"})

    verdict = verifier.verify_after("enable_startup_item", result)
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS


# -- before acting -------------------------------------------------------------

class _LegacyStartupDriver:
    """A device whose agent still reports startup items as bare booleans."""

    name = "legacy"

    def supports(self, action_id):
        return True

    def capture_state(self, scope):
        return {"Teams": True}


def test_disabling_an_item_that_is_already_off_is_refused(verifier, driver):
    """A failed disable is rolled back from the saved copy, which would switch
    on an item the user had turned off."""
    driver.execute("disable_startup_item", {"item_name": "Spotify"})
    result = verifier.verify_before("disable_startup_item", {"item_name": "Spotify"}, driver)

    assert result.status is PreCheckStatus.FAILED
    assert "nothing to disable" in _refusal(result)


def test_restoring_an_item_with_no_saved_copy_is_refused(verifier, driver):
    """Enabling rolls back by disabling, so a failed enable here would switch
    off an item nobody asked to touch."""
    result = verifier.verify_before("enable_startup_item", {"item_name": "OneDrive"}, driver)

    assert result.status is PreCheckStatus.FAILED
    assert "nothing to restore" in _refusal(result)


def test_restoring_a_saved_item_is_allowed(verifier, driver):
    driver.execute("disable_startup_item", {"item_name": "Spotify"})
    result = verifier.verify_before("enable_startup_item", {"item_name": "Spotify"}, driver)
    assert result.status is PreCheckStatus.PASSED


def test_an_unreadable_startup_record_is_refused_before_acting(verifier):
    """A post-check could never verify it, so the action does not start."""
    result = verifier.verify_before(
        "disable_startup_item", {"item_name": "Teams"}, _LegacyStartupDriver()
    )
    assert result.status is PreCheckStatus.FAILED
    assert "cannot be read in full" in _refusal(result)
