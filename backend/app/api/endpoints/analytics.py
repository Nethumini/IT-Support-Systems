from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.ticket import TicketDB

from app.services.sla_service import get_or_initialize_sla_service
# Define the router
router = APIRouter(tags=["Analytics"])

def fallback_prediction(priority: str, description: str = "") -> float:
    """Simple rule-based prediction when ML model unavailable"""
    base_hours = {'critical': 2, 'high': 8, 'medium': 24, 'low': 48}
    return base_hours.get(priority.lower(), 24.0)

@router.get("/sla-risk")
async def get_sla_risk_report(db: Session = Depends(get_db)):
    """
    Fetches all OPEN tickets and predicts if they will breach SLA.
    Works with or without ML models (uses fallback rules).
    """
    try:
        # Get the SLA service (lazy loaded)
        service = get_or_initialize_sla_service()
        
        # Get active tickets
        open_tickets = db.query(TicketDB).filter(
            TicketDB.status.in_(['open', 'in_progress'])
        ).all()
        
        report_data = []
        
        for t in open_tickets:
            # Predict using ML or fallback
            if service:
                try:
                    predicted_hours = service.predict_resolution_time(
                        category=t.title, 
                        priority_str=t.priority, 
                        description=t.description or ""
                    )
                except:
                    predicted_hours = fallback_prediction(t.priority, t.description or "")
            else:
                predicted_hours = fallback_prediction(t.priority, t.description or "")
            
            # SLA limits by priority
            sla_limits = {'critical': 4, 'high': 24, 'medium': 48, 'low': 72}
            sla_limit = sla_limits.get(t.priority.lower(), 48)
            
            report_data.append({
                "id": t.id,
                "title": t.title,
                "category": t.title, 
                "priority": t.priority,
                "predicted_hours": predicted_hours,
                "sla_limit": sla_limit
            })
            
        # Sort by risk (predicted - limit)
        report_data.sort(key=lambda x: x['predicted_hours'] - x['sla_limit'], reverse=True)
        
        return report_data
    except Exception as e:
        logging.error(f"SLA report error: {e}")
        return []  # Return empty instead of failing

@router.get("/weekly-trends")
async def get_weekly_trends(db: Session = Depends(get_db)):
    """
    Returns ticket counts for the last 4 weeks.
    """
    today = datetime.now()
    trends = []

    # Loop back 4 weeks
    for i in range(4):
        start_of_week = today - timedelta(weeks=i+1)
        end_of_week = today - timedelta(weeks=i)
        
        # Count tickets created in this range
        count = db.query(TicketDB).filter(
            TicketDB.created_at >= start_of_week,
            TicketDB.created_at < end_of_week
        ).count()
        
        trends.append({
            "week_label": f"Week {4-i}", # Week 4, Week 3...
            "count": count
        })
    
    # Reverse so Week 1 comes first
    return trends[::-1]