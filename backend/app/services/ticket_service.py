"""
Ticket service - CRUD operations and business logic for tickets.
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.ticket import (
    TicketDB, TicketCreate, TicketUpdate, TicketStatus,
    TicketPriority, TicketCategory
)
from app.models.user import UserDB

logger = logging.getLogger(__name__)


class TicketService:
    """Service for managing support tickets."""
    
    @staticmethod
    def create_ticket(db: Session, ticket_data: TicketCreate) -> Dict:
        """
        Create a new ticket with AI analysis and smart assignment.
        
        Returns:
            {
                "ticket": TicketDB,
                "assignment": {
                    "assigned_to": "agent@example.com",
                    "reason": "Assignment reason",
                    "confidence": 0.85
                }
            }
        """
        # Create ticket in database
        db_ticket = TicketDB(
            title=ticket_data.title,
            description=ticket_data.description,
            user_email=ticket_data.user_email,
            status=TicketStatus.OPEN,
            priority=ticket_data.priority or TicketPriority.MEDIUM,
            category=ticket_data.category or TicketCategory.OTHER,
            assigned_to=ticket_data.assigned_to  # Manual assignment if provided
        )
        
        # Simple ticket creation - AI analysis happens in chat endpoint
        # The multi-agent system in /chat provides better analysis
        try:
            db_ticket.ai_analysis = "Ticket created. Use /chat endpoint for AI-powered troubleshooting."
            
        except Exception as e:
            logger.error(f"Error in ticket creation: {e}")
            db_ticket.ai_analysis = f"Error during creation: {str(e)}"
        
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        
        # NOTE: We do NOT auto-assign on creation anymore!
        # Assignment happens ONLY when AI agent cannot resolve and escalates.
        # This allows the AI to try solving the issue first.
        # See chat_simple.py for escalation-based assignment logic.
        assignment_result = None
        
        return {
            "ticket": db_ticket,
            "assignment": assignment_result
        }
    
    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Optional[TicketDB]:
        """Get a ticket by ID."""
        return db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
    
    @staticmethod
    def get_tickets(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        category: Optional[TicketCategory] = None
    ) -> List[TicketDB]:
        """Get tickets with optional filtering."""
        query = db.query(TicketDB)
        
        if status:
            query = query.filter(TicketDB.status == status)
        if priority:
            query = query.filter(TicketDB.priority == priority)
        if category:
            query = query.filter(TicketDB.category == category)
        
        return query.order_by(desc(TicketDB.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_ticket(
        db: Session,
        ticket_id: int,
        ticket_update: TicketUpdate
    ) -> Optional[TicketDB]:
        """Update a ticket."""
        db_ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
        
        if not db_ticket:
            return None
        
        # Update fields
        update_data = ticket_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_ticket, field, value)
        
        # Update resolved_at if status changed to resolved or closed
        if ticket_update.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            if not db_ticket.resolved_at:
                db_ticket.resolved_at = datetime.utcnow()
        
        db_ticket.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_ticket)
        
        return db_ticket
    
    @staticmethod
    def delete_ticket(db: Session, ticket_id: int) -> bool:
        """Delete a ticket."""
        db_ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
        
        if not db_ticket:
            return False
        
        db.delete(db_ticket)
        db.commit()
        
        return True
    
    @staticmethod
    def get_team_members(db: Session, manager_id: int) -> List[str]:
        """
        Get all team members' emails for a manager.
        Returns list of user emails who have this manager as their manager_id or work in same department.
        """
        manager = db.query(UserDB).filter(UserDB.id == manager_id).first()
        if not manager:
            return []
        
        # Get direct reports (users with this manager_id)
        direct_reports = db.query(UserDB).filter(UserDB.manager_id == manager_id).all()
        team_emails = [user.email for user in direct_reports]
        
        # Optionally: get users in same department
        if manager.department:
            dept_users = db.query(UserDB).filter(
                UserDB.department == manager.department,
                UserDB.id != manager_id  # Exclude the manager themselves
            ).all()
            team_emails.extend([user.email for user in dept_users if user.email not in team_emails])
        
        return team_emails
    
    @staticmethod
    def get_ticket_stats(db: Session) -> dict:
        """Get statistics about tickets."""
        total = db.query(TicketDB).count()
        open_tickets = db.query(TicketDB).filter(TicketDB.status == TicketStatus.OPEN).count()
        in_progress = db.query(TicketDB).filter(TicketDB.status == TicketStatus.IN_PROGRESS).count()
        resolved = db.query(TicketDB).filter(TicketDB.status == TicketStatus.RESOLVED).count()
        closed = db.query(TicketDB).filter(TicketDB.status == TicketStatus.CLOSED).count()
        
        # Priority breakdown
        critical = db.query(TicketDB).filter(TicketDB.priority == TicketPriority.CRITICAL).count()
        high = db.query(TicketDB).filter(TicketDB.priority == TicketPriority.HIGH).count()
        medium = db.query(TicketDB).filter(TicketDB.priority == TicketPriority.MEDIUM).count()
        low = db.query(TicketDB).filter(TicketDB.priority == TicketPriority.LOW).count()
        
        # Category breakdown
        user_error = db.query(TicketDB).filter(TicketDB.category == TicketCategory.USER_ERROR).count()
        system_issue = db.query(TicketDB).filter(TicketDB.category == TicketCategory.SYSTEM_ISSUE).count()
        feature_request = db.query(TicketDB).filter(TicketDB.category == TicketCategory.FEATURE_REQUEST).count()
        
        return {
            "total": total,
            "by_status": {
                "open": open_tickets,
                "in_progress": in_progress,
                "resolved": resolved,
                "closed": closed
            },
            "by_priority": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low
            },
            "by_category": {
                "user_error": user_error,
                "system_issue": system_issue,
                "feature_request": feature_request
            }
        }
    

# Create global service instance
ticket_service = TicketService()
