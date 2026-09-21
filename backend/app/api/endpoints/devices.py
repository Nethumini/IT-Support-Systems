"""Endpoint device administration.

A device is a machine running the AutoOps agent. Registering one grants that
machine the right to execute already-approved remediation actions on itself, so
every route here is administrator-only and every change is audited.

There is deliberately **no self-enrolment endpoint**. An unknown machine cannot
join by calling in; an administrator registers it and hands over the secret out
of band. That closes the obvious attack on an agent fleet - a rogue host
enrolling itself and then collecting other people's work.

The agent's own routes (collecting work, returning results) live in
``agent_work.py`` and authenticate with the device credential instead.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db, require_permission
from app.models.audit_log import AuditAction
from app.models.device import DeviceDB, new_device_id
from app.models.role import Permission
from app.models.user import UserDB
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)
router = APIRouter()


class DeviceRegisterRequest(BaseModel):
    """What an administrator supplies to register a machine."""

    name: str = Field(..., min_length=1, max_length=120, description="Hostname")
    owner_email: EmailStr = Field(..., description="Whose machine this is")
    os_name: Optional[str] = Field(None, max_length=60, description="e.g. Windows")
    os_version: Optional[str] = Field(None, max_length=60)


class DeviceRegisterResponse(BaseModel):
    """The secret appears here and nowhere else, ever."""

    device: dict
    secret: str = Field(
        ...,
        description=(
            "Shown once. Store it in the agent's configuration now - it is held "
            "only as a hash and cannot be retrieved again."
        ),
    )


def require_real_owner(db: Session, owner_email: str) -> UserDB:
    """Refuse an owner who is not a user of this system.

    The owner is how a person is joined to their machine: the chat looks up
    devices whose owner matches the signed-in user. An owner nobody logs in with
    creates a machine that can never be reached, and the mistake stays invisible
    until someone wonders why their agent is being ignored.
    """
    owner = db.query(UserDB).filter(UserDB.email == owner_email).first()
    if owner is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"No user with the email {owner_email}. Add the person first, "
                f"or use the address they sign in with - a machine is matched "
                f"to its owner by that address."
            ),
        )
    return owner


def _audit(
    db: Session,
    action: AuditAction,
    actor: UserDB,
    device: DeviceDB,
    details: str,
    request: Optional[Request] = None,
) -> None:
    """Record a device change against the acting administrator."""
    AuditService.log_action(
        db=db,
        action=action,
        success="success",
        user_email=actor.email,
        user_role=actor.role,
        resource_type="device",
        resource_id=device.device_id,
        details=details,
        ip_address=request.client.host if request and request.client else None,
        action_metadata={
            "device_name": device.name,
            "owner_email": device.owner_email,
            "os_name": device.os_name,
        },
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=DeviceRegisterResponse)
async def register_device(
    payload: DeviceRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_permission(Permission.SYSTEM_ADMIN)),
):
    """Register a machine and mint its credential.

    The secret is returned exactly once. Losing it means registering the device
    again, which is the intended trade - a secret that can be read back is a
    secret sitting in a database waiting to be read by someone else.
    """
    require_real_owner(db, payload.owner_email)

    device = DeviceDB(
        device_id=new_device_id(),
        name=payload.name,
        owner_email=payload.owner_email,
        os_name=payload.os_name,
        os_version=payload.os_version,
        is_active=True,
    )
    secret = device.issue_secret()

    db.add(device)
    db.commit()
    db.refresh(device)

    _audit(
        db, AuditAction.DEVICE_REGISTERED, current_user, device,
        f"Registered device {device.name} for {device.owner_email}",
        request,
    )
    logger.info("Device %s registered for %s", device.device_id, device.owner_email)

    return DeviceRegisterResponse(device=device.to_dict(), secret=secret)


@router.get("")
async def list_devices(
    include_revoked: bool = Query(False, description="Also list revoked devices"),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_permission(Permission.SYSTEM_ADMIN)),
) -> List[dict]:
    """Every registered machine. Secrets are never included."""
    query = db.query(DeviceDB)
    if not include_revoked:
        query = query.filter(DeviceDB.is_active.is_(True))
    return [d.to_dict() for d in query.order_by(DeviceDB.id.desc()).all()]


@router.get("/mine")
async def list_my_devices(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
) -> List[dict]:
    """The machines belonging to whoever is logged in.

    This is what joins a person to their computer. A remediation targets a
    device id, and the browser has only a logged-in user - so the chat asks here
    which machines that user owns.

    Most recently seen first, because a person with two machines is usually
    sitting at the one that called in last.
    """
    devices = (
        db.query(DeviceDB)
        .filter(DeviceDB.owner_email == current_user.email)
        .filter(DeviceDB.is_active.is_(True))
        .all()
    )
    devices.sort(key=lambda d: (d.last_seen_at is not None, d.last_seen_at), reverse=True)
    return [d.to_dict() for d in devices]


@router.post("/{device_id}/revoke")
async def revoke_device(
    device_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_permission(Permission.SYSTEM_ADMIN)),
) -> dict:
    """Stop a machine receiving any further work.

    Irreversible by design: re-enabling a device whose secret may have leaked
    would defeat the point, so recovery means registering it again with a new
    credential.
    """
    device = db.query(DeviceDB).filter(DeviceDB.device_id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    if not device.is_active:
        return {"device": device.to_dict(), "message": "Device was already revoked"}

    device.revoke()
    db.commit()
    db.refresh(device)

    _audit(
        db, AuditAction.DEVICE_REVOKED, current_user, device,
        f"Revoked device {device.name}",
        request,
    )
    logger.info("Device %s revoked by %s", device.device_id, current_user.email)

    return {"device": device.to_dict(), "message": "Device revoked"}
