"""
Audit log models for tracking all security-sensitive actions.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from pydantic import BaseModel
from app.core.database import Base


class AuditAction(str, Enum):
    """Types of auditable actions."""
    # Authentication
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    
    # Ticket actions
    TICKET_VIEW = "ticket_view"
    TICKET_CREATE = "ticket_create"
    TICKET_UPDATE = "ticket_update"
    TICKET_DELETE = "ticket_delete"
    TICKET_ASSIGN = "ticket_assign"
    TICKET_ESCALATE = "ticket_escalate"
    TICKET_RESOLVE = "ticket_resolve"
    
    # Troubleshooting actions
    TROUBLESHOOT_RUN = "troubleshoot_run"
    TROUBLESHOOT_AUTO_RESOLVE = "troubleshoot_auto_resolve"
    SYSTEM_DIAGNOSTICS = "system_diagnostics"
    
    # Admin actions
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_ROLE_CHANGE = "user_role_change"
    USER_DEACTIVATE = "user_deactivate"
    
    # Access control
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHECK = "permission_check"
    
    # System actions
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    KB_UPDATE = "kb_update"


class AuditLogDB(Base):
    """Audit log database model for tracking all actions."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # User information
    user_id = Column(String, index=True, nullable=True)  # Can be null for system actions
    user_email = Column(String, index=True, nullable=True)
    user_role = Column(String, index=True, nullable=True)
    
    # Action details
    action = Column(String, index=True, nullable=False)  # AuditAction enum value
    resource_type = Column(String, nullable=True)  # e.g., "ticket", "user", "system"
    resource_id = Column(String, nullable=True)  # ID of the resource being acted upon
    
    # Request context
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Action result
    success = Column(String, nullable=False)  # "success", "failure", "denied"
    details = Column(Text, nullable=True)  # Human-readable description
    action_metadata = Column(JSON, nullable=True)  # Additional structured data
    
    # Error information (if action failed)
    error_message = Column(Text, nullable=True)


# Pydantic Models
class AuditLogCreate(BaseModel):
    """Schema for creating an audit log entry."""
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    action: AuditAction
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: str  # "success", "failure", "denied"
    details: Optional[str] = None
    action_metadata: Optional[dict] = None
    error_message: Optional[str] = None


class AuditLog(BaseModel):
    """Audit log response schema."""
    id: int
    timestamp: datetime
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    success: str
    details: Optional[str] = None
    action_metadata: Optional[dict] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class AuditLogFilter(BaseModel):
    """Filter for querying audit logs."""
    user_email: Optional[str] = None
    action: Optional[AuditAction] = None
    resource_type: Optional[str] = None
    success: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
