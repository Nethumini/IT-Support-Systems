"""
Enhanced Chat Endpoint - LLM-First Architecture with Intelligent RAG Integration

Flow:
1. User Message → LLM Classifier (is this technical?)
2. If Technical → RAG Search (find similar issues in knowledge base)
3. If RAG Found → LLM + RAG Context (guided response with past solutions)
4. If RAG Not Found → LLM Only (general troubleshooting)
5. Ticket Intelligence Agent (create/update tickets)
6. Ticket Status Agent (manage lifecycle)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import logging

from app.services.agents.llm_conversation_agent import get_llm_conversation_agent
from app.services.dataset_analyzer import DatasetAnalyzer
from app.services.agents.action_executor_agent import get_action_executor
from app.core.database import get_db
from sqlalchemy.orm import Session
import os

logger = logging.getLogger(__name__)

# Setup dedicated chat logger
chat_logger = logging.getLogger('chat_conversation')
if not chat_logger.handlers:
    # Ensure logs directory exists
    log_dir = 'app/logs'
    os.makedirs(log_dir, exist_ok=True)
    chat_handler = logging.FileHandler('app/logs/chat.log')
    chat_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    chat_logger.addHandler(chat_handler)
    chat_logger.setLevel(logging.INFO)

router = APIRouter()


class ChatRequest(BaseModel):
    message: Optional[str] = None
    messages: Optional[list] = None
    ticket_id: Optional[int] = None
    user_email: Optional[str] = None
    session_id: Optional[str] = None  # For tracking conversation sessions
    agent_mode: Optional[bool] = None  # Agent mode toggle


class ChatResponse(BaseModel):
    message: str
    is_technical: bool
    should_escalate: bool
    is_resolved: bool
    ticket_id: Optional[int] = None
    session_id: Optional[str] = None  # Return session ID for frontend tracking
    suggested_actions: Optional[List[Dict]] = None  # Automated remediation actions
    agent_mode: bool = False  # Current agent mode state
    agent_mode_suggestion: Optional[str] = None  # Suggest enabling agent mode
    metadata: dict


class IntentClassification(BaseModel):
    """Result of LLM intent classification."""
    is_technical: bool
    category: str  # hardware, software, network, account, other
    urgency: str   # low, medium, high, critical
    confidence: float
    reasoning: str


def classify_intent_with_llm(
    llm_agent,
    user_message: str,
    conversation_history: List[Dict]
) -> IntentClassification:
    """
    STEP 1: Use LLM to classify if the message is technical.
    This is more accurate than keyword matching.
    """
    # Build context from recent conversation - use more context for resumed chats
    recent_context = ""
    if conversation_history:
        recent_msgs = conversation_history[-8:]  # Last 8 messages for better context
        for msg in recent_msgs:
            role = "User" if msg.get('role') == 'user' else "Bot"
            content = msg.get('content', '')[:500]  # Limit each message length
            recent_context += f"{role}: {content}\n"
    
    classification_prompt = f"""Analyze this IT support conversation and classify the user's intent.

Recent conversation:
{recent_context}

Current user message: "{user_message}"

