"""
Smart Ticket Assignment Service - LLM-Based Agent Matching

Uses Gemini LLM to intelligently assign tickets to support agents based on:
1. Ticket category and complexity
2. Agent specialization and expertise
3. Agent role level (L1/L2/L3)
4. Current workload
5. Availability status

No ML training required - pure LLM reasoning!
"""
import logging
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
import google.generativeai as genai

from app.models.user import UserDB
from app.models.ticket import TicketDB, TicketPriority, TicketCategory
from app.models.role import Role
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AssignmentService:
    """LLM-powered ticket assignment service."""
    
    def __init__(self):
        """Initialize with Gemini LLM."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(
            settings.gemini_model,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,  # Low temperature for consistent decisions
                max_output_tokens=200
            ),
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
            }
        )
        logger.info("Assignment Service initialized with Gemini LLM")
    
    def assign_ticket(
        self, 
        ticket: TicketDB, 
        db: Session
    ) -> Dict[str, any]:
        """
        Assign ticket to best available support agent using LLM reasoning.
        
        Args:
            ticket: Ticket to assign
            db: Database session
        
        Returns:
            {
                "assigned_to": "agent@example.com",
                "agent_name": "Agent Name",
                "agent_role": "support_l2",
                "reason": "Why this agent was chosen",
                "confidence": 0.85
            }
        """
        try:
            # Step 1: Get all available support agents
            available_agents = self._get_available_agents(db)
            
            if not available_agents:
                logger.warning("[ASSIGNMENT] No support agents available!")
                return {
                    "assigned_to": None,
                    "reason": "No support agents available in the system",
                    "confidence": 0.0
                }
            
            # Step 2: Build context for LLM
            agent_profiles = self._build_agent_profiles(available_agents)
            ticket_context = self._build_ticket_context(ticket)
            
            # Step 3: Ask LLM to choose best agent
            assignment_decision = self._llm_choose_agent(
                ticket_context, 
                agent_profiles
            )
            
            # Step 4: Validate and return decision
            if assignment_decision and assignment_decision.get('agent_email'):
                # Update ticket
                ticket.assigned_to = assignment_decision['agent_email']
                
                # Update agent workload
                agent = db.query(UserDB).filter(
                    UserDB.email == assignment_decision['agent_email']
                ).first()
                
                if agent:
                    agent.current_workload = (agent.current_workload or 0) + 1
                    db.commit()
                
                logger.info(
                    f"[ASSIGNMENT] Ticket #{ticket.id} assigned to "
                    f"{assignment_decision['agent_email']} - "
                    f"Reason: {assignment_decision.get('reason', 'N/A')}"
                )
                
                return assignment_decision
            else:
                logger.warning("[ASSIGNMENT] LLM failed to make decision")
                return self._fallback_assignment(available_agents, ticket, db)
        
        except Exception as e:
            logger.error(f"[ASSIGNMENT] Error: {e}")
            # Fallback to simple round-robin
            return self._fallback_assignment(
                self._get_available_agents(db), 
                ticket, 
                db
            )
    
    def _get_available_agents(self, db: Session) -> List[UserDB]:
        """Get all active support agents (L1, L2, L3)."""
        support_roles = [
            Role.SUPPORT_L1.value,
            Role.SUPPORT_L2.value,
            Role.SUPPORT_L3.value
        ]
        
        agents = db.query(UserDB).filter(
            and_(
                UserDB.role.in_(support_roles),
                UserDB.is_active == True
            )
        ).all()
        
        logger.info(f"[ASSIGNMENT] Found {len(agents)} available support agents")
        return agents
    
    def _build_agent_profiles(self, agents: List[UserDB]) -> str:
        """Build agent profile descriptions for LLM."""
        profiles = []
        
        for agent in agents:
            specializations = agent.specialization or []
            workload = agent.current_workload or 0
            
            # Map role to level
            role_level = {
                Role.SUPPORT_L1.value: "Level 1 (Basic Support)",
                Role.SUPPORT_L2.value: "Level 2 (Advanced Support)",
                Role.SUPPORT_L3.value: "Level 3 (Senior Engineer)"
            }.get(agent.role, "Support Staff")
            
            profile = f"""
