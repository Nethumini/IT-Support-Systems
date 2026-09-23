"""Pre-action and post-action verification for remediation.

Two questions, asked at two different moments:

* **Before**: is it safe and permitted to run this now? (thesis 5.3.4, TC06)
* **After**: did the user's problem actually go away? (thesis 8, TC08)

The second question is the contribution. A command that exits zero has proved
only that it ran. So post-checks never read the exit code - they compare the
state captured before and after against what the action was supposed to change.

Three outcomes are possible afterwards, and the third one matters:

* ``VERIFIED_SUCCESS`` - the expected change is observable
* ``VERIFIED_FAILURE`` - it demonstrably did not happen
* ``INCONCLUSIVE`` - it cannot be determined from the evidence available

``INCONCLUSIVE`` is never reported as resolved. A system that cannot tell must
say so rather than guess, which is why it is a distinct outcome and not folded
into either success or failure.

Every check here is deterministic Python. No LLM decides whether a remediation
worked; thesis 6.4.1 requires these to be unit-testable from their inputs.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)

__all__ = [
    "PreCheckStatus",
    "PostCheckStatus",
    "CheckOutcome",
    "PreVerification",
    "PostVerification",
    "ActionContract",
    "VerificationService",
    "CONTRACTS",
]


class PreCheckStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"


class PostCheckStatus(str, Enum):
    VERIFIED_SUCCESS = "verified_success"
    VERIFIED_FAILURE = "verified_failure"
    INCONCLUSIVE = "inconclusive"


@dataclass
class CheckOutcome:
    """One named check and what it found."""

    name: str
    passed: bool
    reason: str
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "reason": self.reason,
            "evidence": dict(self.evidence),
        }


@dataclass
class PreVerification:
    """Result of everything checked before execution."""

    status: PreCheckStatus
    checks: List[CheckOutcome] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.status is PreCheckStatus.PASSED

    @property
    def failures(self) -> List[CheckOutcome]:
        return [c for c in self.checks if not c.passed]

    @property
    def failure_reasons(self) -> List[str]:
        return [f"{c.name}: {c.reason}" for c in self.failures]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "checks": [c.to_dict() for c in self.checks],
            "failure_reasons": self.failure_reasons,
        }


@dataclass
class PostVerification:
    """Result of checking whether the problem is actually gone."""

    status: PostCheckStatus
    reason: str
    expected: str = ""
    observed: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_resolved(self) -> bool:
        """Only an observed success counts. Inconclusive is not resolved."""
        return self.status is PostCheckStatus.VERIFIED_SUCCESS

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "reason": self.reason,
            "expected": self.expected,
            "observed": self.observed,
            "evidence": dict(self.evidence),
        }


# ---------------------------------------------------------------------------
# Contracts
# ---------------------------------------------------------------------------

#: A precondition takes the parameters and the state read just before running,
#: and returns one outcome.
PreconditionFn = Callable[[Dict[str, Any], Dict[str, Any]], CheckOutcome]

#: A postcondition compares before/after state and returns a verdict.
PostconditionFn = Callable[[Dict[str, Any], Dict[str, Any], Dict[str, Any]], PostVerification]


@dataclass
class ActionContract:
    """What must hold before an action runs, and what must change after it."""

    action_id: str
    #: State scope to snapshot for this action, e.g. "disk".
    state_scope: str
    #: Parameters that must be present and non-empty.
    required_parameters: Sequence[str] = ()
    #: Action id that undoes this one, when one exists. ``None`` means no safe
    #: rollback - failure escalates instead of being retried blindly.
    rollback_action_id: Optional[str] = None
    #: Action-specific safety prerequisites.
    preconditions: Sequence[PreconditionFn] = ()
    #: How to tell whether it worked. ``None`` means the action changes nothing
    #: observable, and is verified by state being unchanged.
    postcondition: Optional[PostconditionFn] = None
    #: True for actions that only read state.
    read_only: bool = False
    description: str = ""

    @property
    def has_rollback(self) -> bool:
        return self.rollback_action_id is not None


#: Snapshot fields that move on their own on a live machine. A Windows desktop
#: starts and stops processes constantly, so the process list differs between
#: two reads taken a second apart even when nothing ran in between.
#:
#: They are excluded from the read-only equality check because they carry no
#: information about whether the action changed anything - and including them
#: made every read-only check fail on real hardware while passing against the
#: simulator, which is the worst possible combination: a verification mechanism
#: that only works where there is nothing to verify.
VOLATILE_STATE_FIELDS = frozenset({"pids", "process_count"})

#: Readings that move continuously on a running machine, with how far they may
#: move between two snapshots and still count as unchanged.
#:
#: Measured, not guessed: on the Windows test machine free space moved about
#: 10 MB in the second a diagnostic took to run, as the operating system wrote
#: logs and temporary files. These allowances sit an order of magnitude above
#: that drift and an order of magnitude below what any state-changing action in
#: the catalogue does - a temp-file clean-up frees hundreds of megabytes - so
#: the check still catches an action mislabelled as read-only.
#:
#: Absolute rather than proportional on purpose. A proportional allowance would
#: scale with the size of the disk, so the same clean-up that fails the check on
#: a small disk would pass on a large one.
READ_ONLY_TOLERANCE = {
    "disk_free_gb": 0.1,        # 100 MB
    "disk_used_percent": 0.1,   # a tenth of a percentage point
}


def _within_tolerance(field: str, before: Any, after: Any) -> bool:
    """Whether two readings of the same field are the same to within its drift."""
    allowance = READ_ONLY_TOLERANCE.get(field)
    if allowance is None:
        return before == after
    if not isinstance(before, (int, float)) or not isinstance(after, (int, float)):
        return before == after
    return abs(float(before) - float(after)) <= allowance


def _unchanged(before: Any, after: Any) -> bool:
    """Compare two snapshots, allowing each reading its own measured drift.

    Recurses so an "all" snapshot, which nests one mapping per scope, is
    compared field by field rather than as one opaque blob.
    """
    if isinstance(before, dict) and isinstance(after, dict):
        if before.keys() != after.keys():
            return False
        return all(
            _unchanged(before[key], after[key])
            if isinstance(before[key], dict)
            else _within_tolerance(key, before[key], after[key])
            for key in before
        )

    return before == after


def _stable(state: Any) -> Any:
    """A snapshot with the self-drifting fields removed, at any nesting depth.

    A scoped snapshot is flat (``{"disk_free_gb": ...}``); an "all" snapshot
    nests one per scope (``{"disk": {...}, "processes": {...}}``), so this
    recurses rather than filtering only the top level.
    """
    if isinstance(state, dict):
        return {
            key: _stable(value)
            for key, value in state.items()
            if key not in VOLATILE_STATE_FIELDS
        }
    return state


def _missing(field_name: str, state: Dict[str, Any]) -> PostVerification:
    return PostVerification(
        status=PostCheckStatus.INCONCLUSIVE,
        reason=(
            f"Cannot verify: {field_name!r} was not captured in the state snapshot, "
            "so the outcome is unknown."
        ),
        evidence={"available_fields": sorted(state)},
    )


def _numeric_increase(field_name: str, label: str):
    """Postcondition: a numeric field must have gone up."""

    def check(before: Dict[str, Any], after: Dict[str, Any], _params: Dict[str, Any]) -> PostVerification:
        if field_name not in before or field_name not in after:
            return _missing(field_name, after)
        was, now = before[field_name], after[field_name]
        evidence = {"before": was, "after": now, "field": field_name}
        if now > was:
            return PostVerification(
                status=PostCheckStatus.VERIFIED_SUCCESS,
                reason=f"{label} rose from {was} to {now}.",
                expected=f"{label} increases",
                observed=f"{was} -> {now}",
                evidence=evidence,
            )
        return PostVerification(
            status=PostCheckStatus.VERIFIED_FAILURE,
            reason=f"{label} did not increase (still {now}). The command completed but the problem remains.",
            expected=f"{label} increases",
            observed=f"{was} -> {now}",
            evidence=evidence,
        )

    return check


def _numeric_decrease(field_name: str, label: str):
    def check(before: Dict[str, Any], after: Dict[str, Any], _params: Dict[str, Any]) -> PostVerification:
        if field_name not in before or field_name not in after:
            return _missing(field_name, after)
        was, now = before[field_name], after[field_name]
        evidence = {"before": was, "after": now, "field": field_name}
        if now < was:
            return PostVerification(
                status=PostCheckStatus.VERIFIED_SUCCESS,
                reason=f"{label} fell from {was} to {now}.",
                expected=f"{label} decreases",
                observed=f"{was} -> {now}",
                evidence=evidence,
            )
        return PostVerification(
            status=PostCheckStatus.VERIFIED_FAILURE,
            reason=f"{label} did not fall (still {now}). The command completed but the problem remains.",
            expected=f"{label} decreases",
            observed=f"{was} -> {now}",
            evidence=evidence,
        )

    return check


def _equals(field_name: str, target: Any, label: str):
    def check(before: Dict[str, Any], after: Dict[str, Any], _params: Dict[str, Any]) -> PostVerification:
        if field_name not in after:
            return _missing(field_name, after)
        now = after[field_name]
        evidence = {"before": before.get(field_name), "after": now, "expected": target}
        if now == target:
            return PostVerification(
                status=PostCheckStatus.VERIFIED_SUCCESS,
                reason=f"{label} is now {target!r} as expected.",
                expected=f"{label} == {target!r}",
                observed=repr(now),
                evidence=evidence,
            )
        return PostVerification(
            status=PostCheckStatus.VERIFIED_FAILURE,
            reason=f"{label} is {now!r}, expected {target!r}. The command completed but the problem remains.",
            expected=f"{label} == {target!r}",
            observed=repr(now),
            evidence=evidence,
        )

    return check


def _process_gone(before: Dict[str, Any], after: Dict[str, Any], params: Dict[str, Any]) -> PostVerification:
    if "pids" not in after:
        return _missing("pids", after)
    try:
        pid = int(params.get("pid"))
    except (TypeError, ValueError):
        return PostVerification(
            status=PostCheckStatus.INCONCLUSIVE,
            reason="Cannot verify: no valid pid parameter to check against.",
            evidence={"parameters": dict(params)},
        )
    evidence = {"pid": pid, "pids_before": before.get("pids"), "pids_after": after.get("pids")}
    if pid not in after["pids"]:
        return PostVerification(
            status=PostCheckStatus.VERIFIED_SUCCESS,
            reason=f"Process {pid} is no longer running.",
            expected=f"PID {pid} absent",
            observed="absent",
            evidence=evidence,
        )
    return PostVerification(
        status=PostCheckStatus.VERIFIED_FAILURE,
        reason=f"Process {pid} is still running. The command completed but the problem remains.",
        expected=f"PID {pid} absent",
        observed="still present",
        evidence=evidence,
    )


def _service_running(before: Dict[str, Any], after: Dict[str, Any], params: Dict[str, Any]) -> PostVerification:
    name = str(params.get("service_name") or params.get("name") or "")
    if not name:
        return PostVerification(
            status=PostCheckStatus.INCONCLUSIVE,
            reason="Cannot verify: no service name given.",
            evidence={"parameters": dict(params)},
        )
    if name not in after:
        return _missing(name, after)
    state = after[name]
    evidence = {"service": name, "before": before.get(name), "after": state}
    if state == "running":
        return PostVerification(
            status=PostCheckStatus.VERIFIED_SUCCESS,
            reason=f"Service {name} is running.",
            expected=f"{name} running",
            observed=state,
            evidence=evidence,
        )
    return PostVerification(
        status=PostCheckStatus.VERIFIED_FAILURE,
        reason=f"Service {name} is {state}, not running. The command completed but the problem remains.",
        expected=f"{name} running",
        observed=state,
        evidence=evidence,
    )


def _startup_item_disabled(before: Dict[str, Any], after: Dict[str, Any], params: Dict[str, Any]) -> PostVerification:
    name = str(params.get("item_name") or params.get("name") or "")
    if not name:
        return PostVerification(
            status=PostCheckStatus.INCONCLUSIVE,
            reason="Cannot verify: no startup item name given.",
            evidence={"parameters": dict(params)},
        )
    if name not in after:
        return _missing(name, after)
    evidence = {"item": name, "before": before.get(name), "after": after[name]}
    if after[name] is False:
        return PostVerification(
            status=PostCheckStatus.VERIFIED_SUCCESS,
            reason=f"Startup item {name} is disabled.",
            expected=f"{name} disabled",
            observed="disabled",
            evidence=evidence,
        )
    return PostVerification(
        status=PostCheckStatus.VERIFIED_FAILURE,
        reason=f"Startup item {name} is still enabled. The command completed but the problem remains.",
        expected=f"{name} disabled",
        observed="enabled",
        evidence=evidence,
    )


def _startup_item_enabled(before: Dict[str, Any], after: Dict[str, Any], params: Dict[str, Any]) -> PostVerification:
    """Did the item come back?

    This is the postcondition of a rollback, and it is written the same way as
    any other: a rollback that reports success is not a rollback that restored
    the machine, and the difference is only visible in observed state.
    """
    name = str(params.get("item_name") or params.get("name") or "")
    if not name:
        return PostVerification(
            status=PostCheckStatus.INCONCLUSIVE,
            reason="Cannot verify: no startup item name given.",
            evidence={"parameters": dict(params)},
        )
    if name not in after:
        return _missing(name, after)
    evidence = {"item": name, "before": before.get(name), "after": after[name]}
    if after[name] is True:
        return PostVerification(
            status=PostCheckStatus.VERIFIED_SUCCESS,
            reason=f"Startup item {name} is enabled again.",
            expected=f"{name} enabled",
            observed="enabled",
            evidence=evidence,
        )
    return PostVerification(
        status=PostCheckStatus.VERIFIED_FAILURE,
        reason=f"Startup item {name} is still disabled. The command completed but the item was not restored.",
        expected=f"{name} enabled",
        observed="disabled",
        evidence=evidence,
    )


# -- action-specific preconditions ------------------------------------------

def _require_pid_exists(params: Dict[str, Any], state: Dict[str, Any]) -> CheckOutcome:
    try:
        pid = int(params.get("pid"))
    except (TypeError, ValueError):
        return CheckOutcome("target_identified", False, "No valid pid given.", {"parameters": dict(params)})
    pids = state.get("pids")
    if pids is None:
        return CheckOutcome("target_identified", False, "Cannot confirm the process exists.", {})
    if pid in pids:
        return CheckOutcome("target_identified", True, f"Process {pid} is running.", {"pid": pid})
    return CheckOutcome("target_identified", False, f"No process with PID {pid} is running.", {"pid": pid})


def _require_service_known(params: Dict[str, Any], state: Dict[str, Any]) -> CheckOutcome:
    name = str(params.get("service_name") or params.get("name") or "")
    if not name:
        return CheckOutcome("target_identified", False, "No service name given.", {})
    if name in state:
        return CheckOutcome("target_identified", True, f"Service {name} exists (currently {state[name]}).", {"service": name})
    return CheckOutcome("target_identified", False, f"Service {name} is not present on this machine.", {"service": name})


def _require_startup_item_known(params: Dict[str, Any], state: Dict[str, Any]) -> CheckOutcome:
    name = str(params.get("item_name") or params.get("name") or "")
    if not name:
        return CheckOutcome("target_identified", False, "No startup item name given.", {})
    if name in state:
        return CheckOutcome("target_identified", True, f"Startup item {name} exists.", {"item": name})
    return CheckOutcome("target_identified", False, f"Startup item {name} not found.", {"item": name})


#: A cleanup is worth running below either of these. Absolute space is what a
#: cleanup recovers, so it is the first test. The proportional arm exists
#: because a large disk can hold 20 GB free and still be at 95% used, which
#: leaves Windows short of the room it wants for updates and paging - and a
#: user looking at that machine is not wrong to call it full.
DISK_LOW_FREE_GB = 20
DISK_LOW_FREE_PERCENT = 10


def _require_disk_actually_low(params: Dict[str, Any], state: Dict[str, Any]) -> CheckOutcome:
    """Do not run a cleanup on a machine that has plenty of space."""
    free = state.get("disk_free_gb")
    if free is None:
        return CheckOutcome("action_appropriate", False, "Cannot read free disk space.", {})

    used_percent = state.get("disk_used_percent")
    free_percent = None if used_percent is None else 100 - used_percent
    evidence = {"disk_free_gb": free, "disk_used_percent": used_percent}

    if free < DISK_LOW_FREE_GB:
        return CheckOutcome(
            "action_appropriate", True,
            f"Free space is {free} GB, cleanup is appropriate.",
            evidence,
        )
    if free_percent is not None and free_percent < DISK_LOW_FREE_PERCENT:
        return CheckOutcome(
            "action_appropriate", True,
            f"Only {free_percent:.1f}% of the disk is free ({free} GB of a large disk), "
            "which is little enough to affect the machine; cleanup is appropriate.",
            evidence,
        )
    return CheckOutcome(
        "action_appropriate",
        False,
        f"Free space is already {free} GB; cleanup would not address a real problem.",
        evidence,
    )


# Whether the machine is in the state an action treats. Until 24 September 2026
# only the disk cleanups asked this, so a user reporting slow internet could
# have the network stack reset - a restart - on a machine whose network was
# working. The check is cheapest where the action is most disruptive.


def _require_dns_cache_not_empty(params: Dict[str, Any], state: Dict[str, Any]) -> CheckOutcome:
    entries = state.get("dns_cache_entries")
    if entries is None:
        return CheckOutcome("action_appropriate", False, "Cannot read the DNS cache.", {})
    if entries > 0:
        return CheckOutcome(
            "action_appropriate", True,
            f"The DNS cache holds {entries} entries, so flushing it can change something.",
            {"dns_cache_entries": entries},
        )
    return CheckOutcome(
        "action_appropriate", False,
        "The DNS cache is already empty; flushing it would not address a real problem.",
        {"dns_cache_entries": entries},
    )


def _require_network_down(params: Dict[str, Any], state: Dict[str, Any]) -> CheckOutcome:
    """Do not interrupt a connection that is working."""
    connected = state.get("connected")
    if connected is None:
        return CheckOutcome("action_appropriate", False, "Cannot read network connectivity.", {})
    if connected is False:
        return CheckOutcome(
            "action_appropriate", True,
            "The machine has no network connection, so a reset is appropriate.",
            {"connected": connected},
        )
    return CheckOutcome(
        "action_appropriate", False,
        "The machine is connected to the network; resetting it would interrupt a working connection.",
        {"connected": connected},
    )


def _require_stack_degraded(params: Dict[str, Any], state: Dict[str, Any]) -> CheckOutcome:
    """A reset that costs the user a restart needs evidence that it is needed.

    Where the stack's health cannot be read at all - real Windows, today - this
    refuses rather than proceeds. An unverifiable justification for a
    destructive action is not a justification, and an expert can still act
    outside the system.
    """
    healthy = state.get("winsock_healthy")
    if healthy is None:
        return CheckOutcome(
            "action_appropriate", False,
            "Cannot confirm the network stack is faulty on this machine, so a reset "
            "that requires a restart is not justified from here.",
            {},
        )
    if healthy is False:
        return CheckOutcome(
            "action_appropriate", True,
            "The network stack reports as degraded, so a reset is appropriate.",
            {"winsock_healthy": healthy},
        )
    return CheckOutcome(
        "action_appropriate", False,
        "The network stack reports as healthy; a reset would cost a restart for nothing.",
        {"winsock_healthy": healthy},
    )


def _read_only_contract(action_id: str, scope: str, description: str) -> ActionContract:
    return ActionContract(
        action_id=action_id,
        state_scope=scope,
        read_only=True,
        description=description,
    )


#: The action contract registry. An action absent from here cannot be executed
#: through the verified path, whatever the catalogue says.
CONTRACTS: Dict[str, ActionContract] = {
    # --- diagnostics: read-only, nothing should change -----------------------
    "check_disk_space": _read_only_contract("check_disk_space", "disk", "Read free disk space"),
    "list_top_processes": _read_only_contract("list_top_processes", "processes", "List processes by memory"),
    "get_process_details": _read_only_contract("get_process_details", "processes", "Read one process"),
    "list_services": _read_only_contract("list_services", "services", "List service states"),
    "test_connectivity": _read_only_contract("test_connectivity", "network", "Test network reachability"),
    "check_system_health": _read_only_contract("check_system_health", "all", "Overall health readout"),
    "get_startup_programs": _read_only_contract("get_startup_programs", "startup", "List startup items"),
    "detect_background_apps": _read_only_contract("detect_background_apps", "processes", "List idle background apps"),
    "check_windows_updates": _read_only_contract("check_windows_updates", "updates", "List pending updates"),
    "analyze_slow_performance": _read_only_contract("analyze_slow_performance", "all", "Summarise likely causes"),

    # --- disk ---------------------------------------------------------------
    "clear_temp_files": ActionContract(
        action_id="clear_temp_files",
        state_scope="disk",
        preconditions=(_require_disk_actually_low,),
        postcondition=_numeric_increase("disk_free_gb", "Free disk space"),
        rollback_action_id=None,  # deleted temp files cannot be restored
        description="Delete temporary files to recover disk space",
    ),
    "clear_windows_temp": ActionContract(
        action_id="clear_windows_temp",
        state_scope="disk",
        preconditions=(_require_disk_actually_low,),
        postcondition=_numeric_increase("disk_free_gb", "Free disk space"),
        description="Delete Windows temporary files",
    ),
    "windows_disk_cleanup": ActionContract(
        action_id="windows_disk_cleanup",
        state_scope="disk",
        preconditions=(_require_disk_actually_low,),
        postcondition=_numeric_increase("disk_free_gb", "Free disk space"),
        description="Run Windows Disk Cleanup",
    ),
    "empty_recycle_bin": ActionContract(
        action_id="empty_recycle_bin",
        state_scope="disk",
        postcondition=_equals("recycle_bin_mb", 0.0, "Recycle Bin size"),
        rollback_action_id=None,  # emptying is irreversible by design
        description="Empty the Recycle Bin",
    ),
    "clear_browser_cache": ActionContract(
        action_id="clear_browser_cache",
        state_scope="disk",
        postcondition=_numeric_increase("disk_free_gb", "Free disk space"),
        description="Clear the browser cache",
    ),

    # --- processes and memory -----------------------------------------------
    "kill_process_by_id": ActionContract(
        action_id="kill_process_by_id",
        state_scope="processes",
        required_parameters=("pid",),
        preconditions=(_require_pid_exists,),
        postcondition=_process_gone,
        rollback_action_id=None,  # a killed process cannot be un-killed
        description="End a process by PID",
    ),
    "close_browser_tabs": ActionContract(
        action_id="close_browser_tabs",
        state_scope="processes",
        postcondition=_numeric_decrease("total_memory_mb", "Total memory in use"),
        description="Close inactive browser tabs",
    ),
    "optimize_memory": ActionContract(
        action_id="optimize_memory",
        state_scope="processes",
        postcondition=_numeric_decrease("total_memory_mb", "Total memory in use"),
        description="Trim process working sets",
    ),
    "restart_explorer": ActionContract(
        action_id="restart_explorer",
        state_scope="processes",
        postcondition=None,
        description="Restart the Windows shell",
    ),

    # --- network ------------------------------------------------------------
    "flush_dns": ActionContract(
        action_id="flush_dns",
        state_scope="network",
        preconditions=(_require_dns_cache_not_empty,),
        postcondition=_equals("dns_cache_entries", 0, "DNS cache entries"),
        description="Flush the DNS resolver cache",
    ),
    "release_renew_ip": ActionContract(
        action_id="release_renew_ip",
        state_scope="network",
        preconditions=(_require_network_down,),
        postcondition=_equals("connected", True, "Network connection"),
        description="Release and renew the IP address",
    ),
    "reset_winsock": ActionContract(
        action_id="reset_winsock",
        state_scope="network",
        preconditions=(_require_stack_degraded,),
        postcondition=_equals("winsock_healthy", True, "Winsock stack health"),
        rollback_action_id=None,  # requires a restart; escalate on failure
        description="Reset the Winsock catalogue",
    ),
    "reset_network_adapter": ActionContract(
        action_id="reset_network_adapter",
        state_scope="network",
        preconditions=(_require_network_down,),
        postcondition=_equals("connected", True, "Network connection"),
        rollback_action_id=None,
        description="Reset the network adapter",
    ),

    # --- services and startup ------------------------------------------------
    "restart_service": ActionContract(
        action_id="restart_service",
        state_scope="services",
        required_parameters=("service_name",),
        preconditions=(_require_service_known,),
        postcondition=_service_running,
        rollback_action_id=None,
        description="Restart a Windows service",
    ),
    "disable_startup_item": ActionContract(
        action_id="disable_startup_item",
        state_scope="startup",
        required_parameters=("item_name",),
        preconditions=(_require_startup_item_known,),
        postcondition=_startup_item_disabled,
        rollback_action_id="enable_startup_item",
        description="Disable an item that runs at startup",
    ),
    # The rollback needs a contract of its own, or recovery would be the one
    # step in the workflow taken on trust. It is also a legitimate action in
    # its own right, so it carries the reverse rollback.
    "enable_startup_item": ActionContract(
        action_id="enable_startup_item",
        state_scope="startup",
        required_parameters=("item_name",),
        preconditions=(_require_startup_item_known,),
        postcondition=_startup_item_enabled,
        rollback_action_id="disable_startup_item",
        description="Restore an item this system disabled at startup",
    ),
}


class VerificationService:
    """Runs the pre-action and post-action checks for a registered action."""

    def __init__(self, contracts: Optional[Dict[str, ActionContract]] = None) -> None:
        self.contracts = contracts if contracts is not None else CONTRACTS

    def get_contract(self, action_id: str) -> Optional[ActionContract]:
        return self.contracts.get(action_id)

    # -- before --------------------------------------------------------------

    def verify_before(
        self,
        action_id: str,
        parameters: Dict[str, Any],
        driver,
        *,
        approval_granted: bool = True,
        evidence_sufficient: bool = True,
        risk_assessment_current: bool = True,
    ) -> PreVerification:
        """Run every mandatory check before an action may execute.

        Any failure blocks execution. The checks mirror thesis 5.3.4 and
        novelty.md section 6, in that order.
        """
        parameters = parameters or {}
        checks: List[CheckOutcome] = []

        contract = self.get_contract(action_id)
        if contract is None:
            checks.append(CheckOutcome(
                "action_supported", False,
                f"No verification contract is registered for {action_id!r}; it cannot be executed.",
                {"action_id": action_id},
            ))
            return PreVerification(status=PreCheckStatus.FAILED, checks=checks)

        checks.append(CheckOutcome(
            "action_supported", True, f"{action_id} has a registered contract.", {"action_id": action_id}
        ))

        # 2. the driver can actually run it here
        supported = driver.supports(action_id)
        checks.append(CheckOutcome(
            "environment_allows", supported,
            f"Driver {driver.name!r} {'supports' if supported else 'does not support'} {action_id}.",
            {"driver": driver.name},
        ))

        # 3. required parameters present
        missing = [p for p in contract.required_parameters if not str(parameters.get(p, "")).strip()]
        checks.append(CheckOutcome(
            "parameters_valid", not missing,
            "All required parameters supplied." if not missing else f"Missing parameters: {', '.join(missing)}.",
            {"required": list(contract.required_parameters), "missing": missing},
        ))

        # 4. evidence behind the diagnosis
        checks.append(CheckOutcome(
            "evidence_sufficient", evidence_sufficient,
            "Diagnosis is supported by retrieved evidence." if evidence_sufficient
            else "No sufficient evidence supports this diagnosis.",
            {},
        ))

        # 5. risk classification still valid
        checks.append(CheckOutcome(
            "risk_current", risk_assessment_current,
            "Risk assessment is current for this action and parameters." if risk_assessment_current
            else "Risk assessment is stale; the action or parameters changed since it was made.",
            {},
        ))

        # 6. approval
        checks.append(CheckOutcome(
            "approval_granted", approval_granted,
            "Required approval is in place." if approval_granted else "Required human approval has not been granted.",
            {},
        ))

        # 7. rollback readiness is recorded, not required
        checks.append(CheckOutcome(
            "rollback_known", True,
            f"Rollback: {contract.rollback_action_id}." if contract.has_rollback
            else "No rollback defined; failure will escalate rather than auto-retry.",
            {"rollback_action_id": contract.rollback_action_id},
        ))

        # 8. action-specific prerequisites, against live state
        if supported and contract.preconditions:
            try:
                state = driver.capture_state(contract.state_scope)
            except Exception as exc:
                checks.append(CheckOutcome(
                    "state_readable", False, f"Could not read system state: {exc}", {}
                ))
                state = None
            if state is not None:
                for precondition in contract.preconditions:
                    checks.append(precondition(parameters, state))

        status = PreCheckStatus.PASSED if all(c.passed for c in checks) else PreCheckStatus.FAILED
        if status is PreCheckStatus.FAILED:
            logger.info("[VERIFY] Pre-check failed for %s: %s", action_id,
                        "; ".join(f"{c.name}: {c.reason}" for c in checks if not c.passed))
        return PreVerification(status=status, checks=checks)

    # -- after ---------------------------------------------------------------

    def verify_after(self, action_id: str, result) -> PostVerification:
        """Decide whether the problem is actually solved.

        Reads the before/after state on ``result``. The command's own success
        flag is used only to reject an action that never ran - it is never
        treated as evidence that the problem is gone.
        """
        contract = self.get_contract(action_id)
        if contract is None:
            return PostVerification(
                status=PostCheckStatus.INCONCLUSIVE,
                reason=f"No contract registered for {action_id!r}; the outcome cannot be verified.",
            )

        if not result.success:
            return PostVerification(
                status=PostCheckStatus.VERIFIED_FAILURE,
                reason=f"The action did not complete: {result.error or 'unknown error'}",
                expected=contract.description,
                observed="action failed to run",
                evidence={"error": result.error},
            )

        if contract.read_only:
            unchanged = _unchanged(_stable(result.state_before), _stable(result.state_after))
            return PostVerification(
                status=PostCheckStatus.VERIFIED_SUCCESS if unchanged else PostCheckStatus.VERIFIED_FAILURE,
                reason="Diagnostic action completed without changing system state." if unchanged
                       else "A read-only action changed system state, which should not happen.",
                expected="no change to system state",
                observed="unchanged" if unchanged else "state changed",
                evidence={"before": result.state_before, "after": result.state_after},
            )

        if contract.postcondition is None:
            return PostVerification(
                status=PostCheckStatus.INCONCLUSIVE,
                reason=(
                    f"{action_id} has no postcondition defined, so success cannot be confirmed "
                    "from observed state."
                ),
                expected=contract.description,
                observed="not checked",
            )

        verdict = contract.postcondition(result.state_before, result.state_after, getattr(result, "parameters", {}) or {})
        logger.info("[VERIFY] Post-check for %s: %s", action_id, verdict.status.value)
        return verdict
