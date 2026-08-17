"""
Dashboard endpoints - Analytics and insights.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.ticket import TicketDB, TicketStatus, TicketPriority, TicketCategory
from app.services.ticket_service import ticket_service

router = APIRouter()


@router.get("/dashboard/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    Get overall dashboard metrics.
    """
    try:
        stats = ticket_service.get_ticket_stats(db)
        
        # Calculate additional metrics
        total_tickets = stats["total"]
        open_and_in_progress = stats["by_status"]["open"] + stats["by_status"]["in_progress"]
        resolution_rate = (
            (stats["by_status"]["resolved"] + stats["by_status"]["closed"]) / total_tickets * 100
            if total_tickets > 0 else 0
        )
        
        # Get recent activity (tickets created in last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_tickets = db.query(TicketDB).filter(
            TicketDB.created_at >= week_ago
        ).count()
        
        return {
            "total_tickets": total_tickets,
            "active_tickets": open_and_in_progress,
            "resolved_tickets": stats["by_status"]["resolved"],
            "resolution_rate_percent": round(resolution_rate, 2),
            "recent_activity_7days": recent_tickets,
            "critical_tickets": stats["by_priority"]["critical"],
            "high_priority_tickets": stats["by_priority"]["high"],
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboard overview: {str(e)}")


@router.get("/dashboard/trends")
async def get_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get ticket trends over time.
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get tickets created per day
        daily_tickets = db.query(
            func.date(TicketDB.created_at).label('date'),
            func.count(TicketDB.id).label('count')
        ).filter(
            TicketDB.created_at >= start_date
        ).group_by(
            func.date(TicketDB.created_at)
        ).all()
        
        # Get tickets resolved per day
        daily_resolved = db.query(
            func.date(TicketDB.resolved_at).label('date'),
            func.count(TicketDB.id).label('count')
        ).filter(
            TicketDB.resolved_at >= start_date
        ).group_by(
            func.date(TicketDB.resolved_at)
        ).all()
        
        return {
            "period_days": days,
            "created_by_day": [
                {"date": str(item.date), "count": item.count}
                for item in daily_tickets
            ],
            "resolved_by_day": [
                {"date": str(item.date), "count": item.count}
                for item in daily_resolved
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trends: {str(e)}")


@router.get("/dashboard/category-breakdown")
async def get_category_breakdown(db: Session = Depends(get_db)):
    """
    Get breakdown of tickets by category.
    """
    try:
        stats = ticket_service.get_ticket_stats(db)
        
        return {
            "categories": [
                {"name": "User Error", "count": stats["by_category"]["user_error"]},
                {"name": "System Issue", "count": stats["by_category"]["system_issue"]},
                {"name": "Feature Request", "count": stats["by_category"]["feature_request"]}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting category breakdown: {str(e)}")


@router.get("/dashboard/priority-distribution")
async def get_priority_distribution(db: Session = Depends(get_db)):
    """
    Get distribution of tickets by priority.
    """
    try:
        stats = ticket_service.get_ticket_stats(db)
        
        return {
            "priorities": [
                {"level": "Critical", "count": stats["by_priority"]["critical"]},
                {"level": "High", "count": stats["by_priority"]["high"]},
                {"level": "Medium", "count": stats["by_priority"]["medium"]},
                {"level": "Low", "count": stats["by_priority"]["low"]}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting priority distribution: {str(e)}")


@router.get("/dashboard/response-time")
async def get_response_time_metrics(db: Session = Depends(get_db)):
    """
    Get average response and resolution times.
    """
    try:
        # Get resolved tickets
        resolved_tickets = db.query(TicketDB).filter(
            TicketDB.resolved_at.isnot(None)
        ).all()
        
        if not resolved_tickets:
            return {
                "average_resolution_hours": 0,
                "median_resolution_hours": 0,
                "total_resolved": 0
            }
        
        # Calculate resolution times
        resolution_times = []
        for ticket in resolved_tickets:
            time_diff = ticket.resolved_at - ticket.created_at
            hours = time_diff.total_seconds() / 3600
            resolution_times.append(hours)
        
        avg_time = sum(resolution_times) / len(resolution_times)
        resolution_times.sort()
        median_time = resolution_times[len(resolution_times) // 2]
        
        return {
            "average_resolution_hours": round(avg_time, 2),
            "median_resolution_hours": round(median_time, 2),
            "total_resolved": len(resolved_tickets),
            "fastest_resolution_hours": round(min(resolution_times), 2),
            "slowest_resolution_hours": round(max(resolution_times), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating response times: {str(e)}")


@router.get("/dashboard/recent-tickets")
async def get_recent_tickets(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get most recent tickets.
    """
    try:
        tickets = ticket_service.get_tickets(db, skip=0, limit=limit)
        return {"tickets": tickets, "count": len(tickets)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recent tickets: {str(e)}")
