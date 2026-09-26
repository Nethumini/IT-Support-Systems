"""What a startup-item snapshot records, and how it is read back.

Until 26 September 2026 a startup snapshot was ``{name: True/False}``. That
said whether an item would run at logon, but not *what* it would run, so the
rollback post-check could only ask "is it enabled?". After a program
re-registers itself - the very reason a disable fails - the item is already
enabled before the rollback runs, and a rollback that did nothing passed.

Each item is now recorded as::

    {
        "enabled": bool,                      # has a value in the Run key
        "backup_exists": bool,                # has a value in AutoOps' own key
        "enabled_command_sha256": str | None, # fingerprint of the Run value
        "backup_command_sha256": str | None,  # fingerprint of the saved value
    }

An item is listed when it is in either key. Absent means "cannot tell", which
is a different answer from "turned off".

**Commands never leave the driver.** A startup command line can carry a user
name, a profile path or an argument nobody meant to publish, and nothing
downstream needs the text: two fingerprints answer "is this the same command"
as well as the commands would. A fingerprint is SHA-256 over the UTF-8 bytes of
the value as Windows returns it, in lower-case hex. The PowerShell query
computes the same thing on the machine, so the simulator and a real device
agree on what a given command looks like.

Pure Python on purpose: verification imports this, and verification must stay
testable without a database or a driver.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, Mapping, Optional

ENABLED = "enabled"
BACKUP_EXISTS = "backup_exists"
ENABLED_COMMAND_SHA256 = "enabled_command_sha256"
BACKUP_COMMAND_SHA256 = "backup_command_sha256"

_FINGERPRINT = re.compile(r"[0-9a-f]{64}")

#: Marks a fingerprint field that held something other than a fingerprint.
_INVALID = object()


def command_fingerprint(command: str) -> str:
    """SHA-256 of a startup command, as the Windows query computes it."""
    return hashlib.sha256(command.encode("utf-8")).hexdigest()


def startup_record(
    enabled_command: Optional[str],
    backup_command: Optional[str],
) -> Dict[str, Any]:
    """One item's record, built from its two registry values.

    ``None`` means the key holds no value for the item. The commands are
    fingerprinted here and not kept.
    """
    return {
        ENABLED: enabled_command is not None,
        BACKUP_EXISTS: backup_command is not None,
        ENABLED_COMMAND_SHA256: (
            command_fingerprint(enabled_command) if enabled_command is not None else None
        ),
        BACKUP_COMMAND_SHA256: (
            command_fingerprint(backup_command) if backup_command is not None else None
        ),
    }


def _fingerprint_field(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str) and _FINGERPRINT.fullmatch(value.lower()):
        return value.lower()
    # Not a fingerprint. It could be a command line that should never have
    # been sent, so the whole record is refused rather than the field dropped.
    return _INVALID


def read_startup_record(record: Any) -> Optional[Dict[str, Any]]:
    """The record if it is complete and consistent, otherwise ``None``.

    Both flags must be real booleans, and each fingerprint must be present
    exactly when its flag says the value exists. Anything else - including the
    bare ``True``/``False`` an agent that has not been updated still sends - is
    unreadable, and the checks treat unreadable as "cannot tell".

    Only the four known fields are copied, so nothing else a driver put in the
    record travels any further.
    """
    if not isinstance(record, Mapping):
        return None

    enabled = record.get(ENABLED)
    backup = record.get(BACKUP_EXISTS)
    if not isinstance(enabled, bool) or not isinstance(backup, bool):
        return None

    enabled_sha = _fingerprint_field(record.get(ENABLED_COMMAND_SHA256))
    backup_sha = _fingerprint_field(record.get(BACKUP_COMMAND_SHA256))
    if enabled_sha is _INVALID or backup_sha is _INVALID:
        return None
    if enabled != (enabled_sha is not None) or backup != (backup_sha is not None):
        return None

    return {
        ENABLED: enabled,
        BACKUP_EXISTS: backup,
        ENABLED_COMMAND_SHA256: enabled_sha,
        BACKUP_COMMAND_SHA256: backup_sha,
    }


def read_startup_snapshot(raw: Any) -> Dict[str, Dict[str, Any]]:
    """Every readable item in a snapshot, by name. Unreadable items are left out.

    Leaving one out makes it "not captured" to the checks, which refuse before
    acting and report inconclusive after - never a guess.
    """
    if not isinstance(raw, Mapping):
        return {}
    snapshot: Dict[str, Dict[str, Any]] = {}
    for name, record in raw.items():
        if not isinstance(name, str) or not name:
            continue
        parsed = read_startup_record(record)
        if parsed is not None:
            snapshot[name] = parsed
    return snapshot
