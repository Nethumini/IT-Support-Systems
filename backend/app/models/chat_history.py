"""
Chat History models for storing conversation history linked to tickets.

This allows:
1. Viewing past conversations for a ticket
2. Resuming conversations to continue troubleshooting
3. Better context for support team reviewing escalated tickets
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from app.core.database import Base


# SQLAlchemy Model
class ChatMessageDB(Base):
    """Chat message database model."""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True, index=True)
    session_id = Column(String, index=True)  # For grouping messages in a session
    user_email = Column(String, index=True)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    # Image upload info (if applicable)
    has_image = Column(Boolean, default=False)
    image_filename = Column(String, nullable=True)
    image_analysis = Column(Text, nullable=True)  # JSON string of image analysis
    
    # Metadata
    is_technical = Column(Boolean, default=False)
    category = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to ticket (optional - not all messages are linked to tickets)
    # ticket = relationship("TicketDB", back_populates="chat_messages")


# Pydantic Models for API
class ChatMessageBase(BaseModel):
    """Base chat message schema."""
    role: str
    content: str
    has_image: bool = False
    image_filename: Optional[str] = None


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a chat message."""
    session_id: str
    user_email: str
    ticket_id: Optional[int] = None
    is_technical: bool = False
    category: Optional[str] = None
    image_analysis: Optional[str] = None


class ChatMessage(ChatMessageBase):
    """Chat message response schema."""
    id: int
    session_id: str
    user_email: str
    ticket_id: Optional[int] = None
    is_technical: bool = False
    category: Optional[str] = None
    image_analysis: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatSession(BaseModel):
    """Schema for a chat session with multiple messages."""
    session_id: str
    ticket_id: Optional[int] = None
    user_email: str
    messages: List[ChatMessage]
    started_at: datetime
    last_message_at: datetime
    message_count: int
    is_resolved: bool = False


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history of a ticket."""
    ticket_id: int
    sessions: List[ChatSession]
    total_messages: int
