"""
Dataset Analyzer - Learns from past tickets to make smart decisions.
Analyzes ticketing_system_data_new.json to:
1. Calculate priority based on user tier, urgency, and past patterns
2. Find similar past issues using embeddings
3. Suggest solutions from knowledge base
"""
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
import numpy as np
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DatasetAnalyzer:
    """Analyzes historical ticket data for smart decision-making with embedding-based similarity."""
    
    def __init__(self, dataset_path: str = None):
        """Load and parse the dataset."""
        if dataset_path is None:
            # Default path relative to backend folder
            dataset_path = Path(__file__).parent.parent.parent / "data" / "raw" / "ticketing_system_data_new.json"
        self.dataset_path = Path(dataset_path)
        self.data = self._load_dataset()
        self.users = {u['id']: u for u in self.data.get('users', [])}
        self.user_history = {u['user_id']: u for u in self.data.get('user_history', [])}
        self.tickets = self.data.get('tickets', [])
        self.knowledge_base = {kb['id']: kb for kb in self.data.get('knowledge_base', [])}
        
        # Initialize embedding model
        genai.configure(api_key=settings.google_api_key)
        self.embedding_cache = {}  # Cache embeddings for performance
        
        logger.info(f"Loaded dataset: {len(self.users)} users, {len(self.tickets)} tickets, {len(self.knowledge_base)} KB articles")
    
    def _load_dataset(self) -> Dict:
        """Load JSON dataset."""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            return {'users': [], 'user_history': [], 'tickets': [], 'knowledge_base': []}
    
    def calculate_priority(
        self,
        user_email: str,
        category: str,
        urgency: str,
        description: str
    ) -> Tuple[int, Dict]:
        """
        Calculate smart priority score (1-3, where 1=critical, 3=low).
        
        Algorithm based on real office IT logic:
        - User tier (manager > staff > contractor)
        - Urgency keywords (meeting, client, deadline, down, crash)
        - Past similar issues
        - Category criticality (hardware > network > software)
        
        Returns:
            Tuple of (priority: int, reasoning: dict)
        """
        score = 50  # Base score
        reasoning = {
            "base_score": 50,
            "adjustments": []
        }
        
        # 1. User Tier Weight (Manager = +20, Staff = +10, Contractor = +0)
        user_id = self._get_user_id_by_email(user_email)
        user_tier = self.users.get(user_id, {}).get('tier', 'staff')
        
        if user_tier == 'manager':
            score += 20
            reasoning['adjustments'].append({"factor": "Manager user", "points": 20})
        elif user_tier == 'staff':
            score += 10
            reasoning['adjustments'].append({"factor": "Staff user", "points": 10})
        else:
            reasoning['adjustments'].append({"factor": "Contractor", "points": 0})
        
        # 2. Urgency Weight
        urgency_scores = {
            'critical': 30,
            'high': 20,
            'medium': 10,
            'low': 0
        }
        urgency_points = urgency_scores.get(urgency.lower(), 10)
        score += urgency_points
        reasoning['adjustments'].append({"factor": f"Urgency: {urgency}", "points": urgency_points})
        
        # 3. Urgency Keywords in Description (Real IT Logic!)
        critical_keywords = ['meeting', 'client', 'deadline', 'urgent', 'asap', 'down', 'crash', 'bsod']
        found_keywords = [kw for kw in critical_keywords if kw in description.lower()]
        
        if found_keywords:
            keyword_score = min(len(found_keywords) * 10, 30)  # Max +30
            score += keyword_score
            reasoning['adjustments'].append({
                "factor": f"Critical keywords: {', '.join(found_keywords)}",
                "points": keyword_score
            })
        
        # 4. Category Criticality
        category_scores = {
            'hardware': 15,  # Physical issues need human
            'network': 12,   # Blocks productivity
            'performance': 8,
            'software': 5,
            'access': 10
        }
        cat_score = category_scores.get(category.lower(), 5)
        score += cat_score
        reasoning['adjustments'].append({"factor": f"Category: {category}", "points": cat_score})
        
        # 5. Past Issues (Repeat offender?)
        past_tickets = self._get_user_past_tickets(user_id)
        if len(past_tickets) >= 3:
            # User has history of issues - may need device replacement
            score += 15
            reasoning['adjustments'].append({
                "factor": f"User has {len(past_tickets)} past tickets",
                "points": 15
            })
        
        # 6. Unresolved Past Issues
        unresolved = [t for t in past_tickets if not t.get('resolved', True)]
        if unresolved:
            score += 20
            reasoning['adjustments'].append({
                "factor": f"{len(unresolved)} unresolved past tickets",
                "points": 20
            })
        
        reasoning['final_score'] = score
        
        # Convert score to priority (1=critical, 2=medium, 3=low)
        if score >= 80:
            priority = 1  # Critical
            reasoning['priority_label'] = "Critical"
        elif score >= 50:
            priority = 2  # Medium
            reasoning['priority_label'] = "Medium"
        else:
            priority = 3  # Low
            reasoning['priority_label'] = "Low"
        
        return priority, reasoning
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using Google's embedding model with caching."""
        # Check cache first
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            embedding = np.array(result['embedding'])
            
            # Cache for future use
            self.embedding_cache[text] = embedding
            
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            # Fallback to zero vector
            return np.zeros(768)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def find_similar_issues(self, description: str, category: str, limit: int = 3) -> List[Dict]:
        """
        Find similar past issues from knowledge base using semantic embeddings.
        
        Returns:
            List of similar KB articles with resolution steps
        """
        similar = []
        
        # Get embedding for user's description
        desc_embedding = self._get_embedding(description)
        
        for kb_id, kb in self.knowledge_base.items():
            # Filter by category or include all if no exact match
            if kb['category'] == category or category == 'other':
                # Get embedding for KB article
                kb_text = f"{kb['title']} {kb['issue_pattern']}"
                kb_embedding = self._get_embedding(kb_text)
                
                # Calculate semantic similarity
                similarity_score = self._cosine_similarity(desc_embedding, kb_embedding)
                
                # Include if similarity is above threshold (0.5)
                if similarity_score > 0.5:
                    similar.append({
                        'kb_id': kb_id,
                        'title': kb['title'],
                        'category': kb['category'],
                        'resolution_steps': kb['resolution_steps'],
                        'similarity_score': round(similarity_score, 3),
                        'used_count': len(kb.get('used_in_tickets', []))
                    })
        
        # Sort by similarity score (weighted with usage)
        similar.sort(key=lambda x: (x['similarity_score'] * 0.8 + (x['used_count'] / 100) * 0.2), reverse=True)
        
        return similar[:limit]
    
    def get_resolution_steps(self, kb_id: str) -> List[str]:
        """Get resolution steps from knowledge base article."""
        kb = self.knowledge_base.get(kb_id)
        if kb:
            return kb.get('resolution_steps', [])
        return []
    
    def should_escalate_to_human(
        self,
        category: str,
        urgency: str,
        user_tier: str,
        description: str,
        attempted_solutions: List[str] = None
    ) -> Dict:
        """
        Decide if issue needs human escalation (like real IT tech decision).
        
        Escalate if:
        - Hardware issue (usually needs physical access)
        - Manager with critical issue
        - Multiple failed troubleshooting attempts
        - BSOD / data loss risk
        - Security concern
        
        Returns:
            Dict with escalation decision and reasoning
        """
        should_escalate = False
        reasons = []
        urgency_level = "medium"
        recommended_team = "l1_support"
        
        # 1. Hardware Issues - Almost Always Escalate
        if category == 'hardware':
            should_escalate = True
            reasons.append("Hardware issues usually require physical access")
            recommended_team = "hardware_team"
            urgency_level = "high"
        
        # 2. Critical Keywords
        critical_keywords = ['bsod', 'blue screen', 'crash', 'data loss', 'security', 'hacked', 'virus']
        if any(kw in description.lower() for kw in critical_keywords):
            should_escalate = True
            reasons.append("Critical issue detected (BSOD/crash/security)")
            recommended_team = "l2_support"
            urgency_level = "high"
        
        # 3. Manager + High/Critical Urgency
        if user_tier == 'manager' and urgency in ['high', 'critical']:
            should_escalate = True
            reasons.append("Manager with high-urgency issue")
            urgency_level = "high"
        
        # 4. Multiple Failed Attempts
        if attempted_solutions and len(attempted_solutions) >= 3:
            should_escalate = True
            reasons.append(f"{len(attempted_solutions)} troubleshooting attempts failed")
            recommended_team = "l2_support"
        
        # 5. Network Issues (May Need Network Team)
        if category == 'network' and urgency in ['high', 'critical']:
            should_escalate = True
            reasons.append("Network issue affecting connectivity")
            recommended_team = "network_team"
        
        return {
            "should_escalate": should_escalate,
            "reasons": reasons,
            "urgency": urgency_level,
            "recommended_team": recommended_team,
            "can_attempt_remote": not should_escalate
        }
    
    def get_user_context(self, user_email: str) -> Dict:
        """Get user context for personalized support."""
        user_id = self._get_user_id_by_email(user_email)
        
        user_info = self.users.get(user_id, {})
        history = self.user_history.get(user_id, {})
        
        return {
            "user_id": user_id,
            "name": user_info.get('name', 'Unknown User'),
            "email": user_email,
            "tier": user_info.get('tier', 'staff'),
            "status": user_info.get('status', 'active'),
            "past_tickets": self._get_user_past_tickets(user_id),
            "account_health": history.get('metrics', {}).get('account_health', 0),
            "network_stability": history.get('metrics', {}).get('network_stability', 0)
        }
    
    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """Find user ID by email."""
        for user_id, user in self.users.items():
            if user.get('email') == email:
                return user_id
        return None
    
    def _get_user_past_tickets(self, user_id: str) -> List[Dict]:
        """Get user's past tickets from history."""
        history = self.user_history.get(user_id, {})
        return history.get('past_tickets', [])
    
    def get_stats(self) -> Dict:
        """Get dataset statistics for dashboard."""
        total_tickets = len(self.tickets)
        resolved = sum(1 for t in self.tickets if t.get('is_resolved'))
        
        # Category breakdown
        categories = {}
        for ticket in self.tickets:
            cat = ticket.get('category', 'other')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_users": len(self.users),
            "total_tickets": total_tickets,
            "resolved_tickets": resolved,
            "resolution_rate": round(resolved / total_tickets * 100, 1) if total_tickets > 0 else 0,
            "categories": categories,
            "kb_articles": len(self.knowledge_base)
        }
    
    def get_user_action_preferences(self, user_email: str) -> Dict:
        """
        Analyze user's past tickets to personalize action suggestions.
        Returns insights about what issues this user commonly faces.
        """
        user_id = self._get_user_id_by_email(user_email)
        if not user_id:
            return {"common_categories": [], "recurring_issues": [], "tier": "staff"}
        
        # Get user history
        history = self.user_history.get(user_id, {})
        past_tickets = history.get('past_tickets', [])
        tier = self.users.get(user_id, {}).get('tier', 'staff')
        
        # Analyze common issue patterns
        issue_keywords = {}
        for ticket in past_tickets:
            issue = ticket.get('issue', '').lower()
            # Extract key terms
            for word in ['vpn', 'outlook', 'network', 'slow', 'wi-fi', 'wifi', 'laptop', 
                        'visual studio', 'vs code', 'zoom', 'audio', 'docker', 'git', 
                        'ssh', 'keyboard', 'mouse', 'dock', 'printer', 'email', 'password']:
                if word in issue:
                    issue_keywords[word] = issue_keywords.get(word, 0) + 1
        
        # Get top recurring issues
        recurring = sorted(issue_keywords.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Get metrics
        metrics = history.get('metrics', {})
        
        return {
            "tier": tier,
            "recurring_issues": [issue[0] for issue in recurring],
            "past_ticket_count": len(past_tickets),
            "account_health": metrics.get('account_health', 100),
            "network_stability": metrics.get('network_stability', 100),
            "last_login": history.get('last_login', None)
        }


# Singleton instance
_analyzer = None

def get_analyzer() -> DatasetAnalyzer:
    """Get or create dataset analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = DatasetAnalyzer()
    return _analyzer
