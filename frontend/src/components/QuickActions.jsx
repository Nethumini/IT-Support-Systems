import { useState, useEffect, useMemo } from 'react'
import {
  Activity,
  HardDrive,
  Wifi,
  RefreshCw,
  Trash2,
  Terminal,
  CheckCircle,
  AlertCircle,
  X,
  Copy,
  Info,
  Search,
  Clock,
  Globe,
  Shield,
  MapPin,
  Monitor,
  List,
  Users,
  Folder,
  Server,
  Cpu,
  Play,
  Settings,
  FileText,
  Star,
  XCircle
} from 'lucide-react'
import { monitoringService } from '../services/monitoringService'
import '../styles/components/QuickActions.css'

const STORAGE_KEY_RECENTLY_USED = 'quickActions_recentlyUsed'

// Icon mapping from string names to React components
const iconMap = {
  Activity, HardDrive, Wifi, RefreshCw, Trash2, Terminal,
  CheckCircle, AlertCircle, X, Copy, Info, Search, Clock,
  Globe, Shield, MapPin, Monitor, List, Users, Folder,
  Server, Cpu, Play, Settings, FileText, Star, XCircle
}

// Detect user's operating system
const detectOS = () => {
  const userAgent = window.navigator.userAgent.toLowerCase()
  const platform = window.navigator.platform.toLowerCase()
  
  if (platform.includes('win') || userAgent.includes('windows')) {
    return 'windows'
  } else if (platform.includes('mac') || userAgent.includes('macintosh') || userAgent.includes('mac os x')) {
    return 'mac'
  } else if (platform.includes('linux') || userAgent.includes('linux')) {
    return 'linux'
  }
  return 'unknown'
}

// Get command for current OS
const getCommandForOS = (commands, os) => {
  if (!commands || typeof commands !== 'object') return null
  
  // Try to get command for detected OS first
  const cmd = commands[os] || commands[os.charAt(0).toUpperCase() + os.slice(1)]
  if (cmd) return cmd
  
  // Fallback to any available command
  return Object.values(commands)[0] || null
}

