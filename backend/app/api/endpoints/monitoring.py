"""
System monitoring endpoint for detecting system-generated issues.
This simulates automated monitoring and creates tickets for detected issues.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.ticket_service import ticket_service
from app.models.ticket import TicketCreate
from datetime import datetime
from typing import Dict, Any, List, Optional
import random

# Try to import psutil for real system monitoring
logger = logging.getLogger(__name__)

# Try to import psutil at module load time
try:
    import psutil
    PSUTIL_AVAILABLE = True
    logger.info("psutil available - real system monitoring enabled")
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available. System monitoring will use simulated data. Install with: pip install psutil")

def check_psutil_available():
    """Check if psutil is available (runtime check)."""
    try:
        import psutil
        return True
    except ImportError:
        return False

router = APIRouter()

# Store current metrics to simulate gradual changes (like real monitoring)
_current_metrics = {
    "cpu_usage": 45.0,
    "memory_usage": 62.0,
    "disk_usage": 78.0,
    "response_time": 1200.0
}

# Simulated system metrics (in production, these would come from real monitoring tools)
def get_mock_system_metrics() -> List[Dict[str, Any]]:
    """
    Simulate system health checks with gradual changes (more realistic).
    In production, this would integrate with:
    - Prometheus, Grafana, Datadog, etc.
    - Windows Performance Counters
    - Linux /proc filesystem
    - Cloud provider monitoring (AWS CloudWatch, Azure Monitor)
    """
    global _current_metrics
    
    # Simulate gradual changes (like real monitoring systems)
    # Each metric changes by a small random amount (±2-5%)
    _current_metrics["cpu_usage"] = max(10, min(100, _current_metrics["cpu_usage"] + random.uniform(-3, 3)))
    _current_metrics["memory_usage"] = max(20, min(100, _current_metrics["memory_usage"] + random.uniform(-2, 2)))
    _current_metrics["disk_usage"] = max(50, min(100, _current_metrics["disk_usage"] + random.uniform(-1, 1)))
    _current_metrics["response_time"] = max(200, min(5000, _current_metrics["response_time"] + random.uniform(-100, 100)))
    
    return [
        {
            "service": "database_server",
            "metric": "cpu_usage",
            "value": round(_current_metrics["cpu_usage"], 1),
            "threshold": 85,
            "unit": "percent",
            "severity_multiplier": 1.2
        },
        {
            "service": "web_application",
            "metric": "memory_usage",
            "value": round(_current_metrics["memory_usage"], 1),
            "threshold": 85,
            "unit": "percent",
            "severity_multiplier": 1.1
        },
        {
            "service": "file_server",
            "metric": "disk_usage",
            "value": round(_current_metrics["disk_usage"], 1),
            "threshold": 90,
            "unit": "percent",
            "severity_multiplier": 1.5
        },
        {
            "service": "backup_service",
            "metric": "response_time",
            "value": round(_current_metrics["response_time"], 0),
            "threshold": 2000,
            "unit": "milliseconds",
            "severity_multiplier": 1.0
        }
    ]


@router.post("/check-systems")
async def check_system_health(
    db: Session = Depends(get_db),
    auto_create_tickets: bool = True
):
    """
    Perform system health monitoring and auto-create tickets for detected issues.
    
    This endpoint simulates what an automated monitoring system does:
    1. Checks various system metrics (CPU, memory, disk, response times)
    2. Compares against thresholds
    3. Auto-creates tickets when thresholds are exceeded
    4. Returns summary of findings
    
    **Safety Note**: All operations are simulated/mocked for hackathon demonstration.
    Real deployment would integrate with actual monitoring tools.
    
    Args:
        auto_create_tickets: If True, automatically create tickets for detected issues
        
    Returns:
        Summary of system checks and any tickets created
    """
    logger.info("Starting automated system health check...")
    
    issues_detected = []
    tickets_created = []
    system_checks = get_mock_system_metrics()
    
    for check in system_checks:
        status = "healthy"
        issue_detected = False
        
        # Check if metric exceeds threshold
        if check["value"] > check["threshold"]:
            issue_detected = True
            severity_ratio = check["value"] / check["threshold"]
            
            # Determine severity level
            if severity_ratio > 1.2:
                severity = "critical"
                priority = 1
            elif severity_ratio > 1.1:
                severity = "high"
                priority = 2
            else:
                severity = "medium"
                priority = 3
            
            status = f"{severity}_issue"
            
            # Create detailed issue description
            description = f"""
