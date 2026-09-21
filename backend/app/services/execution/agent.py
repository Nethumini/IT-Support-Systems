"""Execution driver that runs actions on an enrolled device.

Every other driver runs the action on the machine hosting the backend. This one
hands it to an agent on the machine that actually has the problem, waits for the
answer, and returns it in the same shape. The orchestrator above cannot tell the
difference, so risk scoring, approval, pre-checks, post-checks, rollback and
audit are identical whether an action runs locally or on a user's laptop. That
interchangeability is the point of the driver boundary, and this driver is the
test of it.

Two properties are worth stating because they are easy to get wrong:

**A timeout is a failure, not a success.** If the device does not answer, the
action may or may not have run. The driver refuses rather than guessing, which
sends the remediation down the recover-or-escalate path. Reporting an unknown
outcome as done would be exactly the failure mode the research exists to
prevent.

**The job carries an action id.** The agent resolves it against its own copy of
the catalogue. Nothing here can send a command string to a remote machine.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from app.models.device import DeviceDB
from app.models.device_job import (
    DeviceJobDB,
    JobKind,
    JobStatus,
    deadline,
    new_job_id,
)

from .base import ExecutionDriver, ExecutionError, ExecutionResult

logger = logging.getLogger(__name__)

#: How long to wait for an agent to finish a job before giving up.
DEFAULT_TIMEOUT_SECONDS = 60

#: How often to look for the answer. Short enough to feel immediate, long enough
#: not to spin the database for a minute.
POLL_INTERVAL_SECONDS = 0.5


@dataclass
class _JobOutcome:
    """What came back, as plain values.

    The ORM row cannot be read once its session closes, and the session must
    close between polls to see another connection's commits - so the poll loop
    copies out what it needs rather than handing back a live row.
    """

    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    job_id: str = ""

    @property
    def payload(self) -> Dict[str, Any]:
        return self.result if isinstance(self.result, dict) else {}


class AgentDriver(ExecutionDriver):
    """Runs catalogue actions on one enrolled device, through its agent."""

    name = "agent"

    def __init__(
        self,
        device_id: str,
        session_factory: Optional[Callable[[], Any]] = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        poll_interval: float = POLL_INTERVAL_SECONDS,
    ) -> None:
        self.device_id = device_id
        self.timeout_seconds = timeout_seconds
        self.poll_interval = poll_interval
        self._actions: Optional[Dict[str, Any]] = None

        if session_factory is None:
            from app.core.database import SessionLocal

            session_factory = SessionLocal
        self._session_factory = session_factory

    # --- catalogue -----------------------------------------------------------

    def _catalogue(self) -> Dict[str, Any]:
        """The same action catalogue every other driver validates against.

        Loaded lazily and cached: it pulls in the wider agent stack, which the
        simulated path has no need of.
        """
        if self._actions is None:
            from app.services.agents.action_executor_agent import ActionExecutorAgent

            self._actions = ActionExecutorAgent().actions
        return self._actions

    def supports(self, action_id: str) -> bool:
        return action_id in self._catalogue()

    def is_available(self) -> bool:
        """Whether this device is enrolled and still permitted to run work."""
        session = self._session_factory()
        try:
            device = (
                session.query(DeviceDB)
                .filter(DeviceDB.device_id == self.device_id)
                .first()
            )
            return device is not None and bool(device.is_active)
        finally:
            session.close()

    # --- the queue -----------------------------------------------------------

    def _queue(
        self,
        kind: JobKind,
        action_id: Optional[str] = None,
        scope: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Put one job on this device's queue and return its id."""
        if not self.is_available():
            raise ExecutionError(
                f"Device {self.device_id} is not enrolled or has been revoked."
            )

        session = self._session_factory()
        try:
            job = DeviceJobDB(
                job_id=new_job_id(),
                device_id=self.device_id,
                kind=kind.value,
                action_id=action_id,
                scope=scope,
                parameters=parameters or {},
                status=JobStatus.QUEUED.value,
                expires_at=deadline(self.timeout_seconds),
            )
            session.add(job)
            session.commit()
            return job.job_id
        finally:
            session.close()

    def _await_result(self, job_id: str) -> _JobOutcome:
        """Block until the agent answers, or the deadline passes.

        Each poll uses a fresh session: the agent commits its result from a
        different connection, and a long-lived session would keep serving the
        snapshot it read first.
        """
        started = time.monotonic()

        while True:
            session = self._session_factory()
            try:
                job = (
                    session.query(DeviceJobDB)
                    .filter(DeviceJobDB.job_id == job_id)
                    .first()
                )
                if job is None:
                    raise ExecutionError(f"Job {job_id} disappeared before it completed.")

                if job.is_finished:
                    return _JobOutcome(job.status, job.result, job.error, job.job_id)

                if time.monotonic() - started >= self.timeout_seconds:
                    job.mark_expired()
                    session.commit()
                    logger.warning(
                        "Device %s did not answer job %s within %ss",
                        self.device_id, job_id, self.timeout_seconds,
                    )
                    return _JobOutcome(JobStatus.EXPIRED.value, None, job.error, job_id)
            finally:
                session.close()

            time.sleep(self.poll_interval)

    # --- the driver interface ------------------------------------------------

    def capture_state(self, scope: str) -> Dict[str, Any]:
        """Read observable state on the device.

        Returns ``{}`` rather than raising when the device cannot be reached. A
        missing snapshot weakens verification, which the post-check reports
        honestly as inconclusive; raising here would instead abort a remediation
        that may still be safe to assess.
        """
        try:
            job = self._await_result(self._queue(JobKind.CAPTURE_STATE, scope=scope))
        except ExecutionError as exc:
            logger.warning("State capture on %s failed: %s", self.device_id, exc)
            return {}

        if job.status != JobStatus.DONE.value:
            logger.warning(
                "State capture %s on %s ended %s: %s",
                job.job_id, self.device_id, job.status, job.error,
            )
            return {}

        state = job.result or {}
        return state if isinstance(state, dict) else {}

    def execute(
        self,
        action_id: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        """Run one registered action on the device and report what happened."""
        if not self.supports(action_id):
            raise ExecutionError(
                f"Action '{action_id}' is not in the catalogue, so it cannot be sent "
                f"to a device."
            )

        started = time.monotonic()
        job = self._await_result(
            self._queue(JobKind.EXECUTE, action_id=action_id, parameters=parameters)
        )
        elapsed_ms = int((time.monotonic() - started) * 1000)

        if job.status == JobStatus.EXPIRED.value:
            # Deliberately an error, not a failed result: we do not know whether
            # the action ran, and a result would claim we do.
            raise ExecutionError(
                f"Device {self.device_id} did not respond within "
                f"{self.timeout_seconds}s. The outcome is unknown."
            )

        payload = job.payload

        if job.status == JobStatus.FAILED.value and not payload:
            return ExecutionResult(
                action_id=action_id,
                success=False,
                driver=self.name,
                error=job.error or "The agent reported a failure.",
                duration_ms=elapsed_ms,
                parameters=dict(parameters or {}),
            )

        return ExecutionResult(
            action_id=action_id,
            success=bool(payload.get("success")),
            driver=self.name,
            output=payload.get("output", "") or "",
            error=payload.get("error") or job.error,
            # The agent times its own work; fall back to the round trip.
            duration_ms=int(payload.get("duration_ms") or elapsed_ms),
            parameters=dict(parameters or {}),
            state_before=dict(payload.get("state_before") or {}),
            state_after=dict(payload.get("state_after") or {}),
        )
