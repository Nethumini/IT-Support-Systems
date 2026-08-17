"""
Action Execution API Endpoints
Handles automated remediation actions with user approval flow.
"""
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from app.services.agents.action_executor_agent import (
    get_action_executor,
    ActionCategory,
    ActionStatus
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/actions", tags=["actions"])


# ═══════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════════════════

class ActionRequestCreate(BaseModel):
    action_id: str
    parameters: Dict[str, Any] = {}
    user_email: str
    ticket_id: Optional[int] = None


class ActionApproval(BaseModel):
    request_id: str
    user_email: str
    approved: bool


class ActionSuggestionRequest(BaseModel):
    issue_description: str
    category: Optional[str] = None


class ActionResponse(BaseModel):
    success: bool
    message: str
    request_id: Optional[str] = None
    action: Optional[Dict] = None
    result: Optional[Dict] = None
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/available")
async def get_available_actions(
    category: Optional[str] = Query(None, description="Filter by category")
) -> Dict[str, Any]:
    """
    Get list of all available actions.
    Optionally filter by category: process, cleanup, network, service, diagnostics, browser
    """
    executor = get_action_executor()
    
    cat_filter = None
    if category:
        try:
            cat_filter = ActionCategory(category)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Valid options: {[c.value for c in ActionCategory]}"
            )
    
    actions = executor.get_available_actions(cat_filter)
    
    return {
        "success": True,
        "actions": actions,
        "categories": [c.value for c in ActionCategory]
    }


@router.get("/action/{action_id}")
async def get_action_details(action_id: str) -> Dict[str, Any]:
    """Get details of a specific action"""
    executor = get_action_executor()
    action = executor.get_action_by_id(action_id)
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    return {
        "success": True,
        "action": {
            "id": action.id,
            "name": action.name,
            "description": action.description,
            "category": action.category.value,
            "risk_level": action.risk_level.value,
            "parameters": action.parameters,
            "requires_elevation": action.requires_elevation,
            "estimated_duration": action.estimated_duration,
            "success_message": action.success_message,
            "failure_message": action.failure_message
        }
    }


@router.post("/suggest")
async def suggest_actions(request: ActionSuggestionRequest) -> Dict[str, Any]:
    """
    Get suggested actions based on issue description.
    The AI analyzes the issue and suggests relevant remediation actions.
    Uses pattern matching first, then LLM classification as fallback for complex issues.
    """
    executor = get_action_executor()
    
    # Use the LLM-enhanced method for better accuracy
    suggestions = await executor.get_suggested_actions_with_llm_fallback(
        request.issue_description,
        context=request.category or ""
    )
    
    return {
        "success": True,
        "suggestions": suggestions,
        "count": len(suggestions)
    }


@router.get("/proactive")
async def get_proactive_suggestions() -> Dict[str, Any]:
    """
    Get proactive action suggestions based on current system metrics.
    These are actions that could prevent issues before users report them.
    
    This endpoint monitors:
    - CPU usage
    - Memory usage
    - Disk space
    - Network latency
    
    And suggests preventive actions when metrics exceed thresholds.
    """
    executor = get_action_executor()
    
    suggestions = await executor.get_dashboard_proactive_actions()
    
    return {
        "success": True,
        "suggestions": suggestions,
        "count": len(suggestions),
        "is_proactive": True,
        "message": "Actions recommended based on current system state" if suggestions else "System metrics are healthy"
    }


@router.post("/request")
async def create_action_request(request: ActionRequestCreate) -> ActionResponse:
    """
    Create a new action request (pending user approval).
    This does NOT execute the action - user must approve first.
    """
    logger.info(f"[ACTION-REQUEST] Received: action_id={request.action_id}, user={request.user_email}, params={request.parameters}, ticket={request.ticket_id}")
    executor = get_action_executor()
    
    # Validate action exists
    action = executor.get_action_by_id(request.action_id)
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{request.action_id}' not found")
    
    # Create pending request
    action_request = executor.create_action_request(
        action_id=request.action_id,
        parameters=request.parameters,
        user_email=request.user_email,
        ticket_id=request.ticket_id
    )
    
    if not action_request:
        raise HTTPException(status_code=400, detail="Failed to create action request. Check parameters.")
    
    logger.info(f"Action request created: {action_request.id} for {request.action_id}")
    
    return ActionResponse(
        success=True,
        message=f"Action '{action.name}' pending approval",
        request_id=action_request.id,
        action={
            "id": action.id,
            "name": action.name,
            "description": action.description,
            "risk_level": action.risk_level.value,
            "parameters": request.parameters,
            "estimated_duration": action.estimated_duration
        }
    )