Classify as JSON:
{{
    "is_technical": true/false,  // Is this about a technical/IT issue?
    "category": "hardware|software|network|account|general|other",
    "urgency": "low|medium|high|critical",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Rules:
- "is_technical" = true for: computers, phones, printers, gaming consoles, software, apps, network issues, login problems
- "is_technical" = false for: greetings, small talk, non-IT questions
- "urgency" = critical if: system down, data loss risk, security issue, deadline mentioned
- "urgency" = high if: blocking work, multiple users affected
- "urgency" = medium if: inconvenience but has workaround
- "urgency" = low if: general question, feature request

Return ONLY the JSON, no other text."""

    try:
        import json
        response = llm_agent.model.generate_content(classification_prompt)
        
        if response and response.text:
            # Parse JSON from response
            text = response.text.strip()
            # Handle markdown code blocks
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            
            result = json.loads(text)
            
            return IntentClassification(
                is_technical=result.get('is_technical', False),
                category=result.get('category', 'other'),
                urgency=result.get('urgency', 'medium'),
                confidence=result.get('confidence', 0.5),
                reasoning=result.get('reasoning', 'Unable to determine')
            )
    except Exception as e:
        logger.warning(f"[CLASSIFIER] LLM classification failed: {e}, using fallback")
    
    # Fallback to keyword-based classification
    return fallback_keyword_classification(user_message)


def fallback_keyword_classification(user_message: str) -> IntentClassification:
    """Fallback keyword-based classification if LLM fails."""
    message_lower = user_message.lower()
    
    # Technical keywords by category
    categories = {
        'hardware': ['computer', 'laptop', 'desktop', 'pc', 'mac', 'phone', 'iphone', 'android',
                    'printer', 'monitor', 'keyboard', 'mouse', 'playstation', 'ps4', 'ps5', 
                    'xbox', 'nintendo', 'console', 'battery', 'charging', 'screen'],
        'software': ['app', 'application', 'software', 'program', 'install', 'update', 
                    'chrome', 'browser', 'outlook', 'teams', 'zoom', 'crash', 'freeze',
                    'developer', 'code', 'web', 'website', 'page', 'changes', 'cache',
                    'docker', 'git', 'visual studio', 'vs code', 'localhost', 'development'],
        'network': ['wifi', 'network', 'internet', 'connection', 'vpn', 'router', 'ethernet', 'slow'],
        'account': ['login', 'password', 'account', 'access', 'locked', 'authentication']
    }
    
    # Issue keywords
    issue_keywords = ['not working', 'broken', 'error', 'problem', 'issue', 'help', 
                     'fix', 'crash', 'freeze', 'slow', 'cant', "can't", 'wont', "won't",
                     'not changing', 'not updating', 'not reflecting', 'not showing']
    
    # Urgency keywords
    urgency_critical = ['urgent', 'emergency', 'critical', 'asap', 'down', 'security']
    urgency_high = ['meeting', 'deadline', 'important', 'blocking', 'cant work']
    
    # Detect category
    detected_category = 'other'
    for cat, keywords in categories.items():
        if any(kw in message_lower for kw in keywords):
            detected_category = cat
            break
    
    # Detect if technical
    has_issue = any(kw in message_lower for kw in issue_keywords)
    has_category = detected_category != 'other'
    is_technical = has_issue or has_category
    
    # Detect urgency
    urgency = 'medium'
    if any(kw in message_lower for kw in urgency_critical):
        urgency = 'critical'
    elif any(kw in message_lower for kw in urgency_high):
        urgency = 'high'
    elif not is_technical:
        urgency = 'low'
    
    return IntentClassification(
        is_technical=is_technical,
        category=detected_category,
        urgency=urgency,
        confidence=0.7 if is_technical else 0.5,
        reasoning="Keyword-based classification (fallback)"
    )


def search_rag_knowledge_base(
    analyzer: DatasetAnalyzer,
    user_message: str,
    category: str
) -> Optional[str]:
    """
    STEP 2: Search RAG knowledge base for similar issues.
    Returns formatted context for LLM if matches found.
    """
    try:
        similar_issues = analyzer.find_similar_issues(
            description=user_message,
            category=category if category != 'other' else None,
            limit=3
        )
        
        if not similar_issues:
            return None
        
        # Filter by minimum similarity threshold
        relevant_issues = [
            issue for issue in similar_issues 
            if issue.get('similarity_score', 0) >= 0.5  # 50% minimum
        ]
        
        if not relevant_issues:
            return None
        
        # Format for LLM
        rag_context = "\n\n".join([
            f"**Similar Issue {i+1}** (Match: {issue['similarity_score']*100:.0f}%)\n"
            f"Problem: {issue['title']}\n"
            f"Solution: {' -> '.join(issue['resolution_steps'])}"
            for i, issue in enumerate(relevant_issues)
        ])
        
        return rag_context
        
    except Exception as e:
        logger.error(f"[RAG] Search error: {e}")
        return None


@router.post("/chat", response_model=ChatResponse)
async def chat_enhanced(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Enhanced LLM-First Chat Endpoint.
    
    Flow:
    1. LLM classifies intent (technical vs general)
    2. If technical → Search RAG
    3. LLM generates response (with or without RAG context)
    4. Ticket agents manage tickets
    5. Save chat messages to database for history
    """
    try:
        from app.services.chat_history_service import ChatHistoryService
        
        # Get user email
        user_email = request.user_email or "anonymous@autoops.ai"
        
        # Get or create session ID
        session_id = request.session_id
        if not session_id:
            session_id = ChatHistoryService.generate_session_id()
        
        # Extract message
        if request.message:
            user_message = request.message.strip()
        elif request.messages and len(request.messages) > 0:
            last_msg = request.messages[-1]
            user_message = last_msg.get('content', '').strip() if isinstance(last_msg, dict) else str(last_msg).strip()
        else:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        logger.info(f"[CHAT] User: {user_email} | Session: {session_id[:8]} | Message: {user_message[:100]}")
        chat_logger.info("=" * 80)
        chat_logger.info(f"USER: {user_email}")
        chat_logger.info(f"SESSION: {session_id[:8]}")
        chat_logger.info(f"MESSAGE: {user_message}")
        
        # Initialize services
        llm_agent = get_llm_conversation_agent()
        analyzer = DatasetAnalyzer()
        
        # Track which ticket's conversation is in memory to prevent cross-contamination
        current_ticket_id = request.ticket_id
        stored_ticket_key = f"{user_email}_ticket"
        stored_ticket_id = getattr(llm_agent, 'current_tickets', {}).get(user_email)
        
        # Initialize ticket tracking dict if needed
        if not hasattr(llm_agent, 'current_tickets'):
            llm_agent.current_tickets = {}
        
        # CRITICAL FIX: Detect ticket context switch
        # If frontend sent history (resumed chat) OR ticket ID changed, use frontend's history
        is_resumed_chat = request.messages and len(request.messages) > 1
        is_ticket_switch = current_ticket_id and stored_ticket_id and current_ticket_id != stored_ticket_id
        
        if is_ticket_switch:
            chat_logger.info(f"TICKET SWITCH DETECTED: {stored_ticket_id} -> {current_ticket_id} - Clearing old context")
            llm_agent.conversations[user_email] = []
        
        # Get conversation history
        conversation_history = llm_agent.conversations.get(user_email, [])
        
        # If this is a resumed chat (frontend sent previous messages), ALWAYS use frontend history
        # This ensures we use the correct ticket's conversation, not a stale one
        if is_resumed_chat:
            # Convert frontend messages to backend format and restore to memory
            frontend_history = []
            for msg in request.messages[:-1]:  # All except the current message
                if isinstance(msg, dict):
                    frontend_history.append({
                        'role': msg.get('role', 'user'),
                        'content': msg.get('content', '')
                    })
            
            if frontend_history:
                conversation_history = frontend_history
                # Replace in-memory history with frontend's history
                llm_agent.conversations[user_email] = frontend_history
                chat_logger.info(f"HISTORY RESTORED: Loaded {len(frontend_history)} messages from frontend for ticket #{current_ticket_id}")
        
        # Update which ticket we're working on
        if current_ticket_id:
            llm_agent.current_tickets[user_email] = current_ticket_id
        
        chat_logger.info(f"CONVERSATION HISTORY: {len(conversation_history)} messages in context (ticket #{current_ticket_id})")
        
        # ═══════════════════════════════════════════════════════════════════
        # AGENT MODE MANAGEMENT - Track mode per session
        # ═══════════════════════════════════════════════════════════════════
        # Initialize agent mode tracking
        if not hasattr(llm_agent, 'agent_modes'):
            llm_agent.agent_modes = {}  # {session_id: bool}
        
        # Get current agent mode from request or session state
        current_agent_mode = llm_agent.agent_modes.get(session_id, False)
        
        # Update agent mode if explicitly toggled by user
        if request.agent_mode is not None:
            current_agent_mode = request.agent_mode
            llm_agent.agent_modes[session_id] = current_agent_mode
            chat_logger.info(f"AGENT MODE: {'ENABLED' if current_agent_mode else 'DISABLED'} by user")
        
        # Check if user is asking to auto-enable agent mode
        auto_enable_triggers = ['can you fix', 'fix it', 'run diagnostic', 'check my system', 'help me fix']
        if not current_agent_mode and any(trigger in user_message.lower() for trigger in auto_enable_triggers):
            current_agent_mode = True
            llm_agent.agent_modes[session_id] = True
            chat_logger.info(f"AGENT MODE: AUTO-ENABLED by user request")
        
        chat_logger.info(f"AGENT MODE STATE: {'ON (Actions Enabled)' if current_agent_mode else 'OFF (Advice Only)'}")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 1: LLM CLASSIFIER - Determine if technical
        # ═══════════════════════════════════════════════════════════════════
        intent = classify_intent_with_llm(llm_agent, user_message, conversation_history)
        
        chat_logger.info(f"CLASSIFIER: Technical={intent.is_technical}, Category={intent.category}, Urgency={intent.urgency}")
        chat_logger.info(f"  Confidence: {intent.confidence:.0%}")
        chat_logger.info(f"  Reasoning: {intent.reasoning}")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 2: RAG SEARCH - Find similar issues (if technical)
        # ═══════════════════════════════════════════════════════════════════
        rag_context = None
        rag_found = False
        
        if intent.is_technical:
            chat_logger.info("RAG SEARCH: Searching knowledge base...")
            rag_context = search_rag_knowledge_base(analyzer, user_message, intent.category)
            
            if rag_context:
                rag_found = True
                chat_logger.info("RAG: [FOUND] Similar issues in knowledge base")
                chat_logger.info(f"  Context preview: {rag_context[:200]}...")
            else:
                chat_logger.info("RAG: [NOT FOUND] No similar issues - LLM will troubleshoot from scratch")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 3: LLM RESPONSE - Generate response (with or without RAG)
        # ═══════════════════════════════════════════════════════════════════
        response = llm_agent.process_message(
            user_email=user_email,
            user_message=user_message,
            rag_context=rag_context
        )
        
        # Override is_technical with our classifier result (more accurate)
        response['is_technical'] = intent.is_technical
        
        chat_logger.info(f"LLM RESPONSE: {response['message'][:200]}...")
        chat_logger.info(f"METADATA: Technical={response['is_technical']}, RAG_Used={rag_found}, Escalate={response['should_escalate']}, Resolved={response['is_resolved']}")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 4: TICKET INTELLIGENCE - Create/update tickets
        # ═══════════════════════════════════════════════════════════════════
        ticket_id = request.ticket_id
        
        # Count REAL user turns (exclude SYSTEM interpretation messages)
        # SYSTEM messages start with "[SYSTEM:" and are auto-generated for action result interpretation
        real_user_messages = [
            m for m in conversation_history 
            if m.get('role') == 'user' and not m.get('content', '').startswith('[SYSTEM:')
        ]
        turn_count = len(real_user_messages)
        
        # Also force ticket creation if user explicitly says issue persists after troubleshooting
        # This handles cases like "still slow", "still not working", etc.
        persistence_keywords = ['still slow', 'still not', 'still having', 'not working', 'didnt work', "didn't work", 'not fixed', 'same problem', 'same issue']
        user_says_issue_persists = any(kw in user_message.lower() for kw in persistence_keywords)
        if user_says_issue_persists and intent.is_technical:
            turn_count = max(turn_count, 3)  # Force ticket creation threshold
        
        # Create ticket for technical issues
        if intent.is_technical and not ticket_id:
            ticket_id = await _handle_ticket_creation(
                db, user_email, conversation_history, rag_context, 
                intent, turn_count, chat_logger
            )
        
        # Update priority if needed
        if ticket_id and turn_count >= 4:
            await _handle_priority_update(
                db, ticket_id, conversation_history, turn_count, chat_logger
            )
        
        # Handle escalation
        if ticket_id and response['should_escalate']:
            await _handle_escalation(db, ticket_id, chat_logger)
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 5: TICKET STATUS - Manage lifecycle
        # ═══════════════════════════════════════════════════════════════════
        if ticket_id:
            await _handle_status_management(
                db, ticket_id, conversation_history, 
                response['is_resolved'], chat_logger
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 6: SAVE CHAT HISTORY - Persist messages to database
        # ═══════════════════════════════════════════════════════════════════
        try:
            # Save user message
            ChatHistoryService.save_message(
                db=db,
                session_id=session_id,
                user_email=user_email,
                role='user',
                content=user_message,
                ticket_id=ticket_id,
                is_technical=intent.is_technical,
                category=intent.category
            )
            
            # Save assistant response
            ChatHistoryService.save_message(
                db=db,
                session_id=session_id,
                user_email=user_email,
                role='assistant',
                content=response['message'],
                ticket_id=ticket_id,
                is_technical=intent.is_technical,
                category=intent.category
            )
            
            # Link session to ticket if not already linked
            if ticket_id:
                ChatHistoryService.link_session_to_ticket(db, session_id, ticket_id)
                
        except Exception as e:
            logger.warning(f"[CHAT-HISTORY] Failed to save messages: {e}")
            # Don't fail the request if history save fails
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 7: SUGGEST AUTOMATED ACTIONS - Only in Agent Mode
        # ═══════════════════════════════════════════════════════════════════
        suggested_actions = None
        troubleshooting_step = 1
        remaining_actions = []
        agent_mode_suggestion = None
        
        # Try to get actions for ANY message that might be technical (even if classifier is unsure)
        # This handles cases where fallback classifier misses developer/technical terms
        should_suggest_actions = (intent.is_technical and not response['is_resolved']) or \
                                any(word in user_message.lower() for word in ['developer', 'code', 'cache', 'not changing', 'not updating', 'not reflecting'])
        
        # AGENT MODE CHECK: Only suggest actions if agent mode is enabled
        if should_suggest_actions and current_agent_mode:
            try:
                action_executor = get_action_executor()
                # Build rich issue context from conversation
                issue_context = user_message
                if conversation_history:
                    # Include both user messages AND assistant responses for context
                    # This helps understand what was already tried/suggested
                    context_parts = []
                    for msg in conversation_history[-6:]:  # Last 6 messages (3 exchanges)
                        role = msg.get('role', 'user')
                        content = msg.get('content', '')
                        if content and not content.startswith('[SYSTEM:'):
                            if role == 'user':
                                context_parts.append(f"User: {content}")
                            else:
                                # Include key parts of assistant response (troubleshooting steps mentioned)
                                context_parts.append(f"Assistant suggested: {content[:200]}")
                    context_parts.append(f"User: {user_message}")
                    issue_context = '\n'.join(context_parts)
                
                # INTELLIGENT ACTION SUGGESTION:
                # Use LLM to understand the issue and suggest the RIGHT actions
                # Not just predefined patterns - truly think about what's needed
                
                chat_logger.info("Using LLM-based intelligent action suggestion")
                all_actions = await action_executor.get_llm_intelligent_actions(
                    issue_description=user_message,
                    conversation_context=issue_context,
                    category=intent.category,
                    urgency=intent.urgency,
                    user_email=user_email
                )
                
                if all_actions:
                    # Step-by-step: Only return the FIRST action
                    # Store remaining actions for follow-up
                    suggested_actions = [all_actions[0]]  # Only first action
                    remaining_actions = all_actions[1:] if len(all_actions) > 1 else []
                    troubleshooting_step = 1
                    
                    chat_logger.info(f"ACTIONS SUGGESTED: Step 1 of {len(all_actions)}")
                    chat_logger.info(f"  - {all_actions[0].get('name')} ({all_actions[0].get('risk_level')})")
                    if remaining_actions:
                        chat_logger.info(f"  Remaining steps: {[a.get('name') for a in remaining_actions]}")
            except Exception as e:
                logger.warning(f"[ACTIONS] Failed to get suggestions: {e}")
                # Don't fail the request if action suggestion fails
        
        # If should suggest actions but agent mode is OFF, suggest enabling it
        elif should_suggest_actions and not current_agent_mode:
            agent_mode_suggestion = "💡 Tip: Enable Agent Mode to get automated troubleshooting actions"
            chat_logger.info("AGENT MODE SUGGESTION: User has technical issue but agent mode is disabled")
        
        chat_logger.info("=" * 80 + "\n")
        
        # Return response
        return ChatResponse(
            message=response['message'],
            is_technical=intent.is_technical,
            should_escalate=response['should_escalate'],
            is_resolved=response['is_resolved'],
            ticket_id=ticket_id,
            session_id=session_id,
            suggested_actions=suggested_actions,
            agent_mode=current_agent_mode,
            agent_mode_suggestion=agent_mode_suggestion,
            metadata={
                **response.get('metadata', {}),
                "category": intent.category,
                "urgency": intent.urgency,
                "rag_found": rag_found,
                "classifier_confidence": intent.confidence,
                "timestamp": datetime.utcnow().isoformat(),
                # Step-by-step troubleshooting info
                "troubleshooting_step": troubleshooting_step if suggested_actions else None,
                "total_steps": len(suggested_actions or []) + len(remaining_actions),
                "remaining_actions": remaining_actions,  # For follow-up steps
                # Agent mode state
                "agent_mode_active": current_agent_mode
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CHAT] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS - Ticket Management
# ═══════════════════════════════════════════════════════════════════════════

async def _handle_ticket_creation(
    db, user_email, conversation_history, rag_context, 
    intent, turn_count, chat_logger
) -> Optional[int]:
    """Handle intelligent ticket creation."""
    try:
        from app.services.agents.ticket_intelligence_agent import get_ticket_intelligence_agent
        from app.services.ticket_service import TicketService
        from app.models.ticket import TicketCreate, TicketPriority
        
        ticket_agent = get_ticket_intelligence_agent()
        
        # Pass the LLM classification result to the ticket agent
        # This ensures tickets are created for technical issues even when
        # user's messages are short like "yes", "okay", "still no"
        create_decision = ticket_agent.should_create_ticket(
            conversation_history=conversation_history,
            turn_count=turn_count,
            is_technical_from_llm=intent.is_technical  # Trust LLM classification!
        )
        
        chat_logger.info(f"TICKET-AI: Create={create_decision['should_create']} ({create_decision['reason']})")
        
        if not create_decision['should_create']:
            return None
        
        # Generate metadata
        metadata = ticket_agent.generate_ticket_metadata(
            conversation_history=conversation_history,
            rag_context=rag_context
        )
        
        # Use classifier urgency to set priority
        priority_map = {
            'critical': TicketPriority.CRITICAL,
            'high': TicketPriority.HIGH,
            'medium': TicketPriority.MEDIUM,
            'low': TicketPriority.LOW
        }
        priority = priority_map.get(intent.urgency, TicketPriority.MEDIUM)
        
        # Map LLM category to TicketCategory enum
        from app.models.ticket import TicketCategory
        category_map = {
            'hardware': TicketCategory.HARDWARE,
            'software': TicketCategory.SOFTWARE,
            'network': TicketCategory.NETWORK,
            'account': TicketCategory.ACCOUNT,
            'other': TicketCategory.OTHER
        }
        category = category_map.get(intent.category.lower(), TicketCategory.OTHER)
        
        # Create ticket
        ticket_data = TicketCreate(
            title=metadata['title'],
            description=metadata['description'],
            user_email=user_email,
            priority=priority,
            category=category  # 🆕 Pass category for smart assignment
        )
        
        result = TicketService.create_ticket(db=db, ticket_data=ticket_data)
        db_ticket = result.get("ticket")
        assignment = result.get("assignment")
        
        chat_logger.info(f"TICKET CREATED: #{db_ticket.id}")
        chat_logger.info(f"  Title: {metadata['title']}")
        chat_logger.info(f"  Category: {category.value}")
        chat_logger.info(f"  Priority: {priority.value}")
        if assignment and assignment.get('assigned_to'):
            chat_logger.info(f"  Assigned to: {assignment['assigned_to']} ({assignment.get('reason', 'N/A')})")
        
        return db_ticket.id
        
    except Exception as e:
        logger.error(f"[TICKET] Creation error: {e}", exc_info=True)
        return None


async def _handle_priority_update(
    db, ticket_id, conversation_history, turn_count, chat_logger
):
    """Handle priority updates based on conversation."""
    try:
        from app.services.agents.ticket_intelligence_agent import get_ticket_intelligence_agent
        from app.services.ticket_service import TicketService
        from app.models.ticket import TicketUpdate, TicketPriority
        
        ticket_agent = get_ticket_intelligence_agent()
        current_ticket = TicketService.get_ticket(db, ticket_id)
        
        if not current_ticket:
            return
        
        update_decision = ticket_agent.should_update_priority(
            conversation_history=conversation_history,
            current_priority=current_ticket.priority.value,
            turn_count=turn_count
        )
        
        if update_decision['should_update']:
            priority_map = {
                'critical': TicketPriority.CRITICAL,
                'high': TicketPriority.HIGH,
                'medium': TicketPriority.MEDIUM,
                'low': TicketPriority.LOW
            }
            new_priority = priority_map.get(update_decision['new_priority'])
            
            if new_priority:
                ticket_update = TicketUpdate(
                    priority=new_priority,
                    ai_analysis=f"Priority escalated: {update_decision['reason']}"
                )
                TicketService.update_ticket(db, ticket_id, ticket_update)
                
                chat_logger.info(f"PRIORITY ESCALATED: #{ticket_id}")
                chat_logger.info(f"  {current_ticket.priority.value} -> {new_priority.value}")
                chat_logger.info(f"  Reason: {update_decision['reason']}")
                
    except Exception as e:
        logger.error(f"[TICKET] Priority update error: {e}", exc_info=True)


async def _handle_escalation(db, ticket_id, chat_logger):
    """Handle escalation to human support - assigns ticket to available agent."""
    try:
        from app.services.ticket_service import TicketService
        from app.services.assignment_service import get_assignment_service
        from app.models.ticket import TicketUpdate, TicketStatus, TicketPriority
        
        # Get current ticket
        current_ticket = TicketService.get_ticket(db, ticket_id)
        
        if not current_ticket:
            logger.warning(f"[ESCALATION] Ticket #{ticket_id} not found")
            return
        
        # Check if already assigned
        if current_ticket.assigned_to:
            logger.info(f"[ESCALATION] Ticket #{ticket_id} already assigned to {current_ticket.assigned_to}")
            chat_logger.info(f"ESCALATION: Ticket already assigned to {current_ticket.assigned_to}")
            return
        
        # NOW assign to human since AI couldn't resolve
        logger.info(f"[ESCALATION] Assigning ticket #{ticket_id} to human support...")
        chat_logger.info(f"ESCALATION: Assigning ticket #{ticket_id} to human support")
        
        try:
            assignment_service = get_assignment_service()
            assignment_result = assignment_service.assign_ticket(current_ticket, db)
            logger.info(f"[ESCALATION] Assignment result: {assignment_result}")
        except Exception as assign_err:
            logger.error(f"[ESCALATION] Assignment service error: {assign_err}")
            assignment_result = None
        
        if assignment_result and assignment_result.get('assigned_to'):
            # Update ticket with assignment
            ticket_update = TicketUpdate(
                status=TicketStatus.ASSIGNED_TO_HUMAN,
                priority=TicketPriority.HIGH,
                ai_analysis=f"AI escalated to human support - Assigned to {assignment_result['assigned_to']} ({assignment_result.get('reason', 'N/A')})"
            )
            TicketService.update_ticket(db, ticket_id, ticket_update)
            
            logger.info(f"[ESCALATION] Ticket #{ticket_id} assigned to {assignment_result['assigned_to']}")
            chat_logger.info(f"ESCALATED TO HUMAN: #{ticket_id}")
            chat_logger.info(f"  Assigned to: {assignment_result['assigned_to']}")
            chat_logger.info(f"  Reason: {assignment_result.get('reason', 'N/A')}")
            chat_logger.info(f"  Confidence: {assignment_result.get('confidence', 0)}")
        else:
            # No agent available - update status but log warning
            ticket_update = TicketUpdate(
                status=TicketStatus.IN_PROGRESS,
                priority=TicketPriority.HIGH,
                ai_analysis="Escalated to human support - awaiting agent assignment (no agents currently available)"
            )
            TicketService.update_ticket(db, ticket_id, ticket_update)
            
            logger.warning(f"[ESCALATION] No agent available for ticket #{ticket_id}")
            chat_logger.info(f"ESCALATED TO HUMAN: #{ticket_id}")
            chat_logger.info(f"  WARNING: No support agents available - ticket queued for manual assignment")
        
    except Exception as e:
        logger.error(f"[ESCALATION] Error: {e}", exc_info=True)


async def _handle_status_management(
    db, ticket_id, conversation_history, is_resolved, chat_logger
):
    """Handle ticket status lifecycle."""
    try:
        from app.services.agents.ticket_status_agent import get_ticket_status_agent
        from app.services.ticket_service import TicketService
        from app.models.ticket import TicketUpdate, TicketStatus
        
        status_agent = get_ticket_status_agent()
        current_ticket = TicketService.get_ticket(db, ticket_id)
        
        if not current_ticket:
            return
        
        status_decision = status_agent.analyze_conversation_status(
            conversation_history=conversation_history,
            current_status=current_ticket.status.value,
            ticket_created_at=current_ticket.created_at,
            llm_resolved_flag=is_resolved
        )
        
        chat_logger.info(f"STATUS-AGENT: {current_ticket.status.value} -> {status_decision['recommended_status']}")
        chat_logger.info(f"  Should Update: {status_decision['should_update']}, Confidence: {status_decision['confidence']}/10")
        
        if status_decision['should_update']:
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
                    resolution_notes=status_decision.get('resolution_summary')
                )
                TicketService.update_ticket(db, ticket_id, ticket_update)
                
                chat_logger.info(f"STATUS CHANGED: #{ticket_id}")
                chat_logger.info(f"  {current_ticket.status.value} -> {new_status.value}")
                chat_logger.info(f"  Reason: {status_decision['reason']}")
        
        if status_decision.get('sla_warning'):
            chat_logger.info(f"SLA WARNING: #{ticket_id} approaching breach!")
            
    except Exception as e:
        logger.error(f"[STATUS] Management error: {e}", exc_info=True)


class ResetRequest(BaseModel):
    user_email: Optional[str] = None


@router.post("/chat/reset")
async def reset_chat(request: ResetRequest):
    """Reset conversation history for user - starts a new session."""
    try:
        from app.services.chat_history_service import ChatHistoryService
        
        user_email = request.user_email or "anonymous@autoops.ai"
        
        # Reset in-memory conversation
        llm_agent = get_llm_conversation_agent()
        llm_agent.reset_conversation(user_email)
        
        # Generate new session ID for frontend
        new_session_id = ChatHistoryService.generate_session_id()
        
        logger.info(f"[CHAT] Conversation reset for {user_email}, new session: {new_session_id[:8]}")
        return {
            "message": "Conversation reset successfully", 
            "user_email": user_email,
            "session_id": new_session_id
        }
    except Exception as e:
        logger.error(f"[CHAT] Reset error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset conversation")


# ═══════════════════════════════════════════════════════════════════════════
# CHAT HISTORY ENDPOINTS - View and resume conversations
# ═══════════════════════════════════════════════════════════════════════════

from app.models.chat_history import ChatHistoryResponse


@router.get("/chat/history/{ticket_id}", response_model=ChatHistoryResponse)
async def get_ticket_chat_history(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all chat history for a ticket.
    Returns all sessions and messages linked to this ticket.
    """
    try:
        from app.services.chat_history_service import ChatHistoryService
        return ChatHistoryService.get_ticket_chat_history(db, ticket_id)
    except Exception as e:
        logger.error(f"[CHAT-HISTORY] Error getting history for ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")


@router.get("/chat/sessions/{user_email}")
async def get_user_sessions(
    user_email: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent chat sessions for a user.
    Useful for showing conversation history on the frontend.
    """
    try:
        from app.services.chat_history_service import ChatHistoryService
        sessions = ChatHistoryService.get_user_recent_sessions(db, user_email, limit)
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        logger.error(f"[CHAT-HISTORY] Error getting sessions for {user_email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sessions")


@router.post("/chat/resume/{session_id}")
async def resume_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Resume a previous chat session.
    Loads conversation history from database into LLM context.
    """
    try:
        from app.services.chat_history_service import ChatHistoryService
        
        # Get session messages from database
        messages = ChatHistoryService.get_session_messages(db, session_id)
        
        if not messages:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Load into LLM agent
        llm_agent = get_llm_conversation_agent()
        user_email = messages[0].user_email
        ticket_id = messages[0].ticket_id
        
        # Clear existing conversation and reload from database
        llm_agent.reset_conversation(user_email)
        
        for msg in messages:
            llm_agent.add_message(user_email, msg.role, msg.content)
        
        logger.info(f"[CHAT] Resumed session {session_id[:8]} for {user_email} with {len(messages)} messages")
        
        return {
            "message": "Session resumed successfully",
            "session_id": session_id,
            "ticket_id": ticket_id,
            "message_count": len(messages),
            "user_email": user_email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CHAT] Error resuming session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to resume session")


# ═══════════════════════════════════════════════════════════════════════════
# IMAGE UPLOAD ENDPOINT - Analyze images and continue with chat flow
# ═══════════════════════════════════════════════════════════════════════════

from fastapi import File, UploadFile, Form


class ImageChatResponse(BaseModel):
    """Response for image-based chat."""
    message: str
    is_technical: bool
    should_escalate: bool
    is_resolved: bool
    ticket_id: Optional[int] = None
    session_id: Optional[str] = None
    image_analysis: Optional[dict] = None  # Contains extracted info from image
    metadata: Optional[dict] = None


@router.post("/chat/image", response_model=ImageChatResponse)
async def chat_with_image(
    image: UploadFile = File(...),
    message: Optional[str] = Form(None),
    user_email: Optional[str] = Form(None),
    ticket_id: Optional[int] = Form(None),
    session_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Chat endpoint with image upload support.
    
    Flow:
    1. Analyze uploaded image with Gemini Vision
    2. Combine image analysis + user message
    3. Continue with normal chat flow (classification → RAG → response → ticket)
    
    Args:
        image: Uploaded image file (PNG, JPG, WEBP, GIF)
        message: Optional user message/context
        user_email: User identifier
        ticket_id: Existing ticket ID (if continuing conversation)
        session_id: Session ID for tracking conversation
    """
    try:
        from app.services.agents.image_analysis_agent import get_image_analysis_agent
        from app.services.chat_history_service import ChatHistoryService
        
        user_email = user_email or "anonymous@autoops.ai"
        user_message = message.strip() if message else ""
        
        # Get or create session ID
        if not session_id:
            session_id = ChatHistoryService.generate_session_id()
        
        logger.info(f"[CHAT-IMAGE] User: {user_email} | Session: {session_id[:8]} | Image: {image.filename}")
        chat_logger.info("=" * 80)
        chat_logger.info(f"USER: {user_email}")
        chat_logger.info(f"SESSION: {session_id[:8]}")
        chat_logger.info(f"IMAGE: {image.filename} ({image.content_type})")
        if user_message:
            chat_logger.info(f"MESSAGE: {user_message}")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 1: ANALYZE IMAGE with Gemini Vision
        # ═══════════════════════════════════════════════════════════════════
        image_agent = get_image_analysis_agent()
        
        # Read image data
        image_data = await image.read()
        mime_type = image.content_type or "image/jpeg"
        
        # Analyze the image
        analysis = image_agent.analyze_image(
            image_data=image_data,
            mime_type=mime_type,
            user_context=user_message if user_message else None
        )
        
        chat_logger.info(f"IMAGE ANALYSIS: {analysis.get('issue_description', 'N/A')[:200]}")
        chat_logger.info(f"  Category: {analysis.get('category', 'unknown')}")
        chat_logger.info(f"  Extracted Text: {analysis.get('extracted_text', 'N/A')[:100]}")
        chat_logger.info(f"  Keywords: {analysis.get('suggested_keywords', [])}")
        
        if not analysis.get('success', False):
            # Image analysis failed - still try to help
            chat_logger.warning(f"IMAGE ANALYSIS FAILED: {analysis.get('error', 'Unknown error')}")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 2: BUILD COMBINED MESSAGE for chat flow
        # ═══════════════════════════════════════════════════════════════════
        
        # Combine user message with image analysis for the chat flow
        combined_message = _build_combined_message(user_message, analysis)
        
        chat_logger.info(f"COMBINED MESSAGE: {combined_message[:200]}")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 3: CONTINUE WITH NORMAL CHAT FLOW
        # ═══════════════════════════════════════════════════════════════════
        
        # Initialize services
        llm_agent = get_llm_conversation_agent()
        analyzer = DatasetAnalyzer()
        
        # Get conversation history
        conversation_history = llm_agent.conversations.get(user_email, [])
        
        # Classify intent (image issues are usually technical)
        intent = classify_intent_with_llm(llm_agent, combined_message, conversation_history)
        
        # Override: If image shows error/hardware, force technical
        if analysis.get('category') in ['error', 'hardware', 'software', 'network']:
            intent.is_technical = True
            intent.category = analysis.get('category')
        
        chat_logger.info(f"CLASSIFIER: Technical={intent.is_technical}, Category={intent.category}, Urgency={intent.urgency}")
        
        # RAG search using suggested keywords from image
        rag_context = None
        rag_found = False
        
        if intent.is_technical:
            # Use image keywords + message for RAG search
            search_query = combined_message
            if analysis.get('suggested_keywords'):
                search_query += " " + " ".join(analysis['suggested_keywords'])
            
            chat_logger.info("RAG SEARCH: Searching knowledge base...")
            rag_context = search_rag_knowledge_base(analyzer, search_query, intent.category)
            
            if rag_context:
                rag_found = True
                chat_logger.info("RAG: [FOUND] Similar issues in knowledge base")
            else:
                chat_logger.info("RAG: [NOT FOUND] No similar issues")
        
        # Generate LLM response with image context
        # Add image analysis to the system prompt
        image_context = f"\n\n## Image Analysis:\n{analysis.get('analysis_prompt', '')}\n"
        if analysis.get('extracted_text') and analysis['extracted_text'].lower() != 'n/a':
            image_context += f"\nError/Text from image: {analysis['extracted_text']}\n"
        
        full_rag_context = (rag_context or "") + image_context
        
        response = llm_agent.process_message(
            user_email=user_email,
            user_message=combined_message,
            rag_context=full_rag_context
        )
        
        response['is_technical'] = intent.is_technical
        
        chat_logger.info(f"LLM RESPONSE: {response['message'][:200]}...")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 4: TICKET MANAGEMENT (same as regular chat)
        # ═══════════════════════════════════════════════════════════════════
        current_ticket_id = ticket_id
        # Count REAL user turns (exclude SYSTEM interpretation messages)
        real_user_messages = [
            m for m in conversation_history 
            if m.get('role') == 'user' and not m.get('content', '').startswith('[SYSTEM:')
        ]
        turn_count = len(real_user_messages)
        
        # Create ticket for technical issues (with image context)
        if intent.is_technical and not current_ticket_id:
            current_ticket_id = await _handle_image_ticket_creation(
                db, user_email, conversation_history, rag_context,
                intent, turn_count, analysis, image.filename, chat_logger
            )
        
        # Update priority if needed
        if current_ticket_id and turn_count >= 4:
            await _handle_priority_update(
                db, current_ticket_id, conversation_history, turn_count, chat_logger
            )
        
        # Handle escalation
        if current_ticket_id and response['should_escalate']:
            await _handle_escalation(db, current_ticket_id, chat_logger)
        
        # Status management
        if current_ticket_id:
            await _handle_status_management(
                db, current_ticket_id, conversation_history,
                response['is_resolved'], chat_logger
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 5: SAVE CHAT HISTORY with image info
        # ═══════════════════════════════════════════════════════════════════
        try:
            import json
            
            # Save user message with image
            ChatHistoryService.save_message(
                db=db,
                session_id=session_id,
                user_email=user_email,
                role='user',
                content=user_message or f"[Image uploaded: {image.filename}]",
                ticket_id=current_ticket_id,
                is_technical=intent.is_technical,
                category=intent.category,
                has_image=True,
                image_filename=image.filename,
                image_analysis=analysis
            )
            
            # Save assistant response
            ChatHistoryService.save_message(
                db=db,
                session_id=session_id,
                user_email=user_email,
                role='assistant',
                content=response['message'],
                ticket_id=current_ticket_id,
                is_technical=intent.is_technical,
                category=intent.category
            )
            
            # Link session to ticket
            if current_ticket_id:
                ChatHistoryService.link_session_to_ticket(db, session_id, current_ticket_id)
                
        except Exception as e:
            logger.warning(f"[CHAT-HISTORY] Failed to save image chat: {e}")
        
        chat_logger.info("=" * 80 + "\n")
        
        return ImageChatResponse(
            message=response['message'],
            is_technical=intent.is_technical,
            should_escalate=response['should_escalate'],
            is_resolved=response['is_resolved'],
            ticket_id=current_ticket_id,
            session_id=session_id,
            image_analysis={
                "success": analysis.get('success', False),
                "issue_description": analysis.get('issue_description', ''),
                "extracted_text": analysis.get('extracted_text', ''),
                "category": analysis.get('category', 'other'),
                "detected_elements": analysis.get('detected_elements', []),
                "suggested_keywords": analysis.get('suggested_keywords', [])
            },
            metadata={
                **response.get('metadata', {}),
                "category": intent.category,
                "urgency": intent.urgency,
                "rag_found": rag_found,
                "image_filename": image.filename,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CHAT-IMAGE] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image processing error: {str(e)}")


def _build_combined_message(user_message: str, analysis: Dict) -> str:
    """Build a combined message from user input and image analysis."""
    parts = []
    
    # User's own message first
    if user_message:
        parts.append(user_message)
    
    # Add image analysis
    if analysis.get('issue_description'):
        parts.append(f"[From uploaded image: {analysis['issue_description']}]")
    
    if analysis.get('extracted_text') and analysis['extracted_text'].lower() != 'n/a':
        parts.append(f"[Error text visible: {analysis['extracted_text']}]")
    
    # Default message if nothing else
    if not parts:
        parts.append("I'm having a technical issue. Please see the uploaded image.")
    
    return " ".join(parts)


async def _handle_image_ticket_creation(
    db, user_email, conversation_history, rag_context,
    intent, turn_count, image_analysis, image_filename, chat_logger
) -> Optional[int]:
    """Handle ticket creation for image-based issues."""
    try:
        from app.services.agents.ticket_intelligence_agent import get_ticket_intelligence_agent
        from app.services.ticket_service import TicketService
        from app.models.ticket import TicketCreate, TicketPriority
        
        ticket_agent = get_ticket_intelligence_agent()
        
        # For image uploads, we're more likely to create a ticket
        # since the user took the effort to screenshot/photograph
        create_decision = ticket_agent.should_create_ticket(
            conversation_history=conversation_history,
            turn_count=max(turn_count, 2),  # Treat as if we have more context
            is_technical_from_llm=intent.is_technical
        )
        
        chat_logger.info(f"TICKET-AI: Create={create_decision['should_create']} ({create_decision['reason']})")
        
        if not create_decision['should_create']:
            return None
        
        # Generate ticket metadata with image info
        metadata = ticket_agent.generate_ticket_metadata(
            conversation_history=conversation_history,
            rag_context=rag_context
        )
        
        # Enhance title with image analysis if needed
        if image_analysis.get('issue_description') and len(metadata.get('title', '')) < 20:
            # Use image description for title if generated title is weak
            metadata['title'] = image_analysis['issue_description'][:80]
        
        # Add image info to description
        enhanced_description = metadata.get('description', '')
        enhanced_description += f"\n\n📷 Image uploaded: {image_filename}"
        if image_analysis.get('extracted_text') and image_analysis['extracted_text'].lower() != 'n/a':
            enhanced_description += f"\n📝 Extracted text: {image_analysis['extracted_text']}"
        if image_analysis.get('detected_elements'):
            enhanced_description += f"\n🔍 Detected: {', '.join(image_analysis['detected_elements'])}"
        
        # Priority from intent
        priority_map = {
            'critical': TicketPriority.CRITICAL,
            'high': TicketPriority.HIGH,
            'medium': TicketPriority.MEDIUM,
            'low': TicketPriority.LOW
        }
        
        # Urgency indicators from image can escalate priority
        if image_analysis.get('urgency_indicators'):
            urgency_keywords = ' '.join(image_analysis['urgency_indicators']).lower()
            if any(w in urgency_keywords for w in ['critical', 'crash', 'data loss', 'security']):
                intent.urgency = 'critical'
            elif any(w in urgency_keywords for w in ['error', 'fail', 'broken']):
                intent.urgency = 'high'
        
        priority = priority_map.get(intent.urgency, TicketPriority.MEDIUM)
        
        # Map LLM category to TicketCategory enum
        from app.models.ticket import TicketCategory
        category_map = {
            'hardware': TicketCategory.HARDWARE,
            'software': TicketCategory.SOFTWARE,
            'network': TicketCategory.NETWORK,
            'account': TicketCategory.ACCOUNT,
            'other': TicketCategory.OTHER
        }
        category = category_map.get(intent.category.lower(), TicketCategory.OTHER)
        
        # Create ticket
        ticket_data = TicketCreate(
            title=metadata['title'][:100],
            description=enhanced_description,
            user_email=user_email,
            priority=priority,
            category=category  # 🆕 Pass category for smart assignment
        )
        
        result = TicketService.create_ticket(db=db, ticket_data=ticket_data)
        db_ticket = result.get("ticket")
        assignment = result.get("assignment")
        
        chat_logger.info(f"TICKET CREATED: #{db_ticket.id}")
        chat_logger.info(f"  Title: {metadata['title']}")
        chat_logger.info(f"  Category: {category.value}")
        chat_logger.info(f"  Priority: {priority.value}")
        chat_logger.info(f"  Image: {image_filename}")
        if assignment and assignment.get('assigned_to'):
            chat_logger.info(f"  Assigned to: {assignment['assigned_to']} ({assignment.get('reason', 'N/A')})")
        
        return db_ticket.id
        
    except Exception as e:
        logger.error(f"[TICKET] Image ticket creation error: {e}", exc_info=True)
        return None

