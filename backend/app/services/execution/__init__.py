"""Execution drivers for remediation actions.

Which driver runs is configuration, not code. ``EXECUTION_DRIVER`` in ``.env``
selects one:

* ``simulated`` - a controllable model of a machine
* ``hybrid`` - real read-only diagnostics, simulated changes (best off Windows)
* ``posix`` - real read-only diagnostics only, macOS and Linux
* ``powershell`` - real execution on Windows
* ``auto`` - powershell where available, otherwise simulated

Everything above this package works against :class:`ExecutionDriver` and cannot
tell which is in use, so risk assessment, approval routing and verification
behave identically in a demo and in production.
"""
from __future__ import annotations

import logging
import platform
from typing import Optional

from .base import ExecutionDriver, ExecutionError, ExecutionResult
from .posix import HybridDriver, PosixDriver
from .simulated import SimulatedDriver, SimulatedProcess, SimulatedSystem

logger = logging.getLogger(__name__)

__all__ = [
    "ExecutionDriver",
    "ExecutionError",
    "ExecutionResult",
    "SimulatedDriver",
    "SimulatedSystem",
    "SimulatedProcess",
    "PosixDriver",
    "HybridDriver",
    "get_driver",
    "reset_driver",
]

_driver: Optional[ExecutionDriver] = None


def _build(name: str) -> ExecutionDriver:
    name = (name or "auto").strip().lower()

    if name == "simulated":
        return SimulatedDriver()

    if name == "posix":
        return PosixDriver()

    if name == "hybrid":
        return HybridDriver()

    if name in ("powershell", "auto"):
        if platform.system() != "Windows":
            if name == "powershell":
                logger.warning(
                    "EXECUTION_DRIVER=powershell but host is %s; falling back to the "
                    "simulated driver so remediation remains testable.",
                    platform.system(),
                )
            return SimulatedDriver()
        from .powershell import PowerShellDriver

        return PowerShellDriver()

    raise ExecutionError(
        f"Unknown execution driver {name!r}. "
        "Use 'simulated', 'hybrid', 'posix', 'powershell' or 'auto'."
    )


def get_driver(name: Optional[str] = None) -> ExecutionDriver:
    """Return the process-wide execution driver, building it on first use."""
    global _driver
    if name is not None:
        return _build(name)
    if _driver is None:
        try:
            from app.config import get_settings

            configured = getattr(get_settings(), "execution_driver", "auto")
        except Exception:  # configuration is optional for unit tests
            configured = "auto"
        _driver = _build(configured)
        logger.info("Execution driver: %s", _driver.name)
    return _driver


def reset_driver() -> None:
    """Drop the cached driver. Used by tests and after a config change."""
    global _driver
    _driver = None
