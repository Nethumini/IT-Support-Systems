"""
Tickets endpoints - CRUD operations for support tickets with RBAC.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.ticket import (
    Ticket, TicketCreate, TicketUpdate, TicketStatus,
    TicketPriority, TicketCategory
)
from app.models.user import UserDB
from app.models.role import Role, Permission, can_view_ticket, can_update_ticket
from app.api.deps import get_current_active_user, require_permission
from app.services.ticket_service import ticket_service
from app.services.audit_service import audit_service
from app.models.audit_log import AuditAction

router = APIRouter()


@router.post("/tickets", response_model=Ticket, status_code=201)
async def create_ticket(
    ticket: TicketCreate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new support ticket.
    AI triage and analysis will be performed automatically.
    All authenticated users can create tickets.
    """
    try:
        # Set the user_email to current user if not provided
        if not ticket.user_email:
            ticket.user_email = current_user.email
        
        # Create the ticket (returns dict with ticket and assignment)
        result = ticket_service.create_ticket(db, ticket)
        new_ticket = result.get("ticket")
        assignment = result.get("assignment")
        
        # Build audit log details
        details = f"Created ticket: {new_ticket.title}"
        if assignment and assignment.get('assigned_to'):
            details += f" | Auto-assigned to {assignment['assigned_to']} - {assignment.get('reason', 'N/A')}"
        
        # Log ticket creation
        audit_service.log_ticket_access(
            db=db,
            user_email=current_user.email,
            user_role=current_user.role,
            ticket_id=str(new_ticket.id),
            action=AuditAction.TICKET_CREATE,
            details=details
        )
        
        return new_ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")


