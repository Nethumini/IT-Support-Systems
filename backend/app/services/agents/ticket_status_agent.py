"""
Ticket Status Agent - Manages ticket lifecycle and status transitions.

This agent is responsible for:
1. Resolution Detection - Detect when issues are resolved
2. Status Transitions - OPEN → IN_PROGRESS → RESOLVED → CLOSED
3. Auto-Close - Close tickets after successful resolution confirmation
4. Re-Open Detection - Detect if user reports same issue recurring
5. Abandonment Detection - Detect if conversation was abandoned
6. SLA Tracking - Time-based escalation warnings
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class TicketStatusTransition(str, Enum):
    """Possible ticket status transitions."""
    OPEN_TO_IN_PROGRESS = "open_to_in_progress"
    IN_PROGRESS_TO_RESOLVED = "in_progress_to_resolved"
    RESOLVED_TO_CLOSED = "resolved_to_closed"
    RESOLVED_TO_REOPENED = "resolved_to_reopened"
    ANY_TO_ESCALATED = "any_to_escalated"


class TicketStatusAgent:
    """
    Agent responsible for managing ticket status lifecycle.
    
    Keeps ticket status in sync with conversation state:
    - Detects when troubleshooting starts (OPEN → IN_PROGRESS)
    - Detects resolution signals (IN_PROGRESS → RESOLVED)
    - Handles re-opening if issue recurs (RESOLVED → OPEN)
    - Tracks SLA and escalation timing
    """
    
    def __init__(self):
        """Initialize the Ticket Status Agent."""
        logger.info("Ticket Status Agent initialized")
        
        # Resolution keywords (user confirms issue is fixed)
        self.resolution_positive_keywords = [
            'fixed', 'it is fixed', 'now it is fixed', 'its fixed', "it's fixed",
            'working now', 'works now', 'working again', 'work now',
            'solved', 'resolved', 'perfect', 'great',
            'that worked', 'it worked', 'that did it', 'that helped',
            'thank you', 'thanks', 'thanks it', 'thanks that',
            'working perfectly', 'all good', 'problem solved',
            'good now', 'fine now', 'ok now', 'okay now',
            'no problem now', 'no issues now', 'sorted', 'all set',
            'yes', 'yep', 'yeah', 'yup'  # Confirmation after "is it working?"
        ]
        
        # Keywords indicating issue NOT resolved
        self.resolution_negative_keywords = [
            'still', 'not working', 'same issue', 'same problem',
            'nothing', 'cant', "can't", 'doesnt work', "doesn't work",
            'no', 'nope', 'problem persists', 'still slow', 'still broken',
            'not fixed', 'didnt work', "didn't work", 'failed',
            'worse', 'getting worse', 'not helping'
        ]
        
        # Keywords indicating issue is recurring (for re-open)
        self.reopen_keywords = [
            'same issue again', 'problem is back', 'happening again',
            'same thing', 'not working again', 'broken again',
            'issue returned', 'came back', 'recurring'
        ]
        
        # Keywords indicating troubleshooting has started
        self.in_progress_keywords = [
            'trying', 'let me try', 'okay', 'ok', 'will do',
            'checking', 'looking', 'opening', 'restarting'
        ]
        
        # Keywords indicating user frustration (may need escalation)
        self.frustration_keywords = [
            'frustrated', 'annoyed', 'angry', 'ridiculous',
            'waste of time', 'useless', 'terrible', 'awful',
            'nothing works', 'give up', 'escalate', 'manager',
            'human', 'real person', 'speak to someone',
            # Urgency signals
            'no time', 'have no time', 'urgent', 'emergency', 'asap',
            'meeting in', 'afraid', 'worried', 'cant wait', "can't wait",
            'please listen', 'please help', 'need help now',
            # User giving up on self-service
            'assign a human', 'talk to human', 'need human',
            'i cant', "i can't", 'not able to', 'unable to'
        ]
    
    def analyze_conversation_status(
        self,
        conversation_history: List[Dict],
        current_status: str,
        ticket_created_at: Optional[datetime] = None,
        llm_resolved_flag: bool = False
    ) -> Dict:
        """
        Analyze conversation to determine appropriate ticket status.
        
        Args:
            conversation_history: List of conversation messages
            current_status: Current ticket status (open, in_progress, resolved, closed)
            ticket_created_at: When the ticket was created (for SLA)
            llm_resolved_flag: Whether LLM detected resolution in response
            
        Returns:
            {
                "recommended_status": str,
                "should_update": bool,
                "transition": str,
                "reason": str,
                "confidence": int (0-10),
                "resolution_summary": str (if resolved),
                "sla_warning": bool,
                "needs_escalation": bool
            }
        """
        result = {
            "recommended_status": current_status,
            "should_update": False,
            "transition": None,
            "reason": "No status change needed",
            "confidence": 0,
            "resolution_summary": None,
            "sla_warning": False,
            "needs_escalation": False
        }
        
        # Get recent messages for analysis
        recent_messages = conversation_history[-10:]  # Last 10 messages
        recent_user_messages = [
            m.get('content', '') for m in recent_messages if m.get('role') == 'user'
        ]
        
        if not recent_user_messages:
            return result
        
        recent_text = ' '.join(recent_user_messages).lower()
        last_user_message = recent_user_messages[-1].lower() if recent_user_messages else ""
        
        # Check for different status transitions based on current status
        if current_status == "open":
            result = self._check_open_transitions(
                recent_text, last_user_message, recent_user_messages, result
            )
        elif current_status == "in_progress":
            result = self._check_in_progress_transitions(
                recent_text, last_user_message, recent_user_messages, llm_resolved_flag, result
            )
        elif current_status == "resolved":
            result = self._check_resolved_transitions(
                recent_text, last_user_message, result
            )
        
        # Check SLA (if ticket older than 4 hours and not resolved)
        if ticket_created_at and current_status not in ["resolved", "closed"]:
            time_elapsed = datetime.utcnow() - ticket_created_at
            if time_elapsed > timedelta(hours=4):
                result["sla_warning"] = True
                logger.warning(f"[STATUS-AGENT] SLA warning: Ticket open for {time_elapsed}")
        
        # Check for escalation needs (lowered threshold for faster response)
        frustration_count = sum(1 for kw in self.frustration_keywords if kw in recent_text)
        if frustration_count >= 1:  # Even 1 signal is enough for escalation
            result["needs_escalation"] = True
            result["reason"] += " | User showing frustration/urgency signals"
            logger.info(f"[STATUS-AGENT] Escalation recommended: {frustration_count} frustration/urgency signals detected")
        
        if result["should_update"]:
            logger.info(f"[STATUS-AGENT] Status change: {current_status} -> {result['recommended_status']} ({result['reason']})")
        
        return result
    
    def _check_open_transitions(
        self,
        recent_text: str,
        last_user_message: str,
        recent_user_messages: List[str],
        result: Dict
    ) -> Dict:
        """Check transitions from OPEN status."""
        
        # Check if troubleshooting has started (user engaging with solutions)
        in_progress_signals = sum(1 for kw in self.in_progress_keywords if kw in recent_text)
        
        # If there are multiple back-and-forth messages, mark as in_progress
        if len(recent_user_messages) >= 3 or in_progress_signals >= 2:
            result["recommended_status"] = "in_progress"
            result["should_update"] = True
            result["transition"] = TicketStatusTransition.OPEN_TO_IN_PROGRESS
            result["reason"] = "User actively troubleshooting"
            result["confidence"] = 7
        
        return result
    
    def _check_in_progress_transitions(
        self,
        recent_text: str,
        last_user_message: str,
        recent_user_messages: List[str],
        llm_resolved_flag: bool,
        result: Dict
    ) -> Dict:
        """Check transitions from IN_PROGRESS status."""
        
        # Count resolution signals
        positive_count = sum(1 for kw in self.resolution_positive_keywords if kw in recent_text)
        negative_count = sum(1 for kw in self.resolution_negative_keywords if kw in recent_text)
        
        # Check last few messages specifically for resolution confirmation
        last_messages_text = ' '.join(recent_user_messages[-3:]).lower()
        recent_positive = sum(1 for kw in self.resolution_positive_keywords if kw in last_messages_text)
        recent_negative = sum(1 for kw in self.resolution_negative_keywords if kw in last_messages_text)
        
        # Resolution conditions:
        # 1. LLM flagged as resolved AND no negative signals in recent messages
        # 2. Multiple positive signals AND no recent negative signals
        # 3. User explicitly confirmed resolution (e.g., "yes it's fixed")
        
        is_resolved = False
        confidence = 0
        resolution_summary = ""
        
        if llm_resolved_flag and recent_negative == 0:
            is_resolved = True
            confidence = 8
            resolution_summary = "LLM detected resolution confirmation"
        elif recent_positive >= 2 and recent_negative == 0:
            is_resolved = True
            confidence = 7 + min(recent_positive, 3)
            resolution_summary = f"User confirmed resolution: '{recent_user_messages[-1][:50]}'"
        elif 'fixed' in last_user_message or 'solved' in last_user_message or 'working now' in last_user_message:
            is_resolved = True
            confidence = 9
            resolution_summary = f"User explicitly confirmed: '{last_user_message[:50]}'"
        
        if is_resolved:
            result["recommended_status"] = "resolved"
            result["should_update"] = True
            result["transition"] = TicketStatusTransition.IN_PROGRESS_TO_RESOLVED
            result["reason"] = resolution_summary
            result["confidence"] = confidence
            result["resolution_summary"] = resolution_summary
        
        return result
    
    def _check_resolved_transitions(
        self,
        recent_text: str,
        last_user_message: str,
        result: Dict
    ) -> Dict:
        """Check transitions from RESOLVED status (re-open detection)."""
        
        # Check for re-open signals
        reopen_signals = sum(1 for kw in self.reopen_keywords if kw in recent_text)
        negative_signals = sum(1 for kw in self.resolution_negative_keywords if kw in last_user_message)
        
        if reopen_signals >= 1 or negative_signals >= 2:
            result["recommended_status"] = "open"
            result["should_update"] = True
            result["transition"] = TicketStatusTransition.RESOLVED_TO_REOPENED
            result["reason"] = "Issue recurring - user reported problem returned"
            result["confidence"] = 7
            logger.warning(f"[STATUS-AGENT] Ticket re-opened: Issue recurring")
        
        return result
    
    def detect_resolution(
        self,
        conversation_history: List[Dict],
        llm_resolved_flag: bool = False
    ) -> Dict:
        """
        Simplified resolution detection for backward compatibility.
        
        Returns:
            {
                "is_resolved": bool,
                "confidence": int (0-10),
                "resolution_summary": str
            }
        """
        result = self.analyze_conversation_status(
            conversation_history=conversation_history,
            current_status="in_progress",
            llm_resolved_flag=llm_resolved_flag
        )
        
        return {
            "is_resolved": result["recommended_status"] == "resolved",
            "confidence": result["confidence"],
            "resolution_summary": result["resolution_summary"] or "No resolution detected"
        }
    
    def should_auto_close(
        self,
        conversation_history: List[Dict],
        last_activity: datetime,
        current_status: str
    ) -> Dict:
        """
        Check if ticket should be auto-closed due to inactivity.
        
        Auto-close conditions:
        - Status is RESOLVED and no activity for 24 hours
        - Status is OPEN/IN_PROGRESS but no response for 72 hours
        
        Returns:
            {
                "should_close": bool,
                "reason": str
            }
        """
        time_since_activity = datetime.utcnow() - last_activity
        
        if current_status == "resolved":
            if time_since_activity > timedelta(hours=24):
                return {
                    "should_close": True,
                    "reason": f"Auto-closed: Resolved ticket inactive for {time_since_activity.days} days"
                }
        elif current_status in ["open", "in_progress"]:
            if time_since_activity > timedelta(hours=72):
                return {
                    "should_close": True,
                    "reason": f"Auto-closed: Abandoned ticket - no activity for {time_since_activity.days} days"
                }
        
        return {"should_close": False, "reason": "Ticket still active"}
    
    def get_sla_status(
        self,
        ticket_created_at: datetime,
        ticket_priority: str,
        current_status: str
    ) -> Dict:
        """
        Get SLA status for a ticket.
        
        SLA targets by priority:
        - CRITICAL: 1 hour response, 4 hours resolution
        - HIGH: 4 hours response, 24 hours resolution
        - MEDIUM: 8 hours response, 48 hours resolution
        - LOW: 24 hours response, 1 week resolution
        
        Returns:
            {
                "sla_breached": bool,
                "sla_warning": bool,
                "time_remaining": str,
                "response_sla": str,
                "resolution_sla": str
            }
        """
        if current_status in ["resolved", "closed"]:
            return {
                "sla_breached": False,
                "sla_warning": False,
                "time_remaining": "N/A - Ticket resolved",
                "response_sla": "Met",
                "resolution_sla": "Met"
            }
        
        sla_targets = {
            "critical": {"response": 1, "resolution": 4},
            "high": {"response": 4, "resolution": 24},
            "medium": {"response": 8, "resolution": 48},
            "low": {"response": 24, "resolution": 168}  # 1 week
        }
        
        targets = sla_targets.get(ticket_priority.lower(), sla_targets["medium"])
        time_elapsed = datetime.utcnow() - ticket_created_at
        hours_elapsed = time_elapsed.total_seconds() / 3600
        
        resolution_target = targets["resolution"]
        time_remaining_hours = resolution_target - hours_elapsed
        
        sla_breached = hours_elapsed > resolution_target
        sla_warning = time_remaining_hours < (resolution_target * 0.25)  # 25% time remaining
        
        if time_remaining_hours > 0:
            if time_remaining_hours > 24:
                time_remaining = f"{int(time_remaining_hours / 24)} days"
            else:
                time_remaining = f"{int(time_remaining_hours)} hours"
        else:
            time_remaining = f"OVERDUE by {int(abs(time_remaining_hours))} hours"
        
        return {
            "sla_breached": sla_breached,
            "sla_warning": sla_warning,
            "time_remaining": time_remaining,
            "response_sla": f"{targets['response']}h target",
            "resolution_sla": f"{targets['resolution']}h target"
        }


# Singleton instance
_ticket_status_agent = None


def get_ticket_status_agent() -> TicketStatusAgent:
    """Get or create the singleton TicketStatusAgent instance."""
    global _ticket_status_agent
    if _ticket_status_agent is None:
        _ticket_status_agent = TicketStatusAgent()
    return _ticket_status_agent
