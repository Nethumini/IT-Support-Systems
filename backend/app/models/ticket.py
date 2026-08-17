"""
Ticket models for database and API.
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from pydantic import BaseModel
from app.core.database import Base


class TicketStatus(str, Enum):
    """Ticket status enumeration."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ASSIGNED_TO_HUMAN = "assigned_to_human"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    """Ticket priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategory(str, Enum):
    """Ticket category enumeration."""
    HARDWARE = "hardware"  # Physical devices, peripherals, BSOD
    SOFTWARE = "software"  # Applications, OS issues, performance
    NETWORK = "network"  # VPN, connectivity, firewall
    ACCOUNT = "account"  # Login, permissions, password
    USER_ERROR = "user_error"  # User mistakes, training needed
    SYSTEM_ISSUE = "system_issue"  # System-wide problems
    FEATURE_REQUEST = "feature_request"  # Enhancement requests
    OTHER = "other"  # Uncategorized


# SQLAlchemy Model
class TicketDB(Base):
    """Ticket database model."""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN)
    priority = Column(SQLEnum(TicketPriority), default=TicketPriority.MEDIUM)
    category = Column(SQLEnum(TicketCategory), nullable=True)
    user_email = Column(String, index=True)
    assigned_to = Column(String, nullable=True)
    resolution = Column(Text, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    troubleshooting_steps = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


# Pydantic Models
class TicketBase(BaseModel):
    """Base ticket schema."""
    title: str
    description: str
    user_email: Optional[str] = None


class TicketCreate(TicketBase):
    """Schema for creating a ticket."""
    priority: Optional[TicketPriority] = TicketPriority.MEDIUM
    category: Optional[TicketCategory] = TicketCategory.OTHER
    assigned_to: Optional[str] = None


class TicketUpdate(BaseModel):
    """Schema for updating a ticket."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None


class Ticket(TicketBase):
    """Ticket response schema."""
    id: int
    status: TicketStatus
    priority: TicketPriority
    category: Optional[TicketCategory] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    ai_analysis: Optional[str] = None
    troubleshooting_steps: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TicketAnalysis(BaseModel):
    """Schema for AI ticket analysis."""
    category: TicketCategory
    priority: TicketPriority
    analysis: str
    suggested_steps: list[str]
    confidence: float
