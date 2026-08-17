"""
LLM-First Conversation Agent - Simple & Intelligent
The LLM is the brain. No hard-coded logic, just smart prompting.
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime
import google.generativeai as genai
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMConversationAgent:
    """
    Pure LLM-driven conversation agent.
    The LLM handles all conversation logic, classification, and response generation.
    """
    
    def __init__(self):
        """Initialize with Gemini LLM."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        genai.configure(api_key=settings.google_api_key)
        # Use the model from settings directly
        self.model = genai.GenerativeModel(
            settings.gemini_model,
            generation_config=genai.types.GenerationConfig(
                temperature=settings.gemini_temperature,
                max_output_tokens=2048,
                top_p=0.95,
                top_k=40
            ),
            safety_settings={
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # Simple conversation memory: {user_email: [messages]}
        self.conversations: Dict[str, List[Dict]] = {}
        
        logger.info("LLM Conversation Agent initialized")
    
    def get_system_prompt(self, rag_context: Optional[str] = None) -> str:
        """
        The brain of the system - comprehensive system prompt.
        This tells the LLM EVERYTHING it needs to know.
        """
        prompt = """You are an intelligent IT Support Assistant. You help users troubleshoot technical issues through natural conversation.

## Your Capabilities:
1. **Support all devices** - Computers, laptops, phones (iPhone/Android), tablets, printers, etc.
2. **Understand user issues** - Ask clarifying questions if needed
3. **Check knowledge base** - Similar past issues will be provided to you
4. **Troubleshoot intelligently** - Suggest concrete, actionable steps
5. **Know when to escalate** - If you can't solve it, escalate to human IT team
6. **Handle non-technical chat** - Be friendly and helpful even for general questions

## Conversation Flow:
1. User describes issue → You ask clarifying questions if needed
2. You check if similar issues exist in knowledge base (provided below)
3. You suggest troubleshooting steps one at a time
4. User tries step and reports back → You adapt based on feedback
5. If solved → Celebrate! If not after 3 attempts → Escalate to human

## Response Format:
Your response should be natural and conversational. Examples:

**Good responses:**
- "I can help! Let's start by checking Task Manager. Press Ctrl+Shift+Esc and tell me what's using the most CPU."
- "For iPhone slowness, let's try clearing Safari cache first. Go to Settings > Safari > Clear History and Website Data."
- "Based on similar issues, this usually happens when Chrome has too many tabs. Try closing some tabs and let me know if it improves."
- "I've tried a few approaches but this seems persistent. I'm escalating this to our specialist team who can investigate deeper."

**Avoid:**
- Robotic templates like "Did that help? Yes/No"
- Asking the same question repeatedly
- Giving multiple steps at once (ONE step at a time!)

"""
        
        if rag_context:
            prompt += f"\n## Knowledge Base - Similar Past Issues:\n{rag_context}\n"
        
        prompt += """
## Current Conversation:
(Previous messages are shown below. Respond naturally to continue the conversation)

Remember: Be helpful, concise, and human-like. One clear step at a time!
"""
        
        return prompt
    
    def add_message(self, user_email: str, role: str, content: str):
        """Add message to conversation history."""
        if user_email not in self.conversations:
            self.conversations[user_email] = []
        
        self.conversations[user_email].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep last 20 messages to avoid context overflow
        if len(self.conversations[user_email]) > 20:
            self.conversations[user_email] = self.conversations[user_email][-20:]
    
    def build_conversation_context(self, user_email: str) -> List:
        """Build conversation context for LLM."""
        messages = self.conversations.get(user_email, [])
        
        # Format for Gemini
        context = []
        for msg in messages:
            context.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]]
            })
        
        return context
    
    def process_message(
        self, 
        user_email: str, 
        user_message: str, 
        rag_context: Optional[str] = None
    ) -> Dict:
        """
        Process user message and generate response.
        This is the ONLY method you need!
        
        Args:
            user_email: User identifier
            user_message: User's message
            rag_context: Similar issues from knowledge base (optional)
        
        Returns:
            {
                "message": "Bot response",
                "is_technical": bool,
                "should_escalate": bool,
                "metadata": {...}
            }
        """
        try:
            # Check if this looks like a fresh conversation start
            # Reset conversation if user sends a simple greeting after having previous history
            greeting_patterns = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
            is_greeting = user_message.lower().strip() in greeting_patterns
            
            existing_history = self.conversations.get(user_email, [])
            
            # If user sends a greeting and there's existing history, 
            # check if we should reset (they might have refreshed the page)
            if is_greeting and len(existing_history) >= 4:
                # Check time gap - if last message was > 5 minutes ago, reset
                if existing_history:
                    last_msg = existing_history[-1]
                    last_time_str = last_msg.get('timestamp', '')
                    if last_time_str:
                        try:
                            last_time = datetime.fromisoformat(last_time_str)
                            time_gap = (datetime.utcnow() - last_time).total_seconds()
                            if time_gap > 300:  # 5 minutes
                                logger.info(f"[LLM] Resetting conversation for {user_email} - greeting after {time_gap:.0f}s gap")
                                self.reset_conversation(user_email)
                        except:
                            pass
            
            # Add user message to history
            self.add_message(user_email, "user", user_message)
            
            # Build conversation context
            system_prompt = self.get_system_prompt(rag_context)
            conversation = self.build_conversation_context(user_email)
            
            # Call LLM with full context
            logger.info(f"[LLM] Processing message for {user_email}: {user_message[:50]}...")
            if rag_context:
                logger.info(f"[LLM] RAG Context provided: {len(rag_context)} chars")
            logger.info(f"[LLM] Conversation history: {len(conversation)} messages")
            
            # Build prompt - use more context for resumed chats (up to 10 messages)
            full_prompt = f"{system_prompt}\n\n"
            context_msgs = conversation[-10:]  # Last 10 messages for better context
            for msg in context_msgs:
                role = "User" if msg["role"] == "user" else "Assistant"
                content = msg['parts'][0][:800]  # Limit message length
                full_prompt += f"{role}: {content}\n"
            
            full_prompt += "\nAssistant:"
            
            # Try to generate response
            response = self.model.generate_content(full_prompt)
            
            # Check if response was blocked by safety filters
            bot_response = None
            try:
                if response and response.text:
                    bot_response = response.text.strip()
            except Exception as text_error:
                # response.text throws exception when blocked by safety filters
                logger.warning(f"[LLM] Safety filter or empty response: {text_error}")
                
            if not bot_response:
                # Try with simpler prompt (without RAG context that might trigger filters)
                if rag_context:
                    logger.info("[LLM] Retrying without RAG context...")
                    simple_prompt = self.get_system_prompt(None) + "\n\n"
                    for msg in context_msgs:
                        role = "User" if msg["role"] == "user" else "Assistant"
                        content = msg['parts'][0][:800]
                        simple_prompt += f"{role}: {content}\n"
                    simple_prompt += "\nAssistant:"
                    
                    try:
                        response = self.model.generate_content(simple_prompt)
                        if response and response.text:
                            bot_response = response.text.strip()
                    except Exception as retry_error:
                        logger.warning(f"[LLM] Retry also failed: {retry_error}")
                    
            if not bot_response:
                logger.warning("[LLM] All attempts failed, using friendly fallback")
                bot_response = "I'm having trouble processing that. Could you rephrase what you need help with?"
            
            # Add bot response to history
            self.add_message(user_email, "assistant", bot_response)
            
            logger.info(f"[LLM] Response generated: {bot_response[:100]}...")
            
            # Analyze conversation for escalation and resolution
            is_technical = self._is_technical_conversation(conversation)
            should_escalate = self._should_escalate_to_human(user_message, bot_response, conversation)
            is_resolved = any(word in bot_response.lower() for word in ["solved", "fixed", "resolved", "glad that helped"])
            
            return {
                "message": bot_response,
                "is_technical": is_technical,
                "should_escalate": should_escalate,
                "is_resolved": is_resolved,
                "metadata": {
                    "turn_count": len(conversation) // 2,
                    "rag_used": bool(rag_context)
                }
            }
            
        except Exception as e:
            logger.error(f"[LLM] Error processing message: {e}")
            
            # Check if it's a rate limit error
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                return {
                    "message": "I'm currently experiencing high demand. Please try again in a few seconds, or I can connect you with our support team for immediate assistance.",
                    "is_technical": False,
                    "should_escalate": True,
                    "is_resolved": False,
                    "metadata": {"error": "rate_limit", "details": str(e)[:200]}
                }
            
            return {
                "message": "I encountered an issue. Let me connect you with our support team who can help you better.",
                "is_technical": False,
                "should_escalate": True,
                "is_resolved": False,
                "metadata": {"error": str(e)}
            }
    
    def _should_escalate_to_human(
        self, 
        user_message: str, 
        bot_response: str, 
        conversation: List
    ) -> bool:
        """
        Comprehensive escalation detection.
        
        Triggers escalation when:
        1. User explicitly asks for human help
        2. User shows urgency/frustration signals
        3. Bot response indicates escalation
        4. Multiple failed troubleshooting attempts
        """
        user_lower = user_message.lower()
        bot_lower = bot_response.lower()
        
        # 1. USER EXPLICITLY ASKS FOR HUMAN
        human_request_phrases = [
            "assign a human", "human agent", "real person", "speak to someone",
            "talk to human", "talk to a human", "escalate", "escalate this",
            "need human", "want human", "get human", "human help",
            "transfer to", "connect me to", "let me talk to",
            "manager", "supervisor", "technician", "specialist"
        ]
        if any(phrase in user_lower for phrase in human_request_phrases):
            logger.info(f"[ESCALATION] User explicitly requested human help")
            return True
        
        # 2. USER URGENCY/FRUSTRATION SIGNALS
        urgency_phrases = [
            "no time", "have no time", "dont have time", "don't have time",
            "meeting in", "urgent", "emergency", "critical", "asap",
            "right now", "immediately", "cant wait", "can't wait",
            "afraid", "worried", "scared", "anxious",
            "frustrated", "annoyed", "angry", "upset",
            "not working", "nothing works", "useless", "waste of time",
            "please help", "please listen", "i need help now",
            "this is important", "very important", "extremely important"
        ]
        urgency_count = sum(1 for phrase in urgency_phrases if phrase in user_lower)
        if urgency_count >= 1:  # Even 1 urgency signal is enough
            logger.info(f"[ESCALATION] User urgency detected: {urgency_count} signals")
            return True
        
        # 3. USER REFUSES/CAN'T DO TROUBLESHOOTING STEPS
        refusal_phrases = [
            "i cant", "i can't", "cant do", "can't do", "unable to",
            "not able to", "dont know how", "don't know how",
            "no i cant", "no i can't", "i refuse", "wont do", "won't do"
        ]
        if any(phrase in user_lower for phrase in refusal_phrases):
            # Check if this is repeated (user said can't multiple times)
            refusal_count = sum(
                1 for msg in conversation 
                if msg.get('role') == 'user' and 
                any(p in msg.get('parts', [''])[0].lower() for p in refusal_phrases)
            )
            if refusal_count >= 2:
                logger.info(f"[ESCALATION] User repeatedly unable to perform steps")
                return True
        
        # 4. BOT RESPONSE INDICATES ESCALATION
        bot_escalation_phrases = [
            "escalat", "specialist team", "human support", "support team",
            "it team", "technician", "pass this to", "transfer to",
            "connect you with", "hand this over"
        ]
        if any(phrase in bot_lower for phrase in bot_escalation_phrases):
            logger.info(f"[ESCALATION] Bot indicated escalation in response")
            return True
        
        # 5. TOO MANY TURNS WITHOUT RESOLUTION (user is stuck)
        turn_count = len([m for m in conversation if m.get('role') == 'user'])
        if turn_count >= 6:
            # Check if issue seems unresolved after many turns
            resolved_keywords = ['fixed', 'working', 'solved', 'thanks', 'thank you', 'great']
            recent_user_msgs = [m.get('parts', [''])[0].lower() for m in conversation[-4:] if m.get('role') == 'user']
            recent_text = ' '.join(recent_user_msgs)
            if not any(kw in recent_text for kw in resolved_keywords):
                logger.info(f"[ESCALATION] Many turns ({turn_count}) without resolution")
                return True
        
        return False
    
    def _is_technical_conversation(self, conversation: List) -> bool:
        """Simple heuristic to detect if conversation is technical."""
        if not conversation:
            return False
        
        # Check ALL user messages for IT keywords (not just first one)
        tech_keywords = [
            "computer", "laptop", "slow", "crash", "error", "wifi", "network",
            "software", "app", "application", "login", "password", "printer",
            "outlook", "email", "teams", "chrome", "browser", "windows", "mac",
            "cpu", "memory", "disk", "task manager", "vs code", "edge", "freeze"
        ]
        
        # Check any user message for technical keywords
        for msg in conversation:
            if msg["role"] == "user":
                content = msg["parts"][0].lower()
                if any(kw in content for kw in tech_keywords):
                    return True
        
        return False
    
    def classify_message(self, user_message: str, conversation_history: Optional[List] = None) -> Dict:
        """
        Fast LLM-based message classification.
        This determines if a message is technical/IT-related BEFORE doing RAG search.
        
        Args:
            user_message: The user's current message
            conversation_history: Optional conversation context
        
        Returns:
            {
                "is_technical": bool,
                "category": str (technical/general/greeting),
                "urgency": str (low/medium/high/critical),
                "topic": str (brief description of the issue)
            }
        """
        try:
            # Build classification prompt
            classification_prompt = f"""You are a message classifier for an IT support system.
Analyze the following user message and determine if it's a technical/IT support issue.

User Message: "{user_message}"

Respond with ONLY a JSON object (no markdown, no explanation):
{{
    "is_technical": true/false,
    "category": "technical" or "general" or "greeting",
    "urgency": "low" or "medium" or "high" or "critical",
    "topic": "brief description if technical, empty string if not"
}}

Classification Rules:
- "technical" = Any IT/tech issue: computer, laptop, phone, software, network, printer, email, apps, devices, gaming consoles (PlayStation, Xbox, Nintendo), slow performance, crashes, errors, connectivity, etc.
- "greeting" = Simple greetings like hi, hello, hey, good morning
- "general" = Non-technical chat, questions about services, or unrelated topics

Urgency Guidelines:
- "critical" = System down, can't work at all, security breach
- "high" = Significant productivity impact, urgent deadline
- "medium" = Annoying but can work around it
- "low" = Minor inconvenience, nice-to-fix

Examples:
- "my laptop is slow" -> {{"is_technical": true, "category": "technical", "urgency": "medium", "topic": "slow laptop performance"}}
- "playstation not connecting to wifi" -> {{"is_technical": true, "category": "technical", "urgency": "medium", "topic": "PlayStation WiFi connectivity"}}
- "hi there" -> {{"is_technical": false, "category": "greeting", "urgency": "low", "topic": ""}}
- "what time does the office close?" -> {{"is_technical": false, "category": "general", "urgency": "low", "topic": ""}}
- "can't access email, urgent client meeting in 1 hour" -> {{"is_technical": true, "category": "technical", "urgency": "critical", "topic": "email access issue before urgent meeting"}}

JSON only:"""

            # Use lower temperature for classification (more deterministic)
            classification_model = genai.GenerativeModel(
                settings.gemini_model,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for consistent classification
                    max_output_tokens=150
                )
            )
            
            response = classification_model.generate_content(classification_prompt)
            
            if response and response.text:
                import json
                # Clean up response (remove markdown if present)
                text = response.text.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                text = text.strip()
                
                try:
                    result = json.loads(text)
                    logger.info(f"[LLM-Classify] Message classified: {result}")
                    return result
                except json.JSONDecodeError as e:
                    logger.warning(f"[LLM-Classify] JSON parse error: {e}, raw: {text}")
                    # Fallback: simple keyword detection
                    return self._fallback_classification(user_message)
            else:
                logger.warning("[LLM-Classify] Empty response, using fallback")
                return self._fallback_classification(user_message)
                
        except Exception as e:
            logger.error(f"[LLM-Classify] Error: {e}")
            return self._fallback_classification(user_message)
    
    def _fallback_classification(self, user_message: str) -> Dict:
        """Fallback keyword-based classification if LLM fails."""
        msg_lower = user_message.lower()
        
        # Check for greetings
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'howdy']
        if msg_lower.strip() in greetings:
            return {
                "is_technical": False,
                "category": "greeting",
                "urgency": "low",
                "topic": ""
            }
        
        # Check for technical keywords
        tech_keywords = [
            "computer", "laptop", "slow", "crash", "error", "wifi", "network",
            "software", "app", "application", "login", "password", "printer",
            "outlook", "email", "teams", "chrome", "browser", "windows", "mac",
            "cpu", "memory", "disk", "freeze", "not working", "broken", "fix",
            "help", "issue", "problem", "phone", "iphone", "android", "tablet",
            "playstation", "ps4", "ps5", "xbox", "nintendo", "switch", "gaming", "console",
            "monitor", "screen", "keyboard", "mouse", "bluetooth", "internet"
        ]
        
        is_technical = any(kw in msg_lower for kw in tech_keywords)
        
        return {
            "is_technical": is_technical,
            "category": "technical" if is_technical else "general",
            "urgency": "medium" if is_technical else "low",
            "topic": "technical issue" if is_technical else ""
        }
    
    def reset_conversation(self, user_email: str):
        """Clear conversation history."""
        if user_email in self.conversations:
            del self.conversations[user_email]
            logger.info(f"[LLM] Reset conversation for {user_email}")


# Global instance
_agent_instance = None

def get_llm_conversation_agent() -> LLMConversationAgent:
    """Get or create the global LLM agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = LLMConversationAgent()
    return _agent_instance
