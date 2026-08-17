"""
Simple Chat Endpoint - LLM-First Approach
No complex logic, just let the LLM handle everything!
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from app.api.deps import get_current_user_email
from app.services.agents.llm_conversation_agent import get_llm_conversation_agent
from app.services.dataset_analyzer import DatasetAnalyzer
from app.core.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Setup dedicated chat logger for conversation tracking
chat_logger = logging.getLogger('chat_conversation')
chat_handler = logging.FileHandler('app/logs/chat.log')
chat_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
chat_logger.addHandler(chat_handler)
chat_logger.setLevel(logging.INFO)

router = APIRouter()


class ChatRequest(BaseModel):
    message: Optional[str] = None  # Single message (new format)
    messages: Optional[list] = None  # Array of messages (frontend format)
    ticket_id: Optional[int] = None
    user_email: Optional[str] = None  # Allow frontend to send email directly


class ChatResponse(BaseModel):
    message: str
    is_technical: bool
    should_escalate: bool
    is_resolved: bool
    ticket_id: Optional[int] = None
    metadata: dict


def get_user_email_optional(
    request: ChatRequest,
    authorization: Optional[str] = Header(None)
) -> str:
    """Get user email from request body or auth token, or use anonymous."""
    # Try request body first
    if request.user_email:
        return request.user_email
    
    # Try to get from token (but don't fail if not authenticated)
    if authorization and authorization.startswith("Bearer "):
        try:
            from app.core.security import verify_token
            token = authorization.replace("Bearer ", "")
            payload = verify_token(token)
            if payload and payload.get("sub"):
                return payload["sub"]
        except:
            pass
    
    # Default to anonymous
    return "anonymous@autoops.ai"


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Simple chat endpoint - LLM does all the work!
    
    Flow:
    1. User sends message
    2. Check RAG for similar issues (if technical)
    3. LLM generates response with RAG context
    4. Handle tickets if needed
    5. Return response
    """
    try:
        # Get user email
        user_email = get_user_email_optional(request)
        
        # Extract message from either format
        if request.message:
            user_message = request.message.strip()
        elif request.messages and len(request.messages) > 0:
            # Get last message from messages array
            last_msg = request.messages[-1]
            user_message = last_msg.get('content', '').strip() if isinstance(last_msg, dict) else str(last_msg).strip()
        else:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        logger.info(f"[CHAT] User: {user_email} | Message: {user_message[:100]}")
        
        # Log to dedicated chat log
        chat_logger.info("="*80)
        chat_logger.info(f"USER: {user_email}")
        chat_logger.info(f"MESSAGE: {user_message}")
        
        # Initialize services
        llm_agent = get_llm_conversation_agent()
        analyzer = DatasetAnalyzer()
        
        # Step 1: Quick check if this seems technical
        tech_keywords = [
            # Computers & Devices
            "computer", "laptop", "desktop", "pc", "mac", "macbook", "imac",
            "phone", "mobile", "iphone", "ipad", "android", "tablet", "device",
            # Gaming devices
            "playstation", "ps4", "ps5", "xbox", "nintendo", "switch", "gaming", "console",
            # Peripherals
            "printer", "scanner", "monitor", "keyboard", "mouse", "webcam", "headset",
            # Software & Apps
            "software", "app", "application", "program", "install", "update",
            "chrome", "edge", "firefox", "browser", "outlook", "teams", "zoom", "slack",
            # Network
            "wifi", "network", "internet", "connection", "vpn", "router", "ethernet",
            # Issues
            "slow", "crash", "error", "freeze", "hang", "not working", "broken",
            "not responding", "blue screen", "bsod", "bug", "issue", "problem",
            # Account
            "login", "password", "account", "access", "locked",
            # Hardware
            "cpu", "memory", "ram", "disk", "storage", "battery", "charging"
        ]
        seems_technical = any(kw in user_message.lower() for kw in tech_keywords)
        
        # Step 2: If technical, search RAG for similar issues
        rag_context = None
        if seems_technical:
            try:
                logger.info(f"[RAG] Searching for similar issues")
                chat_logger.info("RAG SEARCH: Searching knowledge base...")
                
                similar_issues = analyzer.find_similar_issues(
                    description=user_message,
                    category="other",  # Will filter inside
                    limit=3
                )
                
                if similar_issues:
                    logger.info(f"[RAG] Found {len(similar_issues)} similar issues")
                    chat_logger.info(f"RAG: [OK] Found {len(similar_issues)} similar issues from knowledge base")
                    for i, issue in enumerate(similar_issues):
                        chat_logger.info(f"  - Issue {i+1}: {issue['title']} (similarity: {issue['similarity_score']*100:.0f}%)")
                    
                    # Format for LLM
                    rag_context = "\\n\\n".join([
                        f"**Issue {i+1}** (similarity: {issue['similarity_score']*100:.0f}%)\\n"
                        f"Title: {issue['title']}\\n"
                        f"Resolution: {' -> '.join(issue['resolution_steps'])}"
                        for i, issue in enumerate(similar_issues)
                    ])
                else:
                    logger.info("[RAG] No similar issues found")
                    chat_logger.info("RAG: [NO] No similar issues found in knowledge base")
            except Exception as e:
                logger.error(f"[RAG] Error: {e}")
        
        # Step 3: Let LLM handle everything
        response = llm_agent.process_message(
            user_email=user_email,
            user_message=user_message,
            rag_context=rag_context
        )
        
        logger.info(f"[LLM] Response: {response['message'][:100]}...")
        logger.info(f"[LLM] Technical: {response['is_technical']}, Escalate: {response['should_escalate']}, Resolved: {response['is_resolved']}")
        
        # Log full bot response to chat log
        chat_logger.info(f"BOT RESPONSE: {response['message']}")
        chat_logger.info(f"METADATA: Technical={response['is_technical']}, Escalate={response['should_escalate']}, Resolved={response['is_resolved']}, RAG_Used={bool(rag_context)}")
        chat_logger.info("="*80 + "\n")
        
        # Step 4: Intelligent ticket management with dedicated agent
        ticket_id = request.ticket_id
        
        # Get conversation history for ticket intelligence
        conversation_history = llm_agent.conversations.get(user_email, [])
        turn_count = len([m for m in conversation_history if m['role'] == 'user'])
        
        # Use Ticket Intelligence Agent for smart decisions
        if response['is_technical'] and not ticket_id:
            try:
                from app.services.agents.ticket_intelligence_agent import get_ticket_intelligence_agent
                from app.services.ticket_service import TicketService
                from app.models.ticket import TicketCreate, TicketPriority
                
                ticket_agent = get_ticket_intelligence_agent()
                
                # Ask ticket agent: Should we create a ticket NOW?
                create_decision = ticket_agent.should_create_ticket(
                    conversation_history=conversation_history,
                    turn_count=turn_count
                )
                
                chat_logger.info(f"TICKET-AI: Create decision = {create_decision['should_create']} ({create_decision['reason']})")
                
                if create_decision['should_create']:
                    # Generate intelligent ticket metadata
                    metadata = ticket_agent.generate_ticket_metadata(
                        conversation_history=conversation_history,
                        rag_context=rag_context
                    )
                    
                    # Analyze priority intelligently
                    priority_analysis = ticket_agent.analyze_priority(
                        conversation_history=conversation_history,
                        issue_description=metadata['description']
                    )
                    
                    # Map priority string to enum
                    priority_map = {
                        'critical': TicketPriority.CRITICAL,
                        'high': TicketPriority.HIGH,
                        'medium': TicketPriority.MEDIUM,
                        'low': TicketPriority.LOW
                    }
                    priority = priority_map.get(priority_analysis['priority'], TicketPriority.MEDIUM)
                    
                    # Create ticket with intelligent metadata
                    ticket_data = TicketCreate(
                        title=metadata['title'],
                        description=metadata['description'],
                        user_email=user_email,
                        priority=priority
                    )
                    
                    db_ticket = TicketService.create_ticket(db=db, ticket_data=ticket_data)
                    ticket_id = db_ticket.id
                    
                    logger.info(f"[TICKET] Created #{ticket_id}: {metadata['title']}")
                    chat_logger.info(f"TICKET: Created #{ticket_id}")
                    chat_logger.info(f"  Title: {metadata['title']}")
                    chat_logger.info(f"  Priority: {priority.value} (urgency: {priority_analysis['urgency_score']}/10)")
                    chat_logger.info(f"  Reason: {priority_analysis['reason']}")
                    if priority_analysis['urgency_signals']:
                        chat_logger.info(f"  Signals: {', '.join(priority_analysis['urgency_signals'])}")
                
            except Exception as e:
                logger.error(f"[TICKET] Error in intelligent ticket creation: {e}", exc_info=True)
        
        # Intelligent priority updates based on conversation dynamics
        if ticket_id and turn_count >= 4:
            try:
                from app.services.agents.ticket_intelligence_agent import get_ticket_intelligence_agent
                from app.services.ticket_service import TicketService
                from app.models.ticket import TicketUpdate, TicketPriority
                
                ticket_agent = get_ticket_intelligence_agent()
                
                # Get current ticket
                current_ticket = TicketService.get_ticket(db, ticket_id)
                if current_ticket:
                    current_priority = current_ticket.priority.value
                    
                    # Check if priority should be escalated
                    update_decision = ticket_agent.should_update_priority(
                        conversation_history=conversation_history,
                        current_priority=current_priority,
                        turn_count=turn_count
                    )
                    
                    if update_decision['should_update']:
                        priority_map = {
                            'critical': TicketPriority.CRITICAL,
                            'high': TicketPriority.HIGH,
                            'medium': TicketPriority.MEDIUM,
                            'low': TicketPriority.LOW
                        }
                        new_priority = priority_map.get(update_decision['new_priority'], current_ticket.priority)
                        
                        ticket_update = TicketUpdate(
                            priority=new_priority,
                            ai_analysis=f"Priority escalated: {update_decision['reason']}"
                        )
                        TicketService.update_ticket(db, ticket_id, ticket_update)
                        
                        logger.info(f"[TICKET] Priority updated: {current_priority} -> {new_priority.value}")
                        chat_logger.info(f"TICKET: Priority escalated #{ticket_id}: {current_priority} -> {new_priority.value}")
                        chat_logger.info(f"  Reason: {update_decision['reason']}")
                        
            except Exception as e:
                logger.error(f"[TICKET] Error updating priority: {e}", exc_info=True)
        
        # 🆕 SMART ESCALATION: Assign human ONLY when AI cannot resolve
        # This happens when:
        # 1. LLM explicitly says it needs to escalate
        # 2. OR ticket_intelligence_agent detects frustration/repeated issues
        escalation_happened = False  # Track if we escalated to prevent status override
        
        if ticket_id and response['should_escalate']:
            try:
                from app.services.ticket_service import TicketService
                from app.services.assignment_service import get_assignment_service
                from app.models.ticket import TicketUpdate, TicketStatus, TicketPriority
                
                # Get current ticket
                current_ticket = TicketService.get_ticket(db, ticket_id)
                
                if current_ticket and not current_ticket.assigned_to:
                    # NOW assign to human since AI couldn't resolve
                    logger.info(f"[ESCALATION] AI could not resolve ticket #{ticket_id}, assigning to human...")
                    chat_logger.info(f"ESCALATION: AI escalating ticket #{ticket_id} to human support")
                    
                    try:
                        assignment_service = get_assignment_service()
                        assignment_result = assignment_service.assign_ticket(current_ticket, db)
                        logger.info(f"[ESCALATION] Assignment result: {assignment_result}")
                    except Exception as assign_init_err:
                        logger.error(f"[ESCALATION] Assignment service error: {assign_init_err}")
                        assignment_result = None
                    
                    if assignment_result and assignment_result.get('assigned_to'):
                        # Update ticket with assignment and escalation info
                        ticket_update = TicketUpdate(
                            status=TicketStatus.ASSIGNED_TO_HUMAN,
                            priority=TicketPriority.HIGH,
                            ai_analysis=f"AI escalated to human support - {assignment_result.get('reason', 'Could not resolve automatically')}"
                        )
                        TicketService.update_ticket(db, ticket_id, ticket_update)
                        escalation_happened = True  # Mark that we escalated
                        
                        logger.info(f"[ESCALATION] Ticket #{ticket_id} assigned to {assignment_result['assigned_to']}")
                        chat_logger.info(f"  Assigned to: {assignment_result['assigned_to']}")
                        chat_logger.info(f"  Reason: {assignment_result.get('reason', 'N/A')}")
                        chat_logger.info(f"  Confidence: {assignment_result.get('confidence', 0)}")
                        
                        # Add assignment info to response metadata
                        response['metadata']['escalated_to'] = assignment_result['assigned_to']
                        response['metadata']['escalation_reason'] = assignment_result.get('reason', 'AI could not resolve')
                    else:
                        # No agent available - still update status to show escalation pending
                        ticket_update = TicketUpdate(
                            status=TicketStatus.IN_PROGRESS,
                            priority=TicketPriority.HIGH,
                            ai_analysis="Escalated to human support - awaiting agent assignment (no agents currently available)"
                        )
                        TicketService.update_ticket(db, ticket_id, ticket_update)
                        escalation_happened = True  # Still counts as escalation attempt
                        logger.warning(f"[ESCALATION] No agent available for ticket #{ticket_id}")
                        chat_logger.info(f"  WARNING: No agent available for assignment")
                        response['metadata']['escalation_pending'] = True
                        response['metadata']['escalation_reason'] = 'No agents available - ticket queued for assignment'
                else:
                    # Already assigned or no ticket
                    if current_ticket and current_ticket.assigned_to:
                        logger.info(f"[ESCALATION] Ticket #{ticket_id} already assigned to {current_ticket.assigned_to}")
                        escalation_happened = True  # Already escalated
                    
            except Exception as e:
                logger.error(f"[ESCALATION] Error during escalation: {e}", exc_info=True)
        
        # Intelligent status management with TicketStatusAgent
        # Handles: OPEN → IN_PROGRESS → RESOLVED, plus re-open detection
        # IMPORTANT: Skip if escalation already happened to prevent override!
        if ticket_id and not escalation_happened:
            try:
                from app.services.agents.ticket_status_agent import get_ticket_status_agent
                from app.services.ticket_service import TicketService
                from app.models.ticket import TicketUpdate, TicketStatus
                
                status_agent = get_ticket_status_agent()
                
                # Get current ticket
                current_ticket = TicketService.get_ticket(db, ticket_id)
                if current_ticket:
                    current_status = current_ticket.status.value
                    
                    # Skip status analysis if ticket is already assigned to human
                    if current_status == 'assigned_to_human':
                        logger.info(f"[STATUS] Skipping status analysis - ticket #{ticket_id} already assigned to human")
                        chat_logger.info(f"STATUS-AGENT: Skipped - ticket already escalated to human")
                    else:
                        # Analyze conversation to determine appropriate status
                        # Pass should_escalate flag to prevent false resolution detection
                        status_decision = status_agent.analyze_conversation_status(
                            conversation_history=conversation_history,
                            current_status=current_status,
                            ticket_created_at=current_ticket.created_at,
                            llm_resolved_flag=response['is_resolved'] and not response['should_escalate']  # Don't mark resolved if escalating
                        )
                        
                        chat_logger.info(f"STATUS-AGENT: Current={current_status}, Recommended={status_decision['recommended_status']}")
                        chat_logger.info(f"  Should Update: {status_decision['should_update']}")
                        chat_logger.info(f"  Confidence: {status_decision['confidence']}/10")
                        chat_logger.info(f"  Reason: {status_decision['reason']}")
                        
                        # DON'T update to resolved if escalation is needed!
                        if status_decision['should_update'] and not (status_decision['recommended_status'] == 'resolved' and response['should_escalate']):
                            # Map status string to enum
                            status_map = {
                                'open': TicketStatus.OPEN,
                                'in_progress': TicketStatus.IN_PROGRESS,
                                'resolved': TicketStatus.RESOLVED,
                                'closed': TicketStatus.CLOSED
                            }
                            new_status = status_map.get(status_decision['recommended_status'])
                            
                            if new_status and new_status != current_ticket.status:
                                ticket_update = TicketUpdate(
                                    status=new_status,
                                    resolution_notes=status_decision['resolution_summary'] if status_decision['resolution_summary'] else None
                                )
                                TicketService.update_ticket(db, ticket_id, ticket_update)
                                
                                logger.info(f"[STATUS] Ticket #{ticket_id}: {current_status} -> {new_status.value} ({status_decision['reason']})")
                                chat_logger.info(f"TICKET STATUS CHANGED: #{ticket_id}")
                                chat_logger.info(f"  From: {current_status}")
                                chat_logger.info(f"  To: {new_status.value}")
                                chat_logger.info(f"  Transition: {status_decision['transition']}")
                                chat_logger.info(f"  Reason: {status_decision['reason']}")
                        
                        # Check for SLA warning
                        if status_decision['sla_warning']:
                            logger.warning(f"[SLA] Ticket #{ticket_id} approaching SLA breach!")
                            chat_logger.info(f"SLA WARNING: Ticket #{ticket_id} may breach SLA")
                        
                        # Check for escalation needs (user frustration, repeated issues, etc.)
                        # This is ANOTHER trigger for human assignment
                        if status_decision['needs_escalation'] and not current_ticket.assigned_to:
                            logger.warning(f"[ESCALATION] Ticket #{ticket_id} user showing frustration signals - assigning human")
                            chat_logger.info(f"ESCALATION NEEDED: Ticket #{ticket_id} - user frustrated, assigning human")
                            
                            try:
                                from app.services.assignment_service import get_assignment_service
                                
                                assignment_service = get_assignment_service()
                                assignment_result = assignment_service.assign_ticket(current_ticket, db)
                                
                                if assignment_result and assignment_result.get('assigned_to'):
                                    ticket_update = TicketUpdate(
                                        status=TicketStatus.ASSIGNED_TO_HUMAN,
                                        ai_analysis=f"User frustration detected - escalated to {assignment_result['assigned_to']}"
                                    )
                                    TicketService.update_ticket(db, ticket_id, ticket_update)
                                    
                                    chat_logger.info(f"  Assigned to: {assignment_result['assigned_to']}")
                                    response['metadata']['escalated_to'] = assignment_result['assigned_to']
                                    response['metadata']['escalation_reason'] = 'User frustration detected'
                            except Exception as assign_err:
                                logger.error(f"[ESCALATION] Assignment error: {assign_err}")
                        
            except Exception as e:
                logger.error(f"[STATUS] Error in status management: {e}", exc_info=True)
        
        # Step 5: Return response
        return ChatResponse(
            message=response['message'],
            is_technical=response['is_technical'],
            should_escalate=response['should_escalate'],
            is_resolved=response['is_resolved'],
            ticket_id=ticket_id,
            metadata={
                **response['metadata'],
                "rag_found": bool(rag_context),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CHAT] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


class ResetRequest(BaseModel):
    user_email: Optional[str] = None


@router.post("/chat/reset")
async def reset_chat(request: ResetRequest):
    """Reset conversation history for user."""
    try:
        user_email = request.user_email or "anonymous@autoops.ai"
        
        llm_agent = get_llm_conversation_agent()
        llm_agent.reset_conversation(user_email)
        logger.info(f"[CHAT] Conversation reset for {user_email}")
        return {"message": "Conversation reset successfully", "user_email": user_email}
    except Exception as e:
        logger.error(f"[CHAT] Reset error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset conversation")
