"""
Chat History Service - Manages chat message persistence and retrieval.

This service:
1. Saves chat messages to database
2. Links messages to tickets
3. Retrieves chat history for tickets
4. Manages chat sessions
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.chat_history import ChatMessageDB, ChatMessageCreate, ChatMessage, ChatSession, ChatHistoryResponse

logger = logging.getLogger(__name__)


class ChatHistoryService:
    """Service for managing chat history in database."""
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate a unique session ID."""
        return str(uuid.uuid4())
    
    @staticmethod
    def save_message(
        db: Session,
        session_id: str,
        user_email: str,
        role: str,
        content: str,
        ticket_id: Optional[int] = None,
        is_technical: bool = False,
        category: Optional[str] = None,
        has_image: bool = False,
        image_filename: Optional[str] = None,
        image_analysis: Optional[Dict] = None
    ) -> ChatMessageDB:
        """
        Save a chat message to the database.
        
        Args:
            db: Database session
            session_id: Unique session identifier
            user_email: User's email
            role: 'user' or 'assistant'
            content: Message content
            ticket_id: Associated ticket ID (if any)
            is_technical: Whether the message is technical
            category: Issue category
            has_image: Whether message has an image
            image_filename: Uploaded image filename
            image_analysis: Image analysis result dict
        
        Returns:
            Created ChatMessageDB instance
        """
        try:
            db_message = ChatMessageDB(
                session_id=session_id,
                user_email=user_email,
                role=role,
                content=content,
                ticket_id=ticket_id,
                is_technical=is_technical,
                category=category,
                has_image=has_image,
                image_filename=image_filename,
                image_analysis=json.dumps(image_analysis) if image_analysis else None
            )
            
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
            
            logger.info(f"[CHAT-HISTORY] Saved message: session={session_id[:8]}, role={role}, ticket={ticket_id}")
            return db_message
            
        except Exception as e:
            db.rollback()
            logger.error(f"[CHAT-HISTORY] Failed to save message: {e}")
            raise
    
    @staticmethod
    def link_session_to_ticket(
        db: Session,
        session_id: str,
        ticket_id: int
    ) -> int:
        """
        Link all messages in a session to a ticket.
        
        Args:
            db: Database session
            session_id: Session ID to link
            ticket_id: Ticket ID to link to
        
        Returns:
            Number of messages updated
        """
        try:
            result = db.query(ChatMessageDB).filter(
                ChatMessageDB.session_id == session_id,
                ChatMessageDB.ticket_id.is_(None)
            ).update({ChatMessageDB.ticket_id: ticket_id})
            
            db.commit()
            logger.info(f"[CHAT-HISTORY] Linked {result} messages from session {session_id[:8]} to ticket #{ticket_id}")
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"[CHAT-HISTORY] Failed to link session to ticket: {e}")
            raise
    
    @staticmethod
    def get_ticket_chat_history(
        db: Session,
        ticket_id: int
    ) -> ChatHistoryResponse:
        """
        Get all chat history for a ticket.
        
        Args:
            db: Database session
            ticket_id: Ticket ID
        
        Returns:
            ChatHistoryResponse with all sessions and messages
        """
        try:
            # Get all messages for this ticket
            messages = db.query(ChatMessageDB).filter(
                ChatMessageDB.ticket_id == ticket_id
            ).order_by(ChatMessageDB.created_at).all()
            
            if not messages:
                return ChatHistoryResponse(
                    ticket_id=ticket_id,
                    sessions=[],
                    total_messages=0
                )
            
            # Group by session
            sessions_dict: Dict[str, List[ChatMessageDB]] = {}
            for msg in messages:
                if msg.session_id not in sessions_dict:
                    sessions_dict[msg.session_id] = []
                sessions_dict[msg.session_id].append(msg)
            
            # Build session objects
            sessions = []
            for session_id, session_messages in sessions_dict.items():
                session_messages.sort(key=lambda m: m.created_at)
                
                # Check if resolved (last assistant message mentions resolution)
                is_resolved = False
                for msg in reversed(session_messages):
                    if msg.role == 'assistant':
                        if any(word in msg.content.lower() for word in ['resolved', 'glad to help', 'all set']):
                            is_resolved = True
                        break
                
                sessions.append(ChatSession(
                    session_id=session_id,
                    ticket_id=ticket_id,
                    user_email=session_messages[0].user_email,
                    messages=[ChatMessage(
                        id=m.id,
                        role=m.role,
                        content=m.content,
                        has_image=m.has_image,
                        image_filename=m.image_filename,
                        session_id=m.session_id,
                        user_email=m.user_email,
                        ticket_id=m.ticket_id,
                        is_technical=m.is_technical,
                        category=m.category,
                        image_analysis=m.image_analysis,
                        created_at=m.created_at
                    ) for m in session_messages],
                    started_at=session_messages[0].created_at,
                    last_message_at=session_messages[-1].created_at,
                    message_count=len(session_messages),
                    is_resolved=is_resolved
                ))
            
            # Sort sessions by start time
            sessions.sort(key=lambda s: s.started_at, reverse=True)
            
            return ChatHistoryResponse(
                ticket_id=ticket_id,
                sessions=sessions,
                total_messages=len(messages)
            )
            
        except Exception as e:
            logger.error(f"[CHAT-HISTORY] Failed to get chat history: {e}")
            raise
    
    @staticmethod
    def get_session_messages(
        db: Session,
        session_id: str
    ) -> List[ChatMessageDB]:
        """
        Get all messages for a session.
        
        Args:
            db: Database session
            session_id: Session ID
        
        Returns:
            List of messages in the session
        """
        return db.query(ChatMessageDB).filter(
            ChatMessageDB.session_id == session_id
        ).order_by(ChatMessageDB.created_at).all()
    
    @staticmethod
    def get_user_recent_sessions(
        db: Session,
        user_email: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent chat sessions for a user.
        
        Args:
            db: Database session
            user_email: User's email
            limit: Maximum number of sessions to return
        
        Returns:
            List of session summaries
        """
        # Get distinct session IDs for user, ordered by most recent
        from sqlalchemy import func
        
        sessions = db.query(
            ChatMessageDB.session_id,
            ChatMessageDB.ticket_id,
            func.min(ChatMessageDB.created_at).label('started_at'),
            func.max(ChatMessageDB.created_at).label('last_message_at'),
            func.count(ChatMessageDB.id).label('message_count')
        ).filter(
            ChatMessageDB.user_email == user_email
        ).group_by(
            ChatMessageDB.session_id,
            ChatMessageDB.ticket_id
        ).order_by(
            desc('last_message_at')
        ).limit(limit).all()
        
        result = []
        for s in sessions:
            # Get first user message as preview
            first_msg = db.query(ChatMessageDB).filter(
                ChatMessageDB.session_id == s.session_id,
                ChatMessageDB.role == 'user'
            ).order_by(ChatMessageDB.created_at).first()
            
            result.append({
                'session_id': s.session_id,
                'ticket_id': s.ticket_id,
                'started_at': s.started_at.isoformat() if s.started_at else None,
                'last_message_at': s.last_message_at.isoformat() if s.last_message_at else None,
                'message_count': s.message_count,
                'preview': first_msg.content[:100] if first_msg else None
            })
        
        return result
    
    @staticmethod
    def delete_session(
        db: Session,
        session_id: str
    ) -> int:
        """
        Delete all messages in a session.
        
        Args:
            db: Database session
            session_id: Session ID to delete
        
        Returns:
            Number of messages deleted
        """
        try:
            result = db.query(ChatMessageDB).filter(
                ChatMessageDB.session_id == session_id
            ).delete()
            
            db.commit()
            logger.info(f"[CHAT-HISTORY] Deleted {result} messages from session {session_id[:8]}")
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"[CHAT-HISTORY] Failed to delete session: {e}")
            raise