**System Monitoring Alert**

Service: {check['service']}
Metric: {check['metric']}
Current Value: {check['value']}{check['unit']}
Threshold: {check['threshold']}{check['unit']}
Severity: {severity.upper()}

**Detected At**: {datetime.utcnow().isoformat()}

**Automated Analysis**:
The system has detected that {check['metric']} on {check['service']} has exceeded 
the configured threshold by {((check['value'] / check['threshold'] - 1) * 100):.1f}%.

**Recommended Actions**:
1. Investigate current workload on {check['service']}
2. Check for resource-intensive processes
3. Review recent changes or deployments
4. Consider scaling resources if issue persists

**Note**: This is an automatically generated ticket from system monitoring.
            """.strip()
            
            issue_info = {
                "service": check["service"],
                "metric": check["metric"],
                "current_value": check["value"],
                "threshold": check["threshold"],
                "unit": check["unit"],
                "severity": severity,
                "priority": priority,
                "exceeded_by_percent": ((check["value"] / check["threshold"] - 1) * 100)
            }
            
            issues_detected.append(issue_info)
            
            # Auto-create ticket if enabled
            if auto_create_tickets:
                try:
                    ticket_data = TicketCreate(
                        title=f"[SYSTEM ALERT] High {check['metric']} on {check['service']}",
                        description=description,
                        user_email="system-monitor@autoops.ai",  # System-generated
                        priority=priority
                    )
                    
                    ticket = ticket_service.create_ticket(db, ticket_data)
                    
                    tickets_created.append({
                        "ticket_id": ticket.id,
                        "ticket_number": f"TKT-{ticket.id}",
                        "severity": severity,
                        "service": check["service"],
                        "created_at": ticket.created_at.isoformat() if ticket.created_at else None
                    })
                    
                    logger.warning(
                        f"Auto-created ticket {ticket.id} for {check['service']} "
                        f"{check['metric']} ({severity} severity)"
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to create ticket for {check['service']}: {e}")
        
        # Log all checks (both healthy and unhealthy)
        logger.info(
            f"System check: {check['service']} - {check['metric']}: "
            f"{check['value']}{check['unit']} (threshold: {check['threshold']}) - {status}"
        )
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks_performed": len(system_checks),
        "issues_detected": len(issues_detected),
        "tickets_created": len(tickets_created),
        "status": "completed",
        "summary": {
            "healthy_services": len(system_checks) - len(issues_detected),
            "unhealthy_services": len(issues_detected)
        },
        "details": {
            "issues": issues_detected,
            "tickets": tickets_created
        }
    }
    
    logger.info(
        f"System health check completed: {len(issues_detected)} issues found, "
        f"{len(tickets_created)} tickets created"
    )
    
    return result


@router.get("/simulate-crash")
async def simulate_application_crash(
    app_name: str = "docker-desktop",
    error_code: str = "0xC0000005",
    db: Session = Depends(get_db)
):
    """
    Simulate an application crash detection and auto-create ticket.
    
    This demonstrates how the system would handle crash detection from:
    - Windows Event Viewer
    - Application crash dumps
    - Log file monitoring
    - Process monitoring tools
    
    **Safety Note**: This only simulates a crash. No real applications are affected.
    
    Args:
        app_name: Name of the application that "crashed"
        error_code: Simulated error code (Windows-style)
        
    Returns:
        Details of the auto-created ticket
    """
    logger.info(f"Simulating crash detection for application: {app_name}")
    
    # Simulate realistic crash log
    crash_timestamp = datetime.utcnow()
    crash_log = f"""
