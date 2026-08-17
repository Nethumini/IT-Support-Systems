"""
Conversation state management for multi-turn diagnostic conversations.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class ConversationPhase(str, Enum):
    """Phases of the diagnostic conversation."""
    GREETING = "greeting"
    ISSUE_GATHERING = "issue_gathering"
    DIAGNOSTICS = "diagnostics"
    TROUBLESHOOTING = "troubleshooting"
    MONITORING = "monitoring"
    RESOLUTION = "resolution"
    ESCALATION = "escalation"


class UrgencyLevel(str, Enum):
    """User urgency indicators."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConversationContext(BaseModel):
    """Context information gathered during conversation."""
    # Issue details
    issue_description: str = ""
    category: Optional[str] = None
    
    # Temporal context
    time_of_occurrence: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    
    # User context
    has_upcoming_meeting: bool = False
    meeting_time_minutes: Optional[int] = None
    blocking_work: bool = False
    urgency_indicators: List[str] = []
    
    # Diagnostic information
    error_messages: List[str] = []
    steps_already_taken: List[str] = []
    affected_systems: List[str] = []
    
    # Troubleshooting
    attempted_solutions: List[Dict[str, Any]] = []
    current_solution_step: int = 0
    solution_feedback: List[str] = []
    
    # Business impact
    business_impact: Optional[str] = None
    affected_users_count: int = 1
    data_at_risk: bool = False
    
    # Conversation metadata
    questions_asked: List[str] = []
    user_frustration_level: int = 0  # 0-10 scale
    confidence_score: float = 0.0  # 0-1 scale for issue identification
    
    # LLM classifications
    is_technical: bool = False
    message_type: Optional[str] = None  # technical_issue, general_chat, non_it


class ConversationState(BaseModel):
    """Complete state of ongoing conversation."""
    conversation_id: str
    user_email: str
    phase: ConversationPhase = ConversationPhase.GREETING
    context: ConversationContext = ConversationContext()
    
    # Agent Mode Configuration
    agent_mode: bool = False  # When True, can suggest and execute actions
    agent_mode_enabled_at: Optional[datetime] = None
    agent_mode_auto_enabled: bool = False  # True if auto-enabled by user request
    
    # Ticket information
    ticket_id: Optional[int] = None
    ticket_created: bool = False
    
    # State management
    created_at: datetime = datetime.utcnow()
    last_updated: datetime = datetime.utcnow()
    turn_count: int = 0
    
    # Decision tracking
    escalation_reasons: List[str] = []
    should_escalate: bool = False
    resolved: bool = False


class DiagnosticQuestion(BaseModel):
    """Structured diagnostic question."""
    question: str
    question_type: str  # time, frequency, error_details, steps_taken, impact
    expected_info: str
    priority: int = 1  # Lower number = ask first


class TroubleshootingStep(BaseModel):
    """A single troubleshooting step to attempt."""
    step_number: int
    instruction: str
    expected_outcome: str
    success_indicators: List[str]
    failure_indicators: List[str]
    estimated_time: str
    difficulty: str  # easy, medium, hard
    requires_restart: bool = False
