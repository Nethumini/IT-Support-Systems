"""AutoOps endpoint agent.

Runs on a user's machine. Asks the backend whether there is any work for this
device, runs it locally, and reports what happened. Nothing else.

Why the agent asks rather than being told: a laptop sits behind a router with no
open port, so an inbound connection is not generally possible. It also means
nothing arriving on the network can start work - the agent only ever acts on a
job it went looking for.

**The agent never receives a command.** It receives a registered action id and
resolves it against its own copy of the catalogue, through the same
:class:`ExecutionDriver` the backend uses locally. An id it does not recognise is
refused and reported as a failure. This is the allow-list rule (thesis 5.3.4)
holding at the remote end: if the server could send text to run, a compromised
server would be remote code execution on every enrolled machine.

The driver is chosen by the machine, not by the server: PowerShell on Windows,
the read-only POSIX set on macOS and Linux. The same file therefore runs on the
Windows test machine and on a developer's Mac, which is how the work loop is
tested without Windows.

Usage::

    export AUTOOPS_BACKEND_URL=http://localhost:8000
    export AUTOOPS_DEVICE_ID=dev_xxxxxxxx
    export AUTOOPS_DEVICE_SECRET=yyyyyyyy
    python agent/autoops_agent.py

    python agent/autoops_agent.py --once      # take at most one job, then stop
"""
from __future__ import annotations

import argparse
import logging
import os
import platform
import socket
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# The agent shares the backend's driver and action catalogue rather than keeping
# a second copy, so the allow-list cannot drift between the two.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import httpx  # noqa: E402

from app.services.execution import get_driver  # noqa: E402
from app.services.execution.base import ExecutionError  # noqa: E402

logger = logging.getLogger("autoops.agent")

DEFAULT_BACKEND_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

#: Gap between polls when there is nothing to do. Short enough that a user does
#: not wait noticeably, long enough not to hammer the server all day.
IDLE_POLL_SECONDS = 2.0

#: Backoff when the backend is unreachable, so a restart storm is not created
#: by every agent retrying in lockstep.
ERROR_BACKOFF_SECONDS = 10.0

HTTP_TIMEOUT_SECONDS = 30.0


class AgentConfig:
    """Where to call, and who this machine claims to be."""

    def __init__(
        self,
        backend_url: str,
        device_id: str,
        device_secret: str,
        driver_name: Optional[str] = None,
    ) -> None:
        self.backend_url = backend_url.rstrip("/")
        self.device_id = device_id
        self.device_secret = device_secret
        self.driver_name = driver_name

    @classmethod
    def from_environment(cls, args: argparse.Namespace) -> "AgentConfig":
        device_id = args.device_id or os.getenv("AUTOOPS_DEVICE_ID", "")
        device_secret = args.device_secret or os.getenv("AUTOOPS_DEVICE_SECRET", "")

        missing = [
            name
            for name, value in (
                ("AUTOOPS_DEVICE_ID", device_id),
                ("AUTOOPS_DEVICE_SECRET", device_secret),
            )
            if not value
        ]
        if missing:
            raise SystemExit(
                "Missing device credentials: "
                + ", ".join(missing)
                + "\nRegister this machine first: an administrator calls "
                "POST /api/v1/devices and gives you the id and secret."
            )

        return cls(
            backend_url=args.backend_url
            or os.getenv("AUTOOPS_BACKEND_URL", DEFAULT_BACKEND_URL),
            device_id=device_id,
            device_secret=device_secret,
            driver_name=args.driver or os.getenv("AUTOOPS_AGENT_DRIVER") or None,
        )

    @property
    def headers(self) -> Dict[str, str]:
        # The secret is sent on every call and never logged.
        return {
            "X-Device-Id": self.device_id,
            "X-Device-Secret": self.device_secret,
        }


