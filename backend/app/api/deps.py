"""
API dependencies - Database sessions, authentication, etc.
"""
import logging
from typing import Optional, Generator, Callable
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import UserDB
from app.models.role import Role, Permission, has_permission
from app.services.audit_service import audit_service
from app.models.audit_log import AuditAction

logger = logging.getLogger(__name__)

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[UserDB]:
    """
    Get current authenticated user from JWT token.
    """
    try:
        if not credentials:
            print("❌ No credentials provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        print(f"🔑 Token received: {token[:20]}...")
        payload = verify_token(token)
        print(f"✓ Token verified: {payload}")
        
        if payload is None:
            print("❌ Token payload is None")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        email = payload.get("sub")
        if email is None:
            print("❌ No email in payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = db.query(UserDB).filter(UserDB.email == email).first()
        if user is None:
            print(f"❌ User {email} not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print(f"✓ User authenticated: {email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(
    current_user: UserDB = Depends(get_current_user)
) -> UserDB:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_permission(permission: Permission):
    """
    Dependency factory that checks if user has a specific permission.
    Returns a dependency function that can be used with Depends().
    
    Usage:
        @app.get("/admin")
        def admin_endpoint(user: UserDB = Depends(require_permission(Permission.SYSTEM_ADMIN))):
            ...
    """
    def permission_checker(
        current_user: UserDB = Depends(get_current_active_user),
        db: Session = Depends(get_db),
        request: Request = None
    ) -> UserDB:
        user_role = Role(current_user.role)
        
        if not has_permission(user_role, permission):
            # Log access denied
            ip_address = request.client.host if request else None
            audit_service.log_access_denied(
                db=db,
                user_email=current_user.email,
                user_role=current_user.role,
                action=permission.value,
                resource="endpoint",
                reason=f"User role {user_role.value} does not have permission {permission.value}",
                ip_address=ip_address
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} required"
            )
        
        return current_user
    
    return permission_checker


def require_any_permission(*permissions: Permission):
    """
    Check if user has ANY of the specified permissions.
    """
    def permission_checker(
        current_user: UserDB = Depends(get_current_active_user),
        db: Session = Depends(get_db),
        request: Request = None
    ) -> UserDB:
        user_role = Role(current_user.role)
        
        if not any(has_permission(user_role, perm) for perm in permissions):
            ip_address = request.client.host if request else None
            audit_service.log_access_denied(
                db=db,
                user_email=current_user.email,
                user_role=current_user.role,
                action=f"any_of_{[p.value for p in permissions]}",
                resource="endpoint",
                reason=f"User role {user_role.value} does not have any required permission",
                ip_address=ip_address
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied: insufficient permissions"
            )
        
        return current_user
    
    return permission_checker


def require_role(*roles: Role):
    """
    Check if user has one of the specified roles.
    """
    def role_checker(
        current_user: UserDB = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> UserDB:
        user_role = Role(current_user.role)
        
        if user_role not in roles:
            audit_service.log_access_denied(
                db=db,
                user_email=current_user.email,
                user_role=current_user.role,
                action="role_check",
                resource="endpoint",
                reason=f"User role {user_role.value} not in allowed roles {[r.value for r in roles]}"
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: one of {[r.value for r in roles]} role required"
            )
        
        return current_user
    
    return role_checker

def get_current_user_email(
    current_user: UserDB = Depends(get_current_active_user)
) -> str:
    """Get email of current authenticated user."""
    return current_user.email


# ═══════════════════════════════════════════════════════════════════════════
# Device authentication
# ═══════════════════════════════════════════════════════════════════════════
#
# An endpoint agent authenticates with a device id and secret, on its own code
# path, and never receives a user token. Keeping the two separate is the point:
# a device may collect work that was already approved and report what happened,
# and it can do nothing a user can do - it cannot approve, reject, or read
# anyone's tickets. A leaked agent secret therefore stays a device problem.


DEVICE_ID_HEADER = "X-Device-Id"
DEVICE_SECRET_HEADER = "X-Device-Secret"

#: One message for every failure. An agent learns only that the pair was
#: rejected, never whether the device id exists or the secret was the wrong
#: half, which would let an attacker enumerate registered machines.
_DEVICE_REJECTED = "Device authentication failed"


def get_current_device(
    request: Request,
    db: Session = Depends(get_db),
):
    """Authenticate the calling agent, or refuse.

    Records the call time on success, so an administrator can see which
    machines are still reporting in.
    """
    from app.models.device import DeviceDB

    device_id = request.headers.get(DEVICE_ID_HEADER)
    secret = request.headers.get(DEVICE_SECRET_HEADER)

    if not device_id or not secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_DEVICE_REJECTED,
        )

    device = db.query(DeviceDB).filter(DeviceDB.device_id == device_id).first()

    # The reason is logged for the administrator and deliberately not returned.
    reason = "Unknown device." if device is None else device.secret_error(secret)
    if reason is not None:
        logger.warning("Device auth refused for %r: %s", device_id, reason)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_DEVICE_REJECTED,
        )

    device.touch()
    db.commit()
    return device
