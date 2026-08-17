"""
Admin endpoints for user management, role assignment, and audit logs.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import UserDB, UserResponse, ManagerAssignmentRequest, UserCreate, UserUpdate
from app.models.role import Role, Permission, ROLE_PERMISSIONS, ROLE_DESCRIPTIONS, RoleInfo
from app.models.audit_log import AuditLog, AuditLogFilter, AuditAction
from app.api.deps import require_permission, get_current_user
from app.services.audit_service import audit_service
from pydantic import BaseModel

router = APIRouter()


class UserRoleUpdate(BaseModel):
    """Schema for updating user role."""
    role: Role


class UserStatusUpdate(BaseModel):
    """Schema for updating user status."""
    is_active: bool


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[Role] = None,
    is_active: Optional[bool] = None,
    current_user: UserDB = Depends(require_permission(Permission.USER_VIEW)),
    db: Session = Depends(get_db)
):
    """
    List all users with optional filtering.
    Requires USER_VIEW permission (Support L1+ or Admin).
    """
    query = db.query(UserDB)
    
    if role:
        query = query.filter(UserDB.role == role.value)
    if is_active is not None:
        query = query.filter(UserDB.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    
    # Convert to response models with permissions
    return [UserResponse.from_db(user) for user in users]


@router.get("/users/assignable", response_model=List[UserResponse])
async def get_assignable_users(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all users who can be assigned tickets.
    Returns active users with roles: IT Admin, System Admin, Support L1/L2/L3.
    Requires authentication.
    """
    print(f"📋 Getting assignable users for user: {current_user.email}")
    assignable_roles = [
        Role.SYSTEM_ADMIN.value,
        Role.IT_ADMIN.value,
        Role.SUPPORT_L1.value,
        Role.SUPPORT_L2.value,
        Role.SUPPORT_L3.value
    ]
    
    users = db.query(UserDB).filter(
        UserDB.role.in_(assignable_roles),
        UserDB.is_active == True
    ).order_by(UserDB.role, UserDB.name).all()
    
    print(f"✓ Found {len(users)} assignable users")
    return [UserResponse.from_db(user) for user in users]


