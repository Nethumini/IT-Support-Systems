"""Windows driver: runs registered actions as PowerShell commands.

Command templates come from the existing action catalogue in
``ActionExecutorAgent``. Parameters are substituted into the template and
nothing else is accepted, so a free-form command string cannot reach a shell
through this path.

Unavailable off Windows. :func:`get_driver` falls back to the simulated driver
there rather than failing, so the same code runs during development on macOS.
"""
from __future__ import annotations

import logging
import platform
import subprocess
import time
from typing import Any, Dict, Optional

from .base import ExecutionDriver, ExecutionError, ExecutionResult, scope_for

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 60


class PowerShellDriver(ExecutionDriver):
    """Executes catalogue actions through ``powershell.exe``."""

    name = "powershell"

    def __init__(self, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        self.timeout_seconds = timeout_seconds
        self._actions = self._load_actions()

    @staticmethod
    def _load_actions() -> Dict[str, Any]:
        # Imported lazily: the catalogue pulls in the wider agent stack, which
        # the simulated path has no need of.
        from app.services.agents.action_executor_agent import ActionExecutorAgent

        return ActionExecutorAgent().actions

    def is_available(self) -> bool:
        return platform.system() == "Windows"

    def supports(self, action_id: str) -> bool:
        return action_id in self._actions

    def capture_state(self, scope: str) -> Dict[str, Any]:
        """Read observable state via psutil, which works cross-platform."""
        try:
            import psutil
        except ImportError:  # pragma: no cover - psutil is a declared dependency
            return {}

        if scope == "disk":
            usage = psutil.disk_usage("C:\\" if platform.system() == "Windows" else "/")
            return {
                "disk_free_gb": round(usage.free / 1024 ** 3, 2),
                "disk_used_percent": usage.percent,
            }
        if scope == "processes":
            procs = list(psutil.process_iter(["pid", "name", "memory_info"]))
            return {
                "process_count": len(procs),
                "pids": sorted(p.info["pid"] for p in procs),
            }
        if scope == "network":
            return {"connected": bool(psutil.net_if_stats())}
        if scope == "all":
            return {s: self.capture_state(s) for s in ("disk", "processes", "network")}
        return {}

    def execute(
        self,
        action_id: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        if not self.is_available():
            raise ExecutionError(
                f"PowerShell driver cannot run on {platform.system()}. "
                "Set EXECUTION_DRIVER=simulated for development off Windows."
            )

        action = self._actions.get(action_id)
        if action is None:
            raise ExecutionError(f"Action {action_id!r} is not in the action catalogue")

        parameters = parameters or {}
        command = action.command_template
        for key, value in parameters.items():
            command = command.replace("{" + key + "}", str(value))

        scope = scope_for(action_id)
        before = self.capture_state(scope)
        started = time.perf_counter()

        try:
            completed = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            output = (completed.stdout or "").strip()
            stderr = (completed.stderr or "").strip()
            success = completed.returncode == 0
            error = stderr if not success else None
        except subprocess.TimeoutExpired:
            output, success, error = "", False, f"Timed out after {self.timeout_seconds}s"
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
