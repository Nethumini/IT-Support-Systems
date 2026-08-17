import { useState, useEffect, useRef } from 'react'
import { BarChart3, TrendingUp, Calendar, Download, AlertTriangle } from 'lucide-react'
import { reportsService } from '../services/reportsService'
import { pdfService } from '../services/pdfService'
import SLARiskReport from './SLARiskReport'
import '../styles/components/Reports.css'

function Reports() {
  const [reportType, setReportType] = useState('sla')
  const [dateRange, setDateRange] = useState('7days')
  const [customStartDate, setCustomStartDate] = useState('')
  const [customEndDate, setCustomEndDate] = useState('')
  const [predictionData, setPredictionData] = useState(null)
  const [ticketStats, setTicketStats] = useState(null)
  const [categoryData, setCategoryData] = useState([])
  const [trendsData, setTrendsData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [resolutionTimeData, setResolutionTimeData] = useState(null)
  const [performanceMetrics, setPerformanceMetrics] = useState(null)
  const [exporting, setExporting] = useState(false)
  const reportContentRef = useRef(null)

  const handleExport = async () => {
    if (!reportContentRef.current) {
      alert('Report content not found')
      return
    }

    try {
      setExporting(true)
      
      const reportTypeLabel = {
        'tickets': 'Ticket Summary',
        'performance': 'Performance Metrics',
        'system': 'System Health'
      }[reportType] || 'Report'

      const dateRangeLabel = {
        'today': 'Today',
        '7days': 'Last 7 Days',
        '30days': 'Last 30 Days',
        '90days': 'Last 90 Days',
        'custom': `${customStartDate} to ${customEndDate}`
      }[dateRange] || 'Last 7 Days'

      const filename = pdfService.generateFilename(reportTypeLabel, dateRangeLabel)

      // Generate PDF using the new service
      await pdfService.generateReport(reportContentRef.current, {
        title: reportTypeLabel,
        subtitle: 'IT Support Systems System Report',
        reportType: reportTypeLabel,
        dateRange: dateRangeLabel,
        filename: filename
      })
      
    } catch (err) {
      console.error('Error generating PDF:', err)
      alert('Failed to generate PDF. Please try again.')
    } finally {
      setExporting(false)
    }
  }

  // Filter tickets by date range
  const filterTicketsByDateRange = (tickets) => {
    const now = new Date()
    let cutoffDate
    
    if (dateRange === 'custom') {
      if (!customStartDate || !customEndDate) {
        // If custom range not set, default to last 7 days
        cutoffDate = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000))
      } else {
        cutoffDate = new Date(customStartDate)
      }
    } else {
      const dateRanges = {
        'today': 1,
        '7days': 7,
        '30days': 30,
        '90days': 90
      }
      
      const daysAgo = dateRanges[dateRange] || 7
      cutoffDate = new Date(now.getTime() - (daysAgo * 24 * 60 * 60 * 1000))
    }
    
    let endDate = new Date(now)
    if (dateRange === 'custom' && customEndDate) {
      endDate = new Date(customEndDate)
    }
    
    return tickets.filter(ticket => {
      const ticketDate = new Date(ticket.created_at || ticket.created_date || now)
      return ticketDate >= cutoffDate && ticketDate <= endDate
    })
  }

  // Calculate stat changes by comparing resolved, open, and total
  const calculateStatChanges = (stats) => {
    if (!stats) return {
      total: 0,
      resolved: 0,
      open: 0,
      escalated: 0,
      avgResolution: null,
      satisfactionRate: null,
      totalChange: null,
      resolvedChange: null,
      openChange: null,
      resolutionSpeedChange: null
    }
    
    // Calculate percentages from available data
    const totalTickets = stats.total || 0
    const resolvedCount = stats.by_status?.resolved || 0
    const openCount = stats.by_status?.open || 0
    
    const resolvedPercentage = totalTickets > 0 ? Math.round((resolvedCount / totalTickets) * 100) : 0
    const openPercentage = totalTickets > 0 ? Math.round((openCount / totalTickets) * 100) : 0
    
    // Calculate actual resolution speed from stats if available
    const avgResolutionMinutes = stats.avg_resolution_time || null
    let avgResolutionStr = null
    if (avgResolutionMinutes) {
      const hours = Math.floor(avgResolutionMinutes / 60)
      const minutes = avgResolutionMinutes % 60
      avgResolutionStr = hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`
    }
    
    // Calculate satisfaction rate from stats if available
    const satisfactionRate = stats.satisfaction_rate !== undefined ? `${stats.satisfaction_rate}%` : null
    
    // Calculate resolution speed change from previous period if available
    let resolutionSpeedChange = null
    if (stats.avg_resolution_time && stats.prev_avg_resolution_time) {
      const speedDiff = stats.prev_avg_resolution_time - stats.avg_resolution_time
      const percentChange = stats.prev_avg_resolution_time > 0 ? Math.round((speedDiff / stats.prev_avg_resolution_time) * 100) : 0
      resolutionSpeedChange = `${percentChange > 0 ? '+' : ''}${percentChange}%`
    }
    
    return {
      total: totalTickets,
      resolved: resolvedCount,
      open: openCount,
      escalated: stats.by_priority?.critical || 0,
      avgResolution: avgResolutionStr,
      satisfactionRate: satisfactionRate,
      totalChange: resolvedPercentage > 0 ? `+${resolvedPercentage}%` : null,
      resolvedChange: resolvedPercentage > 0 ? `+${resolvedPercentage}%` : null,
      openChange: openPercentage > 0 ? `${openPercentage > 50 ? '+' : '-'}${openPercentage}%` : null,
      resolutionSpeedChange: resolutionSpeedChange
    }
  }

  // Fetch all report data
  useEffect(() => {
    const fetchReportData = async () => {
      try {
        setLoading(true)
        setError(null)

        // Fetch ticket statistics
        const statsResponse = await reportsService.getTicketStats()
        const enrichedStats = calculateStatChanges(statsResponse)
        setTicketStats(enrichedStats)

        // Fetch all tickets for category analysis
        const ticketsResponse = await reportsService.getTickets({ limit: 1000 })
        let tickets = Array.isArray(ticketsResponse) ? ticketsResponse : ticketsResponse.data || []
        
        // Apply date range filter
        tickets = filterTicketsByDateRange(tickets)
        
        // Process tickets for category data
        const categoryMap = {}
        tickets.forEach(ticket => {
          const category = ticket.category
          if (category && category.toLowerCase() !== 'other') {
            categoryMap[category] = (categoryMap[category] || 0) + 1
          }
        })
        
        const validTickets = Object.values(categoryMap).reduce((sum, count) => sum + count, 0) || 1
        const categories = Object.entries(categoryMap)
          .map(([category, count]) => ({
            category,
            count,
            percentage: Math.round((count / validTickets) * 100)
          }))
          .sort((a, b) => b.count - a.count)
        
        setCategoryData(categories)

        // Generate trends data from ticket dates
        const weekData = generateWeeklyTrends(tickets)
        setTrendsData(weekData)

        // Fetch system metrics for prediction
        const metricsResponse = await reportsService.getSystemMetrics()
        
        // Get health prediction based on metrics
        const predictionResponse = await reportsService.predictHealth(metricsResponse)
        setPredictionData(predictionResponse)

        // Calculate resolution time distribution from tickets
        const resolutionDist = calculateResolutionTimeDistribution(tickets)
        setResolutionTimeData(resolutionDist)

        // Calculate performance metrics from tickets and stats
        const perfMetrics = calculatePerformanceMetrics(tickets, statsResponse)
        setPerformanceMetrics(perfMetrics)
      } catch (err) {
        console.error('Failed to fetch report data:', err)
        setError('Failed to load report data.')
        // Set empty data on error
        setTicketStats({
          total: 0,
          resolved: 0,
          open: 0,
          escalated: 0,
          avgResolution: null,
          satisfactionRate: null,
          totalChange: null,
          resolvedChange: null,
          openChange: null,
          resolutionSpeedChange: null
        })
      } finally {
        setLoading(false)
      }
    }

    fetchReportData()
    // Refresh predictions every minute
    const interval = setInterval(fetchReportData, 60000)
    return () => clearInterval(interval)
  }, [dateRange, customStartDate, customEndDate, reportType])

  // Helper function to generate weekly trends
  const generateWeeklyTrends = (tickets) => {
    const weeklyCount = {
      'Week 1': 0,
      'Week 2': 0,
      'Week 3': 0,
      'Week 4': 0
    }

    const now = new Date()
    tickets.forEach(ticket => {
      if (!ticket.created_at) return
      
      try {
        const ticketDate = new Date(ticket.created_at)
        const daysDiff = Math.floor((now - ticketDate) / (1000 * 60 * 60 * 24))
        
        if (daysDiff >= 0 && daysDiff < 7) weeklyCount['Week 4']++
        else if (daysDiff >= 7 && daysDiff < 14) weeklyCount['Week 3']++
        else if (daysDiff >= 14 && daysDiff < 21) weeklyCount['Week 2']++
        else if (daysDiff >= 21 && daysDiff < 28) weeklyCount['Week 1']++
      } catch (err) {
        console.error('Error parsing ticket date:', err)
      }
    })

    return Object.entries(weeklyCount).map(([week, tickets]) => ({ week, tickets }))
  }

  // Calculate resolution time distribution
  const calculateResolutionTimeDistribution = (tickets) => {
    let lessThanHour = 0
    let oneToFourHours = 0
    let fourToTwentyFourHours = 0
    let moreThanTwentyFourHours = 0
    let resolvedTicketsCount = 0

    tickets.forEach(ticket => {
      // Check if ticket has resolution data
      const hasResolutionTime = ticket.resolved_at && ticket.created_at

      if (hasResolutionTime) {
        try {
          const created = new Date(ticket.created_at)
          const resolved = new Date(ticket.resolved_at)
          const minutes = Math.floor((resolved - created) / (1000 * 60))

          if (!isNaN(minutes) && minutes >= 0) {
            resolvedTicketsCount++

            if (minutes < 60) lessThanHour++
            else if (minutes < 240) oneToFourHours++
            else if (minutes < 1440) fourToTwentyFourHours++
            else moreThanTwentyFourHours++
          }
        } catch (err) {
          console.error('Error parsing ticket dates:', err)
        }
      }
    })

    // If no resolved tickets, distribute sample data for demo
    if (resolvedTicketsCount === 0) {
      return {
        lessThanHour: 0,
        oneToFourHours: 0,
        fourToTwentyFourHours: 0,
        moreThanTwentyFourHours: 0,
        resolvedCount: 0
      }
    }

    const total = resolvedTicketsCount

    return {
      lessThanHour: Math.round((lessThanHour / total) * 100),
      oneToFourHours: Math.round((oneToFourHours / total) * 100),
      fourToTwentyFourHours: Math.round((fourToTwentyFourHours / total) * 100),
      moreThanTwentyFourHours: Math.round((moreThanTwentyFourHours / total) * 100),
      resolvedCount: resolvedTicketsCount
    }
  }

  // Calculate performance metrics from tickets
  const calculatePerformanceMetrics = (tickets, stats) => {
    let totalResolutionTime = 0
    let resolvedTickets = 0
    let totalFirstResponseTime = 0
    let respondedTickets = 0

    tickets.forEach(ticket => {
      // Calculate average resolution time for resolved tickets
      if (ticket.resolved_at && ticket.created_at) {
        try {
          const created = new Date(ticket.created_at)
          const resolved = new Date(ticket.resolved_at)
          const minutes = Math.floor((resolved - created) / (1000 * 60))
          
          if (!isNaN(minutes) && minutes >= 0) {
            totalResolutionTime += minutes
            resolvedTickets++
          }
        } catch (err) {
          console.error('Error calculating resolution time:', err)
        }
      }

      // Calculate first response time - use updated_at as proxy if no explicit response time
      if (ticket.created_at && (ticket.updated_at || ticket.created_at)) {
        try {
          const created = new Date(ticket.created_at)
          const firstResponse = new Date(ticket.updated_at || ticket.created_at)
          const minutes = Math.floor((firstResponse - created) / (1000 * 60))
          
          if (!isNaN(minutes) && minutes >= 0) {
            totalFirstResponseTime += minutes
            respondedTickets++
          }
        } catch (err) {
          console.error('Error calculating first response time:', err)
        }
      }
    })

    const avgFirstResponse = respondedTickets > 0 ? Math.round(totalFirstResponseTime / respondedTickets) : 0
    const avgResolutionTime = resolvedTickets > 0 ? Math.round(totalResolutionTime / resolvedTickets) : 0
    const totalTickets = tickets.length || 1
    const resolvedCount = stats?.by_status?.resolved || resolvedTickets
    const openCount = stats?.by_status?.open || 0
    const resolutionRate = totalTickets > 0 ? Math.round((resolvedCount / totalTickets) * 100) : 0
    
    // Calculate escalation rate from critical/high priority tickets
    const criticalCount = stats?.by_priority?.critical || 0
    const highCount = stats?.by_priority?.high || 0
    const escalatedTickets = criticalCount + highCount
    const escalationRate = totalTickets > 0 ? Math.round((escalatedTickets / totalTickets) * 100) : 0

    return {
      firstResponseTime: avgFirstResponse,
      avgResolutionTime: avgResolutionTime,
      satisfactionRate: stats?.satisfactionRate || null,
      resolutionRate,
      escalationRate,
      resolvedCount,
      openCount
    }
  }

  // Render report content based on type
  const renderReportContent = () => {
    const baseStats = (
      <>
        <div className="stats-overview">
          <div className="stat-box">
            <div className="stat-label">Total Tickets</div>
            <div className="stat-value">{ticketStats?.total !== undefined ? ticketStats.total : '-'}</div>
            <div className="stat-change positive">{ticketStats?.totalChange || '-'} vs last period</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Resolved</div>
            <div className="stat-value">{ticketStats?.resolved !== undefined ? ticketStats.resolved : '-'}</div>
            <div className="stat-change positive">{ticketStats?.resolvedChange || '-'} this period</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Open Tickets</div>
            <div className="stat-value">{ticketStats?.open !== undefined ? ticketStats.open : '-'}</div>
            <div className="stat-change neutral">{ticketStats?.openChange || '-'} pending</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Avg Resolution</div>
            <div className="stat-value">{ticketStats?.avgResolution || '-'}</div>
            <div className="stat-change positive">{ticketStats?.resolutionSpeedChange || '-'} faster</div>
          </div>
        </div>
      </>
    )

    switch (reportType) {
      case 'sla':
        return (
          <>
            {/* SLA Risk Analysis - Full Width */}
            <div className="report-card report-card-full-width">
              <SLARiskReport />
            </div>
          </>
        )

      case 'tickets':
        return (
          <>
            {baseStats}

            <div className="reports-grid">
              <div className="report-card">
                <div className="card-header">
                  <h3>
                    <BarChart3 size={20} />
                    Tickets by Category
                  </h3>
                </div>
                <div className="chart-container">
                  {categoryData && categoryData.length > 0 ? (
                    categoryData.map((item, idx) => (
                      <div key={idx} className="bar-item">
                        <div className="bar-label">
                          <span>{item.category}</span>
                          <span className="bar-count">{item.count}</span>
                        </div>
                        <div className="bar-graph">
                          <div 
                            className="bar-fill" 
                            style={{ width: `${item.percentage * 4}%` }}
                          ></div>
                          <span className="bar-percentage">{item.percentage}%</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="no-data">No category data available</div>
                  )}
                </div>
              </div>

              <div className="report-card">
                <div className="card-header">
                  <h3>
                    <TrendingUp size={20} />
                    Weekly Trends
                  </h3>
                </div>
                <div className="trend-chart">
                  {trendsData && trendsData.length > 0 ? (
                    trendsData.map((item, idx) => (
                      <div key={idx} className="trend-bar">
                        <div 
                          className="trend-fill" 
                          style={{ height: `${(item.tickets / Math.max(...trendsData.map(t => t.tickets), 1)) * 100}%` }}
                        ></div>
                        <div className="trend-label">{item.week}</div>
                        <div className="trend-value">{item.tickets}</div>
                      </div>
                    ))
                  ) : (
                    <div className="no-data">No trend data available</div>
                  )}
                </div>
              </div>
            </div>

            <div className="reports-grid">
              <div className="report-card">
                <div className="card-header">
                  <h3>
                    <Calendar size={20} />
                    Resolution Time Distribution
                  </h3>
                </div>
                <div className="distribution-chart">
                  <div className="dist-item">
                    <span className="dist-label">{'< 1 hour'}</span>
                    <div className="dist-bar">
                      <div className="dist-fill" style={{ width: `${resolutionTimeData?.lessThanHour !== undefined ? resolutionTimeData.lessThanHour : 0}%` }}></div>
                    </div>
                    <span className="dist-value">{resolutionTimeData?.lessThanHour !== undefined ? resolutionTimeData.lessThanHour + '%' : '-'}</span>
                  </div>
                  <div className="dist-item">
                    <span className="dist-label">1-4 hours</span>
                    <div className="dist-bar">
                      <div className="dist-fill" style={{ width: `${resolutionTimeData?.oneToFourHours !== undefined ? resolutionTimeData.oneToFourHours : 0}%` }}></div>
                    </div>
                    <span className="dist-value">{resolutionTimeData?.oneToFourHours !== undefined ? resolutionTimeData.oneToFourHours + '%' : '-'}</span>
                  </div>
                  <div className="dist-item">
                    <span className="dist-label">4-24 hours</span>
                    <div className="dist-bar">
                      <div className="dist-fill" style={{ width: `${resolutionTimeData?.fourToTwentyFourHours !== undefined ? resolutionTimeData.fourToTwentyFourHours : 0}%` }}></div>
                    </div>
                    <span className="dist-value">{resolutionTimeData?.fourToTwentyFourHours !== undefined ? resolutionTimeData.fourToTwentyFourHours + '%' : '-'}</span>
                  </div>
                  <div className="dist-item">
                    <span className="dist-label">{'> 24 hours'}</span>
                    <div className="dist-bar">
                      <div className="dist-fill" style={{ width: `${resolutionTimeData?.moreThanTwentyFourHours !== undefined ? resolutionTimeData.moreThanTwentyFourHours : 0}%` }}></div>
                    </div>
                    <span className="dist-value">{resolutionTimeData?.moreThanTwentyFourHours !== undefined ? resolutionTimeData.moreThanTwentyFourHours + '%' : '-'}</span>
                  </div>
                </div>
              </div>
            </div>
          </>
        )

      case 'performance':
        return (
          <>
            {baseStats}
            <div className="reports-grid">
              <div className="report-card">
                <div className="card-header">
                  <h3>Performance Metrics</h3>
                </div>
                <div className="metrics-list">
                  <div className="metric-item">
                    <span className="metric-name">First Response Time</span>
                    <span className="metric-value">{performanceMetrics?.firstResponseTime !== undefined && performanceMetrics.firstResponseTime > 0 ? performanceMetrics.firstResponseTime + ' min' : '-'}</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-name">Avg Resolution Time</span>
                    <span className="metric-value">{performanceMetrics?.avgResolutionTime !== undefined && performanceMetrics.avgResolutionTime > 0 ? Math.floor(performanceMetrics.avgResolutionTime / 60) + 'h ' + (performanceMetrics.avgResolutionTime % 60) + 'm' : '-'}</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-name">Resolution Rate</span>
                    <span className="metric-value">{performanceMetrics?.resolutionRate !== undefined && performanceMetrics.resolutionRate > 0 ? performanceMetrics.resolutionRate + '%' : '-'}</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-name">Escalation Rate</span>
                    <span className="metric-value">{performanceMetrics?.escalationRate !== undefined && performanceMetrics.escalationRate > 0 ? performanceMetrics.escalationRate + '%' : '-'}</span>
                  </div>
                </div>
              </div>

              <div className="report-card">
                <div className="card-header">
                  <h3>
                    <Calendar size={20} />
                    Resolution Time Distribution
                  </h3>
                </div>
                <div className="distribution-chart">
                  <div className="dist-item">
                    <span className="dist-label">{'< 1 hour'}</span>
                    <div className="dist-bar">
                      <div className="dist-fill" style={{ width: `${resolutionTimeData?.lessThanHour !== undefined ? resolutionTimeData.lessThanHour : 0}%` }}></div>
                    </div>
                    <span className="dist-value">{resolutionTimeData?.lessThanHour !== undefined ? resolutionTimeData.lessThanHour + '%' : '-'}</span>
                  </div>
                  <div className="dist-item">
                    <span className="dist-label">1-4 hours</span>
                    <div className="dist-bar">
                      <div className="dist-fill" style={{ width: `${resolutionTimeData?.oneToFourHours !== undefined ? resolutionTimeData.oneToFourHours : 0}%` }}></div>
                    </div>
                    <span className="dist-value">{resolutionTimeData?.oneToFourHours !== undefined ? resolutionTimeData.oneToFourHours + '%' : '-'}</span>
                  </div>
                  <div className="dist-item">
                    <span className="dist-label">4-24 hours</span>
                    <div className="dist-bar">
                      <div className="dist-fill" style={{ width: `${resolutionTimeData?.fourToTwentyFourHours !== undefined ? resolutionTimeData.fourToTwentyFourHours : 0}%` }}></div>
                    </div>
                    <span className="dist-value">{resolutionTimeData?.fourToTwentyFourHours !== undefined ? resolutionTimeData.fourToTwentyFourHours + '%' : '-'}</span>
                  </div>
                  <div className="dist-item">
                    <span className="dist-label">{'> 24 hours'}</span>
                    <div className="dist-bar">
                      <div className="dist-fill" style={{ width: `${resolutionTimeData?.moreThanTwentyFourHours !== undefined ? resolutionTimeData.moreThanTwentyFourHours : 0}%` }}></div>
                    </div>
                    <span className="dist-value">{resolutionTimeData?.moreThanTwentyFourHours !== undefined ? resolutionTimeData.moreThanTwentyFourHours + '%' : '-'}</span>
                  </div>
                </div>
              </div>
            </div>
          </>
        )

      case 'system':
        return (
          <>
            {baseStats}
            <div className="reports-grid">
              <div className="report-card prediction-card">
                <div className="card-header">
                  <h3>
                    <AlertTriangle size={20} />
                    Predictive Health Monitoring
                  </h3>
                </div>
                <div className="prediction-content">
                  {predictionData ? (
                    <>
                      <div className={`prediction-status ${predictionData.status?.toLowerCase() || 'unknown'}`}>
                        <span className="status-badge">{predictionData.status || 'Unknown'}</span>
                        <span className="confidence">Confidence: {predictionData.confidence !== undefined ? predictionData.confidence : 'N/A'}%</span>
                      </div>
                      
                      <div className="prediction-metrics">
                        <div className="metric-row">
                          <span>CPU Usage</span>
                          <div className="bar-bg">
                            <div className="bar-fg" style={{ width: `${predictionData.metrics?.cpu_usage !== undefined ? predictionData.metrics.cpu_usage : 0}%` }}></div>
                          </div>
                          <span className="metric-value">{predictionData.metrics?.cpu_usage !== undefined ? predictionData.metrics.cpu_usage + '%' : 'N/A'}</span>
                        </div>
                        <div className="metric-row">
                          <span>RAM Usage</span>
                          <div className="bar-bg">
                            <div className="bar-fg" style={{ width: `${predictionData.metrics?.ram_usage !== undefined ? predictionData.metrics.ram_usage : 0}%` }}></div>
                          </div>
                          <span className="metric-value">{predictionData.metrics?.ram_usage !== undefined ? predictionData.metrics.ram_usage + '%' : 'N/A'}</span>
                        </div>
                        <div className="metric-row">
                          <span>Disk Usage</span>
                          <div className="bar-bg">
                            <div className="bar-fg" style={{ width: `${predictionData.metrics?.disk_usage !== undefined ? predictionData.metrics.disk_usage : 0}%` }}></div>
                          </div>
                          <span className="metric-value">{predictionData.metrics?.disk_usage !== undefined ? predictionData.metrics.disk_usage + '%' : 'N/A'}</span>
                        </div>
                        <div className="metric-row">
                          <span>Temperature</span>
                          <div className="bar-bg">
                            <div className="bar-fg" style={{ width: `${predictionData.metrics?.temperature !== undefined ? (predictionData.metrics.temperature / 100 * 100) : 0}%` }}></div>
                          </div>
                          <span className="metric-value">{predictionData.metrics?.temperature !== undefined ? predictionData.metrics.temperature + '°C' : 'N/A'}</span>
                        </div>
                      </div>

                      {predictionData.alerts && predictionData.alerts.length > 0 && (
                        <div className="prediction-alerts">
                          <h4>Active Alerts</h4>
                          {predictionData.alerts.map((alert, idx) => (
                            <div key={idx} className="alert-item">
                              <AlertTriangle size={16} />
                              <span>{alert}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {predictionData.recommendations && (
                        <div className="prediction-recommendations">
                          <h4>Recommendations</h4>
                          <p>{predictionData.recommendations}</p>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="loading">Loading predictions...</div>
                  )}
                </div>
              </div>
            </div>
          </>
        )

      default:
        return (
          <>
            {baseStats}
            <div className="reports-grid">
              <div className="no-data" style={{ textAlign: 'center', padding: '2rem' }}>
                Select a valid report type
              </div>
            </div>
          </>
        )
    }
  }

  return (
    <div className="reports-container">
      <div className="reports-header">
        <div>
          <h1>Reports & Analytics</h1>
          <p>Comprehensive insights into system performance and ticket trends</p>
        </div>
        <div className="header-actions">
          <button onClick={handleExport} className="export-btn" disabled={exporting || loading}>
            <Download size={18} />
            <span>{exporting ? 'Generating PDF...' : 'Export PDF'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      <div className="report-controls">
        <div className="control-group">
          <label>Report Type:</label>
          <select value={reportType} onChange={(e) => setReportType(e.target.value)}>
            <option value="sla">SLA Risk Analysis</option>
            <option value="tickets">Ticket Summary</option>
            <option value="performance">Performance</option>
            <option value="system">System Health</option>
          </select>
        </div>
        <div className="control-group">
          <label>Date Range:</label>
          <select value={dateRange} onChange={(e) => setDateRange(e.target.value)}>
            {reportType === 'sla' && (
              <>
                <option value="7days">Last 7 Days</option>
                <option value="30days">Last 30 Days</option>
                <option value="90days">Last 90 Days</option>
              </>
            )}
            {reportType === 'tickets' && (
              <>
                <option value="today">Today</option>
                <option value="7days">Last 7 Days</option>
                <option value="30days">Last 30 Days</option>
                <option value="90days">Last 90 Days</option>
                <option value="custom">Custom Range</option>
              </>
            )}
            {reportType === 'performance' && (
              <>
                <option value="7days">Last 7 Days</option>
                <option value="30days">Last 30 Days</option>
                <option value="90days">Last 90 Days</option>
                <option value="custom">Custom Range</option>
              </>
            )}
            {reportType === 'system' && (
              <>
                <option value="today">Today</option>
                <option value="7days">Last 7 Days</option>
                <option value="30days">Last 30 Days</option>
                <option value="custom">Custom Range</option>
              </>
            )}
          </select>
        </div>
        {dateRange === 'custom' && (
          <>
            <div className="control-group">
              <label>Start Date:</label>
              <input 
                type="date" 
                value={customStartDate}
                onChange={(e) => setCustomStartDate(e.target.value)}
                className="date-input"
              />
            </div>
            <div className="control-group">
              <label>End Date:</label>
              <input 
                type="date" 
                value={customEndDate}
                onChange={(e) => setCustomEndDate(e.target.value)}
                className="date-input"
              />
            </div>
          </>
        )}
      </div>

      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading report data...</p>
        </div>
      ) : (
        <div ref={reportContentRef}>
          {renderReportContent()}
        </div>
      )}
    </div>
  )
}

export default Reports
