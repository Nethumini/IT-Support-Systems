"""Read-only diagnostics against the real host, for macOS and Linux.

Reads actual disk, memory, process and network state through ``psutil``. Every
action here is read-only: this driver refuses anything that would change the
machine. Genuine remediation on a developer's own laptop is not something a
research prototype should be doing.

**Scope, stated plainly.** This reads the host running the backend, which in a
single-machine development setup is also the user's laptop. In a real
deployment they are different machines, and inspecting a user's own device
would need a lightweight agent installed on it. That agent would be one more
driver behind this same interface - the risk, approval and verification layers
would not change. Recorded as future work rather than claimed as implemented.
"""
from __future__ import annotations

import logging
import platform
import socket
import time
from typing import Any, Dict, Optional

from .base import ExecutionDriver, ExecutionError, ExecutionResult, scope_for

logger = logging.getLogger(__name__)

#: Read-only actions this driver can answer from the real machine. Windows
#: specific diagnostics (services, startup items, Windows Update) are absent
#: because they have no honest equivalent here.
SUPPORTED_ACTIONS = {
    "check_disk_space",
    "list_top_processes",
    "get_process_details",
    "check_system_health",
    "test_connectivity",
    "detect_background_apps",
    "analyze_slow_performance",
}


def _psutil():
    try:
        import psutil

        return psutil
    except ImportError as exc:  # pragma: no cover - psutil is a dependency
        raise ExecutionError("psutil is required for the posix driver") from exc


