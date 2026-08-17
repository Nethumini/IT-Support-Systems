"""
User models for database and API.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr
from app.core.database import Base
from app.models.role import Role, Permission, get_role_permissions


# SQLAlchemy Model
class UserDB(Base):
    """User database model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)  # User's full name
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=Role.STAFF.value)  # Using Role enum
    tier = Column(String, default="staff")  # Deprecated: kept for backward compatibility
    department = Column(String, nullable=True)  # For team-based access control
    manager_id = Column(Integer, nullable=True)  # ID of user's manager for team hierarchy
    specialization = Column(JSON, nullable=True)  # Agent expertise: ["hardware", "network", "software"]
    current_workload = Column(Integer, default=0)  # Number of active assigned tickets
    is_active = Column(Boolean, default=False)  # Inactive by default - admin must activate
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    name: str
    password: str
    role: Role = Role.STAFF
    department: Optional[str] = None
    password: str
    tier: str = "staff"  # staff, manager, contractor


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response (without password)."""
    id: int
    email: str
    name: str
    role: str
    department: Optional[str] = None
    manager_id: Optional[int] = None
    specialization: Optional[List[str]] = None  # Agent expertise areas
    current_workload: Optional[int] = 0  # Active tickets assigned
    is_active: bool
    created_at: datetime
    permissions: Optional[List[str]] = None  # Computed field
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_db(cls, user_db: "UserDB"):
        """Create UserResponse from UserDB with computed permissions."""
        user_role = Role(user_db.role)
        permissions = [p.value for p in get_role_permissions(user_role)]
        
        return cls(
            id=user_db.id,
            email=user_db.email,
            name=user_db.name,
            role=user_db.role,
            department=user_db.department,
            manager_id=user_db.manager_id,
            specialization=user_db.specialization,
            current_workload=user_db.current_workload or 0,
            is_active=user_db.is_active,
            created_at=user_db.created_at,
            permissions=permissions
        )
        from_attributes = True


class Token(BaseModel):
    """Authentication token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ManagerAssignmentRequest(BaseModel):
    """Request to assign a manager to a user."""
    manager_id: Optional[int] = None


class UserCreate(BaseModel):
    """User creation request."""
    email: EmailStr
    name: str
    password: str
    role: Role = Role.STAFF
    department: Optional[str] = None
    specialization: Optional[List[str]] = None  # Agent expertise areas


class UserUpdate(BaseModel):
    """User update request."""
    email: EmailStr
    name: str
    password: Optional[str] = None
    role: Role = Role.STAFF
    department: Optional[str] = None
    specialization: Optional[List[str]] = None  # Agent expertise areas
