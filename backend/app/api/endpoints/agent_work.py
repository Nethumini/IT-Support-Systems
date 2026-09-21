"""The two routes an endpoint agent uses.

An agent asks for work and posts back what happened. It authenticates with its
device credential, and both routes are scoped to that credential rather than to
anything the agent sends: it can only take jobs addressed to itself, and only
complete jobs it was given. A device id in a URL or body is never trusted.

**What an agent still cannot do**, by construction: propose a remediation, score
one, approve one, reject one, or read another machine's work. It receives an
action id that has already passed risk assessment and approval on the server,
and it reports an outcome. Every decision stays where it can be audited.

**Known trust boundary, stated plainly.** The agent reports its own machine's
state, and post-action verification reads that report. A compromised agent could
therefore claim a fix that did not happen - the same exposure any monitoring
agent has. Closing it needs attested measurement, which is outside this
prototype. What the server does control is that a fabricated report is still
recorded, attributable to one revocable device credential, and comparable with
the before-snapshot from the same run.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_device, get_db
from app.models.device_job import DeviceJobDB, JobStatus

logger = logging.getLogger(__name__)
router = APIRouter()

#: Ceiling on what an agent may send back per job. Generous for command output,
#: small enough that a misbehaving agent cannot fill the database.
MAX_RESULT_CHARS = 64_000


class JobResultPayload(BaseModel):
    """What the agent reports once it has run a job."""

    success: bool = Field(..., description="Whether the command itself completed")
    output: Optional[str] = Field(None, description="Captured output, for EXECUTE")
    error: Optional[str] = None
    duration_ms: Optional[int] = Field(None, ge=0)
    state_before: Optional[Dict[str, Any]] = None
    state_after: Optional[Dict[str, Any]] = None
    #: For CAPTURE_STATE jobs: the state that was read.
    state: Optional[Dict[str, Any]] = None


@router.get("/work")
async def take_next_job(
    db: Session = Depends(get_db),
    current_device=Depends(get_current_device),
) -> Dict[str, Any]:
    """Hand this device its next job, if it has one.

    Returns ``{"job": null}`` when there is nothing to do, so a polling agent
    treats an idle server as a normal answer rather than an error.

    Jobs past their deadline are retired here rather than handed over: the
    caller that queued one has already given up on it, and running it now would
    act on state that has since moved on.
    """
    jobs = (
        db.query(DeviceJobDB)
        .filter(DeviceJobDB.device_id == current_device.device_id)
        .filter(DeviceJobDB.status == JobStatus.QUEUED.value)
        .order_by(DeviceJobDB.id.asc())
        .all()
    )

    for job in jobs:
        if job.is_expired():
            job.mark_expired()
            db.commit()
            continue

        job.mark_taken()
        db.commit()
        db.refresh(job)
        logger.info(
            "Device %s took job %s (%s %s)",
            current_device.device_id, job.job_id, job.kind, job.action_id or job.scope,
        )
        return {"job": job.to_agent_dict()}

    return {"job": None}


@router.post("/work/{job_id}/result")
async def report_job_result(
    job_id: str,
    payload: JobResultPayload,
    db: Session = Depends(get_db),
    current_device=Depends(get_current_device),
) -> Dict[str, Any]:
    """Record what the device observed.

    A job can be completed once. A repeat submission is refused rather than
    overwriting, so a retrying or replaying agent cannot rewrite an outcome that
    verification has already been run against.
    """
    job = db.query(DeviceJobDB).filter(DeviceJobDB.job_id == job_id).first()

    # Same answer whether the job belongs to another device or does not exist,
    # so an agent cannot probe for other machines' work.
    if job is None or job.device_id != current_device.device_id:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.is_finished:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job already {job.status}; results cannot be resubmitted.",
        )

    result: Dict[str, Any] = payload.model_dump(exclude_none=True)

    if payload.output and len(payload.output) > MAX_RESULT_CHARS:
        result["output"] = payload.output[:MAX_RESULT_CHARS] + "\n[truncated]"

    # A CAPTURE_STATE job answers with the state itself, so the driver can read
    # it directly rather than unwrapping an envelope.
    if job.kind == "capture_state":
        state = payload.state if payload.state is not None else {}
        if payload.success:
            job.mark_done(state)
        else:
            job.mark_failed(payload.error or "State capture failed.", state)
    elif payload.success:
        job.mark_done(result)
    else:
        job.mark_failed(payload.error or "The action failed on the device.", result)

    db.commit()
    logger.info(
        "Device %s reported job %s as %s",
        current_device.device_id, job.job_id, job.status,
    )

    return {"job_id": job.job_id, "status": job.status}
