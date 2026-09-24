"""Execution driver interface.

The remediation flow never runs a command directly. It asks a *driver* to run a
registered action, and the driver decides how that happens on this machine.

Thesis 5.3.4 requires that "the executor rejects free-form commands and invokes
only registered adapters", and that state is captured before and after so the
outcome can be verified against reality rather than against an exit code. Both
obligations live at this boundary.

Three drivers are anticipated:

* ``simulated`` - a controllable model of a machine. Used for development on
  non-Windows hosts and for evaluation, because it can reproduce a failure on
  demand. A verification-failure scenario cannot be staged reliably on real
  hardware.
* ``powershell`` - the real Windows implementation.
* ``posix`` - a small set of safe macOS/Linux equivalents, if ever needed.

They are interchangeable: the orchestrator above them cannot tell which is in
use, so the risk, approval and verification logic is identical in a demo and in
production.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


class ExecutionError(Exception):
    """Raised when a driver is asked to do something it must refuse.

    Distinct from an action that ran and failed: that returns an
    ``ExecutionResult`` with ``success=False``. This means the request itself
    was not executable - an unknown action, or a driver that cannot run here.
    """


class DeviceUnreachableError(ExecutionError):
    """The machine never answered, so nobody knows whether the action ran.

    Distinct from other refusals because it is the one failure a person has to
    go and look at: the request was well-formed, the action was permitted, and
    the machine simply did not reply.
    """


@dataclass
class ExecutionResult:
    """What happened when a driver ran an action.

    ``success`` means the command completed, nothing more. Whether the user's
    problem was actually solved is a separate question answered by post-action
    verification against ``state_after`` - the distinction thesis 8 calls the
    most important part of the contribution.
    """

    action_id: str
    success: bool
    driver: str
    output: str = ""
    error: Optional[str] = None
    duration_ms: int = 0
    #: Parameters the action ran with. Post-checks need these to know what to
    #: look for, and the audit trail needs them to be replayable.
    parameters: Dict[str, Any] = field(default_factory=dict)
    #: Relevant system state captured immediately before execution.
    state_before: Dict[str, Any] = field(default_factory=dict)
    #: The same fields captured immediately after.
    state_after: Dict[str, Any] = field(default_factory=dict)
    #: Set when the driver deliberately simulated a fault, so evaluation data
    #: can separate injected failures from genuine ones.
    fault_injected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "success": self.success,
            "driver": self.driver,
            "output": self.output,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "parameters": dict(self.parameters),
            "state_before": dict(self.state_before),
            "state_after": dict(self.state_after),
            "fault_injected": self.fault_injected,
        }


class ExecutionDriver(ABC):
    """Runs registered remediation actions and reports observable state."""

    #: Short driver name recorded on every result and audit entry.
    name: str = "base"

    @abstractmethod
    def supports(self, action_id: str) -> bool:
        """Whether this driver can run the given registered action."""

    @abstractmethod
    def capture_state(self, scope: str) -> Dict[str, Any]:
        """Read the observable state for a scope, e.g. ``disk`` or ``processes``.

        Used for the before/after snapshots that post-action verification
        compares. Must not change anything.
        """

    @abstractmethod
    def execute(
        self,
        action_id: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        """Run one registered action.

        Takes an action identifier, never a command string: a driver must not
        be reachable with free-form text, or the allow-list means nothing.
        """

    def is_available(self) -> bool:
        """Whether this driver can run on the current host."""
        return True


def scope_for(action_id: str) -> str:
    """Which slice of state to snapshot around this action.

    Read from the action's verification contract, so the driver snapshots
    exactly what the post-check will compare. Hardcoding a wider scope here
    made read-only checks fail on busy machines, because the extra state
    changed on its own between the two reads.
    """
    try:
        from app.services.verification import CONTRACTS
    except Exception:  # pragma: no cover - verification is optional for tests
        return "all"

    contract = CONTRACTS.get(action_id)
    return contract.state_scope if contract else "all"