@router.post("/approve")
async def approve_or_cancel_action(approval: ActionApproval) -> ActionResponse:
    """
    Approve or cancel a pending action.
    If approved, the action will be executed immediately.
    """
    executor = get_action_executor()
    
    if approval.approved:
        # Approve the action
        if not executor.approve_action(approval.request_id, approval.user_email):
            raise HTTPException(status_code=404, detail="Action request not found or unauthorized")
        
        # Execute immediately after approval
        result = await executor.execute_action(approval.request_id)
        
        return ActionResponse(
            success=result.get("success", False),
            message=result.get("message", "Action executed"),
            request_id=approval.request_id,
            result=result
        )
    else:
        # Cancel the action
        if not executor.cancel_action(approval.request_id, approval.user_email):
            raise HTTPException(status_code=404, detail="Action request not found or unauthorized")
        
        return ActionResponse(
            success=True,
            message="Action cancelled",
            request_id=approval.request_id
        )


@router.post("/execute/{action_id}")
async def execute_action_directly(
    action_id: str,
    user_email: str = Query(..., description="User email"),
    ticket_id: Optional[int] = Query(None)
) -> ActionResponse:
    """
    Quick execute: Create, approve, and execute an action in one call.
    Use this for low-risk diagnostic actions.
    For higher risk actions, use the request/approve flow.
    """
    executor = get_action_executor()
    
    # No parameters needed for direct execution
    parameters = {}
    
    # Check action exists and risk level
    action = executor.get_action_by_id(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    # Only allow direct execution for low-risk actions
    if action.risk_level.value != "low":
        raise HTTPException(
            status_code=403,
            detail=f"Action '{action.name}' requires approval (risk level: {action.risk_level.value}). Use /request and /approve endpoints."
        )
    
    # Create and immediately approve
    action_request = executor.create_action_request(
        action_id=action_id,
        parameters=parameters,
        user_email=user_email,
        ticket_id=ticket_id
    )
    
    if not action_request:
        raise HTTPException(status_code=400, detail="Failed to create action request")
    
    executor.approve_action(action_request.id, user_email)
    
    # Execute
    result = await executor.execute_action(action_request.id)
    
    # Get follow-up action suggestions based on the result
    followup_actions = []
    if result.get("success") and result.get("output"):
        try:
            output_str = result.get("output", "")
            if isinstance(output_str, dict):
                output_str = str(output_str)
            followup_actions = executor.get_followup_actions(action_id, output_str)
        except Exception as e:
            logger.warning(f"Failed to get follow-up actions: {e}")
    
    return ActionResponse(
        success=result.get("success", False),
        message=result.get("message", "Action executed"),
        request_id=action_request.id,
        result={
            **result,
            "followup_actions": followup_actions  # Include follow-up suggestions
        }
    )


@router.get("/pending")
async def get_pending_actions(
    user_email: str = Query(..., description="User email")
) -> Dict[str, Any]:
    """Get all pending actions for a user"""
    executor = get_action_executor()
    
    pending = []
    for request_id, request in executor.pending_actions.items():
        if request.user_email == user_email:
            action = executor.get_action_by_id(request.action_id)
            pending.append({
                "request_id": request.id,
                "action_id": request.action_id,
                "action_name": action.name if action else "Unknown",
                "parameters": request.parameters,
                "status": request.status.value,
                "created_at": request.created_at.isoformat(),
                "ticket_id": request.ticket_id
            })
    
    return {
        "success": True,
        "pending_actions": pending,
        "count": len(pending)
    }


@router.get("/history")
async def get_action_history(
    user_email: str = Query(..., description="User email"),
    limit: int = Query(20, description="Max results")
) -> Dict[str, Any]:
    """Get action execution history for a user"""
    executor = get_action_executor()
    
    history = []
    for request in reversed(executor.action_history):
        if request.user_email == user_email:
            action = executor.get_action_by_id(request.action_id)
            history.append({
                "request_id": request.id,
                "action_id": request.action_id,
                "action_name": action.name if action else "Unknown",
                "parameters": request.parameters,
                "status": request.status.value,
                "created_at": request.created_at.isoformat(),
                "executed_at": request.executed_at.isoformat() if request.executed_at else None,
                "completed_at": request.completed_at.isoformat() if request.completed_at else None,
                "result": request.result,
                "error": request.error,
                "ticket_id": request.ticket_id
            })
            
            if len(history) >= limit:
                break
    
    return {
        "success": True,
        "history": history,
        "count": len(history)
    }


# ═══════════════════════════════════════════════════════════════════════════
# Quick Diagnostic Actions (no approval needed)
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/diagnose/processes")
async def diagnose_top_processes(
    user_email: str = Query(..., description="User email")
) -> Dict[str, Any]:
    """Quick diagnostic: Get top processes by CPU usage"""
    executor = get_action_executor()
    
    action_request = executor.create_action_request(
        action_id="list_top_processes",
        parameters={},
        user_email=user_email
    )
    
    if action_request:
        executor.approve_action(action_request.id, user_email)
        result = await executor.execute_action(action_request.id)
        return {
            "success": result.get("success", False),
            "processes": result.get("output", []),
            "message": result.get("message")
        }
    
    return {"success": False, "error": "Failed to execute diagnostic"}


@router.get("/diagnose/system")
async def diagnose_system_health(
    user_email: str = Query(..., description="User email")
) -> Dict[str, Any]:
    """Quick diagnostic: Get system health (CPU, Memory, Disk)"""
    executor = get_action_executor()
    
    action_request = executor.create_action_request(
        action_id="check_system_health",
        parameters={},
        user_email=user_email
    )
    
    if action_request:
        executor.approve_action(action_request.id, user_email)
        result = await executor.execute_action(action_request.id)
        return {
            "success": result.get("success", False),
            "health": result.get("output", {}),
            "message": result.get("message")
        }
    
    return {"success": False, "error": "Failed to execute diagnostic"}


@router.get("/diagnose/network")
async def diagnose_network(
    user_email: str = Query(..., description="User email")
) -> Dict[str, Any]:
    """Quick diagnostic: Test network connectivity"""
    executor = get_action_executor()
    
    action_request = executor.create_action_request(
        action_id="test_connectivity",
        parameters={},
        user_email=user_email
    )
    
    if action_request:
        executor.approve_action(action_request.id, user_email)
        result = await executor.execute_action(action_request.id)
        return {
            "success": result.get("success", False),
            "connectivity": result.get("output", {}),
            "message": result.get("message")
        }
    
    return {"success": False, "error": "Failed to execute diagnostic"}


@router.get("/diagnose/disk")
async def diagnose_disk_space(
    user_email: str = Query(..., description="User email")
) -> Dict[str, Any]:
    """Quick diagnostic: Check disk space"""
    executor = get_action_executor()
    
    action_request = executor.create_action_request(
        action_id="check_disk_space",
        parameters={},
        user_email=user_email
    )
    
    if action_request:
        executor.approve_action(action_request.id, user_email)
        result = await executor.execute_action(action_request.id)
        return {
            "success": result.get("success", False),
            "disk_info": result.get("output", []),
            "message": result.get("message")
        }
    
    return {"success": False, "error": "Failed to execute diagnostic"}


# ═══════════════════════════════════════════════════════════════════════════
# Smart Analysis & Remediation
# ═══════════════════════════════════════════════════════════════════════════

class AnalyzeRequest(BaseModel):
    diagnostic_output: Dict[str, Any]
    diagnostic_type: str  # "processes", "system_health", "disk", "network"


@router.post("/analyze")
async def analyze_and_suggest(
    request: AnalyzeRequest,
    user_email: str = Query(..., description="User email")
) -> Dict[str, Any]:
    """
    Analyze diagnostic output and suggest specific remediation actions.
    This is the "smart" part - it looks at the data and recommends fixes.
    """
    executor = get_action_executor()
    suggestions = []
    analysis = []
    
    output = request.diagnostic_output
    diag_type = request.diagnostic_type
    
    if diag_type == "processes":
        # Analyze process list
        if isinstance(output, list):
            for proc in output:
                mem_mb = proc.get("WorkingSet64", 0) / (1024 * 1024) if proc.get("WorkingSet64") else 0
                cpu = proc.get("CPU", 0) or 0
                name = proc.get("Name", "Unknown")
                
                # Flag high memory processes
                if mem_mb > 500:
                    analysis.append({
                        "type": "warning",
                        "message": f"'{name}' is using {mem_mb:.0f} MB of memory",
                        "process": name,
                        "process_id": proc.get("Id")
                    })
                    suggestions.append({
                        "action_id": "kill_process_by_id",
                        "name": f"Kill {name} (PID: {proc.get('Id')})",
                        "description": f"Terminate {name} to free {mem_mb:.0f} MB of memory",
                        "risk_level": "medium",
                        "parameters": {"process_id": proc.get("Id")},
                        "impact": f"Will free approximately {mem_mb:.0f} MB of RAM"
                    })
                    
        # Always suggest memory optimization
        suggestions.append({
            "action_id": "optimize_memory",
            "name": "Optimize System Memory",
            "description": "Free up RAM by clearing working sets",
            "risk_level": "low",
            "parameters": {}
        })
        suggestions.append({
            "action_id": "stop_background_apps",
            "name": "Stop Background Apps",
            "description": "Close Teams, Slack, Discord, Spotify, etc.",
            "risk_level": "medium",
            "parameters": {}
        })
        
    elif diag_type == "system_health":
        # Parse system health text output
        if isinstance(output, str):
            if "Memory Used:" in output:
                try:
                    mem_pct = float(output.split("Memory Used:")[1].split("%")[0].strip())
                    if mem_pct > 85:
                        analysis.append({
                            "type": "critical",
                            "message": f"Memory usage is critically high at {mem_pct}%"
                        })
                        suggestions.append({
                            "action_id": "optimize_memory",
                            "name": "Optimize Memory (Recommended)",
                            "description": f"Memory is at {mem_pct}% - optimization needed",
                            "risk_level": "low",
                            "parameters": {},
                            "priority": "high"
                        })
                        suggestions.append({
                            "action_id": "stop_background_apps",
                            "name": "Stop Background Apps",
                            "description": "Close non-essential applications",
                            "risk_level": "medium",
                            "parameters": {}
                        })
                    elif mem_pct > 70:
                        analysis.append({
                            "type": "warning",
                            "message": f"Memory usage is elevated at {mem_pct}%"
                        })
                except:
                    pass
                    
            if "Disk Free:" in output:
                try:
                    disk_free = float(output.split("Disk Free:")[1].split("GB")[0].strip())
                    if disk_free < 10:
                        analysis.append({
                            "type": "critical",
                            "message": f"Disk space critically low: {disk_free} GB remaining"
                        })
                        suggestions.append({
                            "action_id": "clear_windows_temp",
                            "name": "Deep Clean Temp Files",
                            "description": "Remove temporary files to free space",
                            "risk_level": "low",
                            "parameters": {}
                        })
                        suggestions.append({
                            "action_id": "empty_recycle_bin",
                            "name": "Empty Recycle Bin",
                            "description": "Permanently delete recycled files",
                            "risk_level": "medium",
                            "parameters": {}
                        })
                except:
                    pass
                    
    elif diag_type == "network":
        if isinstance(output, str):
            if "Internet: False" in output or "DNS: False" in output:
                analysis.append({
                    "type": "critical",
                    "message": "Network connectivity issues detected"
                })
                suggestions.append({
                    "action_id": "flush_dns",
                    "name": "Flush DNS Cache",
                    "description": "Clear DNS resolver cache",
                    "risk_level": "low",
                    "parameters": {}
                })
                suggestions.append({
                    "action_id": "release_renew_ip",
                    "name": "Renew IP Address",
                    "description": "Get a fresh IP from DHCP",
                    "risk_level": "medium",
                    "parameters": {}
                })
                suggestions.append({
                    "action_id": "reset_winsock",
                    "name": "Reset Network Stack",
                    "description": "Complete network reset (requires restart)",
                    "risk_level": "high",
                    "parameters": {}
                })
    
    return {
        "success": True,
        "analysis": analysis,
        "suggested_actions": suggestions[:5],  # Top 5 suggestions
        "diagnostic_type": diag_type
    }


@router.post("/quick-fix/{issue_type}")
async def quick_fix(
    issue_type: str,
    user_email: str = Query(..., description="User email")
) -> Dict[str, Any]:
    """
    Execute a quick fix for common issues.
    Runs multiple related actions in sequence.
    """
    executor = get_action_executor()
    results = []
    
    if issue_type == "slow_computer":
        # Run a series of optimization actions
        actions_to_run = ["analyze_slow_performance", "optimize_memory", "clear_temp_files"]
        
    elif issue_type == "network_issues":
        actions_to_run = ["test_connectivity", "flush_dns"]
        
    elif issue_type == "disk_full":
        actions_to_run = ["check_disk_space", "clear_windows_temp", "empty_recycle_bin"]
        
    elif issue_type == "browser_slow":
        actions_to_run = ["clear_browser_cache", "clear_temp_files"]
        
    else:
        return {"success": False, "error": f"Unknown issue type: {issue_type}"}
    
    for action_id in actions_to_run:
        try:
            action_request = executor.create_action_request(
                action_id=action_id,
                parameters={},
                user_email=user_email
            )
            if action_request:
                executor.approve_action(action_request.id, user_email)
                result = await executor.execute_action(action_request.id)
                results.append({
                    "action": action_id,
                    "success": result.get("success", False),
                    "output": result.get("output"),
                    "message": result.get("message")
                })
        except Exception as e:
            results.append({
                "action": action_id,
                "success": False,
                "error": str(e)
            })
    
    return {
        "success": all(r.get("success") for r in results),
        "issue_type": issue_type,
        "actions_executed": len(results),
        "results": results
    }