Agent: {agent.name}
Email: {agent.email}
Role: {role_level}
Specializations: {', '.join(specializations) if specializations else 'General IT Support'}
Current Workload: {workload} active tickets
Department: {agent.department or 'IT Support'}
"""
            profiles.append(profile.strip())
        
        return "\n\n".join(profiles)
    
    def _build_ticket_context(self, ticket: TicketDB) -> str:
        """Build ticket context for LLM."""
        priority_desc = {
            TicketPriority.CRITICAL: "CRITICAL - System down, urgent",
            TicketPriority.HIGH: "HIGH - Work blocking, needs quick resolution",
            TicketPriority.MEDIUM: "MEDIUM - Standard issue",
            TicketPriority.LOW: "LOW - Minor issue, no urgency"
        }.get(ticket.priority, "MEDIUM")
        
        category_desc = {
            TicketCategory.HARDWARE: "Hardware (physical devices, BSOD, peripherals)",
            TicketCategory.SOFTWARE: "Software (applications, OS, performance)",
            TicketCategory.NETWORK: "Network (VPN, connectivity, firewall)",
            TicketCategory.ACCOUNT: "Account (login, permissions, password)"
        }.get(ticket.category, ticket.category or "General IT Issue")
        
        context = f"""
Ticket ID: #{ticket.id}
Title: {ticket.title}
Description: {ticket.description[:300]}...
Priority: {priority_desc}
Category: {category_desc}
User: {ticket.user_email}
"""
        return context.strip()
    
    def _llm_choose_agent(
        self, 
        ticket_context: str, 
        agent_profiles: str
    ) -> Optional[Dict]:
        """Use LLM to choose the best agent."""
        
        prompt = f"""You are an IT support ticket routing system. Analyze the ticket and available support agents, then assign the ticket to the BEST agent.

TICKET DETAILS:
{ticket_context}

AVAILABLE SUPPORT AGENTS:
{agent_profiles}

ASSIGNMENT RULES:
1. Match agent specialization to ticket category (hardware → hardware specialist)
2. Prefer agents with lower workload (< 5 tickets is good, > 10 is heavy)
3. CRITICAL/HIGH priority → prefer L2/L3 agents if available
4. Hardware failures (BSOD) → must go to L2/L3
5. Simple software/network issues → L1 can handle
6. If no specialization match, choose least busy agent

Choose the BEST agent and respond ONLY with this JSON format:
{{
    "agent_email": "agent@example.com",
    "agent_name": "Agent Name",
    "reason": "Brief reason (one sentence)",
    "confidence": 0.85
}}