class Agent:
    """The poll-run-report loop."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.driver = get_driver(config.driver_name)
        self._client = httpx.Client(
            base_url=f"{config.backend_url}{API_PREFIX}",
            headers=config.headers,
            timeout=HTTP_TIMEOUT_SECONDS,
        )

    # --- talking to the backend ---------------------------------------------

    def take_job(self) -> Optional[Dict[str, Any]]:
        """Ask for work. ``None`` means there is nothing to do right now."""
        response = self._client.get("/devices/work")
        if response.status_code == 401:
            raise SystemExit(
                "The backend rejected this device's credentials. Check "
                "AUTOOPS_DEVICE_ID and AUTOOPS_DEVICE_SECRET, or ask an "
                "administrator whether this device has been revoked."
            )
        response.raise_for_status()
        return response.json().get("job")

    def report(self, job_id: str, payload: Dict[str, Any]) -> None:
        """Send back what happened.

        A rejected report is logged and dropped, never retried: the server
        refuses a second result for the same job precisely so a retry cannot
        overwrite an outcome it has already acted on.
        """
        response = self._client.post(f"/devices/work/{job_id}/result", json=payload)
        if response.status_code >= 400:
            logger.error(
                "Backend rejected the result for %s (%s): %s",
                job_id, response.status_code, response.text[:200],
            )
            return
        logger.info("Reported %s as %s", job_id, response.json().get("status"))

    # --- doing the work ------------------------------------------------------

    def run_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Carry out one job and build the result the backend expects."""
        kind = job.get("kind")

        if kind == "capture_state":
            scope = job.get("scope") or "all"
            logger.info("Reading %s state", scope)
            return {"success": True, "state": self.driver.capture_state(scope)}

        if kind != "execute":
            # An unknown kind is refused rather than guessed at.
            return {"success": False, "error": f"Unknown job kind {kind!r}."}

        action_id = job.get("action_id") or ""

        # The allow-list, enforced here as well as on the server. The agent is
        # the last line: it runs what it recognises and nothing else.
        if not self.driver.supports(action_id):
            logger.warning("Refusing unknown action %r", action_id)
            return {
                "success": False,
                "error": (
                    f"Action {action_id!r} is not in this machine's catalogue, "
                    f"so it was not run."
                ),
            }

        logger.info("Running %s", action_id)
        try:
            result = self.driver.execute(action_id, job.get("parameters") or {})
        except ExecutionError as exc:
            # The driver refused: the action never started.
            return {"success": False, "error": str(exc)}
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Action %s raised", action_id)
            return {"success": False, "error": f"The agent failed to run it: {exc}"}

        data = result.to_dict()
        return {
            "success": data.get("success", False),
            "output": str(data.get("output") or ""),
            "error": data.get("error"),
            "duration_ms": data.get("duration_ms"),
            "state_before": data.get("state_before") or {},
            "state_after": data.get("state_after") or {},
        }

    # --- the loop ------------------------------------------------------------

    def poll_once(self) -> bool:
        """Take at most one job. Returns whether there was one."""
        job = self.take_job()
        if not job:
            return False

        job_id = job.get("job_id")
        logger.info("Took job %s (%s)", job_id, job.get("kind"))
        self.report(job_id, self.run_job(job))
        return True

    def run_forever(self) -> None:
        logger.info(
            "Agent started on %s (%s) as %s, driver=%s, backend=%s",
            socket.gethostname(), platform.system(), self.config.device_id,
            self.driver.name, self.config.backend_url,
        )

        while True:
            try:
                # Straight back round when there was work: a queued batch should
                # not be paced by the idle interval.
                if self.poll_once():
                    continue
                time.sleep(IDLE_POLL_SECONDS)
            except KeyboardInterrupt:
                logger.info("Stopping.")
                return
            except httpx.HTTPError as exc:
                logger.warning(
                    "Backend unreachable (%s); retrying in %ss",
                    exc, ERROR_BACKOFF_SECONDS,
                )
                time.sleep(ERROR_BACKOFF_SECONDS)

    def close(self) -> None:
        self._client.close()


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AutoOps endpoint agent: runs approved remediation actions on this machine.",
    )
    parser.add_argument("--backend-url", help=f"Default: {DEFAULT_BACKEND_URL}")
    parser.add_argument("--device-id", help="Or set AUTOOPS_DEVICE_ID")
    parser.add_argument("--device-secret", help="Or set AUTOOPS_DEVICE_SECRET")
    parser.add_argument(
        "--driver",
        help=(
            "Override the execution driver. Normally left unset so the machine "
            "chooses: PowerShell on Windows, read-only POSIX elsewhere."
        ),
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Take at most one job and exit. Used for testing.",
    )
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
    )

    agent = Agent(AgentConfig.from_environment(args))
    try:
        if args.once:
            took = agent.poll_once()
            logger.info("Took a job." if took else "Nothing queued.")
            return 0
        agent.run_forever()
        return 0
    finally:
        agent.close()


if __name__ == "__main__":
    raise SystemExit(main())
