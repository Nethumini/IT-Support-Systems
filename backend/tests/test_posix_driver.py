"""Tests for the real-host and hybrid drivers.

The posix driver reads the actual machine, so these assert shape and safety
rather than exact values: a real disk reading cannot be predicted, but it can
be required to be positive, and the driver can be required to refuse anything
that would change the host.
"""
import platform

import pytest

from app.services.execution import (
    ExecutionError,
    HybridDriver,
    PosixDriver,
    SimulatedDriver,
    get_driver,
    reset_driver,
)
from app.services.verification import CONTRACTS, PostCheckStatus, VerificationService

posix_only = pytest.mark.skipif(
    platform.system() not in ("Darwin", "Linux"),
    reason="posix driver only runs on macOS and Linux",
)


@pytest.fixture(autouse=True)
def _clean_driver_cache():
    reset_driver()
    yield
    reset_driver()


@pytest.fixture
def posix():
    return PosixDriver()


@pytest.fixture
def hybrid():
    return HybridDriver()


# --------------------------------------------------------------------------
# Selection
# --------------------------------------------------------------------------

def test_posix_driver_is_selectable():
    assert get_driver("posix").name == "posix"


def test_hybrid_driver_is_selectable():
    assert get_driver("hybrid").name == "hybrid"


@posix_only
def test_posix_is_available_here(posix):
    assert posix.is_available() is True


# --------------------------------------------------------------------------
# Read-only guarantee - the point of this driver
# --------------------------------------------------------------------------

def test_posix_refuses_every_state_changing_action(posix):
    """Nothing that would modify the developer's own machine may run."""
    changing = [
        action_id for action_id, contract in CONTRACTS.items()
        if not contract.read_only
    ]
    assert changing, "expected some state-changing actions in the registry"
    for action_id in changing:
        assert posix.supports(action_id) is False
        with pytest.raises(ExecutionError, match="read-only"):
            posix.execute(action_id)


def test_posix_refuses_unknown_actions(posix):
    with pytest.raises(ExecutionError):
        posix.execute("rm_rf_everything")


def test_posix_only_claims_read_only_contracts(posix):
    """Every action it supports must be marked read-only in the registry."""
    for action_id in CONTRACTS:
        if posix.supports(action_id):
            assert CONTRACTS[action_id].read_only is True


# --------------------------------------------------------------------------
# Real readings
# --------------------------------------------------------------------------

@posix_only
def test_disk_reading_is_real_and_plausible(posix):
    state = posix.capture_state("disk")
    assert state["disk_free_gb"] > 0
    assert 0 <= state["disk_used_percent"] <= 100


@posix_only
def test_process_reading_finds_this_test_process(posix):
    import os

    state = posix.capture_state("processes")
    assert state["process_count"] > 0
    assert os.getpid() in state["pids"]


@posix_only
def test_check_disk_space_reports_the_real_host(posix):
    result = posix.execute("check_disk_space")
    assert result.success is True
    assert "GB free" in result.output
    assert platform.system() in result.output


@posix_only
def test_read_only_action_leaves_disk_unchanged(posix):
    result = posix.execute("check_disk_space")
    assert result.state_before["disk_free_gb"] == pytest.approx(
        result.state_after["disk_free_gb"], abs=0.5
    )


@posix_only
def test_system_health_includes_memory_and_cpu(posix):
    output = posix.execute("check_system_health").output
    assert "memory" in output.lower()
    assert "cpu" in output.lower()


def test_unreadable_scope_returns_empty_not_a_guess(posix):
    """Windows-only scopes have no honest posix equivalent."""
    assert posix.capture_state("services") == {}
    assert posix.capture_state("startup") == {}


@posix_only
def test_real_diagnostic_still_passes_post_verification(posix):
    """A real reading must verify the same way a simulated one does."""
    verifier = VerificationService()
    result = posix.execute("check_disk_space")
    verdict = verifier.verify_after("check_disk_space", result)
    assert verdict.status is PostCheckStatus.VERIFIED_SUCCESS


# --------------------------------------------------------------------------
# Hybrid routing
# --------------------------------------------------------------------------

@posix_only
def test_hybrid_sends_diagnostics_to_the_real_host(hybrid):
    result = hybrid.execute("check_disk_space")
    assert result.driver == "posix"
    assert platform.system() in result.output


def test_hybrid_sends_changes_to_the_simulated_machine(hybrid):
    result = hybrid.execute("clear_temp_files")
    assert result.driver == "simulated"


def test_hybrid_does_not_touch_the_real_disk(hybrid):
    """The whole point: a cleanup in a demo must not delete real files."""
    before = hybrid.system.disk_free_gb
    hybrid.execute("clear_temp_files")
    assert hybrid.system.disk_free_gb > before  # the simulated one changed


def test_hybrid_supports_both_kinds(hybrid):
    assert hybrid.supports("clear_temp_files") is True
    assert hybrid.supports("check_disk_space") is True
    assert hybrid.supports("not_an_action") is False


def test_hybrid_state_comes_from_the_simulated_machine(hybrid):
    """Pre-checks for a state-changing action must match the world it will
    change, or preconditions and postconditions disagree."""
    assert hybrid.capture_state("disk")["disk_free_gb"] == pytest.approx(
        hybrid.system.disk_free_gb, abs=0.01
    )


def test_hybrid_supports_fault_injection(hybrid):
    """The verification-failure demo must still work under hybrid."""
    hybrid.inject_fault("clear_temp_files")
    result = hybrid.execute("clear_temp_files")
    assert result.success is True
    assert result.fault_injected is True
    assert result.state_before == result.state_after


def test_hybrid_full_flow_still_verifies(hybrid):
    verifier = VerificationService()
    pre = verifier.verify_before("clear_temp_files", {}, hybrid)
    assert pre.passed is True
    result = hybrid.execute("clear_temp_files")
    assert verifier.verify_after("clear_temp_files", result).status is PostCheckStatus.VERIFIED_SUCCESS


def test_hybrid_catches_a_silent_failure(hybrid):
    verifier = VerificationService()
    hybrid.inject_fault("clear_temp_files")
    result = hybrid.execute("clear_temp_files")
    assert verifier.verify_after("clear_temp_files", result).status is PostCheckStatus.VERIFIED_FAILURE