Return ONLY the JSON, nothing else."""

        try:
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                import json
                text = response.text.strip()
                
                # Clean markdown code blocks
                if text.startswith('```'):
                    text = text.split('```')[1]
                    if text.startswith('json'):
                        text = text[4:]
                    text = text.strip()
                
                result = json.loads(text)
                
                # Validate required fields
                if 'agent_email' in result:
                    return {
                        "assigned_to": result['agent_email'],
                        "agent_email": result['agent_email'],
                        "agent_name": result.get('agent_name', 'Unknown'),
                        "agent_role": "support",  # Will be updated from DB
                        "reason": result.get('reason', 'Best match based on analysis'),
                        "confidence": result.get('confidence', 0.8)
                    }
            
            logger.warning("[ASSIGNMENT] LLM returned invalid response")
            return None
        
        except Exception as e:
            logger.error(f"[ASSIGNMENT] LLM decision failed: {e}")
            return None
    
    def _fallback_assignment(
        self, 
        agents: List[UserDB], 
        ticket: TicketDB, 
        db: Session
    ) -> Dict:
        """Fallback to simple round-robin if LLM fails - filters by specialization first."""
        if not agents:
            return {
                "assigned_to": None,
                "reason": "No agents available",
                "confidence": 0.0
            }
        
        # Filter agents by matching specialization to ticket category
        matching_agents = []
        ticket_category = ticket.category.value if hasattr(ticket.category, 'value') else str(ticket.category)
        
        for agent in agents:
            if agent.specialization:
                # specialization can be list or JSON string
                specializations = agent.specialization
                if isinstance(specializations, str):
                    import json
                    try:
                        specializations = json.loads(specializations)
                    except:
                        specializations = [specializations]
                
                # Check if ticket category matches any agent specialization
                if ticket_category.lower() in [s.lower() for s in specializations]:
                    matching_agents.append(agent)
        
        # If no matching specialists, fall back to all available agents
        candidates = matching_agents if matching_agents else agents
        
        # Sort by workload (least busy first)
        agents_sorted = sorted(candidates, key=lambda a: a.current_workload or 0)
        chosen_agent = agents_sorted[0]
        
        # Update ticket and workload
        ticket.assigned_to = chosen_agent.email
        chosen_agent.current_workload = (chosen_agent.current_workload or 0) + 1
        db.commit()
        
        match_type = "matching specialist" if matching_agents else "available agent"
        logger.info(
            f"[ASSIGNMENT] Fallback: Assigned ticket #{ticket.id} ({ticket_category}) to "
            f"{chosen_agent.email} ({match_type}, workload: {chosen_agent.current_workload})"
        )
        
        return {
            "assigned_to": chosen_agent.email,
            "agent_email": chosen_agent.email,
            "agent_name": chosen_agent.name,
            "agent_role": chosen_agent.role,
            "reason": f"Assigned to least busy {match_type} (fallback mode)",
            "confidence": 0.7 if matching_agents else 0.5
        }
    
    def unassign_ticket(self, ticket: TicketDB, db: Session):
        """Remove assignment and decrement agent workload."""
        if ticket.assigned_to:
            agent = db.query(UserDB).filter(
                UserDB.email == ticket.assigned_to
            ).first()
            
            if agent and agent.current_workload:
                agent.current_workload = max(0, agent.current_workload - 1)
            
            ticket.assigned_to = None
            db.commit()
            
            logger.info(f"[ASSIGNMENT] Ticket #{ticket.id} unassigned")
    
    def reassign_ticket(
        self, 
        ticket: TicketDB, 
        new_agent_email: str, 
        db: Session
    ) -> Dict:
        """Manually reassign ticket to a specific agent."""
        # Decrement old agent workload
        if ticket.assigned_to:
            old_agent = db.query(UserDB).filter(
                UserDB.email == ticket.assigned_to
            ).first()
            
            if old_agent and old_agent.current_workload:
                old_agent.current_workload = max(0, old_agent.current_workload - 1)
        
        # Increment new agent workload
        new_agent = db.query(UserDB).filter(
            UserDB.email == new_agent_email
        ).first()
        
        if not new_agent:
            logger.error(f"[ASSIGNMENT] Agent {new_agent_email} not found")
            return {
                "success": False,
                "reason": "Agent not found"
            }
        
        ticket.assigned_to = new_agent_email
        new_agent.current_workload = (new_agent.current_workload or 0) + 1
        db.commit()
        
        logger.info(
            f"[ASSIGNMENT] Ticket #{ticket.id} reassigned to {new_agent_email}"
        )
        
        return {
            "success": True,
            "assigned_to": new_agent_email,
            "agent_name": new_agent.name,
            "reason": "Manually reassigned by admin"
        }


# Singleton instance
_assignment_service = None

def get_assignment_service() -> AssignmentService:
    """Get singleton assignment service instance."""
    global _assignment_service
    if _assignment_service is None:
        _assignment_service = AssignmentService()
    return _assignment_service