@router.get("/users/available-managers", response_model=List[UserResponse])
async def get_available_managers(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all users who can be managers (Manager role and above).
    Returns active users with roles: Manager, IT Support L3, IT Admin, System Admin.
    """
    print(f"📋 Getting available managers for user: {current_user.email}")
    manager_roles = [
        Role.SYSTEM_ADMIN.value,
        Role.IT_ADMIN.value,
        Role.SUPPORT_L3.value,
        Role.MANAGER.value
    ]
    
    managers = db.query(UserDB).filter(
        UserDB.role.in_(manager_roles),
        UserDB.is_active == True,
        UserDB.id != current_user.id  # Exclude current user
    ).order_by(UserDB.role, UserDB.name).all()
    
    print(f"✓ Found {len(managers)} available managers")
    return [UserResponse.from_db(user) for user in managers]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: UserDB = Depends(require_permission(Permission.USER_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID.
    Requires USER_VIEW permission.
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.from_db(user)


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    current_user: UserDB = Depends(require_permission(Permission.USER_MANAGE_ROLES)),
    db: Session = Depends(get_db)
):
    """
    Update a user's role.
    Requires USER_MANAGE_ROLES permission (IT Admin or System Admin only).
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_role = user.role
    user.role = role_update.role.value
    
    db.commit()
    db.refresh(user)
    
    # Log role change
    audit_service.log_action(
        db=db,
        action=AuditAction.USER_ROLE_CHANGE,
        success="success",
        user_email=current_user.email,
        user_role=current_user.role,
        resource_type="user",
        resource_id=str(user_id),
        details=f"Changed role from {old_role} to {role_update.role.value} for user {user.email}",
        action_metadata={"old_role": old_role, "new_role": role_update.role.value, "target_user": user.email}
    )
    
    return UserResponse.from_db(user)


@router.put("/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    current_user: UserDB = Depends(require_permission(Permission.USER_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Activate or deactivate a user.
    Requires USER_MANAGE permission (Support L3+ or Admin).
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-deactivation
    if user.id == current_user.id and not status_update.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    old_status = user.is_active
    user.is_active = status_update.is_active
    
    db.commit()
    db.refresh(user)
    
    # Log status change
    audit_service.log_action(
        db=db,
        action=AuditAction.USER_DEACTIVATE if not status_update.is_active else AuditAction.USER_UPDATE,
        success="success",
        user_email=current_user.email,
        user_role=current_user.role,
        resource_type="user",
        resource_id=str(user_id),
        details=f"Changed user {user.email} status from {old_status} to {status_update.is_active}",
        action_metadata={"old_status": old_status, "new_status": status_update.is_active, "target_user": user.email}
    )
    
    return UserResponse.from_db(user)


@router.get("/roles", response_model=List[RoleInfo])
async def list_roles(
    current_user: UserDB = Depends(require_permission(Permission.USER_VIEW))
):
    """
    List all available roles and their permissions.
    Requires USER_VIEW permission.
    """
    roles = []
    for role in Role:
        permissions = list(ROLE_PERMISSIONS.get(role, set()))
        roles.append(RoleInfo(
            role=role,
            permissions=[p.value for p in permissions],
            description=ROLE_DESCRIPTIONS.get(role, "")
        ))
    
    return roles


@router.get("/audit-logs", response_model=List[AuditLog])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_email: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    success: Optional[str] = None,
    current_user: UserDB = Depends(require_permission(Permission.SYSTEM_ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get audit logs with optional filtering.
    Requires SYSTEM_ADMIN permission (Admin only).
    """
    from app.models.audit_log import AuditLogDB
    from sqlalchemy import desc
    
    query = db.query(AuditLogDB)
    
    if user_email:
        query = query.filter(AuditLogDB.user_email == user_email)
    if action:
        query = query.filter(AuditLogDB.action == action)
    if resource_type:
        query = query.filter(AuditLogDB.resource_type == resource_type)
    if success:
        query = query.filter(AuditLogDB.success == success)
    
    logs = query.order_by(desc(AuditLogDB.timestamp)).offset(skip).limit(limit).all()
    
    return logs


@router.get("/audit-logs/me", response_model=List[AuditLog])
async def get_my_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for the current user.
    All authenticated users can view their own audit logs.
    """
    logs = audit_service.get_user_audit_logs(db, current_user.email, limit)
    return logs


@router.get("/audit-logs/failed-access")
async def get_failed_access_attempts(
    hours: int = Query(24, ge=1, le=168),
    current_user: UserDB = Depends(require_permission(Permission.SYSTEM_ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get failed access attempts in the last N hours.
    Requires SYSTEM_ADMIN permission.
    Useful for security monitoring.
    """
    logs = audit_service.get_failed_access_attempts(db, hours)
    return logs


@router.put("/users/{user_id}/manager", response_model=UserResponse)
async def assign_manager(
    user_id: int,
    request: ManagerAssignmentRequest,
    current_user: UserDB = Depends(require_permission(Permission.USER_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Assign a manager to a user for team hierarchy.
    Requires USER_MANAGE permission.
    manager_id=None to unassign.
    """
    manager_id = request.manager_id
    
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if manager_id is not None:
        manager = db.query(UserDB).filter(UserDB.id == manager_id).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manager not found"
            )
        if manager.id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User cannot be their own manager"
            )
    
    user.manager_id = manager_id
    db.commit()
    db.refresh(user)
    
    # Audit log
    manager_name = f"User {manager_id}" if manager_id else "None"
    audit_service.log_action(
        db=db,
        action=AuditAction.USER_UPDATE,
        success="success",
        user_email=current_user.email,
        user_role=current_user.role,
        resource_type="user",
        resource_id=str(user_id),
        details=f"Manager assigned to user {user.email}: {manager_name}"
    )
    
    return UserResponse.from_db(user)


@router.post("/users", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    current_user: UserDB = Depends(require_permission(Permission.USER_MANAGE)),
    db: Session = Depends(get_db)
):
    """Create a new user. Admin/Manager only."""
    
    # Check if user already exists
    existing_user = db.query(UserDB).filter(UserDB.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Import security function
    from app.core.security import get_password_hash
    
    # Create new user
    new_user = UserDB(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role.value,
        department=user_data.department,
        specialization=user_data.specialization,
        current_workload=0,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Audit log
    audit_service.log_action(
        db=db,
        action=AuditAction.USER_UPDATE,
        success="success",
        user_email=current_user.email,
        user_role=current_user.role,
        resource_type="user",
        resource_id=str(new_user.id),
        details=f"New user created: {new_user.email} (Role: {new_user.role})"
    )
    
    return UserResponse.from_db(new_user)


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: UserDB = Depends(require_permission(Permission.USER_MANAGE)),
    db: Session = Depends(get_db)
):
    """Update user details (email, name, password, role, department). Admin/Manager only."""
    
    # Get user
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-modification of role
    if user_id == current_user.id and user_data.role != Role(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role"
        )
    
    # Check if email is taken by another user
    if user_data.email != user.email:
        existing_user = db.query(UserDB).filter(UserDB.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Import security function
    from app.core.security import get_password_hash
    
    # Track changes for audit log
    changes = []
    
    if user_data.email != user.email:
        changes.append(f"Email: {user.email} → {user_data.email}")
        user.email = user_data.email
    
    if user_data.name != user.name:
        changes.append(f"Name: {user.name} → {user_data.name}")
        user.name = user_data.name
    
    if user_data.password:
        changes.append("Password updated")
        user.hashed_password = get_password_hash(user_data.password)
    
    if user_data.role.value != user.role:
        changes.append(f"Role: {user.role} → {user_data.role.value}")
        user.role = user_data.role.value
    
    if user_data.department != user.department:
        changes.append(f"Department: {user.department} → {user_data.department}")
        user.department = user_data.department
    
    if user_data.specialization != user.specialization:
        changes.append(f"Specialization updated")
        user.specialization = user_data.specialization
    
    db.commit()
    db.refresh(user)
    
    # Audit log
    if changes:
        audit_service.log_action(
            db=db,
            action=AuditAction.USER_UPDATE,
            success="success",
            user_email=current_user.email,
            user_role=current_user.role,
            resource_type="user",
            resource_id=str(user_id),
            details=f"User updated: {', '.join(changes)}"
        )
    
    return UserResponse.from_db(user)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: UserDB = Depends(require_permission(Permission.USER_MANAGE)),
    db: Session = Depends(get_db)
):
    """Delete a user. Admin/Manager only."""
    
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself"
        )
    
    # Get user
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_email = user.email
    
    # Delete user
    db.delete(user)
    db.commit()
    
    # Audit log
    audit_service.log_action(
        db=db,
        action=AuditAction.USER_UPDATE,
        success="success",
        user_email=current_user.email,
        user_role=current_user.role,
        resource_type="user",
        resource_id=str(user_id),
        details=f"User deleted: {user_email}"
    )
    
    return {"message": "User deleted successfully", "user_id": user_id}