class PosixDriver(ExecutionDriver):
    """Real, read-only diagnostics on a macOS or Linux host."""

    name = "posix"

    def is_available(self) -> bool:
        return platform.system() in ("Darwin", "Linux")

    def supports(self, action_id: str) -> bool:
        return action_id in SUPPORTED_ACTIONS

    # -- state ---------------------------------------------------------------

    def capture_state(self, scope: str) -> Dict[str, Any]:
        psutil = _psutil()

        if scope == "disk":
            usage = psutil.disk_usage("/")
            return {
                "disk_free_gb": round(usage.free / 1024 ** 3, 2),
                "disk_used_percent": usage.percent,
            }

        if scope == "processes":
            procs = list(psutil.process_iter(["pid", "name", "memory_info"]))
            total_mb = sum(
                (p.info["memory_info"].rss if p.info.get("memory_info") else 0)
                for p in procs
            ) // (1024 ** 2)
            return {
                "process_count": len(procs),
                "total_memory_mb": int(total_mb),
                "pids": sorted(p.info["pid"] for p in procs),
            }

        if scope == "network":
            return {
                "connected": self._has_connectivity(),
                "hostname": socket.gethostname(),
            }

        if scope == "all":
            return {s: self.capture_state(s) for s in ("disk", "processes", "network")}

        # A scope this driver cannot read honestly returns nothing rather than
        # a guess; post-checks treat missing fields as INCONCLUSIVE.
        return {}

    @staticmethod
    def _has_connectivity(timeout: float = 1.5) -> bool:
        try:
            with socket.create_connection(("1.1.1.1", 53), timeout=timeout):
                return True
        except OSError:
            return False

    # -- execution -----------------------------------------------------------

    def execute(
        self,
        action_id: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        parameters = parameters or {}

        if not self.supports(action_id):
            raise ExecutionError(
                f"The posix driver is read-only and cannot run {action_id!r}. "
                "State-changing actions require the simulated or powershell driver."
            )

        scope = scope_for(action_id)
        before = self.capture_state(scope)
        started = time.perf_counter()

        try:
            output = getattr(self, f"_{action_id}")(parameters)
            success, error = True, None
        except Exception as exc:
            output, success, error = "", False, str(exc)

        return ExecutionResult(
            action_id=action_id,
            success=success,
            driver=self.name,
            output=output,
            error=error,
            duration_ms=int((time.perf_counter() - started) * 1000),
            parameters=dict(parameters),
            state_before=before,
            state_after=self.capture_state(scope),
        )

    # -- handlers ------------------------------------------------------------

    def _check_disk_space(self, _p: Dict[str, Any]) -> str:
        psutil = _psutil()
        usage = psutil.disk_usage("/")
        return (
            f"{usage.free / 1024 ** 3:.1f} GB free of {usage.total / 1024 ** 3:.0f} GB "
            f"({usage.percent}% used) on this {platform.system()} host."
        )

    def _list_top_processes(self, _p: Dict[str, Any]) -> str:
        psutil = _psutil()
        procs = [
            p for p in psutil.process_iter(["pid", "name", "memory_info"])
            if p.info.get("memory_info")
        ]
        top = sorted(procs, key=lambda p: p.info["memory_info"].rss, reverse=True)[:5]
        rows = [
            f"  {p.info['name'][:30]} (PID {p.info['pid']}): "
            f"{p.info['memory_info'].rss / 1024 ** 2:.0f} MB"
            for p in top
        ]
        return "Top processes by memory:\n" + "\n".join(rows)

    def _get_process_details(self, p: Dict[str, Any]) -> str:
        psutil = _psutil()
        pid = int(p.get("pid", 0))
        try:
            proc = psutil.Process(pid)
        except psutil.NoSuchProcess:
            raise ValueError(f"No process with PID {pid}")
        with proc.oneshot():
            return (
                f"{proc.name()} (PID {pid}): "
                f"{proc.memory_info().rss / 1024 ** 2:.0f} MB, status {proc.status()}"
            )

    def _check_system_health(self, _p: Dict[str, Any]) -> str:
        psutil = _psutil()
        usage = psutil.disk_usage("/")
        memory = psutil.virtual_memory()
        return (
            f"Disk {usage.free / 1024 ** 3:.1f} GB free ({usage.percent}% used); "
            f"memory {memory.percent}% used; "
            f"{len(psutil.pids())} processes; "
            f"CPU {psutil.cpu_percent(interval=0.3)}%."
        )

    def _test_connectivity(self, _p: Dict[str, Any]) -> str:
        if self._has_connectivity():
            return f"Connectivity OK from {socket.gethostname()}."
        return "No outbound connectivity: test host unreachable."

    def _detect_background_apps(self, _p: Dict[str, Any]) -> str:
        psutil = _psutil()
        idle = [
            p.info["name"]
            for p in psutil.process_iter(["name", "cpu_percent"])
            if (p.info.get("cpu_percent") or 0) < 1
        ]
        return f"{len(idle)} processes currently using under 1% CPU."

    def _analyze_slow_performance(self, _p: Dict[str, Any]) -> str:
        psutil = _psutil()
        usage = psutil.disk_usage("/")
        memory = psutil.virtual_memory()
        causes = []
        if usage.percent > 90:
            causes.append(f"low disk space ({usage.free / 1024 ** 3:.1f} GB free)")
        if memory.percent > 85:
            causes.append(f"high memory pressure ({memory.percent}% used)")
        if psutil.cpu_percent(interval=0.3) > 80:
            causes.append("sustained high CPU")
        return "Likely causes: " + (", ".join(causes) if causes else "none detected")




class HybridDriver(ExecutionDriver):
    """Real diagnostics, simulated changes.

    Routes each action by what it does:

    * **read-only** -> :class:`PosixDriver`, reporting the real machine
    * **anything that changes state** -> :class:`SimulatedDriver`

    This is the useful configuration for developing and demonstrating on a
    Mac. Diagnostics show true numbers, so the evidence in a demo is real,
    while nothing on the developer's own machine is modified.

    ``capture_state`` deliberately answers from the simulated system. Pre-action
    checks for a state-changing action must be consistent with the world that
    action will actually change; mixing a real reading into a simulated
    remediation would make preconditions and postconditions disagree.
    """

    name = "hybrid"

    def __init__(self, simulated=None, real=None) -> None:
        from .simulated import SimulatedDriver

        self.simulated = simulated or SimulatedDriver()
        self.real = real or PosixDriver()

    @property
    def system(self):
        """The simulated machine, for scenario setup and fault injection."""
        return self.simulated.system

    def inject_fault(self, action_id: str, reason: str = "injected for evaluation") -> None:
        self.simulated.inject_fault(action_id, reason)

    def clear_faults(self) -> None:
        self.simulated.clear_faults()

    def _is_real(self, action_id: str) -> bool:
        from app.services.verification import CONTRACTS

        contract = CONTRACTS.get(action_id)
        return bool(contract and contract.read_only and self.real.supports(action_id))

    def is_available(self) -> bool:
        return True

    def supports(self, action_id: str) -> bool:
        return self._is_real(action_id) or self.simulated.supports(action_id)

    def capture_state(self, scope: str) -> Dict[str, Any]:
        return self.simulated.capture_state(scope)

    def execute(
        self,
        action_id: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        if self._is_real(action_id):
            logger.info("[HYBRID] %s -> real host", action_id)
            return self.real.execute(action_id, parameters)
        logger.info("[HYBRID] %s -> simulated", action_id)
        return self.simulated.execute(action_id, parameters)
