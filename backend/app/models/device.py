"""Persistence for enrolled endpoint devices.

A device is a machine running the AutoOps agent, which executes approved
remediation actions on itself and reports what it observed. Diagnostics used to
read whichever host ran the backend; a device lets the same driver interface
reach the machine that actually has the problem.

Three rules keep this safe to add, and each one is enforced here rather than
left to the caller:

* **A device decides nothing.** It receives an action id the server has already
  scored, routed and approved, runs it, and reports the result. Risk assessment,
  approval and verification stay on the server where they can be audited. An
  agent that could approve its own work would defeat the entire contribution.
* **A device credential is not a user credential.** The secret is stored as a
  hash, is checked on its own code path, and carries no user identity - so a
  stolen agent secret cannot be replayed against any user-facing route.
* **A device is registered by an administrator, never by itself.** There is no
  open enrolment endpoint, so an unknown machine cannot join by guessing.
"""
from __future__ import annotations

import secrets
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.security import get_password_hash, verify_password

#: Bytes of entropy in a device secret. Long enough that guessing is hopeless,
#: short enough to stay inside bcrypt's 72-byte input limit once encoded.
SECRET_BYTES = 32


class DeviceDB(Base):
    """One machine permitted to run remediation actions on itself."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)

    #: Public identifier the agent sends with every request. Opaque and random,
    #: so it leaks nothing about how many devices exist.
    device_id = Column(String, unique=True, index=True, nullable=False)

    #: Hostname as the agent reported it. Display only - never trusted for
    #: authorisation, because the agent chooses what to send.
    name = Column(String, nullable=False)
    os_name = Column(String, nullable=True)
    os_version = Column(String, nullable=True)

    #: Whose machine this is. Used to decide which remediations may target it.
    owner_email = Column(String, index=True, nullable=False)

    #: bcrypt hash of the device secret. The plaintext is returned exactly once,
    #: at registration, and is never stored or logged.
    secret_hash = Column(String, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # --- credential handling -------------------------------------------------

    def issue_secret(self) -> str:
        """Mint this device's secret and store only its hash.

        Returns the plaintext once, for the administrator to paste into the
        agent's configuration. There is no way to read it back afterwards; a
        lost secret means registering the device again.
        """
        secret = secrets.token_urlsafe(SECRET_BYTES)
        self.secret_hash = get_password_hash(secret)
        return secret

    def secret_error(self, secret: Optional[str]) -> Optional[str]:
        """Why this secret cannot be used, or ``None`` if it is valid.

        Returns a reason rather than a bare boolean so the caller can audit the
        refusal, but callers must not echo it to the agent - an attacker should
        not learn whether a device id exists, only that the pair was rejected.
        """
        if not self.is_active:
            return "Device has been revoked."
        if not secret:
            return "No device secret was supplied."
        if not verify_password(secret, self.secret_hash):
            return "Device secret does not match."
        return None

    def touch(self) -> None:
        """Record that the agent just called in."""
        self.last_seen_at = datetime.utcnow()

    def revoke(self) -> None:
        """Stop this device receiving any further work, permanently."""
        self.is_active = False
        self.revoked_at = datetime.utcnow()

    # --- serialisation -------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Public view. Deliberately has no field that could carry the secret."""
        return {
            "device_id": self.device_id,
            "name": self.name,
            "os_name": self.os_name,
            "os_version": self.os_version,
            "owner_email": self.owner_email,
            "is_active": self.is_active,
            "enrolled_at": self.enrolled_at.isoformat() if self.enrolled_at else None,
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
        }


def new_device_id() -> str:
    """An opaque public identifier for a newly registered device."""
    return f"dev_{secrets.token_urlsafe(16)}"