**Application Crash Detected**

Application: {app_name}
Event Type: Application Crash
Detection Time: {crash_timestamp.isoformat()}

**Error Details**:
- Error Code: {error_code} (Access Violation)
- Process ID: {random.randint(1000, 9999)}
- Thread ID: {random.randint(100, 999)}
- Module: {app_name}.exe
- Fault Address: 0x{random.randint(100000, 999999):X}

**System Context**:
- OS: Windows 11 Professional
- Memory: 16GB
- CPU: Intel Core i7
- Last Known State: Running normally

**Stack Trace** (Simulated):
```
{app_name}.exe!MainFunction+0x123
{app_name}.exe!ProcessRequest+0x456
{app_name}.exe!HandleEvent+0x789
kernel32.dll!BaseThreadInitThunk+0x14
ntdll.dll!RtlUserThreadStart+0x21
```

**Automated Recommendation**:
1. Check Windows Event Viewer for additional details
2. Review recent application updates
3. Verify system resources (RAM, disk space)
4. Consider reinstalling or updating {app_name}
5. Check for conflicting software

**Note**: This is a simulated crash for demonstration purposes. 
In production, this would be detected from real system logs.
    """.strip()
    
    try:
        ticket_data = TicketCreate(
            title=f"[CRASH DETECTED] {app_name} Application Crash",
            description=crash_log,
            user_email="crash-monitor@autoops.ai",
            priority=1  # Crashes are high priority
        )
        
        ticket = ticket_service.create_ticket(db, ticket_data)
        
        logger.warning(f"Auto-created ticket {ticket.id} for {app_name} crash")
        
        return {
            "status": "success",
            "detection_type": "application_crash",
            "application": app_name,
            "error_code": error_code,
            "ticket_id": ticket.id,
            "ticket_number": f"TKT-{ticket.id}",
            "auto_created": True,
            "severity": "high",
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
            "message": f"Ticket {ticket.id} created automatically from crash detection",
            "next_steps": [
                "Ticket assigned to IT support queue",
                "Automated diagnostics will be run",
                "User will be notified of troubleshooting steps"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to create crash ticket: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create crash detection ticket: {str(e)}"
        )


@router.get("/sample-logs")
async def get_sample_system_logs():
    """
    Provide sample system logs demonstrating what the monitoring system analyzes.
    
    This endpoint shows the types of system signals that trigger automatic detection.
    These examples demonstrate the log patterns the AI learns to recognize.
    
    **Use Case**: Documentation and demonstration of monitoring capabilities.
    """
    sample_logs = {
        "high_cpu_logs": {
            "description": "CPU usage exceeding threshold triggers investigation",
            "threshold": "85% for more than 5 minutes",
            "sample_entries": [
                "[2025-01-27 10:15:23] WARNING: CPU usage at 92% for process 'docker.exe' (PID: 4532)",
                "[2025-01-27 10:15:24] WARNING: System response time degraded to 3.2s (normal: 0.5s)",
                "[2025-01-27 10:15:25] ERROR: Process 'chrome.exe' not responding (PID: 8765)",
                "[2025-01-27 10:15:30] INFO: High CPU sustained for 6 minutes, creating alert"
            ],
            "automated_action": "Create ticket, suggest process investigation"
        },
        "disk_space_logs": {
            "description": "Low disk space can cause system failures",
            "threshold": "90% disk usage or less than 10GB free",
            "sample_entries": [
                "[2025-01-27 09:30:15] WARNING: Disk C: usage at 94% (12GB free of 500GB)",
                "[2025-01-27 09:30:16] INFO: Temp files consuming 8GB in C:\\Windows\\Temp",
                "[2025-01-27 09:30:17] WARNING: Low disk space affecting system performance",
                "[2025-01-27 09:30:18] ERROR: Unable to create pagefile due to low disk space"
            ],
            "automated_action": "Create ticket, suggest disk cleanup procedures"
        },
        "network_logs": {
            "description": "Network connectivity issues affecting users",
            "threshold": "3 or more failures in 5 minutes",
            "sample_entries": [
                "[2025-01-27 11:20:10] ERROR: VPN connection attempt failed - timeout after 30s",
                "[2025-01-27 11:20:15] ERROR: DNS resolution failed for internal.company.com",
                "[2025-01-27 11:20:20] WARNING: Network adapter 'Wi-Fi' disconnected unexpectedly",
                "[2025-01-27 11:20:25] ERROR: Cannot reach domain controller at 10.0.0.5"
            ],
            "automated_action": "Create ticket, run network diagnostics"
        },
        "application_crash_logs": {
            "description": "Application crashes requiring immediate attention",
            "threshold": "Any application crash event",
            "sample_entries": [
                "[2025-01-27 14:45:30] CRITICAL: Application 'vscode.exe' crashed unexpectedly",
                "[2025-01-27 14:45:30] ERROR: Exception 0xC0000005 (Access Violation) at 0x7FFE1234ABCD",
                "[2025-01-27 14:45:31] INFO: Crash dump created: C:\\dumps\\vscode_crash_20250127.dmp",
                "[2025-01-27 14:45:32] WARNING: Process terminated abnormally (exit code: -1)"
            ],
            "automated_action": "Create high-priority ticket, collect crash dump"
        },
        "service_failure_logs": {
            "description": "Critical services not responding",
            "threshold": "Service down for more than 2 minutes",
            "sample_entries": [
                "[2025-01-27 16:10:00] CRITICAL: Service 'DatabaseService' not responding",
                "[2025-01-27 16:10:15] ERROR: Health check failed: Connection timeout",
                "[2025-01-27 16:10:30] ERROR: Dependent services affected: WebApp, API Gateway",
                "[2025-01-27 16:10:45] CRITICAL: Service restart attempt failed"
            ],
            "automated_action": "Create critical ticket, attempt service restart, escalate if needed"
        },
        "memory_leak_logs": {
            "description": "Application consuming excessive memory over time",
            "threshold": "Memory growth > 500MB/hour for single process",
            "sample_entries": [
                "[2025-01-27 08:00:00] INFO: Process 'webapp.exe' using 2.1GB memory",
                "[2025-01-27 09:00:00] WARNING: Process 'webapp.exe' using 2.8GB memory (+700MB)",
                "[2025-01-27 10:00:00] ERROR: Process 'webapp.exe' using 3.6GB memory (+800MB)",
                "[2025-01-27 11:00:00] CRITICAL: Process 'webapp.exe' using 4.5GB memory, suspected leak"
            ],
            "automated_action": "Create ticket, recommend process restart, memory analysis"
        }
    }
    
    return {
        "description": "Sample system logs that trigger automatic issue detection and ticket creation",
        "log_categories": list(sample_logs.keys()),
        "total_patterns": len(sample_logs),
        "sample_logs": sample_logs,
        "detection_methods": {
            "real_time_monitoring": "Continuous log streaming and analysis",
            "threshold_based": "Alert when metrics exceed defined thresholds",
            "pattern_matching": "AI recognizes known problem patterns",
            "anomaly_detection": "ML models detect unusual behavior",
            "correlation": "Links related events across multiple services"
        },
        "integration_points": {
            "windows": "Event Viewer, Performance Counters, WMI",
            "linux": "/proc filesystem, syslog, journalctl",
            "cloud": "CloudWatch (AWS), Azure Monitor, GCP Logging",
            "apm_tools": "Datadog, New Relic, Prometheus, Grafana"
        }
    }


@router.get("/stats")
async def get_real_system_stats():
    """
    Get real system statistics using psutil (Task Manager data).
    
    Simple implementation - just CPU, RAM, and Disk usage percentages.
    
    Returns:
        Real system metrics: CPU %, RAM %, Disk %
    """
    # Check psutil availability at runtime
    if not check_psutil_available():
        raise HTTPException(
            status_code=503,
            detail="psutil not available. Please install psutil: python -m pip install psutil==5.9.8"
        )
    
    # Import psutil and platform
    import psutil
    import platform
    
    try:
        # CPU % - use interval=1 for accurate reading
        cpu = psutil.cpu_percent(interval=1)
        
        # RAM % (cross-platform)
        memory = psutil.virtual_memory()
        ram = memory.percent
        
        # Get disk usage percentage
        if platform.system() == 'Windows':
            disk_usage = psutil.disk_usage('C:\\')
        else:
            disk_usage = psutil.disk_usage('/')
        
        # Calculate network activity (bytes per second, normalized to percentage)
        # Get current network stats
        network_io = psutil.net_io_counters()
        
        # For network, we'll show a simplified activity indicator
        # This isn't a true "percentage" but shows relative activity
        # Max expected: 100 Mbps = 12.5 MB/s, we'll use this as baseline
        current_time = datetime.utcnow().timestamp()
        
        # Store previous values for rate calculation
        if not hasattr(get_real_system_stats, '_last_network'):
            get_real_system_stats._last_network = {
                'bytes': network_io.bytes_sent + network_io.bytes_recv,
                'time': current_time
            }
            network_percent = 0
        else:
            time_diff = current_time - get_real_system_stats._last_network['time']
            if time_diff > 0:
                bytes_diff = (network_io.bytes_sent + network_io.bytes_recv) - get_real_system_stats._last_network['bytes']
                bytes_per_sec = bytes_diff / time_diff
                # Normalize to percentage (assuming 100 Mbps max = 12.5 MB/s)
                network_percent = min(100, (bytes_per_sec / (12.5 * 1024 * 1024)) * 100)
            else:
                network_percent = 0
            get_real_system_stats._last_network = {
                'bytes': network_io.bytes_sent + network_io.bytes_recv,
                'time': current_time
            }
        
        return {
            "cpu": round(cpu, 1),
            "ram": round(ram, 1),
            "disk": round(disk_usage.percent, 1),
            "network": round(network_percent, 1),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "psutil",
            "details": {
                "cpu_cores": psutil.cpu_count(),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_total_gb": round(disk_usage.total / (1024**3), 2),
                "disk_used_gb": round(disk_usage.used / (1024**3), 2),
                "disk_free_gb": round(disk_usage.free / (1024**3), 2)
            }
        }
    except Exception as e:
        logger.error(f"Error getting system stats with psutil: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve system statistics: {str(e)}"
        )


@router.get("/metrics")
async def get_system_metrics():
    """
    Get current system metrics for real-time monitoring display.
    
    Tries to use real psutil data first, falls back to simulated data if unavailable.
    
    Returns:
        Current system metrics including CPU, Memory, Disk, and Network usage
    """
    logger.info("Fetching system metrics for monitoring dashboard...")
    
    # Try to get real system stats first (check at runtime)
    if check_psutil_available():
        try:
            real_stats = await get_real_system_stats()
            # Convert to the format expected by frontend
            metrics = {
                "cpu": real_stats["cpu"],
                "memory": real_stats["ram"],
                "disk": real_stats["disk"],
                "network": real_stats["network"]
            }
            
            # Create checks array for logs
            all_checks = [
                {
                    "service": "system",
                    "metric": "cpu_usage",
                    "value": metrics["cpu"],
                    "threshold": 85,
                    "unit": "percent",
                    "status": "healthy" if metrics["cpu"] <= 85 else "unhealthy",
                    "severity": "critical" if metrics["cpu"] > 85 * 1.2 else 
                               "high" if metrics["cpu"] > 85 * 1.1 else
                               "medium" if metrics["cpu"] > 85 else "normal"
                },
                {
                    "service": "system",
                    "metric": "memory_usage",
                    "value": metrics["memory"],
                    "threshold": 85,
                    "unit": "percent",
                    "status": "healthy" if metrics["memory"] <= 85 else "unhealthy",
                    "severity": "critical" if metrics["memory"] > 85 * 1.2 else 
                               "high" if metrics["memory"] > 85 * 1.1 else
                               "medium" if metrics["memory"] > 85 else "normal"
                },
                {
                    "service": "system",
                    "metric": "disk_usage",
                    "value": metrics["disk"],
                    "threshold": 90,
                    "unit": "percent",
                    "status": "healthy" if metrics["disk"] <= 90 else "unhealthy",
                    "severity": "critical" if metrics["disk"] > 90 * 1.2 else 
                               "high" if metrics["disk"] > 90 * 1.1 else
                               "medium" if metrics["disk"] > 90 else "normal"
                }
            ]
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics,
                "checks": all_checks,
                "status": "active",
                "source": "psutil",
                "real_data": True
            }
        except Exception as e:
            logger.warning(f"Failed to get real system stats, using simulated: {e}")
            # Fall through to simulated data
    
    # Fallback to simulated data
    system_checks = get_mock_system_metrics()
    
    # Extract metrics by type - use the actual values from checks
    metrics = {
        "cpu": 0,
        "memory": 0,
        "disk": 0,
        "network": 0
    }
    
    # Map service metrics to display metrics
    for check in system_checks:
        metric_name = check["metric"]
        value = check["value"]
        
        if metric_name == "cpu_usage":
            metrics["cpu"] = value
        elif metric_name == "memory_usage":
            metrics["memory"] = value
        elif metric_name == "disk_usage":
            metrics["disk"] = value
        elif metric_name == "response_time":
            # Convert response time to network activity percentage
            # Normalize: 0-2000ms = 0-50%, 2000-5000ms = 50-100%
            normalized = min(100, max(0, ((value - 500) / 4500) * 100))
            metrics["network"] = normalized
    
    # Get all checks with their status for logs
    all_checks = []
    for check in system_checks:
        is_healthy = check["value"] <= check["threshold"]
        severity = "normal"
        if not is_healthy:
            severity_ratio = check["value"] / check["threshold"]
            if severity_ratio > 1.2:
                severity = "critical"
            elif severity_ratio > 1.1:
                severity = "high"
            else:
                severity = "medium"
        
        all_checks.append({
            "service": check["service"],
            "metric": check["metric"],
            "value": check["value"],
            "threshold": check["threshold"],
            "unit": check["unit"],
            "status": "healthy" if is_healthy else "unhealthy",
            "severity": severity
        })
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics,
        "checks": all_checks,
        "status": "active",
        "source": "simulated",
        "real_data": False
    }


@router.get("/system-status")
async def get_system_status(db: Session = Depends(get_db)):
    """
    Get current system monitoring status and statistics.
    
    Shows:
    - Active monitoring status
    - Recent alerts
    - Ticket creation statistics
    - System health overview
    """
    # Get recent system-generated tickets
    recent_tickets = db.query(ticket_service.model).filter(
        ticket_service.model.user_email.like("%@autoops.ai")
    ).order_by(
        ticket_service.model.created_at.desc()
    ).limit(10).all()
    
    ticket_stats = {
        "total_system_tickets": len(recent_tickets),
        "open_tickets": len([t for t in recent_tickets if t.status == "open"]),
        "in_progress_tickets": len([t for t in recent_tickets if t.status == "in_progress"]),
        "resolved_tickets": len([t for t in recent_tickets if t.status == "resolved"])
    }
    
    recent_ticket_summaries = [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "priority": t.priority,
            "created_at": t.created_at.isoformat() if t.created_at else None
        }
        for t in recent_tickets[:5]
    ]
    
    return {
        "monitoring_status": "active",
        "last_check": datetime.utcnow().isoformat(),
        "ticket_statistics": ticket_stats,
        "recent_alerts": recent_ticket_summaries,
        "capabilities": {
            "system_health_checks": True,
            "crash_detection": True,
            "performance_monitoring": True,
            "auto_ticket_creation": True,
            "log_analysis": True
        },
        "message": "System monitoring is operational and actively detecting issues"
    }
