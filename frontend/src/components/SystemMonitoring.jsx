import { useState, useEffect } from 'react'
import { Activity, Cpu, Server, RefreshCw, AlertTriangle, CheckCircle, Monitor, Shield } from 'lucide-react'
import { monitoringService } from '../services/monitoringService'
import PermissionModal from './PermissionModal'
import '../styles/components/SystemMonitoring.css'

function SystemMonitoring() {
  const [refreshing, setRefreshing] = useState(false)
  const [hasPermission, setHasPermission] = useState(false)
  const [showPermissionModal, setShowPermissionModal] = useState(false)
  const [usingRealData, setUsingRealData] = useState(false)
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: 0,
    memory: 0
  })

  const [systemInfo, setSystemInfo] = useState({
    os: 'Unknown',
    browser: 'Unknown',
    screenResolution: 'Unknown',
    timezone: 'Unknown',
    language: 'Unknown',
    userAgent: 'Unknown'
  })

  const [systemDetails, setSystemDetails] = useState(null)

  const [services, setServices] = useState([
    { name: 'API Server', status: 'running', port: '8000', uptime: '5d 12h', health: 'healthy' },
    { name: 'Database', status: 'running', port: '5432', uptime: '12d 3h', health: 'healthy' },
    { name: 'AI Engine', status: 'running', port: '8001', uptime: '3d 8h', health: 'healthy' },
    { name: 'Redis Cache', status: 'running', port: '6379', uptime: '8d 15h', health: 'healthy' },
    { name: 'Message Queue', status: 'running', port: '5672', uptime: '6d 22h', health: 'healthy' },
    { name: 'Backup Service', status: 'running', port: 'N/A', uptime: '10d 5h', health: 'healthy' }
  ])

  const [logs, setLogs] = useState([])

  // Get system information
  const getSystemInfo = () => {
    const userAgent = navigator.userAgent
    let os = 'Unknown'
    let browser = 'Unknown'

    // Detect OS
    if (userAgent.includes('Win')) os = 'Windows'
    else if (userAgent.includes('Mac')) os = 'macOS'
    else if (userAgent.includes('Linux')) os = 'Linux'
    else if (userAgent.includes('Android')) os = 'Android'
    else if (userAgent.includes('iOS')) os = 'iOS'

    // Detect Browser
    if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) browser = 'Chrome'
    else if (userAgent.includes('Firefox')) browser = 'Firefox'
    else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) browser = 'Safari'
    else if (userAgent.includes('Edg')) browser = 'Edge'
    else if (userAgent.includes('Opera') || userAgent.includes('OPR')) browser = 'Opera'

    const screenRes = `${window.screen.width}x${window.screen.height}`
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
    const language = navigator.language || navigator.userLanguage

    return {
      os,
      browser,
      screenResolution: screenRes,
      timezone,
      language,
      userAgent: userAgent.substring(0, 100) + '...'
    }
  }

  // Check permission on mount
  useEffect(() => {
    const permissionStatus = localStorage.getItem('system_monitoring_permission')
    if (permissionStatus === 'granted') {
      setHasPermission(true)
    } else {
      setShowPermissionModal(true)
    }
  }, [])

  // Fetch real-time system metrics
  const fetchSystemMetrics = async () => {
    if (!hasPermission) return

    try {
      // Try to get real stats first (psutil)
      try {
        const realStats = await monitoringService.getRealStats()
        setUsingRealData(true)
        
        setSystemMetrics({
          cpu: realStats.cpu || 0,
          memory: realStats.ram || 0
        })

        if (realStats.details) {
          setSystemDetails(realStats.details)
        }

        const timestamp = new Date().toLocaleTimeString()
        const newLog = {
          time: timestamp,
          level: 'info',
          message: `System stats: CPU ${realStats.cpu}%, RAM ${realStats.ram}%`
        }
        
        setLogs(prev => [newLog, ...prev].slice(0, 20))
        return
        
      } catch (realStatsError) {
        // Fallback to metrics endpoint
        const response = await monitoringService.getMetrics()
        const isRealData = response.real_data || false
        setUsingRealData(isRealData)
        
        if (response && response.metrics) {
          setSystemMetrics({
            cpu: response.metrics.cpu || 0,
            memory: response.metrics.memory || 0
          })

          if (response.checks && response.checks.length > 0) {
            const timestamp = new Date().toLocaleTimeString()
            const newLogs = response.checks.map(check => {
              const isHealthy = check.status === 'healthy'
              const level = check.severity === 'critical' ? 'error' : 
                           check.severity === 'high' ? 'warning' : 
                           check.severity === 'medium' ? 'warning' : 'info'
              
              const metricName = check.metric.replace('_', ' ')
              const unit = check.unit === 'percent' ? '%' : check.unit === 'milliseconds' ? 'ms' : check.unit
              
              return {
                time: timestamp,
                level: isHealthy ? 'info' : level,
                message: `${check.service}: ${metricName} at ${check.value}${unit} ${isHealthy ? '✓' : '⚠'}`
              }
            })
            
            setLogs(prev => {
              const lastLog = prev[0]
              const firstNewLog = newLogs[0]
              
              if (!lastLog || lastLog.message !== firstNewLog?.message) {
                return [...newLogs, ...prev].slice(0, 20)
              }
              return prev
            })
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch system metrics:', error)
    }
  }

  useEffect(() => {
    setSystemInfo(getSystemInfo())

    if (hasPermission) {
      fetchSystemMetrics()
      const interval = setInterval(() => {
        fetchSystemMetrics()
      }, 2000)

      return () => clearInterval(interval)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasPermission])

  const handleRefresh = async () => {
    if (!hasPermission) {
      setShowPermissionModal(true)
      return
    }
    setRefreshing(true)
    await fetchSystemMetrics()
    setSystemInfo(getSystemInfo())
    setTimeout(() => setRefreshing(false), 1000)
  }

  const handleGrantPermission = () => {
    setHasPermission(true)
    setShowPermissionModal(false)
    localStorage.setItem('system_monitoring_permission', 'granted')
    fetchSystemMetrics()
  }

  const handleDenyPermission = () => {
    setShowPermissionModal(false)
    localStorage.setItem('system_monitoring_permission', 'denied')
  }

  const getMetricColor = (value) => {
    if (value < 50) return 'good'
    if (value < 80) return 'warning'
    return 'critical'
  }

  const MetricCard = ({ icon: Icon, title, value, unit, color }) => (
    <div className={`metric-card ${color}`}>
      <div className="metric-icon">
        <Icon size={28} />
      </div>
      <div className="metric-info">
        <span className="metric-title">{title}</span>
        <div className="metric-value">
          <span className="value">{typeof value === 'number' ? value.toFixed(1) : value}</span>
          <span className="unit">{unit}</span>
        </div>
      </div>
      <div className="metric-bar">
        <div className="metric-fill" style={{ width: `${value}%` }}></div>
      </div>
    </div>
  )

  return (
    <div className="monitoring-container">
      <PermissionModal
        isOpen={showPermissionModal}
        onClose={handleDenyPermission}
        onGrant={handleGrantPermission}
        onDeny={handleDenyPermission}
      />

      <div className="monitoring-header">
        <div>
          <h1>System Monitoring</h1>
          <p>
            Real-time system health and performance metrics
            {usingRealData && (
              <span className="real-data-badge">
                <Shield size={14} />
                Real Task Manager Data
              </span>
            )}
          </p>
        </div>
        <div className="header-actions">
          {!hasPermission && (
            <button 
              onClick={() => setShowPermissionModal(true)}
              className="permission-request-btn"
            >
              <Shield size={18} />
              <span>Grant Access</span>
            </button>
          )}
          <button 
            onClick={handleRefresh} 
            className={`refresh-btn ${refreshing ? 'refreshing' : ''}`}
            disabled={!hasPermission}
          >
            <RefreshCw size={20} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {!hasPermission && (
        <div className="permission-banner">
          <Shield size={20} />
          <div>
            <strong>Permission Required</strong>
            <p>Grant access to view real-time system monitoring data from Task Manager</p>
          </div>
          <button onClick={() => setShowPermissionModal(true)} className="grant-btn">
            Grant Access
          </button>
        </div>
      )}

      {/* System Information Panel */}
      <div className="system-info-panel">
        <div className="info-header">
          <Monitor size={20} />
          <h2>System Information</h2>
        </div>
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Operating System</span>
            <span className="info-value">{systemInfo.os}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Browser</span>
            <span className="info-value">{systemInfo.browser}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Screen Resolution</span>
            <span className="info-value">{systemInfo.screenResolution}</span>
          </div>
          {systemDetails && (
            <>
              <div className="info-item">
                <span className="info-label">CPU Cores</span>
                <span className="info-value">{systemDetails.cpu_cores}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Total RAM</span>
                <span className="info-value">{systemDetails.memory_total_gb} GB</span>
              </div>
              <div className="info-item">
                <span className="info-label">Available RAM</span>
                <span className="info-value">{systemDetails.memory_available_gb} GB</span>
              </div>
              <div className="info-item">
                <span className="info-label">Total Disk</span>
                <span className="info-value">{systemDetails.disk_total_gb} GB</span>
              </div>
              <div className="info-item">
                <span className="info-label">Free Disk</span>
                <span className="info-value">{systemDetails.disk_free_gb} GB</span>
              </div>
            </>
          )}
          <div className="info-item">
            <span className="info-label">Timezone</span>
            <span className="info-value">{systemInfo.timezone}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Language</span>
            <span className="info-value">{systemInfo.language}</span>
          </div>
        </div>
      </div>

      <div className="metrics-grid metrics-grid-2">
        <MetricCard
          icon={Cpu}
          title="CPU Usage"
          value={systemMetrics.cpu}
          unit="%"
          color={getMetricColor(systemMetrics.cpu)}
        />
        <MetricCard
          icon={Activity}
          title="Memory Usage"
          value={systemMetrics.memory}
          unit="%"
          color={getMetricColor(systemMetrics.memory)}
        />
      </div>

      <div className="monitoring-content">
        <div className="services-section">
          <div className="section-header">
            <h2>
              <Server size={20} />
              Running Services
            </h2>
          </div>
          <div className="services-table">
            <table>
              <thead>
                <tr>
                  <th>Service</th>
                  <th>Status</th>
                  <th>Port</th>
                  <th>Uptime</th>
                  <th>Health</th>
                </tr>
              </thead>
              <tbody>
                {services.map((service, idx) => (
                  <tr key={idx}>
                    <td className="service-name">{service.name}</td>
                    <td>
                      <span className={`status-badge ${service.status}`}>
                        {service.status === 'running' ? (
                          <CheckCircle size={14} />
                        ) : (
                          <AlertTriangle size={14} />
                        )}
                        {service.status}
                      </span>
                    </td>
                    <td className="port">{service.port}</td>
                    <td className="uptime">{service.uptime}</td>
                    <td>
                      <span className={`health-badge ${service.health}`}>
                        {service.health}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="logs-section">
          <div className="section-header">
            <h2>
              <Activity size={20} />
              System Logs
              <span className="realtime-indicator">
                <span className="realtime-dot"></span>
                Live
              </span>
            </h2>
          </div>
          <div className="logs-container">
            {logs.length === 0 ? (
              <div className="empty-logs">
                <p>No recent system activity. Metrics will appear here as they are detected.</p>
              </div>
            ) : (
              logs.map((log, idx) => (
                <div key={idx} className={`log-entry ${log.level}`}>
                  <span className="log-time">{log.time}</span>
                  <span className={`log-level ${log.level}`}>{log.level.toUpperCase()}</span>
                  <span className="log-message">{log.message}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default SystemMonitoring
