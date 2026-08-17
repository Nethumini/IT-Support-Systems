"""
Audit logging service for tracking security-sensitive actions.
"""
import logging
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.audit_log import AuditLogDB, AuditLogCreate, AuditAction

logger = logging.getLogger(__name__)


class AuditService:
    """Service for managing audit logs."""
    
    @staticmethod
    def log_action(
        db: Session,
        action: AuditAction,
        success: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[str] = None,
        action_metadata: Optional[dict] = None,
        error_message: Optional[str] = None
    ) -> AuditLogDB:
        """
        Log an action to the audit log.
        
        Args:
            db: Database session
            action: The action being performed
            success: "success", "failure", or "denied"
            user_id: ID of user performing action
            user_email: Email of user performing action
            user_role: Role of user performing action
            resource_type: Type of resource (e.g., "ticket", "user")
            resource_id: ID of the resource
            ip_address: IP address of the request
            user_agent: User agent string
            details: Human-readable description
            action_metadata: Additional structured data
            error_message: Error message if action failed
        
        Returns:
            Created audit log entry
        """
        try:
            audit_log = AuditLogDB(
                user_id=user_id,
                user_email=user_email,
                user_role=user_role,
                action=action.value,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                details=details,
                action_metadata=action_metadata,
                error_message=error_message
            )
            
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            
            # Also log to application logger for immediate visibility
            log_message = f"AUDIT: {action.value} by {user_email or 'system'} - {success}"
            if resource_type and resource_id:
                log_message += f" - {resource_type}:{resource_id}"
            
            if success == "success":
                logger.info(log_message)
            elif success == "denied":
                logger.warning(f"{log_message} - DENIED: {details or 'No details'}")
            else:
                logger.error(f"{log_message} - FAILED: {error_message or 'No error message'}")
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            # Don't raise - audit logging should never break the main flow
            return None
    
    @staticmethod
    def log_login(db: Session, user_email: str, success: bool, 
                  ip_address: Optional[str] = None, error: Optional[str] = None):
        """Log a login attempt."""
        return AuditService.log_action(
            db=db,
            action=AuditAction.LOGIN_SUCCESS if success else AuditAction.LOGIN_FAILED,
            success="success" if success else "failure",
            user_email=user_email,
            ip_address=ip_address,
            details=f"Login {'successful' if success else 'failed'} for {user_email}",
            error_message=error
        )
    
    @staticmethod
    def log_ticket_access(db: Session, user_email: str, user_role: str, 
                          ticket_id: str, action: AuditAction, 
                          success: bool = True, details: Optional[str] = None):
        """Log ticket access or modification."""
        return AuditService.log_action(
            db=db,
            action=action,
            success="success" if success else "denied",
            user_email=user_email,
            user_role=user_role,
            resource_type="ticket",
            resource_id=ticket_id,
            details=details or f"User {user_email} performed {action.value} on ticket {ticket_id}"
        )
    
    @staticmethod
    def log_access_denied(db: Session, user_email: str, user_role: str,
                          action: str, resource: str, reason: str,
                          ip_address: Optional[str] = None):
        """Log an access denied event."""
        return AuditService.log_action(
            db=db,
            action=AuditAction.ACCESS_DENIED,
            success="denied",
            user_email=user_email,
            user_role=user_role,
            resource_type=resource,
            ip_address=ip_address,
            details=f"Access denied: {reason}",
            action_metadata={"attempted_action": action, "resource": resource}
        )
    
    @staticmethod
    def log_troubleshooting(db: Session, user_email: str, user_role: str,
                           ticket_id: str, action_taken: str, result: str):
        """Log troubleshooting actions."""
        return AuditService.log_action(
            db=db,
            action=AuditAction.TROUBLESHOOT_RUN,
            success="success",
            user_email=user_email,
            user_role=user_role,
            resource_type="ticket",
            resource_id=ticket_id,
            details=f"Troubleshooting action: {action_taken}",
            action_metadata={"action": action_taken, "result": result}
        )
    
    @staticmethod
    def get_user_audit_logs(db: Session, user_email: str, limit: int = 100):
        """Get audit logs for a specific user."""
        return db.query(AuditLogDB)\
            .filter(AuditLogDB.user_email == user_email)\
            .order_by(desc(AuditLogDB.timestamp))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_recent_logs(db: Session, limit: int = 100):
        """Get recent audit logs (admin only)."""
        return db.query(AuditLogDB)\
            .order_by(desc(AuditLogDB.timestamp))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_failed_access_attempts(db: Session, hours: int = 24):
        """Get failed access attempts in the last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return db.query(AuditLogDB)\
            .filter(AuditLogDB.timestamp >= cutoff)\
            .filter(AuditLogDB.success.in_(["failure", "denied"]))\
            .order_by(desc(AuditLogDB.timestamp))\
            .all()


# Create singleton instance
audit_service = AuditService()