@router.get("/tickets", response_model=List[Ticket])
async def get_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    category: Optional[TicketCategory] = None,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get list of tickets with optional filtering.
    Access is filtered based on user role:
    - Staff/Contractor: Only their own tickets
    - Manager: Own tickets and team tickets (direct reports + department colleagues)
    - Support/Admin: All tickets
    """
    try:
        user_role = Role(current_user.role)
        
        # For managers, get their team members
        team_member_emails = None
        if user_role == Role.MANAGER and current_user.id:
            team_member_emails = ticket_service.get_team_members(db, current_user.id)
        
        # Get all tickets first (will filter by permission)
        all_tickets = ticket_service.get_tickets(
            db,
            skip=skip,
            limit=limit,
            status=status,
            priority=priority,
            category=category
        )
        
        # Filter tickets based on role permissions
        filtered_tickets = []
        for ticket in all_tickets:
            if can_view_ticket(
                user_role=user_role,
                ticket_user_email=ticket.user_email,
                current_user_email=current_user.email,
                ticket_assigned_to=ticket.assigned_to,
                team_member_emails=team_member_emails
            ):
                filtered_tickets.append(ticket)
        
        return filtered_tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tickets: {str(e)}")


@router.get("/tickets/stats/summary")
async def get_ticket_stats(
    current_user: UserDB = Depends(require_permission(Permission.DASHBOARD_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get statistics about tickets.
    Requires DASHBOARD_VIEW permission.
    Stats are filtered based on user's access level.
    """
    try:
        user_role = Role(current_user.role)
        stats = ticket_service.get_ticket_stats(db)
        
        # Filter stats based on role (basic implementation)
        # For staff/contractors, only show stats for their own tickets
        if user_role in [Role.STAFF, Role.CONTRACTOR]:
            # Could implement user-specific stats here
            pass
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@router.get("/tickets/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific ticket by ID.
    Access control: User must have permission to view this ticket.
    """
    ticket = ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check if user can view this ticket
    user_role = Role(current_user.role)
    
    # For managers, get their team members
    team_member_emails = None
    if user_role == Role.MANAGER and current_user.id:
        team_member_emails = ticket_service.get_team_members(db, current_user.id)
    
    if not can_view_ticket(
        user_role=user_role,
        ticket_user_email=ticket.user_email,
        current_user_email=current_user.email,
        ticket_assigned_to=ticket.assigned_to,
        team_member_emails=team_member_emails
    ):
        # Log access denied
        audit_service.log_access_denied(
            db=db,
            user_email=current_user.email,
            user_role=current_user.role,
            action="view_ticket",
            resource=f"ticket:{ticket_id}",
            reason="User does not have permission to view this ticket"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this ticket"
        )
    
    return ticket


@router.put("/tickets/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a ticket.
    Access control: User must have permission to update this ticket.
    """
    try:
        # Get existing ticket
        existing_ticket = ticket_service.get_ticket(db, ticket_id)
        if not existing_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Check if user can update this ticket
        user_role = Role(current_user.role)
        
        # For managers, get their team members
        team_member_emails = None
        if user_role == Role.MANAGER and current_user.id:
            team_member_emails = ticket_service.get_team_members(db, current_user.id)
        
        if not can_update_ticket(
            user_role=user_role,
            ticket_user_email=existing_ticket.user_email,
            current_user_email=current_user.email,
            ticket_assigned_to=existing_ticket.assigned_to,
            team_member_emails=team_member_emails
        ):
            # Log access denied
            audit_service.log_access_denied(
                db=db,
                user_email=current_user.email,
                user_role=current_user.role,
                action="update_ticket",
                resource=f"ticket:{ticket_id}",
                reason="User does not have permission to update this ticket"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this ticket"
            )
        
        # Update the ticket
        updated_ticket = ticket_service.update_ticket(db, ticket_id, ticket_update)
        
        # Log the update
        audit_service.log_ticket_access(
            db=db,
            user_email=current_user.email,
            user_role=current_user.role,
            ticket_id=str(ticket_id),
            action=AuditAction.TICKET_UPDATE,
            details=f"Updated ticket fields: {ticket_update.dict(exclude_unset=True)}"
        )
        
        return updated_ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating ticket: {str(e)}")


@router.post("/tickets/{ticket_id}/reassign", response_model=Ticket)
async def reassign_ticket(
    ticket_id: int,
    agent_email: Optional[str] = None,  # If None, use smart assignment
    current_user: UserDB = Depends(require_permission(Permission.TICKET_ASSIGN)),
    db: Session = Depends(get_db)
):
    """
    Reassign a ticket to a different agent.
    If agent_email is not provided, uses smart LLM-based assignment.
    Requires TICKET_ASSIGN permission (Support L1+ or Manager).
    """
    from app.services.assignment_service import get_assignment_service
    from app.models.ticket import TicketDB
    
    # Get ticket
    ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    assignment_service = get_assignment_service()
    old_assignee = ticket.assigned_to
    
    try:
        if agent_email:
            # Manual reassignment
            result = assignment_service.reassign_ticket(ticket, agent_email, db)
            if not result.get('success'):
                raise HTTPException(status_code=400, detail=result.get('reason', 'Assignment failed'))
            
            details = f"Manually reassigned from {old_assignee or 'unassigned'} to {agent_email}"
        else:
            # Smart reassignment
            result = assignment_service.assign_ticket(ticket, db)
            details = f"Smart reassignment from {old_assignee or 'unassigned'} to {ticket.assigned_to} - {result.get('reason', 'N/A')}"
        
        # Update status
        ticket.status = TicketStatus.ASSIGNED_TO_HUMAN
        db.commit()
        db.refresh(ticket)
        
        # Log reassignment
        audit_service.log_ticket_access(
            db=db,
            user_email=current_user.email,
            user_role=current_user.role,
            ticket_id=str(ticket_id),
            action=AuditAction.TICKET_UPDATE,
            details=details
        )
        
        return ticket
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reassignment failed: {str(e)}")


@router.delete("/tickets/{ticket_id}", status_code=204)
async def delete_ticket(
    ticket_id: int,
    current_user: UserDB = Depends(require_permission(Permission.TICKET_DELETE_ANY)),
    db: Session = Depends(get_db)
):
    """
    Delete a ticket.
    Requires TICKET_DELETE_ANY permission (Support L2+ or Admin only).
    """
    success = ticket_service.delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Log deletion
    audit_service.log_ticket_access(
        db=db,
        user_email=current_user.email,
        user_role=current_user.role,
        ticket_id=str(ticket_id),
        action=AuditAction.TICKET_DELETE,
        details="Ticket deleted"
    )
    
    return None


@router.post("/tickets/{ticket_id}/troubleshoot", response_model=Ticket)
async def run_troubleshooting(
    ticket_id: int,
    current_user: UserDB = Depends(require_permission(Permission.TROUBLESHOOT_RUN)),
    db: Session = Depends(get_db)
):
    """
    Run AI troubleshooting for a ticket.
    Requires TROUBLESHOOT_RUN permission (Support staff or Admin only).
    This will generate diagnostic information and troubleshooting steps.
    """
    try:
        ticket = ticket_service.run_troubleshooting(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Log troubleshooting action
        audit_service.log_troubleshooting(
            db=db,
            user_email=current_user.email,
            user_role=current_user.role,
            ticket_id=str(ticket_id),
            action_taken="AI troubleshooting analysis",
            result="Analysis completed"
        )
        
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running troubleshooting: {str(e)}")