function QuickActions({ hideHeader = false }) {
  const [loading, setLoading] = useState(null)
  const [result, setResult] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [modalContent, setModalContent] = useState(null)
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [pendingAction, setPendingAction] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [recentlyUsed, setRecentlyUsed] = useState([])

  // Load recently used actions from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY_RECENTLY_USED)
    if (stored) {
      try {
        setRecentlyUsed(JSON.parse(stored))
      } catch (e) {
        console.error('Failed to load recently used actions:', e)
      }
    }
  }, [])

  // Save to recently used when action is executed
  const trackAction = (actionId) => {
    const updated = [actionId, ...recentlyUsed.filter(id => id !== actionId)].slice(0, 5)
    setRecentlyUsed(updated)
    localStorage.setItem(STORAGE_KEY_RECENTLY_USED, JSON.stringify(updated))
  }

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      showResult('success', 'Copied to clipboard!')
    } catch (err) {
      showResult('error', 'Failed to copy')
    }
  }

  // Open terminal with command by downloading and running a script
  const openTerminalWithCommand = async (command, platform) => {
    const detectedOS = detectOS()
    const os = platform || detectedOS
    const cmd = command

    let scriptContent = ''
    let filename = ''
    let mimeType = ''

    try {
      if (os === 'windows') {
        // Create a batch file for Windows
        filename = 'run-command.bat'
        mimeType = 'application/x-bat'
        scriptContent = `@echo off\nchcp 65001 > nul\n${cmd}\npause\n`
      } else if (os === 'mac' || os === 'linux') {
        // Create a shell script for Mac/Linux
        filename = 'run-command.sh'
        mimeType = 'text/plain'
        scriptContent = `#!/bin/bash\n${cmd}\nread -p "Press Enter to close..."\n`
      } else {
        showResult('error', 'Unable to create script for your operating system')
        return
      }

      // Create blob and download
      const blob = new Blob([scriptContent], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      showResult('success', `Downloaded ${filename}. Double-click to run in terminal.`)
    } catch (error) {
      console.error('Failed to create terminal script:', error)
      showResult('error', 'Failed to create script file. Please copy the command manually.')
    }
  }

  const showResult = (type, message) => {
    setResult({ type, message })
    setTimeout(() => setResult(null), 3000)
  }

  const showInstructions = (title, content, command = null) => {
    setModalContent({ title, content, command })
    setShowModal(true)
  }

  const confirmAction = (actionId, actionHandler) => {
    setPendingAction({ id: actionId, handler: actionHandler })
    setShowConfirmation(true)
  }

  const executePendingAction = async () => {
    if (pendingAction && pendingAction.handler) {
      setShowConfirmation(false)
      await pendingAction.handler()
      setPendingAction(null)
    }
  }

  const cancelAction = () => {
    setShowConfirmation(false)
    setPendingAction(null)
  }

  // Wrap action handlers to track usage
  const wrapAction = (actionId, handler, requiresConfirmation = false) => {
    if (requiresConfirmation) {
      return () => confirmAction(actionId, () => {
        trackAction(actionId)
        handler()
      })
    }
    return () => {
      trackAction(actionId)
      handler()
    }
  }

  // Handler functions
  const handleSystemCheck = async () => {
    setLoading('system-check')
    try {
      const response = await monitoringService.checkSystemHealth()
      if (response && response.issues_detected > 0) {
        showResult('warning', `Found ${response.issues_detected} system issue${response.issues_detected > 1 ? 's' : ''}. Check monitoring page for details.`)
      } else {
        showResult('success', 'System check completed. All systems healthy!')
      }
    } catch (error) {
      console.error('System check error:', error)
      showResult('error', error.message || 'Failed to run system check. Please try again.')
    } finally {
      setLoading(null)
    }
  }

  // Define all action handlers
  const handlers = {
    'system-check': () => confirmAction('system-check', handleSystemCheck),
    'disk-space': () => showInstructions('Check Disk Space', 'Run these commands to check disk space on your system:', {
      windows: 'wmic logicaldisk get size,freespace,caption',
      mac: 'df -h',
      linux: 'df -h'
    }),
    'network-test': () => showInstructions('Network Connectivity Test', 'Test your network connectivity with these commands:', {
      windows: 'ping google.com -n 4',
      mac: 'ping -c 4 google.com',
      linux: 'ping -c 4 google.com'
    }),
    'flush-dns': () => showInstructions('Flush DNS Cache', 'Clear your DNS cache to resolve connectivity issues:', {
      windows: 'ipconfig /flushdns',
      mac: 'sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder',
      linux: 'sudo systemd-resolve --flush-caches'
    }),
    'clear-cache': () => showInstructions('Clear Browser Cache', 'Clear your browser cache to resolve loading issues:', {
      chrome: 'Press Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)',
      firefox: 'Press Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)',
      edge: 'Press Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)'
    }),
    'restart-service': () => showInstructions('Restart Service', 'Restart a service using these commands:', {
      windows: 'net stop "ServiceName" && net start "ServiceName"',
      mac: 'sudo launchctl stop com.service.name && sudo launchctl start com.service.name',
      linux: 'sudo systemctl restart service-name'
    }),
    'system-file-check': () => showInstructions('System File Checker', 'Check and repair system files:', {
      windows: 'sfc /scannow',
      mac: 'sudo diskutil verifyVolume /',
      linux: 'sudo fsck -f /dev/sda1'
    }),
    'view-ip-config': () => showInstructions('View IP Configuration', 'View your current IP address, subnet, gateway, and DNS servers:', {
      windows: 'ipconfig /all',
      mac: 'ifconfig',
      linux: 'ip addr'
    }),
    'check-open-ports': () => showInstructions('Check Open Ports', 'See which ports are listening or in use:', {
      windows: 'netstat -ano',
      mac: 'netstat -an',
      linux: 'ss -tuln'
    }),
    'trace-route': () => showInstructions('Trace Route', 'Trace the network path to a host:', {
      windows: 'tracert google.com',
      mac: 'traceroute google.com',
      linux: 'traceroute google.com'
    }),
    'release-renew-ip': () => showInstructions('Release/Renew IP Address', 'Reset your network configuration:', {
      windows: 'ipconfig /release && ipconfig /renew',
      mac: 'sudo ipconfig set en0 DHCP',
      linux: 'sudo dhclient -r && sudo dhclient'
    }),
    'check-network-adapter': () => showInstructions('Check Network Adapter Status', 'View all network interfaces and their status:', {
      windows: 'netsh interface show interface',
      mac: 'ifconfig -a',
      linux: 'ifconfig -a'
    }),
    'view-system-info': () => showInstructions('View System Information', 'Display OS version, hardware specs, and system details:', {
      windows: 'systeminfo',
      mac: 'system_profiler SPHardwareDataType',
      linux: 'uname -a && lscpu && free -h'
    }),
    'view-processes': () => showInstructions('View Running Processes', 'Show all running processes with CPU/memory usage:', {
      windows: 'tasklist',
      mac: 'ps aux',
      linux: 'ps aux'
    }),
    'kill-process': () => showInstructions('Kill Process by Name', 'Terminate a stuck or frozen process. Use with caution!', {
      windows: 'taskkill /F /IM processname.exe',
      mac: 'killall processname',
      linux: 'pkill processname'
    }),
    'check-uptime': () => showInstructions('Check System Uptime', 'Show how long your system has been running:', {
      windows: 'systeminfo | findstr /B /C:"System Boot Time"',
      mac: 'uptime',
      linux: 'uptime'
    }),
    'view-event-logs': () => showInstructions('View Event Logs', 'Access system event logs for troubleshooting:', {
      windows: 'eventvwr.msc',
      mac: 'log show --predicate \'eventMessage contains "error"\' --last 1h',
      linux: 'journalctl -n 50'
    }),
    'check-disk-health': () => showInstructions('Check Disk Health', 'Analyze disk health and check for bad sectors. This may take time:', {
      windows: 'chkdsk C: /f',
      mac: 'diskutil verifyDisk disk0',
      linux: 'sudo badblocks -v /dev/sda'
    }),
    'check-firewall': () => showInstructions('Check Firewall Status', 'View firewall configuration and status:', {
      windows: 'netsh advfirewall show allprofiles',
      mac: 'sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate',
      linux: 'sudo ufw status'
    }),
    'view-user-accounts': () => showInstructions('View User Accounts', 'List all user accounts on the system:', {
      windows: 'net user',
      mac: 'dscl . list /Users',
      linux: 'cat /etc/passwd | cut -d: -f1'
    }),
    'check-file-permissions': () => showInstructions('Check File Permissions', 'View or modify file permissions (troubleshooting access issues):', {
      windows: 'icacls "C:\\path\\to\\file"',
      mac: 'ls -la /path/to/file',
      linux: 'ls -la /path/to/file'
    }),
    'scan-malware': () => showInstructions('Scan for Malware', 'Quick security scan instructions:', {
      windows: 'Windows Defender: Open Windows Security > Virus & threat protection > Quick scan',
      mac: 'Built-in security scan: System Preferences > Security & Privacy',
      linux: 'clamscan -r /home'
    }),
    'find-large-files': () => showInstructions('Find Large Files', 'Locate files taking up disk space:', {
      windows: 'forfiles /p C:\\ /s /m *.* /c "cmd /c if @fsize gtr 1000000000 echo @path @fsize"',
      mac: 'find / -type f -size +1G 2>/dev/null',
      linux: 'find / -type f -size +1G 2>/dev/null'
    }),
    'clear-temp-files': () => confirmAction('clear-temp-files', () => showInstructions('Clear Temp Files', 'Clean temporary files to free up disk space:', {
      windows: 'del /q/f/s %TEMP%\\*',
      mac: 'rm -rf ~/Library/Caches/*',
      linux: 'sudo rm -rf /tmp/*'
    }), 'This will delete temporary files. Continue?'),
    'view-disk-usage': () => showInstructions('View Disk Usage by Folder', 'See which folders use the most space:', {
      windows: 'wmic logicaldisk get size,freespace,caption',
      mac: 'du -sh /* | sort -h',
      linux: 'du -sh /* | sort -h'
    }),
    'check-disk-io': () => showInstructions('Check Disk I/O', 'Monitor disk read/write activity:', {
      windows: 'typeperf "\\PhysicalDisk(*)\\Disk Reads/sec"',
      mac: 'iostat -x 1',
      linux: 'iostat -x 1'
    }),
    'view-cpu-memory': () => showInstructions('View CPU/Memory Usage', 'Monitor real-time resource usage:', {
      windows: 'taskmgr',
      mac: 'top',
      linux: 'top'
    }),
    'check-startup-programs': () => showInstructions('Check Startup Programs', 'View programs that start with the system:', {
      windows: 'msconfig',
      mac: 'System Preferences > Users & Groups > Login Items',
      linux: 'systemctl list-unit-files | grep enabled'
    }),
    'optimize-disk': () => confirmAction('optimize-disk', () => showInstructions('Optimize Disk', 'Defragment or optimize your disk:', {
      windows: 'defrag C: /O',
      mac: 'sudo trimforce enable',
      linux: 'sudo fstrim -av'
    }), 'Disk optimization may take a long time. Continue?')
  }

  // Define all actions with categories
  const allActions = [
    { id: 'view-ip-config', label: 'View IP Configuration', icon: Globe, color: 'blue', category: 'network', description: 'Show IP address, subnet, gateway, DNS' },
    { id: 'network-test', label: 'Network Test', icon: Wifi, color: 'green', category: 'network', description: 'Test network connectivity' },
    { id: 'check-open-ports', label: 'Check Open Ports', icon: Shield, color: 'green', category: 'network', description: 'See which ports are listening' },
    { id: 'trace-route', label: 'Trace Route', icon: MapPin, color: 'purple', category: 'network', description: 'Trace network path to host' },
    { id: 'flush-dns', label: 'Flush DNS', icon: RefreshCw, color: 'purple', category: 'network', description: 'Clear DNS cache' },
    { id: 'release-renew-ip', label: 'Release/Renew IP', icon: RefreshCw, color: 'orange', category: 'network', description: 'Reset network configuration', requiresConfirmation: true, confirmationMessage: 'This will reset your network configuration. Continue?' },
    { id: 'check-network-adapter', label: 'Network Adapter Status', icon: Activity, color: 'blue', category: 'network', description: 'View network interfaces status' },
    { id: 'system-check', label: 'Run System Check', icon: Activity, color: 'blue', category: 'system', description: 'Check system health and detect issues', requiresConfirmation: true, confirmationMessage: 'This will run a comprehensive system health check. Continue?' },
    { id: 'view-system-info', label: 'View System Information', icon: Monitor, color: 'blue', category: 'system', description: 'Display OS version and hardware specs' },
    { id: 'view-processes', label: 'View Running Processes', icon: List, color: 'orange', category: 'system', description: 'Show all running processes' },
    { id: 'kill-process', label: 'Kill Process', icon: XCircle, color: 'red', category: 'system', description: 'Terminate a stuck process', requiresConfirmation: true, confirmationMessage: 'Warning: This will force-terminate a process. Continue?' },
    { id: 'check-uptime', label: 'Check System Uptime', icon: Clock, color: 'green', category: 'system', description: 'Show system uptime' },
    { id: 'view-event-logs', label: 'View Event Logs', icon: FileText, color: 'orange', category: 'system', description: 'Access system event logs' },
    { id: 'system-file-check', label: 'System File Check', icon: Terminal, color: 'orange', category: 'system', description: 'Check and repair system files' },
    { id: 'check-disk-health', label: 'Check Disk Health', icon: HardDrive, color: 'orange', category: 'system', description: 'Analyze disk health', requiresConfirmation: true, confirmationMessage: 'Disk health check may take a long time. Continue?' },
    { id: 'restart-service', label: 'Restart Service', icon: RefreshCw, color: 'blue', category: 'system', description: 'Restart a system service' },
    { id: 'check-firewall', label: 'Check Firewall Status', icon: Shield, color: 'red', category: 'security', description: 'View firewall configuration' },
    { id: 'view-user-accounts', label: 'View User Accounts', icon: Users, color: 'blue', category: 'security', description: 'List all user accounts' },
    { id: 'check-file-permissions', label: 'Check File Permissions', icon: Shield, color: 'orange', category: 'security', description: 'View file permissions' },
    { id: 'scan-malware', label: 'Scan for Malware', icon: Shield, color: 'red', category: 'security', description: 'Quick security scan instructions' },
    { id: 'disk-space', label: 'Check Disk Space', icon: HardDrive, color: 'orange', category: 'storage', description: 'View disk usage and free space' },
    { id: 'find-large-files', label: 'Find Large Files', icon: Search, color: 'orange', category: 'storage', description: 'Locate files taking up space' },
    { id: 'clear-temp-files', label: 'Clear Temp Files', icon: Trash2, color: 'red', category: 'storage', description: 'Clean temporary files', requiresConfirmation: true, confirmationMessage: 'This will delete temporary files. Continue?' },
    { id: 'view-disk-usage', label: 'View Disk Usage', icon: Folder, color: 'orange', category: 'storage', description: 'See folders using most space' },
    { id: 'check-disk-io', label: 'Check Disk I/O', icon: Activity, color: 'blue', category: 'storage', description: 'Monitor disk read/write activity' },
    { id: 'clear-cache', label: 'Clear Cache', icon: Trash2, color: 'red', category: 'storage', description: 'Clear browser cache' },
    { id: 'view-cpu-memory', label: 'View CPU/Memory', icon: Cpu, color: 'green', category: 'performance', description: 'Monitor resource usage' },
    { id: 'check-startup-programs', label: 'Startup Programs', icon: Play, color: 'blue', category: 'performance', description: 'View startup programs' },
    { id: 'optimize-disk', label: 'Optimize Disk', icon: HardDrive, color: 'green', category: 'performance', description: 'Defragment or optimize disk', requiresConfirmation: true, confirmationMessage: 'Disk optimization may take a long time. Continue?' }
  ]

  // Category labels and icons
  const categories = {
    network: { label: 'Network & Connectivity', icon: Wifi },
    system: { label: 'System Diagnostics', icon: Monitor },
    security: { label: 'Security & Permissions', icon: Shield },
    storage: { label: 'Storage Management', icon: HardDrive },
    performance: { label: 'Performance Tools', icon: Cpu }
  }

  // Filter actions based on search query
  const filteredActions = useMemo(() => {
    if (!searchQuery.trim()) return allActions
    const query = searchQuery.toLowerCase()
    return allActions.filter(action => 
      action.label.toLowerCase().includes(query) ||
      action.description.toLowerCase().includes(query) ||
      action.category.toLowerCase().includes(query)
    )
  }, [searchQuery])

  // Group actions by category
  const actionsByCategory = useMemo(() => {
    const grouped = {}
    filteredActions.forEach(action => {
      if (!grouped[action.category]) {
        grouped[action.category] = []
      }
      grouped[action.category].push(action)
    })
    return grouped
  }, [filteredActions])

  // Get recently used actions (limit to 5)
  const recentActions = useMemo(() => {
    return recentlyUsed
      .map(id => allActions.find(a => a.id === id))
      .filter(Boolean)
      .slice(0, 5)
  }, [recentlyUsed])

  // Execute action with tracking
  const executeAction = (action) => {
    const handler = handlers[action.id]
    if (handler) {
      if (action.requiresConfirmation) {
        confirmAction(action.id, async () => {
          trackAction(action.id)
          await handler()
        })
      } else {
        trackAction(action.id)
        handler()
      }
    }
  }


  return (
    <div className="quick-actions-widget">
      {!hideHeader && (
        <div className="widget-header">
          <div>
            <h2>Quick Actions</h2>
            <p>Common troubleshooting actions</p>
          </div>
        </div>
      )}

      {/* Search Bar */}
      <div className="quick-actions-search">
        <div className="search-input-wrapper">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            placeholder="Search actions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="search-clear-btn"
              title="Clear search"
            >
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      {result && (
        <div className={`action-result ${result.type}`}>
          {result.type === 'success' && <CheckCircle size={16} />}
          {result.type === 'error' && <AlertCircle size={16} />}
          {result.type === 'warning' && <AlertCircle size={16} />}
          <span>{result.message}</span>
        </div>
      )}

      {/* Recently Used Section */}
      {recentActions.length > 0 && !searchQuery && (
        <div className="actions-section">
          <div className="section-header">
            <Clock size={20} />
            <h3>Recently Used</h3>
          </div>
          <div className="actions-grid">
            {recentActions.map((action) => {
              const Icon = action.icon
              const isLoading = loading === action.id
              
              return (
                <button
                  key={action.id}
                  onClick={() => executeAction(action)}
                  disabled={isLoading}
                  className={`action-button ${action.color} ${isLoading ? 'loading' : ''}`}
                  title={action.description}
                >
                  <div className="action-icon">
                    {isLoading ? (
                      <RefreshCw size={24} className="spinning" />
                    ) : (
                      <Icon size={24} />
                    )}
                  </div>
                  <span className="action-label">{action.label}</span>
                  <Star size={14} className="recent-indicator" />
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Categorized Sections */}
      {Object.entries(categories).map(([categoryKey, categoryInfo]) => {
        const categoryActions = actionsByCategory[categoryKey] || []
        if (categoryActions.length === 0) return null

        const CategoryIcon = categoryInfo.icon

        return (
          <div key={categoryKey} className="actions-section">
            <div className="section-header">
              <CategoryIcon size={20} />
              <h3>{categoryInfo.label}</h3>
              <span className="action-count">({categoryActions.length})</span>
            </div>
            <div className="actions-grid">
              {categoryActions.map((action) => {
                const Icon = action.icon
                const isLoading = loading === action.id
                
                return (
                  <button
                    key={action.id}
                    onClick={() => executeAction(action)}
                    disabled={isLoading}
                    className={`action-button ${action.color} ${isLoading ? 'loading' : ''}`}
                    title={action.description}
                  >
                    <div className="action-icon">
                      {isLoading ? (
                        <RefreshCw size={24} className="spinning" />
                      ) : (
                        <Icon size={24} />
                      )}
                    </div>
                    <span className="action-label">{action.label}</span>
                  </button>
                )
              })}
            </div>
          </div>
        )
      })}

      {/* No results message */}
      {searchQuery && Object.keys(actionsByCategory).length === 0 && (
        <div className="no-results">
          <Search size={48} />
          <p>No actions found matching "{searchQuery}"</p>
          <button onClick={() => setSearchQuery('')} className="clear-search-btn">
            Clear Search
          </button>
        </div>
      )}

      {/* Confirmation Dialog */}
      {showConfirmation && pendingAction && (
        <div className="modal-overlay" onClick={cancelAction}>
          <div className="confirmation-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="confirmation-header">
              <AlertCircle size={24} className="confirmation-icon" />
              <h3>Confirm Action</h3>
            </div>
            <div className="confirmation-body">
              <p>{allActions.find(a => a.id === pendingAction.id)?.confirmationMessage || 'Are you sure you want to proceed?'}</p>
            </div>
            <div className="confirmation-actions">
              <button className="confirm-btn-cancel" onClick={cancelAction}>
                Cancel
              </button>
              <button className="confirm-btn-ok" onClick={executePendingAction}>
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Instructions Modal */}
      {showModal && modalContent && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{modalContent.title}</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <p className="modal-description">{modalContent.content}</p>
              {modalContent.command && (
                <div className="commands-list">
                  {Object.entries(modalContent.command).map(([platform, cmd]) => {
                    const detectedOS = detectOS()
                    const isCurrentOS = platform.toLowerCase() === detectedOS
                    
                    return (
                      <div key={platform} className={`command-item ${isCurrentOS ? 'current-os' : ''}`}>
                        <div className="command-header">
                          <div className="platform-info">
                            <span className="platform-label">
                              {platform.charAt(0).toUpperCase() + platform.slice(1)}
                              {isCurrentOS && <span className="os-badge">Your OS</span>}
                            </span>
                          </div>
                          <div className="command-actions">
                            <button
                              className="copy-command-btn"
                              onClick={() => copyToClipboard(cmd)}
                              title="Copy command to clipboard"
                            >
                              <Copy size={14} />
                              Copy
                            </button>
                            <button
                              className="open-terminal-btn"
                              onClick={() => openTerminalWithCommand(cmd, platform.toLowerCase())}
                              title="Download and run script in terminal"
                            >
                              <Terminal size={14} />
                              Open Terminal
                            </button>
                          </div>
                        </div>
                        <code className="command-code">{cmd}</code>
                      </div>
                    )
                  })}
                </div>
              )}
              <div className="modal-info">
                <Info size={16} />
                <span>
                  <strong>Tips:</strong> Click "Copy" to copy the command to clipboard, or "Open Terminal" to download a script file that will run the command. 
                  Some commands may require administrator/sudo privileges.
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default QuickActions
