"""A simulated machine, for development off Windows and for evaluation.

Actions here change a small model of a computer: disk space, running processes,
services, network state and startup items. Post-action verification then reads
that model back, exactly as it would read a real machine.

This is not a stub that returns ``success: True``. If it were, it would defeat
the point of the research: the claim under test is that a command completing is
not the same as a problem being solved. So the model must be able to complete a
command and leave the problem in place - which is what :meth:`inject_fault`
arranges.

Being able to reproduce a failure on demand is why this driver is preferable to
real hardware for evaluation, not merely a substitute for it.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .base import ExecutionDriver, ExecutionError, ExecutionResult, scope_for

logger = logging.getLogger(__name__)


@dataclass
class SimulatedProcess:
    pid: int
    name: str
    memory_mb: int
    cpu_percent: float


@dataclass
class SimulatedSystem:
    """The observable state of one simulated machine.

    Default values describe a machine with a realistic problem present: a
    nearly-full disk, a memory-hungry browser and a stopped print spooler. That
    way a scenario can start from "broken" without having to set it up.
    """

    disk_total_gb: float = 256.0
    disk_free_gb: float = 4.2
    temp_files_mb: float = 8600.0
    recycle_bin_mb: float = 2400.0

    processes: List[SimulatedProcess] = field(
        default_factory=lambda: [
            SimulatedProcess(4812, "chrome.exe", 4820, 34.5),
            SimulatedProcess(2210, "Code.exe", 1860, 12.1),
            SimulatedProcess(6604, "Docker Desktop.exe", 3200, 22.7),
            SimulatedProcess(1180, "Teams.exe", 940, 4.2),
            SimulatedProcess(980, "explorer.exe", 210, 1.1),
        ]
    )

    services: Dict[str, str] = field(
        default_factory=lambda: {
            "Spooler": "stopped",
            "Dnscache": "running",
            "WSearch": "running",
            "wuauserv": "running",
        }
    )

    dns_cache_entries: int = 412
    network_connected: bool = True
    winsock_healthy: bool = False
    ip_address: str = "10.14.7.88"

    startup_items: Dict[str, bool] = field(
        default_factory=lambda: {
            "Teams": True,
            "Spotify": True,
            "OneDrive": True,
            "Docker Desktop": True,
            "ScreenRecorder": True,
        }
    )

    #: What each disabled item was set to before this system disabled it. The
    #: real action writes the same record to a registry key of its own; without
    #: it ``enable_startup_item`` would have nothing to restore and the
    #: registered rollback would be a promise the machine cannot keep.
    startup_backup: Dict[str, bool] = field(default_factory=dict)

    #: Items whose own launcher re-registers them, so removing the startup
    #: entry does not stop them starting. Teams, OneDrive and Spotify all do
    #: this in reality. It is the reason a disable can complete successfully
    #: and still leave the problem in place, which is precisely the case
    #: post-action verification exists to catch.
    self_restoring_startup_items: frozenset[str] = frozenset({"Teams"})

    pending_updates: int = 3
    reboot_required: bool = False

    @property
    def disk_used_percent(self) -> float:
        return round((self.disk_total_gb - self.disk_free_gb) / self.disk_total_gb * 100, 1)

    def find_process(self, pid: int) -> Optional[SimulatedProcess]:
        return next((p for p in self.processes if p.pid == pid), None)

    def find_processes_by_name(self, name: str) -> List[SimulatedProcess]:
        needle = name.lower().replace(".exe", "")
        return [p for p in self.processes if needle in p.name.lower()]

    def total_memory_mb(self) -> int:
        return sum(p.memory_mb for p in self.processes)


class SimulatedDriver(ExecutionDriver):
    """Executes registered actions against a :class:`SimulatedSystem`."""

    name = "simulated"

    def __init__(self, system: Optional[SimulatedSystem] = None) -> None:
        self.system = system or SimulatedSystem()
        #: action_id -> reason. A faulted action reports success but changes
        #: nothing, which is what post-action verification must catch.
        self._faults: Dict[str, str] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], str]] = self._build_handlers()

    # -- fault injection -----------------------------------------------------

    def inject_fault(self, action_id: str, reason: str = "injected for evaluation") -> None:
        """Make an action report success while changing nothing.

        This is the verification-failure scenario: the command "worked", the
        problem remains, and the system must not report the ticket as resolved.
        """
        self._faults[action_id] = reason

    def clear_faults(self) -> None:
        self._faults.clear()

    # -- driver interface ----------------------------------------------------

    def supports(self, action_id: str) -> bool:
        return action_id in self._handlers

    def capture_state(self, scope: str) -> Dict[str, Any]:
        s = self.system
        if scope == "disk":
            return {
                "disk_free_gb": round(s.disk_free_gb, 2),
                "disk_used_percent": s.disk_used_percent,
                "temp_files_mb": round(s.temp_files_mb, 1),
                "recycle_bin_mb": round(s.recycle_bin_mb, 1),
            }
        if scope == "processes":
            return {
                "process_count": len(s.processes),
                "total_memory_mb": s.total_memory_mb(),
                "top_process": max(s.processes, key=lambda p: p.memory_mb).name if s.processes else None,
                "pids": sorted(p.pid for p in s.processes),
            }
        if scope == "network":
            return {
                "connected": s.network_connected,
                "dns_cache_entries": s.dns_cache_entries,
                "winsock_healthy": s.winsock_healthy,
                "ip_address": s.ip_address,
            }
        if scope == "services":
            return dict(s.services)
        if scope == "startup":
            return dict(s.startup_items)
        if scope == "updates":
            return {"pending_updates": s.pending_updates, "reboot_required": s.reboot_required}
        if scope == "all":
            return {
                scope_name: self.capture_state(scope_name)
                for scope_name in ("disk", "processes", "network", "services", "startup", "updates")
            }
        raise ExecutionError(f"Unknown state scope: {scope!r}")

    def execute(
        self,
        action_id: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        parameters = parameters or {}
        handler = self._handlers.get(action_id)
        if handler is None:
            raise ExecutionError(
                f"Action {action_id!r} is not registered with the simulated driver"
            )

        scope = scope_for(action_id)
        before = self.capture_state(scope)
        started = time.perf_counter()

        fault = self._faults.get(action_id)
        if fault is not None:
            # Report success, change nothing. The command "worked".
            logger.info("[SIMULATED] Fault injected for %s: %s", action_id, fault)
            after = self.capture_state(scope)
            return ExecutionResult(
                action_id=action_id,
                success=True,
                driver=self.name,
                output=f"{action_id} completed successfully.",
                duration_ms=int((time.perf_counter() - started) * 1000),
                parameters=dict(parameters),
                state_before=before,
                state_after=after,
                fault_injected=True,
            )

        try:
            output = handler(parameters)
            success = True
            error = None
        except ExecutionError:
            raise
        except Exception as exc:  # a simulated action failing is a real outcome
            logger.info("[SIMULATED] %s failed: %s", action_id, exc)
            output = ""
            success = False
            error = str(exc)

        after = self.capture_state(scope)
        return ExecutionResult(
            action_id=action_id,
            success=success,
            driver=self.name,
            output=output,
            error=error,
            duration_ms=int((time.perf_counter() - started) * 1000),
            parameters=dict(parameters),
            state_before=before,
            state_after=after,
        )

    # -- action handlers -----------------------------------------------------

    def _build_handlers(self) -> Dict[str, Callable[[Dict[str, Any]], str]]:
        return {
            # read-only
            "check_disk_space": self._check_disk_space,
            "list_top_processes": self._list_top_processes,
            "get_process_details": self._get_process_details,
            "list_services": self._list_services,
            "test_connectivity": self._test_connectivity,
            "check_system_health": self._check_system_health,
            "get_startup_programs": self._get_startup_programs,
            "detect_background_apps": self._detect_background_apps,
            "check_windows_updates": self._check_windows_updates,
            "analyze_slow_performance": self._analyze_slow_performance,
            # state-changing
            "clear_temp_files": self._clear_temp_files,
            "clear_windows_temp": self._clear_temp_files,
            "windows_disk_cleanup": self._disk_cleanup,
            "empty_recycle_bin": self._empty_recycle_bin,
            "kill_process_by_id": self._kill_process,
            "close_browser_tabs": self._close_browser_tabs,
            "clear_browser_cache": self._clear_browser_cache,
            "optimize_memory": self._optimize_memory,
            "restart_explorer": self._restart_explorer,
            "flush_dns": self._flush_dns,
            "release_renew_ip": self._release_renew_ip,
            "reset_winsock": self._reset_winsock,
            "reset_network_adapter": self._reset_network_adapter,
            "restart_service": self._restart_service,
            "disable_startup_item": self._disable_startup_item,
            "enable_startup_item": self._enable_startup_item,
        }

    # read-only handlers

    def _check_disk_space(self, _p: Dict[str, Any]) -> str:
        s = self.system
        return (
            f"Drive C: {s.disk_free_gb:.1f} GB free of {s.disk_total_gb:.0f} GB "
            f"({s.disk_used_percent}% used)."
        )

    def _list_top_processes(self, _p: Dict[str, Any]) -> str:
        top = sorted(self.system.processes, key=lambda p: p.memory_mb, reverse=True)[:5]
        rows = [f"  {p.name} (PID {p.pid}): {p.memory_mb} MB, {p.cpu_percent}% CPU" for p in top]
        return "Top processes by memory:\n" + "\n".join(rows)

    def _get_process_details(self, p: Dict[str, Any]) -> str:
        pid = int(p.get("pid", 0))
        proc = self.system.find_process(pid)
        if proc is None:
            raise ValueError(f"No process with PID {pid}")
        return f"{proc.name} (PID {proc.pid}): {proc.memory_mb} MB, {proc.cpu_percent}% CPU"

    def _list_services(self, _p: Dict[str, Any]) -> str:
        rows = [f"  {name}: {state}" for name, state in sorted(self.system.services.items())]
        return "Services:\n" + "\n".join(rows)

    def _test_connectivity(self, _p: Dict[str, Any]) -> str:
        s = self.system
        if not s.network_connected:
            return "No network connectivity: all test hosts unreachable."
        health = "healthy" if s.winsock_healthy else "degraded (intermittent loss)"
        return f"Connectivity OK from {s.ip_address}. Network stack {health}."

    def _check_system_health(self, _p: Dict[str, Any]) -> str:
        s = self.system
        return (
            f"Disk free {s.disk_free_gb:.1f} GB; {len(s.processes)} processes using "
            f"{s.total_memory_mb()} MB; {s.pending_updates} updates pending."
        )

    def _get_startup_programs(self, _p: Dict[str, Any]) -> str:
        enabled = [n for n, on in self.system.startup_items.items() if on]
        return f"{len(enabled)} startup items enabled: " + ", ".join(sorted(enabled))

    def _detect_background_apps(self, _p: Dict[str, Any]) -> str:
        idle = [p.name for p in self.system.processes if p.cpu_percent < 5]
        return f"{len(idle)} background apps with low CPU: " + ", ".join(idle)

    def _check_windows_updates(self, _p: Dict[str, Any]) -> str:
        s = self.system
        return f"{s.pending_updates} updates pending. Reboot required: {s.reboot_required}."

    def _analyze_slow_performance(self, _p: Dict[str, Any]) -> str:
        s = self.system
        causes = []
        if s.disk_free_gb < 10:
            causes.append("low disk space")
        if s.total_memory_mb() > 8000:
            causes.append("high memory usage")
        if sum(1 for on in s.startup_items.values() if on) > 3:
            causes.append("many startup items")
        return "Likely causes: " + (", ".join(causes) if causes else "none detected")

    # state-changing handlers

    def _clear_temp_files(self, _p: Dict[str, Any]) -> str:
        s = self.system
        freed_mb = s.temp_files_mb
        s.temp_files_mb = 0.0
        s.disk_free_gb += freed_mb / 1024
        return f"Removed {freed_mb:.0f} MB of temporary files. Free space now {s.disk_free_gb:.1f} GB."

    def _disk_cleanup(self, _p: Dict[str, Any]) -> str:
        s = self.system
        freed_gb = 1.8
        s.disk_free_gb += freed_gb
        return f"Disk Cleanup removed {freed_gb} GB. Free space now {s.disk_free_gb:.1f} GB."

    def _empty_recycle_bin(self, _p: Dict[str, Any]) -> str:
        s = self.system
        freed_mb = s.recycle_bin_mb
        s.recycle_bin_mb = 0.0
        s.disk_free_gb += freed_mb / 1024
        return f"Recycle Bin emptied, {freed_mb:.0f} MB recovered."

    def _kill_process(self, p: Dict[str, Any]) -> str:
        pid = int(p.get("pid", 0))
        proc = self.system.find_process(pid)
        if proc is None:
            raise ValueError(f"No process with PID {pid}")
        self.system.processes.remove(proc)
        return f"Ended {proc.name} (PID {pid}), releasing {proc.memory_mb} MB."

    def _close_browser_tabs(self, _p: Dict[str, Any]) -> str:
        freed = 0
        for proc in self.system.find_processes_by_name("chrome"):
            released = int(proc.memory_mb * 0.6)
            proc.memory_mb -= released
            freed += released
        if freed == 0:
            raise ValueError("No browser processes found")
        return f"Closed inactive tabs, releasing {freed} MB."

    def _clear_browser_cache(self, _p: Dict[str, Any]) -> str:
        s = self.system
        s.disk_free_gb += 0.6
        return f"Browser cache cleared, 600 MB recovered. Free space now {s.disk_free_gb:.1f} GB."

    def _optimize_memory(self, _p: Dict[str, Any]) -> str:
        for proc in self.system.processes:
            proc.memory_mb = int(proc.memory_mb * 0.9)
        return f"Working sets trimmed. Total now {self.system.total_memory_mb()} MB."

    def _restart_explorer(self, _p: Dict[str, Any]) -> str:
        proc = next((p for p in self.system.processes if p.name == "explorer.exe"), None)
        if proc is not None:
            proc.memory_mb = 180
            proc.cpu_percent = 0.8
        return "Windows Explorer restarted. Desktop and taskbar reloaded."

    def _flush_dns(self, _p: Dict[str, Any]) -> str:
        cleared = self.system.dns_cache_entries
        self.system.dns_cache_entries = 0
        return f"DNS resolver cache flushed, {cleared} entries removed."

    def _release_renew_ip(self, _p: Dict[str, Any]) -> str:
        s = self.system
        s.ip_address = "10.14.7.132"
        s.network_connected = True
        return f"IP address released and renewed. New address {s.ip_address}."

    def _reset_winsock(self, _p: Dict[str, Any]) -> str:
        s = self.system
        s.winsock_healthy = True
        s.reboot_required = True
        return "Winsock catalogue reset. A restart is required to complete."

    def _reset_network_adapter(self, _p: Dict[str, Any]) -> str:
        s = self.system
        s.network_connected = True
        s.dns_cache_entries = 0
        s.reboot_required = True
        return "Network adapter reset. A restart is required to complete."

    def _restart_service(self, p: Dict[str, Any]) -> str:
        name = str(p.get("service_name") or p.get("name") or "").strip()
        if not name:
            raise ValueError("service_name parameter is required")
        if name not in self.system.services:
            raise ValueError(f"Unknown service: {name}")
        self.system.services[name] = "running"
        return f"Service {name} restarted and is now running."

    def _disable_startup_item(self, p: Dict[str, Any]) -> str:
        name = str(p.get("item_name") or p.get("name") or "").strip()
        if not name:
            raise ValueError("item_name parameter is required")
        if name not in self.system.startup_items:
            raise ValueError(f"Unknown startup item: {name}")
        self.system.startup_backup[name] = self.system.startup_items[name]
        self.system.startup_items[name] = False
        if name in self.system.self_restoring_startup_items:
            # The entry was removed and the program's own launcher put it
            # straight back. The command did exactly what it was asked to do,
            # so nothing before the post-check can tell that it achieved
            # nothing.
            self.system.startup_items[name] = True
        return f"Startup item {name} disabled."

    def _enable_startup_item(self, p: Dict[str, Any]) -> str:
        name = str(p.get("item_name") or p.get("name") or "").strip()
        if not name:
            raise ValueError("item_name parameter is required")
        if name not in self.system.startup_backup:
            # Mirrors the real action, which restores a saved command line and
            # cannot invent one. An item this system never disabled fails
            # loudly instead of being guessed back into existence - and a
            # failed rollback must escalate, not be reported as recovery.
            raise ValueError(f"No saved startup command for {name}; cannot re-enable")
        self.system.startup_items[name] = self.system.startup_backup.pop(name)
        return f"Startup item {name} re-enabled."


#: Which state scope matters for each action's before/after snapshot.
