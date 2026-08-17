"""
Action Executor Agent - Automated Remediation System
Executes safe, whitelisted system actions with user permission.
"""
import logging
import subprocess
import platform
import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class ActionCategory(str, Enum):
    PROCESS = "process"
    CLEANUP = "cleanup"
    NETWORK = "network"
    SERVICE = "service"
    DIAGNOSTICS = "diagnostics"
    BROWSER = "browser"


class ActionRiskLevel(str, Enum):
    LOW = "low"          # Safe, read-only operations
    MEDIUM = "medium"    # May affect running apps
    HIGH = "high"        # System-level changes


class ActionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ActionDefinition:
    """Defines a safe, whitelisted action"""
    id: str
    name: str
    description: str
    category: ActionCategory
    risk_level: ActionRiskLevel
    command_template: str  # PowerShell command with {placeholders}
    parameters: List[Dict[str, Any]]  # Expected parameters
    requires_elevation: bool = False
    estimated_duration: int = 5  # seconds
    success_message: str = "Action completed successfully"
    failure_message: str = "Action failed"


@dataclass
class ActionRequest:
    """A request to execute an action"""
    id: str
    action_id: str
    parameters: Dict[str, Any]
    user_email: str
    ticket_id: Optional[int]
    status: ActionStatus
    created_at: datetime
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ActionExecutorAgent:
    """
    Executes safe, whitelisted system actions.
    Security-first approach with user approval required.
    """
    
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.pending_actions: Dict[str, ActionRequest] = {}
        self.action_history: List[ActionRequest] = []
        
        # Define all available actions (whitelist)
        self.actions = self._define_actions()
        
        logger.info(f"Action Executor Agent initialized with {len(self.actions)} actions")
    
    def _define_actions(self) -> Dict[str, ActionDefinition]:
        """Define all whitelisted safe actions"""
        actions = {}
        
        # # ═══════════════════════════════════════════════════════════════
        # # PROCESS MANAGEMENT
        # # ═══════════════════════════════════════════════════════════════
        # actions["kill_process"] = ActionDefinition(
        #     id="kill_process",
        #     name="End Process",
        #     description="Forcefully terminate a running process by name",
        #     category=ActionCategory.PROCESS,
        #     risk_level=ActionRiskLevel.MEDIUM,
        #     command_template='Stop-Process -Name "{process_name}" -Force -ErrorAction SilentlyContinue',
        #     parameters=[{
        #         "name": "process_name",
        #         "type": "string",
        #         "description": "Name of the process (without .exe)",
        #         "required": True,
        #         "allowed_values": [
        #             "chrome", "firefox", "msedge", "Code", "Teams", 
        #             "Slack", "Discord", "spotify", "Zoom", "notepad",
        #             "explorer", "outlook", "WINWORD", "EXCEL", "POWERPNT"
        #         ]
        #     }],
        #     success_message="Process '{process_name}' has been terminated",
        #     failure_message="Failed to terminate process '{process_name}'"
        # )
        
        actions["list_top_processes"] = ActionDefinition(
            id="list_top_processes",
            name="List Top Processes",
            description="Show processes using the most memory with termination suggestions",
            category=ActionCategory.DIAGNOSTICS,
            risk_level=ActionRiskLevel.LOW,
            command_template='$procs = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10 Name, Id, @{N="CPU";E={[math]::Round($_.CPU,1)}}, @{N="MemMB";E={[math]::Round($_.WorkingSet64/1MB,0)}}; $procs | ConvertTo-Json',
            parameters=[],
            success_message="Retrieved top 10 processes - click on a process to terminate it",
            failure_message="Failed to retrieve process list"
        )
        
        actions["get_process_details"] = ActionDefinition(
            id="get_process_details",
            name="Get Process Details",
            description="Get detailed information about a specific process",
            category=ActionCategory.DIAGNOSTICS,
            risk_level=ActionRiskLevel.LOW,
            command_template='Get-Process -Name "{process_name}" -ErrorAction SilentlyContinue | Select-Object Name, Id, CPU, WorkingSet64, StartTime, Path | ConvertTo-Json',
            parameters=[{
                "name": "process_name",
                "type": "string",
                "description": "Name of the process",
                "required": True
            }],
            success_message="Retrieved process details for '{process_name}'",
            failure_message="Failed to get process details"
        )
        
        # ═══════════════════════════════════════════════════════════════
        # CLEANUP ACTIONS
        # ═══════════════════════════════════════════════════════════════
        actions["clear_temp_files"] = ActionDefinition(
            id="clear_temp_files",
            name="Clear Temporary Files",
            description="Delete temporary files to free up disk space",
            category=ActionCategory.CLEANUP,
            risk_level=ActionRiskLevel.LOW,
            command_template='Remove-Item -Path "$env:TEMP\\*" -Recurse -Force -ErrorAction SilentlyContinue; $freed = [math]::Round((Get-ChildItem "$env:TEMP" -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB, 2); Write-Output "Cleared temp files"',
            parameters=[],
            success_message="Temporary files cleared successfully",
            failure_message="Failed to clear temporary files"
        )
        
        actions["empty_recycle_bin"] = ActionDefinition(
            id="empty_recycle_bin",
            name="Empty Recycle Bin",
            description="Permanently delete items in Recycle Bin",
            category=ActionCategory.CLEANUP,
            risk_level=ActionRiskLevel.MEDIUM,
            command_template='Clear-RecycleBin -Force -ErrorAction SilentlyContinue',
            parameters=[],
            success_message="Recycle Bin emptied successfully",
            failure_message="Failed to empty Recycle Bin"
        )
        
        actions["clear_browser_cache"] = ActionDefinition(
            id="clear_browser_cache",
            name="Clear Browser Cache",
            description="Clear cache for specified browser (Chrome only for now)",
            category=ActionCategory.CLEANUP,
            risk_level=ActionRiskLevel.MEDIUM,
            command_template='$cachePath = "$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Cache"; if (Test-Path $cachePath) { Remove-Item -Path "$cachePath\\*" -Recurse -Force -ErrorAction SilentlyContinue; Write-Output "Chrome cache cleared" } else { Write-Output "Chrome cache folder not found" }',
            parameters=[{
                "name": "browser",
                "type": "string",
                "description": "Browser to clear cache for",
                "required": True,
                "allowed_values": ["chrome", "edge", "firefox", "all"]
            }],
            success_message="Browser cache cleared for '{browser}'",
            failure_message="Failed to clear browser cache"
        )
        
        # ═══════════════════════════════════════════════════════════════
        # NETWORK ACTIONS
        # ═══════════════════════════════════════════════════════════════
        actions["flush_dns"] = ActionDefinition(
            id="flush_dns",
            name="Flush DNS Cache",
            description="Clear the DNS resolver cache to fix name resolution issues",
            category=ActionCategory.NETWORK,
            risk_level=ActionRiskLevel.LOW,
            command_template='ipconfig /flushdns',
            parameters=[],
            success_message="DNS cache flushed successfully",
            failure_message="Failed to flush DNS cache"
        )
        
        actions["release_renew_ip"] = ActionDefinition(
            id="release_renew_ip",
            name="Release & Renew IP Address",
            description="Get a new IP address from DHCP server",
            category=ActionCategory.NETWORK,
            risk_level=ActionRiskLevel.MEDIUM,
            command_template='ipconfig /release; Start-Sleep -Seconds 2; ipconfig /renew',
            parameters=[],
            estimated_duration=15,
            success_message="IP address renewed successfully",
            failure_message="Failed to renew IP address"
        )
        
        actions["reset_network_adapter"] = ActionDefinition(
            id="reset_network_adapter",
            name="Reset Network Adapter",
            description="Disable and re-enable network adapter",
            category=ActionCategory.NETWORK,
            risk_level=ActionRiskLevel.HIGH,
            command_template='Get-NetAdapter | Where-Object Status -eq "Up" | Restart-NetAdapter -Confirm:$false',
            parameters=[],
            requires_elevation=True,
            estimated_duration=10,
            success_message="Network adapter reset successfully",
            failure_message="Failed to reset network adapter"
        )
        
        actions["test_connectivity"] = ActionDefinition(
            id="test_connectivity",
            name="Test Network Connectivity",
            description="Check internet connection and DNS resolution",
            category=ActionCategory.DIAGNOSTICS,
            risk_level=ActionRiskLevel.LOW,
            command_template='$internet = Test-Connection -ComputerName 8.8.8.8 -Count 1 -Quiet; $dns = Test-Connection -ComputerName google.com -Count 1 -Quiet; Write-Output "Internet: $internet, DNS: $dns"',
            parameters=[],
            success_message="Network connectivity test completed",
            failure_message="Failed to test network connectivity"
        )
        
        # ═══════════════════════════════════════════════════════════════
        # SERVICE MANAGEMENT
        # ═══════════════════════════════════════════════════════════════
        actions["restart_service"] = ActionDefinition(
            id="restart_service",
            name="Restart Windows Service",
            description="Stop and start a Windows service",
            category=ActionCategory.SERVICE,
            risk_level=ActionRiskLevel.HIGH,
            command_template='Restart-Service -Name "{service_name}" -Force',
            parameters=[{
                "name": "service_name",
                "type": "string",
                "description": "Name of the Windows service",
                "required": True,
                "allowed_values": [
                    "Spooler",           # Print Spooler
                    "wuauserv",          # Windows Update
                    "BITS",              # Background Intelligent Transfer
                    "Dnscache",          # DNS Client
                    "AudioSrv",          # Windows Audio
                    "Audiosrv",          # Windows Audio
                    "WSearch",           # Windows Search
                    "Themes"             # Themes
                ]
            }],
            requires_elevation=True,
            estimated_duration=10,
            success_message="Service '{service_name}' restarted successfully",
            failure_message="Failed to restart service '{service_name}'"
        )
        
        actions["list_services"] = ActionDefinition(
            id="list_services",
            name="List Services Status",
            description="Show status of key Windows services",
            category=ActionCategory.DIAGNOSTICS,
            risk_level=ActionRiskLevel.LOW,
            command_template='Get-Service -Name Spooler,wuauserv,BITS,Dnscache,AudioSrv,WSearch | Select-Object Name, Status, DisplayName | ConvertTo-Json',
            parameters=[],
            success_message="Retrieved service status",
            failure_message="Failed to retrieve service status"
        )
        
        # ═══════════════════════════════════════════════════════════════
        # SYSTEM DIAGNOSTICS
        # ═══════════════════════════════════════════════════════════════
        actions["check_disk_space"] = ActionDefinition(
            id="check_disk_space",
            name="Check Disk Space",
            description="Show available disk space on all drives",
            category=ActionCategory.DIAGNOSTICS,
            risk_level=ActionRiskLevel.LOW,
            command_template='Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free | ConvertTo-Json',
            parameters=[],
            success_message="Retrieved disk space information",
            failure_message="Failed to retrieve disk space"
        )
        
        actions["check_system_health"] = ActionDefinition(
            id="check_system_health",
            name="System Health Check",
            description="Quick system health overview with recommendations",
            category=ActionCategory.DIAGNOSTICS,
            risk_level=ActionRiskLevel.LOW,
            command_template='$os = Get-CimInstance Win32_OperatingSystem; $cpu = Get-CimInstance Win32_Processor | Select-Object -ExpandProperty LoadPercentage; $disk = Get-PSDrive C; $memPct = [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100, 2); $memFree = [math]::Round($os.FreePhysicalMemory / 1MB, 2); $diskFree = [math]::Round($disk.Free / 1GB, 2); $diskPct = [math]::Round($disk.Used / ($disk.Used + $disk.Free) * 100, 2); Write-Output "=== SYSTEM HEALTH REPORT ==="; Write-Output "CPU Usage: $cpu%"; Write-Output "Memory: $memPct% used ($memFree GB free)"; Write-Output "Disk C: $diskPct% used ($diskFree GB free)"; Write-Output ""; Write-Output "=== RECOMMENDATIONS ==="; if ($cpu -gt 80) { Write-Output "[!] HIGH CPU: Close unused applications or check for runaway processes" }; if ($memPct -gt 85) { Write-Output "[!] HIGH MEMORY: Close browser tabs, restart heavy apps like Teams/Chrome" }; if ($diskPct -gt 90) { Write-Output "[!] LOW DISK: Run Disk Cleanup, empty Recycle Bin, remove old files" }; if ($cpu -le 80 -and $memPct -le 85 -and $diskPct -le 90) { Write-Output "[OK] System is healthy!" }',
            parameters=[],
            success_message="System health check completed",
            failure_message="Failed to check system health"
        )
        
        actions["get_startup_programs"] = ActionDefinition(
            id="get_startup_programs",
            name="List Startup Programs",
            description="Show programs that run at Windows startup",
            category=ActionCategory.DIAGNOSTICS,
            risk_level=ActionRiskLevel.LOW,
            command_template='Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | ConvertTo-Json',
            parameters=[],
            success_message="Retrieved startup programs list",
            failure_message="Failed to retrieve startup programs"
        )
        
        # ═══════════════════════════════════════════════════════════════
        # BROWSER MANAGEMENT
        # ═══════════════════════════════════════════════════════════════
        actions["close_browser_tabs"] = ActionDefinition(
            id="close_browser_tabs",
            name="Close All Browser Tabs",
            description="Close all tabs in a browser (closes browser completely)",
            category=ActionCategory.BROWSER,
            risk_level=ActionRiskLevel.MEDIUM,
            command_template='Stop-Process -Name "{browser}" -Force -ErrorAction SilentlyContinue',
            parameters=[{
                "name": "browser",
                "type": "string",
                "description": "Browser to close",
                "required": True,
                "allowed_values": ["chrome", "firefox", "msedge"]
            }],
            success_message="Closed all {browser} tabs",
            failure_message="Failed to close {browser}"
        )
        
        # ═══════════════════════════════════════════════════════════════
        # ADVANCED REMEDIATION ACTIONS
        # ═══════════════════════════════════════════════════════════════
        actions["kill_process_by_id"] = ActionDefinition(
            id="kill_process_by_id",
            name="Kill Process by ID",
            description="Forcefully terminate a process by its Process ID (PID)",
            category=ActionCategory.PROCESS,
            risk_level=ActionRiskLevel.MEDIUM,
            command_template='Stop-Process -Id {process_id} -Force -ErrorAction Stop; Write-Output "Process {process_id} terminated"',
            parameters=[{
                "name": "process_id",
                "type": "integer",
                "description": "Process ID (PID) to terminate",
                "required": True
            }],
            success_message="Process {process_id} has been terminated successfully",
            failure_message="Failed to terminate process {process_id}"
        )
        
        actions["optimize_memory"] = ActionDefinition(
            id="optimize_memory",
            name="Optimize System Memory",
            description="Free up RAM by clearing standby memory and working sets",
            category=ActionCategory.CLEANUP,
            risk_level=ActionRiskLevel.LOW,
            command_template='[System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers(); $before = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB, 2); Get-Process | ForEach-Object { $_.MinWorkingSet = $_.MinWorkingSet }; Start-Sleep -Seconds 2; $after = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB, 2); Write-Output "Memory freed: Before=$before GB, After=$after GB"',
            parameters=[],
            estimated_duration=10,
            success_message="Memory optimization completed",
            failure_message="Failed to optimize memory"
        )
        
        actions["windows_disk_cleanup"] = ActionDefinition(
            id="windows_disk_cleanup",
            name="Windows Disk Cleanup",
            description="Run Windows Disk Cleanup utility to free disk space",
            category=ActionCategory.CLEANUP,
            risk_level=ActionRiskLevel.MEDIUM,
            command_template='$before = [math]::Round((Get-PSDrive C).Free/1GB, 2); cleanmgr /sagerun:1; Start-Sleep -Seconds 3; Write-Output "Disk Cleanup initiated. Free space before: $before GB"',
            parameters=[],
            estimated_duration=60,
            success_message="Windows Disk Cleanup has been initiated",
            failure_message="Failed to run Disk Cleanup"
        )
        
        # REMOVED: stop_background_apps - unreliable and potentially disruptive
        # Users should manually close apps they don't need
        # actions["stop_background_apps"] = ActionDefinition(
        #     id="stop_background_apps",
        #     name="Stop Background Apps",
        #     description="Detect and stop resource-heavy background applications",
        #     category=ActionCategory.PROCESS,
        #     risk_level=ActionRiskLevel.MEDIUM,
        #     command_template=r'$apps = @("Teams", "Slack", "Discord", "Spotify", "OneDrive", "Dropbox", "GoogleDriveFS", "Telegram", "WhatsApp", "Zoom"); $stopped = @(); foreach ($app in $apps) { $proc = Get-Process -Name $app -ErrorAction SilentlyContinue; if ($proc) { $mem = [math]::Round(($proc | Measure-Object WorkingSet64 -Sum).Sum/1MB, 0); Stop-Process -Name $app -Force -ErrorAction SilentlyContinue; $stopped += "$app - $mem MB" } }; if ($stopped.Count -gt 0) { Write-Output "=== STOPPED APPLICATIONS ==="; $stopped | ForEach-Object { Write-Output "  [X] $_" } } else { Write-Output "No background apps were running."; Write-Output "Apps checked: $($apps -join ", ")" }',
        #     parameters=[],
        #     success_message="Background applications stopped",
        #     failure_message="Failed to stop background apps"
        # )
        
        actions["restart_explorer"] = ActionDefinition(
            id="restart_explorer",
            name="Restart Windows Explorer",
            description="Restart explorer.exe to fix UI issues and refresh taskbar",
            category=ActionCategory.PROCESS,
            risk_level=ActionRiskLevel.MEDIUM,
            command_template='Stop-Process -Name explorer -Force; Start-Sleep -Seconds 2; Start-Process explorer; Write-Output "Windows Explorer restarted"',
            parameters=[],
            estimated_duration=5,
            success_message="Windows Explorer restarted successfully",
            failure_message="Failed to restart Explorer"
        )
        
        actions["detect_background_apps"] = ActionDefinition(
            id="detect_background_apps",
            name="Detect Background Apps",
            description="Scan for running background applications without stopping them",
            category=ActionCategory.DIAGNOSTICS,
            risk_level=ActionRiskLevel.LOW,
            command_template=r'$apps = @("Teams", "Slack", "Discord", "Spotify", "OneDrive", "Dropbox", "GoogleDriveFS", "Telegram", "WhatsApp", "Zoom", "Skype", "Steam", "EpicGamesLauncher", "Origin"); $found = @(); foreach ($app in $apps) { $proc = Get-Process -Name $app -ErrorAction SilentlyContinue; if ($proc) { $mem = [math]::Round(($proc | Measure-Object WorkingSet64 -Sum).Sum/1MB, 0); $found += "$app - $mem MB (PID: $($proc[0].Id))" } }; if ($found.Count -gt 0) { Write-Output "=== DETECTED BACKGROUND APPS ==="; $found | ForEach-Object { Write-Output "  $_" }; Write-Output ""; Write-Output "Click STOP BACKGROUND APPS to terminate these." } else { Write-Output "No common background apps detected running." }',
            parameters=[],
            success_message="Background app scan completed",
            failure_message="Failed to scan for background apps"
        )
        
        actions["clear_windows_temp"] = ActionDefinition(
            id="clear_windows_temp",
            name="Deep Clean Temp Files",
            description="Clear Windows temp, user temp, and prefetch files",
            category=ActionCategory.CLEANUP,
            risk_level=ActionRiskLevel.LOW,
            command_template='$count = 0; $paths = @("$env:TEMP", "$env:WINDIR\\Temp", "$env:WINDIR\\Prefetch"); foreach ($p in $paths) { if (Test-Path $p) { $items = Get-ChildItem $p -Recurse -ErrorAction SilentlyContinue; $count += $items.Count; Remove-Item "$p\\*" -Recurse -Force -ErrorAction SilentlyContinue } }; Write-Output "Cleaned $count items from temp folders"',
            parameters=[],
            success_message="Temp files cleaned successfully",
            failure_message="Failed to clean temp files"
        )
        
        actions["reset_winsock"] = ActionDefinition(
            id="reset_winsock",
            name="Reset Winsock & TCP/IP",
            description="Reset network stack to fix connectivity issues (requires restart)",
            category=ActionCategory.NETWORK,
            risk_level=ActionRiskLevel.HIGH,
            command_template='netsh winsock reset; netsh int ip reset; ipconfig /flushdns; Write-Output "Network stack reset. Please restart your computer for changes to take effect."',
            parameters=[],
            requires_elevation=True,
            estimated_duration=10,
            success_message="Network stack reset - restart required",
            failure_message="Failed to reset network stack"
        )
        
        actions["disable_startup_item"] = ActionDefinition(
            id="disable_startup_item",
            name="Disable Startup Item",
            description="Disable a program from running at Windows startup",
            category=ActionCategory.PROCESS,
            risk_level=ActionRiskLevel.MEDIUM,
            command_template='$path = "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"; Remove-ItemProperty -Path $path -Name "{program_name}" -ErrorAction SilentlyContinue; Write-Output "Disabled {program_name} from startup"',
            parameters=[{
                "name": "program_name",
                "type": "string",
                "description": "Name of the startup program to disable",
                "required": True
            }],
            success_message="Disabled {program_name} from startup",
            failure_message="Failed to disable {program_name}"
        )
        
        actions["check_windows_updates"] = ActionDefinition(
            id="check_windows_updates",
            name="Check Windows Updates",
            description="Check for pending Windows updates",
            category=ActionCategory.DIAGNOSTICS,
            risk_level=ActionRiskLevel.LOW,
            command_template='$updates = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5 HotFixID, Description, InstalledOn; $updates | ConvertTo-Json',
            parameters=[],
            success_message="Retrieved Windows update history",
            failure_message="Failed to check updates"
        )
        
        actions["analyze_slow_performance"] = ActionDefinition(
            id="analyze_slow_performance",
            name="Analyze Performance Issues",
            description="Comprehensive analysis with specific fix recommendations",
            category=ActionCategory.DIAGNOSTICS,
            risk_level=ActionRiskLevel.LOW,
            command_template='$cpu = (Get-CimInstance Win32_Processor).LoadPercentage; $os = Get-CimInstance Win32_OperatingSystem; $mem = [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100, 2); $disk = Get-PSDrive C; $diskPct = [math]::Round($disk.Used/($disk.Used+$disk.Free)*100, 2); $topProc = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 5 Name, Id, @{N="MemMB";E={[math]::Round($_.WorkingSet64/1MB,0)}}; Write-Output "=== PERFORMANCE ANALYSIS ==="; Write-Output "CPU Load: $cpu%"; Write-Output "Memory Used: $mem%"; Write-Output "Disk Used: $diskPct%"; Write-Output ""; Write-Output "=== TOP MEMORY CONSUMERS ==="; $topProc | ForEach-Object { Write-Output "  $($_.Name) (PID: $($_.Id)) - $($_.MemMB) MB" }; Write-Output ""; Write-Output "=== RECOMMENDATIONS ==="; if ($mem -gt 85) { Write-Output "[!] HIGH MEMORY ($mem%): Click OPTIMIZE MEMORY button below" }; if ($mem -gt 70 -and $mem -le 85) { Write-Output "[i] Memory is moderate ($mem%). Consider closing unused apps" }; if ($cpu -gt 80) { Write-Output "[!] HIGH CPU ($cpu%): Check for updates or heavy processes" }; if ($diskPct -gt 90) { Write-Output "[!] LOW DISK SPACE: Run Disk Cleanup" }; if ($mem -le 70 -and $cpu -le 80 -and $diskPct -le 90) { Write-Output "[OK] System resources look healthy!" }',
            parameters=[],
            success_message="Performance analysis completed",
            failure_message="Failed to analyze performance"
        )
        
        return actions
    
    def get_available_actions(self, category: Optional[ActionCategory] = None) -> List[Dict]:
        """Get list of available actions, optionally filtered by category"""
        result = []
        for action_id, action in self.actions.items():
            if category and action.category != category:
                continue
            result.append({
                "id": action.id,
                "name": action.name,
                "description": action.description,
                "category": action.category.value,
                "risk_level": action.risk_level.value,
                "parameters": action.parameters,
                "requires_elevation": action.requires_elevation,
                "estimated_duration": action.estimated_duration
            })
        return result
    
    def get_action_by_id(self, action_id: str) -> Optional[ActionDefinition]:
        """Get action definition by ID, including dynamic action IDs"""
        # First check if it's a static action
        if action_id in self.actions:
            return self.actions[action_id]
        
        # Handle dynamic action IDs like "kill_process_msedge"
        if action_id.startswith("kill_process_") and action_id != "kill_process_by_id":
            # Extract process name from action_id (e.g., "kill_process_msedge" -> "msedge")
            process_name = action_id.replace("kill_process_", "")
            # Return base action with process name embedded
            base_action = self.actions.get("kill_process")
            if base_action:
                # Create a copy with the dynamic ID
                import copy
                dynamic_action = copy.deepcopy(base_action)
                dynamic_action.id = action_id
                dynamic_action.name = f"End {process_name.title()} Process"
                return dynamic_action
        
        return None
    
    def validate_parameters(self, action: ActionDefinition, params: Dict[str, Any]) -> tuple[bool, str]:
        """Validate action parameters against definition"""
        for param_def in action.parameters:
            param_name = param_def["name"]
            
            # Check required parameters
            if param_def.get("required", False) and param_name not in params:
                return False, f"Missing required parameter: {param_name}"
            
            # Check allowed values
            if param_name in params and "allowed_values" in param_def:
                if params[param_name] not in param_def["allowed_values"]:
                    return False, f"Invalid value for {param_name}. Allowed: {param_def['allowed_values']}"
        
        # Security check: sanitize inputs
        for key, value in params.items():
            if isinstance(value, str):
                # Block shell injection attempts
                if re.search(r'[;&|`$]', value):
                    return False, f"Invalid characters in parameter: {key}"
        
        return True, "Valid"
    
    def create_action_request(
        self,
        action_id: str,
        parameters: Dict[str, Any],
        user_email: str,
        ticket_id: Optional[int] = None
    ) -> Optional[ActionRequest]:
        """Create a pending action request that needs user approval"""
        action = self.get_action_by_id(action_id)
        if not action:
            logger.warning(f"Unknown action requested: {action_id}")
            return None
        
        # For dynamic kill_process actions, auto-populate process_name from action_id
        if action_id.startswith("kill_process_") and action_id != "kill_process_by_id":
            process_name = action_id.replace("kill_process_", "")
            if "process_name" not in parameters:
                parameters["process_name"] = process_name
                logger.info(f"Auto-populated process_name='{process_name}' from action_id '{action_id}'")
        
        # Validate parameters
        is_valid, message = self.validate_parameters(action, parameters)
        if not is_valid:
            logger.warning(f"Invalid parameters for {action_id}: {message}")
            return None
        
        # Create request
        import uuid
        request = ActionRequest(
            id=str(uuid.uuid4())[:8],
            action_id=action_id,
            parameters=parameters,
            user_email=user_email,
            ticket_id=ticket_id,
            status=ActionStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.pending_actions[request.id] = request
        logger.info(f"Created action request {request.id} for {action_id}")
        
        return request
    
    def approve_action(self, request_id: str, user_email: str) -> bool:
        """Approve a pending action (user confirmation)"""
        request = self.pending_actions.get(request_id)
        if not request:
            return False
        
        if request.user_email != user_email:
            logger.warning(f"User {user_email} tried to approve action for {request.user_email}")
            return False
        
        request.status = ActionStatus.APPROVED
        logger.info(f"Action {request_id} approved by {user_email}")
        return True
    
    def cancel_action(self, request_id: str, user_email: str) -> bool:
        """Cancel a pending action"""
        request = self.pending_actions.get(request_id)
        if not request:
            return False
        
        if request.user_email != user_email:
            return False
        
        request.status = ActionStatus.CANCELLED
        self.action_history.append(request)
        del self.pending_actions[request_id]
        
        logger.info(f"Action {request_id} cancelled by {user_email}")
        return True
    
    async def execute_action(self, request_id: str) -> Dict[str, Any]:
        """Execute an approved action"""
        request = self.pending_actions.get(request_id)
        if not request:
            return {"success": False, "error": "Action request not found"}
        
        if request.status != ActionStatus.APPROVED:
            return {"success": False, "error": "Action not approved"}
        
        action = self.get_action_by_id(request.action_id)
        if not action:
            return {"success": False, "error": "Action definition not found"}
        
        # Update status
        request.status = ActionStatus.EXECUTING
        request.executed_at = datetime.utcnow()
        
        try:
            # Build command from template - use safe substitution
            command = action.command_template
            for key, value in request.parameters.items():
                placeholder = "{" + key + "}"
                command = command.replace(placeholder, str(value))
            
            logger.info(f"Executing action {request.action_id}: {command[:100]}...")
            
            # Execute command
            if self.is_windows:
                result = await self._execute_powershell(command)
            else:
                result = {"success": False, "error": "Only Windows is supported"}
            
            # Log the result for debugging
            logger.info(f"Action {request.action_id} result: success={result.get('success')}, has_output={bool(result.get('output'))}")
            if result.get("error"):
                logger.error(f"Action error: {result.get('error')}")
            
            # Update request
            request.completed_at = datetime.utcnow()
            
            if result["success"]:
                request.status = ActionStatus.COMPLETED
                request.result = result
                
                # Format success message - use safe substitution
                success_msg = action.success_message
                for key, value in request.parameters.items():
                    placeholder = "{" + key + "}"
                    success_msg = success_msg.replace(placeholder, str(value))
                result["message"] = success_msg
            else:
                request.status = ActionStatus.FAILED
                request.error = result.get("error", "Unknown error")
                
                # Format failure message - use safe substitution
                failure_msg = action.failure_message
                for key, value in request.parameters.items():
                    placeholder = "{" + key + "}"
                    failure_msg = failure_msg.replace(placeholder, str(value))
                result["message"] = failure_msg
            
            # Move to history
            self.action_history.append(request)
            del self.pending_actions[request_id]
            
            return result
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            request.status = ActionStatus.FAILED
            request.error = str(e)
            request.completed_at = datetime.utcnow()
            
            self.action_history.append(request)
            del self.pending_actions[request_id]
            
            return {"success": False, "error": str(e)}
    
    async def _execute_powershell(self, command: str) -> Dict[str, Any]:
        """Execute a PowerShell command safely"""
        import subprocess
        
        def run_command():
            """Run the PowerShell command in a subprocess"""
            try:
                result = subprocess.run(
                    ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    shell=False
                )
                return result
            except subprocess.TimeoutExpired:
                return None
            except Exception as e:
                logger.error(f"Subprocess run error: {type(e).__name__}: {e}")
                raise
        
        try:
            logger.info(f"Starting PowerShell subprocess for command...")
            logger.info(f"Command: {command[:200]}...")
            
            # Run in thread pool to not block the event loop
            result = await asyncio.get_event_loop().run_in_executor(None, run_command)
            
            if result is None:
                logger.error("PowerShell command timed out")
                return {"success": False, "error": "Command timed out after 30 seconds"}
            
            stdout_text = result.stdout.strip() if result.stdout else ""
            stderr_text = result.stderr.strip() if result.stderr else ""
            
            logger.info(f"PowerShell completed: returncode={result.returncode}, stdout_len={len(stdout_text)}, stderr_len={len(stderr_text)}")
            if stderr_text:
                logger.warning(f"PowerShell stderr: {stderr_text[:500]}")
            if stdout_text:
                logger.info(f"PowerShell stdout preview: {stdout_text[:300]}")
            
            # Consider it success if we have ANY meaningful stdout output
            # PowerShell returns non-zero for many reasons (some processes can't be queried, etc)
            # If we got output that looks like a real response, it's a success
            has_meaningful_output = stdout_text and len(stdout_text.strip()) > 10
            logger.info(f"Has meaningful output: {has_meaningful_output}, stdout length: {len(stdout_text.strip()) if stdout_text else 0}")
            
            if result.returncode == 0 or has_meaningful_output:
                # Try to parse JSON output
                output = stdout_text
                try:
                    import json
                    output = json.loads(stdout_text)
                    logger.info(f"Parsed JSON output successfully")
                except Exception as json_err:
                    logger.info(f"Output is not JSON, returning as text")
                
                return {
                    "success": True,
                    "output": output,
                    "return_code": result.returncode
                }
            else:
                error_msg = stderr_text or stdout_text or "Command failed"
                logger.error(f"PowerShell failed with code {result.returncode}: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "return_code": result.returncode
                }
                
        except Exception as e:
            logger.error(f"PowerShell execution exception: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1: NATURAL LANGUAGE PATTERNS FOR ACTION TRIGGERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Regex patterns for detecting issues naturally
    PERFORMANCE_PATTERNS = [
        r"(very\s+)?slow",
        r"taking\s+(forever|ages|too\s+long|a\s+while|so\s+long)",
        r"(can'?t|cannot|won'?t|doesn'?t)\s+(open|load|start|run|work)",
        r"(stuck|frozen|freezing|hanging|not\s+responding|unresponsive)",
        r"waiting\s+(for|on)",
        r"(crawling|snail|turtle|molasses)",  # metaphors
        r"used\s+to\s+be\s+fast(er)?",
        r"(worse|slower)\s+than\s+(before|yesterday|usual|normal)",
        r"(takes|taking)\s+\d+\s*(min|minute|sec|second|hour)",
        r"high\s*(cpu|memory|ram|usage|utilization)",
        r"(lag|lagging|laggy|stuttering|choppy)",
        r"(poor|bad|terrible|awful)\s+performance",
        r"(performance|speed)\s+(issue|problem)",
        r"not\s+(running|working)\s+(well|properly|correctly)",
        r"(computer|laptop|pc|system|machine)\s+is\s+(slow|struggling)",
        r"everything\s+(is\s+)?(slow|takes)",
        r"apps?\s+(crash|crashing|keep\s+closing)",
    ]
    
    MEMORY_PATTERNS = [
        r"out\s+of\s+(memory|ram)",
        r"not\s+enough\s+(memory|ram|space)",
        r"(too\s+many|lots\s+of)\s+(tabs|windows|apps|programs)",
        r"memory\s+(full|exhausted|maxed|high|issue|problem|leak)",
        r"ram\s+(full|exhausted|maxed|high|issue|problem)",
        r"(using|eating|consuming)\s+(all|too\s+much)\s+(memory|ram)",
        r"low\s+(on\s+)?(memory|ram)",
    ]
    
    NETWORK_PATTERNS = [
        r"(can'?t|cannot|won'?t|unable\s+to)\s+(connect|access|reach|get\s+to|browse)",
        r"(no|lost|losing|dropped|intermittent)\s+(internet|connection|wifi|network|connectivity)",
        r"(website|page|site)s?\s+(not|won'?t|can'?t|doesn'?t)\s+(load|work|open|respond)",
        r"keeps?\s+(disconnecting|dropping|losing\s+connection)",
        r"(internet|wifi|network|connection)\s+(down|not\s+working|issues?|problems?)",
        r"(slow|bad|poor|terrible)\s+(internet|wifi|connection|network)",
        r"(can'?t|cannot)\s+(browse|surf|access\s+internet)",
        r"dns\s+(error|issue|problem|not\s+resolving)",
        r"(page|website)\s+not\s+found",
        r"connection\s+(timed?\s*out|refused|reset)",
        r"vpn\s+(not|won'?t|can'?t|doesn'?t)\s+(connect|work)",
    ]
    
    STORAGE_PATTERNS = [
        r"(disk|drive|storage|hard\s*drive)\s+(full|space|low|issue|problem)",
        r"(no|not\s+enough|low|running\s+out\s+of)\s+(disk\s+)?space",
        r"(can'?t|cannot)\s+(save|download|install)",
        r"(need|free\s+up)\s+(more\s+)?space",
        r"(c:?\s*drive|hard\s*drive)\s+(is\s+)?(full|red|low)",
        r"storage\s+(warning|alert|notification)",
    ]
    
    STARTUP_PATTERNS = [
        r"(slow|long|takes\s+forever)\s+(to\s+)?(startup|boot|start|turn\s+on)",
        r"(startup|boot)\s+(slow|takes|issue|problem)",
        r"(too\s+many|lots\s+of)\s+(startup|boot)\s+(programs|apps|items)",
        r"(computer|laptop|pc)\s+(takes|taking)\s+(long|forever|ages)\s+to\s+(start|boot)",
        r"when\s+i\s+(start|turn\s+on|boot)",
    ]
    
    BROWSER_PATTERNS = [
        r"(browser|chrome|firefox|edge)\s+(slow|not\s+working|crashing|freezing)",
        r"(pages?|websites?|tabs?)\s+(slow|not\s+loading|crashing)",
        r"(too\s+many|lots\s+of)\s+tabs?",
        r"browser\s+(cache|history|data)",
        r"(clear|delete)\s+(cache|cookies|history)",
    ]
    
    DEVELOPER_PATTERNS = [
        r"(web|website|page|code|changes?).*not.*(changing|updating|reflecting|showing)",
        r"(change|code|update|fix).*not.*(showing|reflecting|visible|working|changing)",
        r"(made|did).*(change|update|fix).*(but|and).*(not|nothing|no)",
        r"(refresh|reload|f5).*(not\s+working|doesn'?t\s+work)",
        r"(cached|cache|old).*(page|version|code)",
        r"(hard\s+refresh|ctrl\s*\+?\s*f5|clear\s+cache)",
        r"developer.*code.*not.*chang",
        r"code.*web.*not.*chang",
    ]
    
    PRINTER_PATTERNS = [
        r"(can'?t|cannot|won'?t|unable\s+to)\s+print",
        r"print(er|ing)?\s+(not\s+working|issue|problem|error|stuck|offline|jammed)",
        r"(print|printer)\s+(queue|job|spooler)",
        r"documents?\s+(stuck|pending|not\s+printing)",
    ]
    
    AUDIO_PATTERNS = [
        r"(no|can'?t\s+hear|lost)\s+(sound|audio)",
        r"(sound|audio|speaker|mic|microphone)\s+(not\s+working|issue|problem|broken)",
        r"(can'?t|cannot)\s+(hear|record|play\s+sound)",
        r"(volume|audio)\s+(muted|low|not\s+working)",
        r"(speaker|headphone|mic|microphone)\s+(not\s+detected|not\s+recognized)",
    ]
    
    DISPLAY_PATTERNS = [
        r"(screen|display|monitor)\s+(black|blank|flickering|not\s+working)",
        r"(taskbar|start\s*menu|desktop|icons?)\s+(not\s+working|missing|frozen|stuck)",
        r"(explorer|windows\s+explorer)\s+(crash|not\s+responding|frozen)",
        r"(can'?t|cannot)\s+see\s+(taskbar|desktop|icons)",
    ]
    
    BLUESCREEN_PATTERNS = [
        r"(blue\s*screen|bsod|crash|crashed)",
        r"(computer|laptop|pc|system)\s+(crash|crashed|restarted|rebooted)\s*(itself|randomly|unexpectedly)?",
        r"(unexpected|random)\s+(restart|reboot|shutdown)",
        r"(error|stop)\s+code",
    ]
    
    def get_suggested_actions(self, issue_description: str, category: Optional[str] = None) -> List[Dict]:
        """Suggest relevant actions based on the issue description using natural language patterns"""
        import re
        
        suggestions = []
        added_ids = set()  # Track added action IDs to prevent duplicates
        issue_lower = issue_description.lower()
        
        # CRITICAL: Check if this is someone else's device (can't help remotely)
        remote_device_keywords = [
            "friend's", "friends", "colleague's", "coworker's", "sister's", "brother's",
            "mom's", "dad's", "parent's", "other laptop", "other computer", "their computer", 
            "their laptop", "his computer", "her computer", "his laptop", "her laptop"
        ]
        if any(keyword in issue_lower for keyword in remote_device_keywords):
            logger.info(f"Pattern matching: Detected remote device in '{issue_description}' - returning no actions")
            return []  # Can't execute actions on someone else's device
        
        # CRITICAL: Check if issue is about external/remote hardware (not the user's PC)
        external_hardware = [
            "printer", "scanner", "phone", "iphone", "android", "tablet", "ipad",
            "external drive", "usb drive", "flash drive", "headphones", "speakers",
            "monitor", "tv", "display", "projector", "webcam", "camera"
        ]
        if any(hw in issue_lower for hw in external_hardware):
            logger.info(f"Pattern matching: Detected external hardware '{issue_description}' - returning no actions")
            return []  # Can't run system checks on external devices
        
        def add_action(action):
            """Helper to add action only if not already added"""
            action_id = action.id if isinstance(action, ActionDefinition) else action.get("id")
            if action_id not in added_ids:
                added_ids.add(action_id)
                suggestions.append(action)
        
        def matches_patterns(text: str, patterns: list) -> bool:
            """Check if text matches any of the regex patterns"""
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            return False
        
        # ═══════════════════════════════════════════════════════════════════
        # PERFORMANCE ISSUES (slow, freezing, lagging, etc.)
        # ═══════════════════════════════════════════════════════════════════
        if matches_patterns(issue_lower, self.PERFORMANCE_PATTERNS):
            add_action(self.actions["check_system_health"])
            add_action(self.actions["analyze_slow_performance"])
            add_action(self.actions["optimize_memory"])
        
        # ═══════════════════════════════════════════════════════════════════
        # MEMORY ISSUES (out of memory, RAM full, etc.)
        # ═══════════════════════════════════════════════════════════════════
        if matches_patterns(issue_lower, self.MEMORY_PATTERNS):
            add_action(self.actions["check_system_health"])
            add_action(self.actions["optimize_memory"])
            add_action(self.actions["analyze_slow_performance"])
        
        # ═══════════════════════════════════════════════════════════════════
        # NETWORK ISSUES (no internet, can't connect, etc.)
        # ═══════════════════════════════════════════════════════════════════
        if matches_patterns(issue_lower, self.NETWORK_PATTERNS):
            add_action(self.actions["test_connectivity"])
            add_action(self.actions["flush_dns"])
            add_action(self.actions["release_renew_ip"])
        
        # ═══════════════════════════════════════════════════════════════════
        # STORAGE ISSUES (disk full, no space, etc.)
        # ═══════════════════════════════════════════════════════════════════
        if matches_patterns(issue_lower, self.STORAGE_PATTERNS):
            add_action(self.actions["check_disk_space"])
            add_action(self.actions["clear_temp_files"])
            add_action(self.actions["clear_windows_temp"])
            add_action(self.actions["empty_recycle_bin"])
        
        # ═══════════════════════════════════════════════════════════════════
        # STARTUP ISSUES (slow boot, too many startup programs)
        # ═══════════════════════════════════════════════════════════════════
        if matches_patterns(issue_lower, self.STARTUP_PATTERNS):
            add_action(self.actions["get_startup_programs"])
            add_action(self.actions["check_system_health"])
        
        # ═══════════════════════════════════════════════════════════════════
        # DEVELOPER ISSUES (code not reflecting, cache problems)
        # Priority: HIGHEST - developers need this immediately
        # ═══════════════════════════════════════════════════════════════════
        if matches_patterns(issue_lower, self.DEVELOPER_PATTERNS):
            add_action(self.actions["clear_browser_cache"])
            add_action(self.actions["clear_temp_files"])
            # Don't suggest system health for developer cache issues
            # Convert to dicts before returning
            result = []
            for action in suggestions[:3]:
                if isinstance(action, ActionDefinition):
                    result.append({
                        "id": action.id,
                        "name": action.name,
                        "description": action.description,
                        "category": action.category.value if hasattr(action.category, 'value') else action.category,
                        "risk_level": action.risk_level.value if hasattr(action.risk_level, 'value') else action.risk_level,
                        "parameters": [p.model_dump() if hasattr(p, 'model_dump') else p.__dict__ for p in action.parameters],
                        "reason": "Developer issue - cache likely causing code not to update"
                    })
                elif isinstance(action, dict):
                    result.append(action)
            return result
        
        # ═══════════════════════════════════════════════════════════════════
        # BROWSER ISSUES (slow browser, general browsing)
        # ═══════════════════════════════════════════════════════════════════
        if matches_patterns(issue_lower, self.BROWSER_PATTERNS):
            # Check if it's a speed/performance issue vs just browsing
            if any(word in issue_lower for word in ['slow', 'lag', 'freeze', 'crash']):
                add_action(self.actions["clear_browser_cache"])
                add_action(self.actions["optimize_memory"])  # Better than system health
                add_action(self.actions["list_running_processes"])  # Show what's consuming
            else:
                add_action(self.actions["clear_browser_cache"])
        
        # ═══════════════════════════════════════════════════════════════════
        # PRINTER ISSUES
        # ═══════════════════════════════════════════════════════════════════
        if matches_patterns(issue_lower, self.PRINTER_PATTERNS):
            spooler_id = "restart_service_Spooler"
            if spooler_id not in added_ids:
                added_ids.add(spooler_id)
                suggestions.append({
                    **self.actions["restart_service"].__dict__,
                    "id": spooler_id,
                    "name": "Restart Print Spooler",
                    "suggested_params": {"service_name": "Spooler"}
                })
        
        # ═══════════════════════════════════════════════════════════════════
        # AUDIO ISSUES
        # ═══════════════════════════════════════════════════════════════════
        if matches_patterns(issue_lower, self.AUDIO_PATTERNS):
            audio_id = "restart_service_AudioSrv"
            if audio_id not in added_ids:
                added_ids.add(audio_id)
                suggestions.append({
                    **self.actions["restart_service"].__dict__,
                    "id": audio_id,
                    "name": "Restart Audio Service",
                    "suggested_params": {"service_name": "AudioSrv"}
                })
        
        # ═══════════════════════════════════════════════════════════════════
        # DISPLAY/UI ISSUES (taskbar, explorer, desktop)
        # ═══════════════════════════════════════════════════════════════════
        if matches_patterns(issue_lower, self.DISPLAY_PATTERNS):
            add_action(self.actions["restart_explorer"])
        
        # ═══════════════════════════════════════════════════════════════════
        # BLUE SCREEN / CRASH ISSUES
        # ═══════════════════════════════════════════════════════════════════
        if matches_patterns(issue_lower, self.BLUESCREEN_PATTERNS):
            add_action(self.actions["check_system_health"])
            add_action(self.actions["analyze_slow_performance"])
        
        # ═══════════════════════════════════════════════════════════════════
        # SPECIFIC APP MENTIONS (kill/restart specific apps)
        # ═══════════════════════════════════════════════════════════════════
        app_mappings = {
            "chrome": "chrome",
            "firefox": "firefox", 
            "edge": "msedge",
            "vs code": "Code",
            "vscode": "Code",
            "visual studio code": "Code",
            "teams": "Teams",
            "slack": "Slack",
            "outlook": "OUTLOOK",
            "excel": "EXCEL",
            "word": "WINWORD",
            "powerpoint": "POWERPNT",
            "zoom": "Zoom"
        }
        
        for app_name, process_name in app_mappings.items():
            if app_name in issue_lower:
                kill_action_id = f"kill_process_{process_name}"
                if kill_action_id not in added_ids:
                    added_ids.add(kill_action_id)
                    suggestions.append({
                        **self.actions["kill_process"].__dict__,
                        "id": kill_action_id,
                        "name": f"End {app_name.title()} Process",
                        "suggested_params": {"process_name": process_name}
                    })
        
        # ═══════════════════════════════════════════════════════════════════
        # FALLBACK: Use category if provided and no matches found
        # ═══════════════════════════════════════════════════════════════════
        if not suggestions and category:
            category_lower = category.lower()
            if category_lower in ["hardware", "performance"]:
                add_action(self.actions["check_system_health"])
                add_action(self.actions["analyze_slow_performance"])
            elif category_lower == "network":
                add_action(self.actions["test_connectivity"])
                add_action(self.actions["flush_dns"])
            elif category_lower == "software":
                add_action(self.actions["check_system_health"])
        
        # ═══════════════════════════════════════════════════════════════════
        # Convert to dicts for JSON serialization
        # ═══════════════════════════════════════════════════════════════════
        result = []
        for action in suggestions[:5]:  # Limit to 5 suggestions
            if isinstance(action, ActionDefinition):
                result.append({
                    "id": action.id,
                    "name": action.name,
                    "description": action.description,
                    "category": action.category.value if hasattr(action.category, 'value') else action.category,
                    "risk_level": action.risk_level.value if hasattr(action.risk_level, 'value') else action.risk_level,
                    "parameters": action.parameters
                })
            elif isinstance(action, dict):
                result.append({
                    "id": action.get("id"),
                    "name": action.get("name"),
                    "description": action.get("description"),
                    "category": action.get("category").value if hasattr(action.get("category"), 'value') else action.get("category"),
                    "risk_level": action.get("risk_level").value if hasattr(action.get("risk_level"), 'value') else action.get("risk_level"),
                    "parameters": action.get("parameters"),
                    "suggested_params": action.get("suggested_params")
                })
        
        return result
    
    def get_user_aware_suggestions(self, issue_description: str, user_email: str, category: Optional[str] = None) -> List[Dict]:
        """
        Get action suggestions enhanced with user history analysis.
        This makes suggestions more intelligent and personalized.
        """
        from app.services.dataset_analyzer import get_analyzer
        
        # Get base suggestions from pattern matching
        base_suggestions = self.get_suggested_actions(issue_description, category)
        
        # Get user preferences from history
        try:
            analyzer = get_analyzer()
            user_prefs = analyzer.get_user_action_preferences(user_email)
            
            # Adjust suggestions based on user history
            recurring_issues = user_prefs.get('recurring_issues', [])
            
            # If user has recurring network issues, prioritize network actions
            if any(issue in recurring_issues for issue in ['vpn', 'network', 'wi-fi', 'wifi']):
                if 'network' in issue_description.lower() or category == 'network':
                    # Add network-specific actions at the front
                    base_suggestions = [s for s in base_suggestions if 'network' in s.get('category', '').lower()] + \
                                     [s for s in base_suggestions if 'network' not in s.get('category', '').lower()]
            
            # If user has recurring docker/dev issues, prioritize cache/cleanup
            if any(issue in recurring_issues for issue in ['docker', 'visual studio', 'vs code', 'git']):
                if any(word in issue_description.lower() for word in ['slow', 'freeze', 'not working']):
                    # Prioritize cleanup actions for developers
                    cleanup_actions = [s for s in base_suggestions if s.get('id') in ['clear_browser_cache', 'clear_temp_files', 'optimize_memory']]
                    other_actions = [s for s in base_suggestions if s.get('id') not in ['clear_browser_cache', 'clear_temp_files', 'optimize_memory']]
                    base_suggestions = cleanup_actions + other_actions
            
            # Add reasoning to top suggestion
            if base_suggestions and recurring_issues:
                base_suggestions[0]['reason'] = f"Based on your history with {', '.join(recurring_issues[:2])}"
            
        except Exception as e:
            logger.warning(f"Could not personalize suggestions: {e}")
        
        return base_suggestions
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1: RESULT-BASED ACTION SUGGESTIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_followup_actions(self, previous_action_id: str, action_result: str) -> List[Dict]:
        """Suggest follow-up actions based on the result of a previous action"""
        import re
        
        suggestions = []
        result_lower = action_result.lower()
        
        # Parse key metrics from results
        memory_match = re.search(r'memory[:\s]+(\d+(?:\.\d+)?)\s*%', result_lower)
        cpu_match = re.search(r'cpu[:\s]+(\d+(?:\.\d+)?)\s*%', result_lower)
        disk_match = re.search(r'disk[:\s]+(\d+(?:\.\d+)?)\s*%', result_lower)
        
        memory_pct = float(memory_match.group(1)) if memory_match else None
        cpu_pct = float(cpu_match.group(1)) if cpu_match else None
        disk_pct = float(disk_match.group(1)) if disk_match else None
        
        # Check for HIGH MEMORY in recommendations
        has_high_memory = "high memory" in result_lower or (memory_pct and memory_pct > 80)
        has_high_cpu = "high cpu" in result_lower or (cpu_pct and cpu_pct > 80)
        has_low_disk = "disk" in result_lower and "full" in result_lower or (disk_pct and disk_pct > 85)
        
        # ═══════════════════════════════════════════════════════════════════
        # FOLLOW-UP BASED ON check_system_health RESULTS
        # ═══════════════════════════════════════════════════════════════════
        if previous_action_id == "check_system_health":
            if has_high_memory:
                suggestions.append({
                    "id": "optimize_memory",
                    "name": self.actions["optimize_memory"].name,
                    "description": "Memory is high - let's free some up",
                    "category": "process",
                    "risk_level": "low",
                    "parameters": [],
                    "reason": f"Memory usage is {memory_pct:.0f}%" if memory_pct else "High memory detected"
                })
            if has_high_cpu:
                suggestions.append({
                    "id": "analyze_slow_performance",
                    "name": self.actions["analyze_slow_performance"].name,
                    "description": "CPU is high - let's see what's using it",
                    "category": "diagnostics",
                    "risk_level": "low",
                    "parameters": [],
                    "reason": f"CPU usage is {cpu_pct:.0f}%" if cpu_pct else "High CPU detected"
                })
            if has_low_disk:
                suggestions.append({
                    "id": "clear_temp_files",
                    "name": self.actions["clear_temp_files"].name,
                    "description": "Disk is getting full - let's clean up",
                    "category": "cleanup",
                    "risk_level": "low",
                    "parameters": [],
                    "reason": f"Disk usage is {disk_pct:.0f}%" if disk_pct else "Low disk space"
                })
        
        # ═══════════════════════════════════════════════════════════════════
        # FOLLOW-UP BASED ON analyze_slow_performance RESULTS
        # ═══════════════════════════════════════════════════════════════════
        elif previous_action_id == "analyze_slow_performance":
            if has_high_memory or "optimize memory" in result_lower:
                suggestions.append({
                    "id": "optimize_memory",
                    "name": self.actions["optimize_memory"].name,
                    "description": "Analysis recommends memory optimization",
                    "category": "process",
                    "risk_level": "low",
                    "parameters": [],
                    "reason": "Recommended by performance analysis"
                })
            
            # Check for specific high-memory apps in results
            high_memory_apps = {
                "chrome": "chrome",
                "msedge": "msedge", 
                "firefox": "firefox",
                "teams": "Teams",
                "code": "Code",
                "outlook": "OUTLOOK"
            }
            for app_name, process_name in high_memory_apps.items():
                if app_name.lower() in result_lower:
                    suggestions.append({
                        "id": f"kill_process_{process_name}",
                        "name": f"End {app_name.title()} Process",
                        "description": f"{app_name.title()} is using significant resources",
                        "category": "process",
                        "risk_level": "medium",
                        "parameters": [],
                        "suggested_params": {"process_name": process_name},
                        "reason": f"{app_name.title()} appears in top memory consumers"
                    })
                    break  # Only suggest one app to avoid overwhelming
        
        # ═══════════════════════════════════════════════════════════════════
        # FOLLOW-UP BASED ON optimize_memory RESULTS
        # ═══════════════════════════════════════════════════════════════════
        elif previous_action_id == "optimize_memory":
            # If memory optimization didn't help much, suggest deeper analysis
            freed_match = re.search(r'after[=:\s]+(\d+(?:\.\d+)?)', result_lower)
            if freed_match:
                after_free = float(freed_match.group(1))
                if after_free < 1.5:  # Less than 1.5GB free after optimization
                    suggestions.append({
                        "id": "analyze_slow_performance",
                        "name": self.actions["analyze_slow_performance"].name,
                        "description": "Memory is still tight - let's identify what's using it",
                        "category": "diagnostics",
                        "risk_level": "low",
                        "parameters": [],
                        "reason": f"Only {after_free:.1f}GB free after optimization"
                    })
        
        # ═══════════════════════════════════════════════════════════════════
        # FOLLOW-UP BASED ON test_connectivity RESULTS
        # ═══════════════════════════════════════════════════════════════════
        elif previous_action_id == "test_connectivity":
            if "dns" in result_lower and ("fail" in result_lower or "error" in result_lower):
                suggestions.append({
                    "id": "flush_dns",
                    "name": self.actions["flush_dns"].name,
                    "description": "DNS issues detected - flushing cache may help",
                    "category": "network",
                    "risk_level": "low",
                    "parameters": [],
                    "reason": "DNS test indicated issues"
                })
            if "gateway" in result_lower and "fail" in result_lower:
                suggestions.append({
                    "id": "release_renew_ip",
                    "name": self.actions["release_renew_ip"].name,
                    "description": "Network connectivity issue - try getting a new IP",
                    "category": "network",
                    "risk_level": "medium",
                    "parameters": [],
                    "reason": "Gateway connectivity test failed"
                })
        
        # ═══════════════════════════════════════════════════════════════════
        # FOLLOW-UP BASED ON flush_dns RESULTS
        # ═══════════════════════════════════════════════════════════════════
        elif previous_action_id == "flush_dns":
            # After flushing DNS, suggest testing connectivity
            suggestions.append({
                "id": "test_connectivity",
                "name": self.actions["test_connectivity"].name,
                "description": "Let's verify if the DNS flush fixed the issue",
                "category": "network",
                "risk_level": "low",
                "parameters": [],
                "reason": "Verify connectivity after DNS flush"
            })
        
        # ═══════════════════════════════════════════════════════════════════
        # FOLLOW-UP BASED ON clear_temp_files RESULTS
        # ═══════════════════════════════════════════════════════════════════
        elif previous_action_id == "clear_temp_files":
            # Check if we freed enough space
            freed_match = re.search(r'freed[:\s]+(\d+(?:\.\d+)?)\s*(gb|mb)', result_lower)
            if freed_match:
                amount = float(freed_match.group(1))
                unit = freed_match.group(2)
                freed_mb = amount * 1024 if unit == 'gb' else amount
                
                if freed_mb < 500:  # Less than 500MB freed
                    suggestions.append({
                        "id": "find_large_files",
                        "name": self.actions["find_large_files"].name,
                        "description": "Temp cleanup wasn't enough - let's find large files",
                        "category": "cleanup",
                        "risk_level": "low",
                        "parameters": [],
                        "reason": f"Only freed {amount}{unit.upper()}"
                    })
                    suggestions.append({
                        "id": "empty_recycle_bin",
                        "name": self.actions["empty_recycle_bin"].name,
                        "description": "Empty the recycle bin for more space",
                        "category": "cleanup",
                        "risk_level": "low",
                        "parameters": [],
                        "reason": "Recycle bin may have old deleted files"
                    })
            else:
                # Default follow-up for disk cleanup
                suggestions.append({
                    "id": "check_disk_space",
                    "name": self.actions["check_disk_space"].name,
                    "description": "Let's check how much space we have now",
                    "category": "diagnostics",
                    "risk_level": "low",
                    "parameters": [],
                    "reason": "Verify disk space after cleanup"
                })
        
        # ═══════════════════════════════════════════════════════════════════
        # FOLLOW-UP BASED ON check_disk_space RESULTS
        # ═══════════════════════════════════════════════════════════════════
        elif previous_action_id == "check_disk_space":
            if has_low_disk or "low" in result_lower or re.search(r'(\d+)%.*used', result_lower):
                pct_match = re.search(r'(\d+)%', result_lower)
                used_pct = int(pct_match.group(1)) if pct_match else 0
                
                if used_pct > 80:
                    suggestions.append({
                        "id": "clear_temp_files",
                        "name": self.actions["clear_temp_files"].name,
                        "description": "Disk is getting full - let's clean up temp files",
                        "category": "cleanup",
                        "risk_level": "low",
                        "parameters": [],
                        "reason": f"Disk is {used_pct}% full"
                    })
                    suggestions.append({
                        "id": "empty_recycle_bin",
                        "name": self.actions["empty_recycle_bin"].name,
                        "description": "Empty the recycle bin for more space",
                        "category": "cleanup",
                        "risk_level": "low",
                        "parameters": [],
                        "reason": "Quick way to free space"
                    })
        
        # ═══════════════════════════════════════════════════════════════════
        # FOLLOW-UP BASED ON restart_print_spooler RESULTS
        # ═══════════════════════════════════════════════════════════════════
        elif previous_action_id == "restart_print_spooler":
            if "fail" in result_lower or "error" in result_lower:
                suggestions.append({
                    "id": "diagnose_printer",
                    "name": self.actions["diagnose_printer"].name,
                    "description": "Spooler restart failed - let's diagnose the printer",
                    "category": "hardware",
                    "risk_level": "low",
                    "parameters": [],
                    "reason": "Print spooler restart unsuccessful"
                })
            else:
                suggestions.append({
                    "id": "diagnose_printer",
                    "name": self.actions["diagnose_printer"].name,
                    "description": "Let's verify the printer is working now",
                    "category": "hardware",
                    "risk_level": "low",
                    "parameters": [],
                    "reason": "Verify printer after spooler restart"
                })
        
        # ═══════════════════════════════════════════════════════════════════
        # FOLLOW-UP BASED ON run_antivirus_scan RESULTS
        # ═══════════════════════════════════════════════════════════════════
        elif previous_action_id == "run_antivirus_scan":
            if "threat" in result_lower or "found" in result_lower or "detected" in result_lower:
                suggestions.append({
                    "id": "check_system_health",
                    "name": self.actions["check_system_health"].name,
                    "description": "Threats detected - let's check overall system health",
                    "category": "diagnostics",
                    "risk_level": "low",
                    "parameters": [],
                    "reason": "Verify system health after threat detection"
                })
        
        # ═══════════════════════════════════════════════════════════════════
        # FOLLOW-UP BASED ON list_startup_items RESULTS  
        # ═══════════════════════════════════════════════════════════════════
        elif previous_action_id == "list_startup_items":
            suggestions.append({
                "id": "analyze_slow_performance",
                "name": self.actions["analyze_slow_performance"].name,
                "description": "Let's analyze what's slowing down your system",
                "category": "diagnostics",
                "risk_level": "low",
                "parameters": [],
                "reason": "Deep performance analysis"
            })
        
        # ═══════════════════════════════════════════════════════════════════
        # FOLLOW-UP BASED ON release_renew_ip RESULTS
        # ═══════════════════════════════════════════════════════════════════
        elif previous_action_id == "release_renew_ip":
            suggestions.append({
                "id": "test_connectivity",
                "name": self.actions["test_connectivity"].name,
                "description": "Let's verify if the new IP fixed the connection",
                "category": "network",
                "risk_level": "low",
                "parameters": [],
                "reason": "Verify connectivity after IP renewal"
            })
        
        return suggestions[:3]  # Limit to 3 follow-up suggestions

    # =============================================================================
    # PHASE 2: LLM-Based Intent Classification
    # =============================================================================
    
    # Intent to action mapping - when LLM detects these intents, suggest these actions
    INTENT_ACTION_MAP = {
        "performance_slow": ["check_system_health", "analyze_slow_performance", "optimize_memory", "clear_temp_files"],
        "high_memory": ["optimize_memory", "list_running_processes", "check_system_health"],
        "high_cpu": ["list_running_processes", "check_system_health", "analyze_slow_performance"],
        "disk_full": ["check_disk_space", "clear_temp_files", "empty_recycle_bin", "find_large_files"],
        "network_slow": ["test_connectivity", "flush_dns", "speed_test"],
        "no_internet": ["test_connectivity", "flush_dns", "release_renew_ip", "restart_network_adapter"],
        "dns_issues": ["flush_dns", "test_connectivity"],
        "app_crash": ["check_system_health", "list_running_processes", "check_event_logs"],
        "app_not_opening": ["list_running_processes", "check_system_health", "clear_temp_files"],
        "startup_slow": ["list_startup_items", "analyze_slow_performance", "check_system_health"],
        "browser_slow": ["clear_browser_cache", "clear_temp_files", "test_connectivity"],
        "printer_issues": ["diagnose_printer", "restart_print_spooler"],
        "audio_issues": ["restart_audio_service", "check_system_health"],
        "display_issues": ["check_system_health", "list_running_processes"],
        "general_help": ["check_system_health", "list_running_processes", "check_disk_space"],
        "security_concern": ["run_antivirus_scan", "check_system_health"],
        "update_issues": ["check_windows_updates", "check_system_health"],
    }
    
    async def classify_intent_with_llm(self, user_message: str, context: str = "") -> dict:
        """
        Use LLM to classify user intent and map to relevant actions.
        This is used when pattern matching doesn't find good matches.
        
        Returns:
            {
                "intent": str,
                "confidence": float,
                "actions": list,
                "reasoning": str
            }
        """
        import google.generativeai as genai
        from app.config import settings
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Get list of available actions for the prompt
            action_list = "\n".join([
                f"- {action_id}: {action.name} ({action.category.value})"
                for action_id, action in self.actions.items()
            ])
            
            prompt = f"""You are an IT support intent classifier. Analyze the user's message and determine:
1. The primary technical issue/intent
2. Which automated actions would help

Available actions:
{action_list}

Known intents: {', '.join(self.INTENT_ACTION_MAP.keys())}

User message: "{user_message}"
{f'Additional context: {context}' if context else ''}

Respond in this exact JSON format only:
{{
    "intent": "one of the known intents or 'unknown'",
    "confidence": 0.0 to 1.0,
    "suggested_action_ids": ["action_id_1", "action_id_2"],
    "reasoning": "brief explanation"
}}

Choose the most relevant 2-4 actions. Be conservative - only high confidence for clear issues."""

            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON from response
            import json
            import re
            
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
                
                # Validate and get action details
                valid_actions = []
                for action_id in result.get("suggested_action_ids", []):
                    if action_id in self.actions:
                        action = self.actions[action_id]
                        valid_actions.append({
                            "id": action_id,
                            "name": action.name,
                            "description": action.description,
                            "category": action.category.value,
                            "risk_level": action.risk_level.value,
                            "parameters": [p.model_dump() if hasattr(p, 'model_dump') else p.__dict__ for p in action.parameters],
                            "reason": result.get("reasoning", "LLM suggested based on intent")
                        })
                
                return {
                    "intent": result.get("intent", "unknown"),
                    "confidence": result.get("confidence", 0.5),
                    "actions": valid_actions,
                    "reasoning": result.get("reasoning", "")
                }
            
            return {"intent": "unknown", "confidence": 0, "actions": [], "reasoning": "Could not parse LLM response"}
            
        except Exception as e:
            logger.error(f"LLM intent classification failed: {e}")
            return {"intent": "error", "confidence": 0, "actions": [], "reasoning": str(e)}
    
    async def get_suggested_actions_with_llm_fallback(self, user_message: str, context: str = "") -> list:
        """
        Get suggested actions using pattern matching first, then LLM fallback if needed.
        This combines the best of both approaches.
        """
        # First try pattern matching (fast, no API cost)
        pattern_suggestions = self.get_suggested_actions(user_message)
        
        # If we got good suggestions from patterns, use them
        if len(pattern_suggestions) >= 2:
            logger.info(f"Pattern matching found {len(pattern_suggestions)} actions")
            return pattern_suggestions
        
        # Otherwise, try LLM classification (slower, but smarter)
        logger.info("Pattern matching insufficient, trying LLM classification")
        llm_result = await self.classify_intent_with_llm(user_message, context)
        
        if llm_result["confidence"] >= 0.6 and llm_result["actions"]:
            logger.info(f"LLM classified intent as '{llm_result['intent']}' with {len(llm_result['actions'])} actions")
            # Combine with any pattern suggestions (avoiding duplicates)
            combined = pattern_suggestions.copy()
            existing_ids = {a["id"] for a in combined}
            
            for action in llm_result["actions"]:
                if action["id"] not in existing_ids:
                    combined.append(action)
                    existing_ids.add(action["id"])
            
            return combined[:6]  # Return up to 6 suggestions
        
        # Return whatever patterns found, even if few
        return pattern_suggestions
    
    async def get_llm_intelligent_actions(
        self, 
        issue_description: str, 
        conversation_context: str,
        category: str,
        urgency: str,
        user_email: str
    ) -> list:
        """
        INTELLIGENT ACTION SUGGESTION - LLM analyzes the issue and suggests the BEST actions.
        This is NOT pattern matching - the LLM truly thinks about what's needed.
        """
        import google.generativeai as genai
        from app.config import get_settings
        from app.services.dataset_analyzer import get_analyzer
        
        settings = get_settings()
        
        try:
            genai.configure(api_key=settings.google_api_key)
            # Use the model from settings (respects .env configuration)
            model = genai.GenerativeModel(
                settings.gemini_model,
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            )
            
            # Get user history for personalization
            try:
                analyzer = get_analyzer()
                user_prefs = analyzer.get_user_action_preferences(user_email)
                user_context = f"\nUser tier: {user_prefs.get('tier', 'staff')}"
                if user_prefs.get('recurring_issues'):
                    user_context += f"\nUser has recurring issues with: {', '.join(user_prefs['recurring_issues'][:3])}"
            except:
                user_context = ""
            
            # Get available actions
            action_list = []
            for action_id, action in self.actions.items():
                action_list.append(f"- {action_id}: {action.name} - {action.description}")
            
            prompt = f"""You are an intelligent IT support system analyzing a technical issue.

USER'S ISSUE:
{issue_description}

CONVERSATION CONTEXT:
{conversation_context}

ISSUE CATEGORY: {category}
URGENCY: {urgency}{user_context}

AVAILABLE ACTIONS:
{chr(10).join(action_list[:30])}  

YOUR TASK:
Analyze this issue intelligently and suggest 2-4 AUTOMATED actions that can be executed immediately to help solve this problem.

CRITICAL RULES:
1. **DEVICE/HARDWARE LOCATION CHECK - MOST IMPORTANT**: Actions run on the LOGGED-IN USER'S LOCAL COMPUTER ONLY
   
   **SOMEONE ELSE'S DEVICES** (NEVER suggest actions):
   - "my friend's laptop is slow" → Friend's device, CAN'T help remotely
   - "my colleague's computer" → Someone else's device, CAN'T access
   - "my sister's phone" → Another person's device, CAN'T fix
   - "my other laptop" → Different device, CAN'T help
   → **Return EMPTY list** - explain user must be on that device
   
   **EXTERNAL HARDWARE** (NEVER suggest system checks):
   - "my printer is slow" → Printer is external, can't check its system health ❌
   - "my phone is slow" → Phone is separate device, can't optimize from PC ❌
   - "scanner not working" → External device, can't check its memory ❌
   - "monitor flickering" → Display issue, not PC performance ❌
   → **Return EMPTY list** - can't run system checks on external hardware
   
   **USER'S COMPUTER/LAPTOP** (can suggest actions):
   - "my computer is slow" → User's current PC ✓
   - "my laptop slow" → User's current laptop ✓  
   - "this computer" → Current machine ✓
   - "windows is slow" → Operating system on current PC ✓
   - No device mentioned → Assume current computer ✓
   
   **REMOTE SERVICES** (don't suggest local checks):
   - "website down", "server not responding" → Remote service, don't suggest check_system_health
   - Can only suggest: test_connectivity, ping

2. ONLY suggest actions from the AVAILABLE ACTIONS list above - these are the ONLY actions you can execute

3. DO NOT suggest manual tasks (like "ask user to restart", "check cables", etc.) - ONLY automated actions

4. Match actions to the issue TYPE and DEVICE:
   - **Local device performance**: analyze_slow_performance, optimize_memory, list_top_processes
   - **Local network issues**: test_connectivity, flush_dns, release_renew_ip
   - **Developer issues on local machine**: clear_browser_cache, clear_temp_files
   - **Remote services**: ONLY network diagnostic actions (ping, test_connectivity)
   - **Someone else's device**: Return EMPTY list

5. Think: Is this the user's CURRENT device or someone else's device?

6. If remote device/someone else's device detected:
   Return: {{"actions": [], "reasoning": "This issue is on [friend's/colleague's/other] device. Actions can only run on your current machine. User must be logged in on that device to get automated help."}}

Return ONLY valid JSON (no markdown, no extra text):
{{
    "actions": [
        {{
            "action_id": "the_action_id",
            "reason": "why this action is relevant for THIS specific issue"
        }}
    ],
    "reasoning": "brief explanation of your analysis"
}}"""

            logger.info("Calling Gemini API for intelligent action suggestion...")
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            logger.info(f"LLM Response received: {response_text[:200]}...")
            
            # Parse JSON
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
                logger.info(f"Parsed JSON result: {result}")
                
                # Build action suggestions
                suggestions = []
                for action_item in result.get("actions", []):
                    action_id = action_item.get("action_id")
                    reason = action_item.get("reason", "Recommended by AI analysis")
                    
                    if action_id in self.actions:
                        action = self.actions[action_id]
                        # Handle parameters - could be dict, Pydantic model, or object
                        params = []
                        for p in action.parameters:
                            if hasattr(p, 'model_dump'):
                                params.append(p.model_dump())
                            elif isinstance(p, dict):
                                params.append(p)
                            else:
                                params.append(p.__dict__)
                        
                        suggestions.append({
                            "id": action_id,
                            "name": action.name,
                            "description": action.description,
                            "category": action.category.value,
                            "risk_level": action.risk_level.value,
                            "parameters": params,
                            "reason": reason
                        })
                    else:
                        logger.warning(f"Action ID '{action_id}' not found in available actions")
                
                logger.info(f"LLM suggested {len(suggestions)} intelligent actions: {[s['id'] for s in suggestions]}")
                
                if suggestions:
                    return suggestions[:4]  # Max 4 actions
                else:
                    logger.warning("LLM suggested no valid actions, falling back to pattern matching")
            else:
                logger.warning(f"Could not extract JSON from LLM response: {response_text[:500]}")
            
        except Exception as e:
            logger.error(f"LLM intelligent action suggestion failed: {e}", exc_info=True)
        
        # Fallback to pattern matching if LLM fails
        logger.warning("LLM failed or returned no suggestions, using pattern matching fallback")
        pattern_suggestions = self.get_suggested_actions(issue_description)
        if pattern_suggestions:
            logger.info(f"Pattern matching fallback found {len(pattern_suggestions)} actions")
            return pattern_suggestions[:4]
        
        logger.warning("No actions found via LLM or patterns")
        return []

    # =============================================================================
    # PHASE 3: Proactive Monitoring Suggestions
    # =============================================================================
    
    def get_proactive_suggestions(self, metrics: dict) -> list:
        """
        Suggest actions based on real-time system metrics.
        This enables proactive remediation before users even report issues.
        
        Args:
            metrics: Dict with keys like 'cpu_usage', 'memory_usage', 'disk_usage', etc.
            
        Returns:
            List of suggested actions based on current system state
        """
        suggestions = []
        added_ids = set()
        
        def add_action(action_id: str, reason: str, urgency: str = "medium"):
            if action_id in self.actions and action_id not in added_ids:
                action = self.actions[action_id]
                suggestions.append({
                    "id": action_id,
                    "name": action.name,
                    "description": action.description,
                    "category": action.category.value,
                    "risk_level": action.risk_level.value,
                    "parameters": [p.model_dump() if hasattr(p, 'model_dump') else p.__dict__ for p in action.parameters],
                    "reason": reason,
                    "urgency": urgency,
                    "proactive": True  # Flag to indicate this is proactive
                })
                added_ids.add(action_id)
        
        # ═══════════════════════════════════════════════════════════════════
        # HIGH CPU USAGE TRIGGERS
        # ═══════════════════════════════════════════════════════════════════
        cpu = metrics.get("cpu_usage", 0)
        if cpu >= 90:
            add_action("list_running_processes", f"CPU at {cpu:.0f}% - identifying high consumers", "high")
            add_action("check_system_health", f"Critical CPU usage ({cpu:.0f}%)", "high")
        elif cpu >= 75:
            add_action("analyze_slow_performance", f"CPU at {cpu:.0f}% - may slow system", "medium")
        
        # ═══════════════════════════════════════════════════════════════════
        # HIGH MEMORY USAGE TRIGGERS
        # ═══════════════════════════════════════════════════════════════════
        memory = metrics.get("memory_usage", 0)
        if memory >= 90:
            add_action("optimize_memory", f"Memory at {memory:.0f}% - system may become unresponsive", "high")
            add_action("list_running_processes", f"Critical memory usage ({memory:.0f}%)", "high")
        elif memory >= 80:
            add_action("optimize_memory", f"Memory at {memory:.0f}% - proactive optimization", "medium")
        
        # ═══════════════════════════════════════════════════════════════════
        # LOW DISK SPACE TRIGGERS
        # ═══════════════════════════════════════════════════════════════════
        disk = metrics.get("disk_usage", 0)
        if disk >= 95:
            add_action("clear_temp_files", f"Disk at {disk:.0f}% - critical cleanup needed", "high")
            add_action("empty_recycle_bin", "Emergency space recovery needed", "high")
            add_action("find_large_files", "Identify large files for removal", "medium")
        elif disk >= 85:
            add_action("clear_temp_files", f"Disk at {disk:.0f}% - preventive cleanup", "medium")
            add_action("check_disk_space", "Review disk usage breakdown", "low")
        
        # ═══════════════════════════════════════════════════════════════════
        # NETWORK LATENCY TRIGGERS
        # ═══════════════════════════════════════════════════════════════════
        latency = metrics.get("network_latency", 0)  # in ms
        if latency >= 500:
            add_action("test_connectivity", f"High network latency ({latency}ms)", "medium")
            add_action("flush_dns", "DNS issues may cause latency", "low")
        
        # ═══════════════════════════════════════════════════════════════════
        # GENERAL HEALTH INDICATOR
        # ═══════════════════════════════════════════════════════════════════
        # If multiple metrics are elevated, suggest comprehensive check
        elevated_count = sum([
            1 if cpu >= 70 else 0,
            1 if memory >= 70 else 0,
            1 if disk >= 80 else 0
        ])
        if elevated_count >= 2:
            add_action("check_system_health", "Multiple metrics elevated - comprehensive check", "medium")
        
        return suggestions
    
    async def get_dashboard_proactive_actions(self) -> list:
        """
        Get proactive action suggestions for the dashboard based on current system state.
        This can be called periodically to show proactive recommendations.
        """
        try:
            import psutil
            
            metrics = {
                "cpu_usage": psutil.cpu_percent(interval=0.5),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent if hasattr(psutil.disk_usage('/'), 'percent') else 0
            }
            
            return self.get_proactive_suggestions(metrics)
        except ImportError:
            logger.warning("psutil not available for proactive monitoring")
            return []
        except Exception as e:
            logger.error(f"Error getting proactive suggestions: {e}")
            return []


# Singleton instance
_action_executor = None

def get_action_executor() -> ActionExecutorAgent:
    """Get singleton instance of ActionExecutorAgent"""
    global _action_executor
    if _action_executor is None:
        _action_executor = ActionExecutorAgent()
    return _action_executor
