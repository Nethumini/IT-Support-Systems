"""
API dependencies - Database sessions, authentication, etc.
"""
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
