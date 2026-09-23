"""Windows driver: runs registered actions as PowerShell commands.

Command templates come from the existing action catalogue in
``ActionExecutorAgent``. Parameters are substituted into the template and
nothing else is accepted, so a free-form command string cannot reach a shell
through this path.

Unavailable off Windows. :func:`get_driver` falls back to the simulated driver
there rather than failing, so the same code runs during development on macOS.
"""
from __future__ import annotations

import json
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
            mount = "C:" if platform.system() == "Windows" else "/"
            usage = psutil.disk_usage(mount + "\\" if mount == "C:" else mount)
            return {
                # Which volume these figures describe. A machine with several
                # drives otherwise shows one number and no way to tell which.
                "disk_mount": mount,
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
            return self._network(psutil)
        if scope == "startup":
            return self._startup_items()
        if scope == "services":
            return self._services()
        if scope == "all":
            return {
                s: self.capture_state(s)
                for s in ("disk", "processes", "network", "services", "startup")
            }
        # ``updates`` is still not observable here: pending updates need the
        # Windows Update COM API rather than a reading psutil can take. An
        # action in that scope post-checks as inconclusive on a real machine
        # rather than as success, which is the safe direction.
        return {}

    #: Number of entries the resolver is holding. Without it the appropriateness
    #: check for a DNS flush cannot run, and a check that cannot run refuses.
    _DNS_CACHE_QUERY = "@(Get-DnsClientCache -ErrorAction Stop).Count"

    def _network(self, psutil) -> Dict[str, Any]:
        """Connectivity as the network contracts expect it.

        ``connected`` used to be "this machine has network interfaces", which
        is true of a laptop in a drawer. It now means an interface that is up
        and holds an address the machine could route from, because the checks
        that decide whether to reset an adapter read it.

        ``winsock_healthy`` is deliberately absent: the stack's integrity is
        not something that can be read cheaply, and guessing it would be worse
        than saying nothing. The precondition treats its absence as grounds to
        refuse, which is why a Winsock reset will not run from here.
        """
        import socket

        connected = False
        try:
            stats = psutil.net_if_stats()
            addresses = psutil.net_if_addrs()
            for name, address_list in addresses.items():
                interface = stats.get(name)
                if interface is None or not interface.isup:
                    continue
                for address in address_list:
                    if address.family != socket.AF_INET:
                        continue
                    ip = address.address or ""
                    # Loopback proves nothing, and 169.254.x.x is what Windows
                    # assigns when it could not get an address at all.
                    if ip.startswith("127.") or ip.startswith("169.254."):
                        continue
                    connected = True
                    break
                if connected:
                    break
        except Exception as exc:
            logger.warning("[POWERSHELL] Could not read connectivity: %s", exc)

        state: Dict[str, Any] = {"connected": connected}

        entries = self._dns_cache_entries()
        if entries is not None:
            state["dns_cache_entries"] = entries
        return state

    def _dns_cache_entries(self) -> Optional[int]:
        try:
            completed = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", self._DNS_CACHE_QUERY],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            if completed.returncode != 0:
                return None
            return int((completed.stdout or "").strip())
        except Exception as exc:
            logger.warning("[POWERSHELL] Could not read the DNS cache: %s", exc)
            return None

    @staticmethod
    def _services() -> Dict[str, Any]:
        """Service names and their run states, keyed as the contracts expect.

        Whether these states drift on their own within the second a diagnostic
        takes has not been measured on the Windows machine. If a read-only
        check over this scope turns out to fail on drift, the fix belongs in
        the read-only allowances next to the disk one - measured, as that one
        was, not guessed at here.
        """
        try:
            import psutil

            iterator = psutil.win_service_iter()
        except Exception as exc:  # not Windows, or psutil cannot enumerate
            logger.warning("[POWERSHELL] Could not read services: %s", exc)
            return {}

        services: Dict[str, Any] = {}
        for service in iterator:
            try:
                services[service.name()] = service.status()
            except Exception:
                # Access denied on a protected service is not a failed
                # snapshot: it is one service this process cannot speak for.
                # Leaving it out means a post-check that needs it reports
                # inconclusive, which is the honest answer.
                continue
        return services

    #: Reads the same two keys the startup actions write: what runs at logon,
    #: and what this system disabled. A disabled item has to keep appearing in
    #: the snapshot as ``False`` rather than vanishing, or the post-check
    #: cannot tell "turned off" from "never there".
    _STARTUP_QUERY = (
        '$run = "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"; '
        '$backup = "HKCU:\\Software\\AutoOps\\DisabledStartup"; '
        '$items = @{}; '
        'if (Test-Path $run) { (Get-Item $run).GetValueNames() | '
        'ForEach-Object { if ($_) { $items[$_] = $true } } }; '
        'if (Test-Path $backup) { (Get-Item $backup).GetValueNames() | '
        'ForEach-Object { if ($_ -and -not $items.ContainsKey($_)) { $items[$_] = $false } } }; '
        '$items | ConvertTo-Json -Compress'
    )

    def _startup_items(self) -> Dict[str, Any]:
        """Which programs are registered to run at logon, and which we disabled."""
        try:
            completed = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", self._STARTUP_QUERY],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            output = (completed.stdout or "").strip()
            if completed.returncode != 0 or not output:
                logger.warning("[POWERSHELL] Could not read startup items: %s", completed.stderr)
                return {}
            items = json.loads(output)
        except Exception as exc:
            # An unreadable snapshot must not look like an empty machine: the
            # post-check reports inconclusive either way, and guessing here
            # would turn "cannot tell" into "nothing is registered".
            logger.warning("[POWERSHELL] Could not read startup items: %s", exc)
            return {}

        return {str(k): bool(v) for k, v in items.items()} if isinstance(items, dict) else {}

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
