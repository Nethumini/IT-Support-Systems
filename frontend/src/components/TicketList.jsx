import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, RefreshCw, AlertCircle, Zap, CheckCircle, Clock, XCircle, Loader, Plus, X, Edit2, Trash2, Search, Filter, LayoutGrid, List, Table, User, Calendar, Tag, MessageSquare, History, ChevronRight, Bot, PlayCircle, Lock } from 'lucide-react'
import { ticketService } from '../services/ticketService'
import { deviceService } from '../services/deviceService'
import { getTicketChatHistory, resumeChatSession } from '../api'
import { usePermissions } from '../hooks/usePermissions'
import { 
  TICKET_PRIORITY, 
  TICKET_PRIORITY_LABELS, 
  TICKET_PRIORITY_TO_API,
  API_PRIORITY_TO_NUMBER,
  TICKET_CATEGORY, 
  TICKET_CATEGORY_LABELS,
  TICKET_STATUS,
  TICKET_STATUS_LABELS,
  STORAGE_KEYS 
} from '../config/constants'
import '../styles/components/TicketList.css'

function TicketList() {
  const navigate = useNavigate()
  const { hasPermission, hasRole, user } = usePermissions()
  
  // Get initial user email
  const getUserEmail = () => {
    const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA)
    if (userData) {
      try {
        const user = JSON.parse(userData)
        return user.email || ''
      } catch {
        return ''
      }
    }
    return ''
  }

  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [creating, setCreating] = useState(false)
  const [updating, setUpdating] = useState(false)
  const [editingTicket, setEditingTicket] = useState(null)
  const [viewMode, setViewMode] = useState('board') // 'board', 'list', 'table'
  const [searchQuery, setSearchQuery] = useState('')
  const [draggedTicket, setDraggedTicket] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: TICKET_PRIORITY.MEDIUM,
    category: TICKET_CATEGORY.OTHER,
    user_email: getUserEmail(),
    assigned_to: '',
    device_id: ''
  })

  // The reporter's own machines, so a ticket can say which one it is about.
  // Optional: plenty of tickets are about no machine at all.
  const [myDevices, setMyDevices] = useState([])
  
  // Chat history panel state
  const [showChatHistory, setShowChatHistory] = useState(false)
  const [selectedTicketForChat, setSelectedTicketForChat] = useState(null)
  const [chatHistory, setChatHistory] = useState([])
  const [loadingChatHistory, setLoadingChatHistory] = useState(false)

  // Assignable users state
  const [assignableUsers, setAssignableUsers] = useState([])
  const [loadingAssignableUsers, setLoadingAssignableUsers] = useState(false)

  useEffect(() => {
    fetchTickets()
    fetchAssignableUsers()
    fetchMyDevices()
    
    // Auto-refresh tickets every 30 seconds to show priority changes
    const interval = setInterval(() => {
      fetchTickets()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const fetchTickets = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      console.log('🎫 Token available for tickets:', token ? 'YES' : 'NO')
      const data = await ticketService.getAll()
      setTickets(data)
      setError(null)
    } catch (err) {
      console.error('❌ Error fetching tickets:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchAssignableUsers = async () => {
    try {
      setLoadingAssignableUsers(true)
      const token = localStorage.getItem('token')
      const { getAssignableUsers } = await import('../services/userService')
      const users = await getAssignableUsers()
      console.log('Assignable users loaded:', users)
      setAssignableUsers(users)
    } catch (err) {
      console.error('Failed to fetch assignable users:', err)
      setAssignableUsers([])
    } finally {
      setLoadingAssignableUsers(false)
    }
  }

  const getPriorityClass = (priority) => {
    // Handle both string (from API) and number (from frontend)
    if (typeof priority === 'string') {
      return priority
    }
    const priorityMap = {
      1: 'critical',
      2: 'high', 
      3: 'medium',
      4: 'low'
    }
    return priorityMap[priority] || 'medium'
  }

  const getPriorityLabel = (priority) => {
    // Handle both string (from API) and number (from frontend)
    if (typeof priority === 'string') {
      const num = API_PRIORITY_TO_NUMBER[priority]
      return TICKET_PRIORITY_LABELS[num] || 'Medium'
    }
    return TICKET_PRIORITY_LABELS[priority] || 'Medium'
  }

  const isCriticalPriority = (priority) => {
    return priority === 'critical' || priority === 1
  }

  const getStatusBadge = (status) => {
    const statusMap = {
      'open': { label: 'Open', class: 'status-open' },
      'in_progress': { label: 'In Progress', class: 'status-progress' },
      'assigned_to_human': { label: 'Assigned to Human', class: 'status-assigned' },
      'resolved': { label: 'Resolved', class: 'status-resolved' },
      'closed': { label: 'Closed', class: 'status-closed' }
    }
    return statusMap[status] || { label: TICKET_STATUS_LABELS[status] || status, class: 'status-open' }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} min ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    return date.toLocaleDateString()
  }

  const getRoleDisplayName = (role) => {
    const roleMap = {
      'system_admin': 'System Admin',
      'it_admin': 'IT Admin',
      'support_l1': 'IT Support L1',
      'support_l2': 'IT Support L2',
      'support_l3': 'IT Support L3',
      'manager': 'Manager',
      'staff': 'Staff',
      'contractor': 'Contractor'
    }
    return roleMap[role] || role
  }

  const formatUserForDisplay = (user) => {
    const roleName = getRoleDisplayName(user.role)
    const teamInfo = user.department ? ` (${user.department} Team)` : ''
    return `${user.name} - ${roleName}${teamInfo}`
  }

  const getAssigneeName = (assigneeEmail) => {
    if (!assigneeEmail) return 'Unassigned'
    const user = assignableUsers.find(u => u.email === assigneeEmail)
    if (user) {
      return user.name || user.email
    }
    return assigneeEmail
  }

  // Permission-based action checks
  const canViewChatHistory = () => {
    return hasPermission('ticket:view:own') || hasPermission('ticket:view:team') || hasPermission('ticket:view:all')
  }

  const canEditTicket = (ticket) => {
    // Check if user can edit their own ticket
    if (user?.email === ticket.user_email && hasPermission('ticket:update:own')) {
      return true
    }
    // Check if user can edit any ticket (support staff, admin)
    if (hasPermission('ticket:update:any')) {
      return true
    }
    // Manager can edit team member tickets
    if (user && hasRole('manager') && hasPermission('ticket:update:own')) {
      // In a real scenario, we'd check if the ticket belongs to the manager's team
      // For now, we allow if they're a manager
      return true
    }
    return false
  }

  const canDeleteTicket = (ticket) => {
    // Check if user can delete their own ticket
    if (user?.email === ticket.user_email && hasPermission('ticket:delete:own')) {
      return true
    }
    // Check if user can delete any ticket (admin)
    if (hasPermission('ticket:delete:any')) {
      return true
    }
    return false
  }

  const canAssignTicket = () => {
    return hasPermission('ticket:assign')
  }

  // A machine list is a convenience, not a requirement: if it cannot be
  // fetched the field simply does not appear and the ticket is still raised.
  const fetchMyDevices = async () => {
    try {
      const response = await deviceService.listMine()
      setMyDevices(response?.devices || response || [])
    } catch (err) {
      console.debug('Could not load devices for the ticket form:', err.message)
      setMyDevices([])
    }
  }

  const handleCreateTicket = async (e) => {
    e.preventDefault()
    setCreating(true)
    try {
      // Convert priority number to API string
      const ticketData = {
        ...formData,
        priority: TICKET_PRIORITY_TO_API[formData.priority],
        // "" would fail the ownership check; no machine named means null.
        device_id: formData.device_id || null
      }
      await ticketService.create(ticketData)
      await fetchTickets()
      setShowCreateModal(false)
      // Reset form but keep user email
      setFormData({
        title: '',
        description: '',
        priority: TICKET_PRIORITY.MEDIUM,
        category: TICKET_CATEGORY.OTHER,
        user_email: getUserEmail(),
        assigned_to: '',
        device_id: ''
      })
    } catch (err) {
      alert('Error creating ticket: ' + err.message)
    } finally {
      setCreating(false)
    }
  }

  const handleEditTicket = (ticket) => {
    setEditingTicket(ticket)
    setFormData({
      title: ticket.title,
      description: ticket.description,
      priority: API_PRIORITY_TO_NUMBER[ticket.priority] || TICKET_PRIORITY.MEDIUM,
      category: ticket.category || TICKET_CATEGORY.OTHER,
      status: ticket.status || TICKET_STATUS.OPEN,
      user_email: ticket.user_email,
      assigned_to: ticket.assigned_to || '',
      device_id: ticket.device_id || ''
    })
    setShowEditModal(true)
  }

  const handleUpdateTicket = async (e) => {
    e.preventDefault()
    setUpdating(true)
    try {
      // Convert priority number to API string
      const ticketData = {
        title: formData.title,
        description: formData.description,
        priority: TICKET_PRIORITY_TO_API[formData.priority],
        category: formData.category,
        status: formData.status,
        user_email: formData.user_email,
        assigned_to: formData.assigned_to || null
      }
      await ticketService.update(editingTicket.id, ticketData)
      await fetchTickets()
      setShowEditModal(false)
      setEditingTicket(null)
      // Reset form with user email
      setFormData({
        title: '',
        description: '',
        priority: TICKET_PRIORITY.MEDIUM,
        category: TICKET_CATEGORY.OTHER,
        status: TICKET_STATUS.OPEN,
        user_email: getUserEmail(),
        assigned_to: '',
        device_id: ''
      })
    } catch (err) {
      alert('Error updating ticket: ' + err.message)
    } finally {
      setUpdating(false)
    }
  }

  const handleDeleteTicket = async (ticketId) => {
    if (!confirm('Are you sure you want to delete this ticket?')) return
    
    try {
      await ticketService.delete(ticketId)
      await fetchTickets()
    } catch (err) {
      alert('Error deleting ticket: ' + err.message)
    }
  }

  const handleViewChatHistory = async (ticket) => {
    setSelectedTicketForChat(ticket)
    setShowChatHistory(true)
    setLoadingChatHistory(true)
    
    try {
      const result = await getTicketChatHistory(ticket.id)
      // API returns { sessions: [{ messages: [...] }] }, flatten all messages
      const allMessages = []
      if (result.sessions && result.sessions.length > 0) {
        result.sessions.forEach(session => {
          if (session.messages) {
            allMessages.push(...session.messages)
          }
        })
        // Sort by created_at
        allMessages.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      }
      setChatHistory(allMessages)
    } catch (err) {
      console.error('Failed to load chat history:', err)
      setChatHistory([])
    } finally {
      setLoadingChatHistory(false)
    }
  }

  const closeChatHistory = () => {
    setShowChatHistory(false)
    setSelectedTicketForChat(null)
    setChatHistory([])
  }

  // Continue existing chat - navigate to chat page with ticket context
  const handleContinueChat = (ticket, existingMessages) => {
    const userEmail = getUserEmail()
    
    // Store ticket context for chat page to pick up
    const chatContext = {
      ticketId: ticket.id,
      ticketTitle: ticket.title,
      ticketDescription: ticket.description,
      ticketPriority: ticket.priority,
      ticketStatus: ticket.status,
      resumeChat: true,
      existingMessages: existingMessages || []
    }
    
    localStorage.setItem(`it_support_systems_resume_ticket_${userEmail}`, JSON.stringify(chatContext))
    
    closeChatHistory()
    navigate('/chat')
  }

  // Start new bot chat for manual ticket (no existing chat history)
  const handleFixWithBot = (ticket) => {
    const userEmail = getUserEmail()
    
    // Store ticket context with initial message about the issue
    const chatContext = {
      ticketId: ticket.id,
      ticketTitle: ticket.title,
      ticketDescription: ticket.description,
      ticketPriority: ticket.priority,
      ticketStatus: ticket.status,
      resumeChat: false,
      isManualTicket: true,
      existingMessages: []
    }
    
    localStorage.setItem(`it_support_systems_resume_ticket_${userEmail}`, JSON.stringify(chatContext))
    
    closeChatHistory()
    navigate('/chat')
  }

  const formatMessageTime = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  const handleDragStart = (e, ticket) => {
    setDraggedTicket(ticket)
    e.dataTransfer.effectAllowed = 'move'
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  const handleDrop = async (e, newStatus) => {
    e.preventDefault()
    if (!draggedTicket) return

    try {
      const ticketData = {
        title: draggedTicket.title,
        description: draggedTicket.description,
        priority: draggedTicket.priority,
        category: draggedTicket.category,
        status: newStatus,
        user_email: draggedTicket.user_email
      }
      await ticketService.update(draggedTicket.id, ticketData)
      await fetchTickets()
      setDraggedTicket(null)
    } catch (err) {
      alert('Error updating ticket status: ' + err.message)
    }
  }

  const filteredTickets = tickets.filter(ticket => {
    // Filter by status
    let statusMatch = true
    if (filter === 'all') statusMatch = true
    else if (filter === 'open') statusMatch = ticket.status === 'open'
    else if (filter === 'in_progress') statusMatch = ticket.status === 'in_progress'
    else if (filter === 'assigned_to_human') statusMatch = ticket.status === 'assigned_to_human'
    else if (filter === 'resolved') statusMatch = ticket.status === 'resolved'
    else if (filter === 'closed') statusMatch = ticket.status === 'closed'
    else if (filter === 'critical') statusMatch = ticket.priority === 'critical' || ticket.priority === 1

    // Filter by search query
    const searchMatch = searchQuery === '' || 
      ticket.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.user_email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.id.toString().includes(searchQuery)

    return statusMatch && searchMatch
  })

  if (loading) {
    return (
      <div className="ticket-list-container">
        <div className="loading-spinner">
          <Loader className="spinner" size={50} />
          <p>Loading tickets...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="ticket-list-container">
        <div className="error-message">
          <AlertCircle className="error-icon" size={48} />
          <p>{error}</p>
          <button onClick={fetchTickets} className="retry-btn">
            <RefreshCw size={18} />
            <span>Retry</span>
          </button>
        </div>
      </div>
    )
  }

  // Board view render
  const renderBoardView = () => {
    const columns = [
      { status: 'open', title: 'Open', icon: <AlertCircle size={16} /> },
      { status: 'in_progress', title: 'In Progress', icon: <Clock size={16} /> },
      { status: 'assigned_to_human', title: 'Assigned', icon: <User size={16} /> },
      { status: 'resolved', title: 'Resolved', icon: <CheckCircle size={16} /> },
      { status: 'closed', title: 'Closed', icon: <XCircle size={16} /> }
    ]

    return (
      <div className="jira-board">
        {columns.map(column => {
          const columnTickets = filteredTickets.filter(t => t.status === column.status)
          return (
            <div 
              key={column.status} 
              className="board-column"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, column.status)}
            >
              <div className="column-header">
                {column.icon}
                <span className="column-title">{column.title}</span>
                <span className="column-count">{columnTickets.length}</span>
              </div>
              <div className="column-content">
                {columnTickets.map(ticket => (
                  <div
                    key={ticket.id}
                    className={`board-ticket priority-${getPriorityClass(ticket.priority)}`}
                    draggable
                    onDragStart={(e) => handleDragStart(e, ticket)}
                  >
                    <div className="board-ticket-header">
                      <span className="ticket-key">#{ticket.id}</span>
                      <span className={`priority-icon priority-${getPriorityClass(ticket.priority)}`}>
                        <Zap size={14} />
                      </span>
                    </div>
                    <h4 className="board-ticket-title">{ticket.title}</h4>
                    <div className="board-ticket-footer">
                      <div className="ticket-meta-section">
                        <div className="ticket-meta-small">
                          <User size={12} />
                          <span>{ticket.user_email.split('@')[0]}</span>
                        </div>
                        {ticket.assigned_to && (
                          <div className="ticket-meta-small assignee-badge">
                            <User size={12} />
                            <span title={getAssigneeName(ticket.assigned_to)}>
                              {getAssigneeName(ticket.assigned_to)}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="ticket-actions-compact">
                        {canViewChatHistory() && (
                          <button onClick={() => handleViewChatHistory(ticket)} className="icon-btn" title="View chat history">
                            <History size={14} />
                          </button>
                        )}
                        {canEditTicket(ticket) && (
                          <button onClick={() => handleEditTicket(ticket)} className="icon-btn">
                            <Edit2 size={14} />
                          </button>
                        )}
                        {canDeleteTicket(ticket) && (
                          <button onClick={() => handleDeleteTicket(ticket.id)} className="icon-btn delete">
                            <Trash2 size={14} />
                          </button>
                        )}
                        {!canViewChatHistory() && !canEditTicket(ticket) && !canDeleteTicket(ticket) && (
                          <span className="no-actions" title="No actions available">
                            <Lock size={14} />
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {columnTickets.length === 0 && (
                  <div className="empty-column">No tickets</div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  // List view render
  const renderListView = () => (
    <div className="jira-list">
      {filteredTickets.map(ticket => {
        const status = getStatusBadge(ticket.status)
        const priorityClass = getPriorityClass(ticket.priority)
        const priorityLabel = getPriorityLabel(ticket.priority)

        return (
          <div key={ticket.id} className="list-ticket">
            <div className="list-ticket-main">
              <div className="list-ticket-id">
                <span className="ticket-key">#{ticket.id}</span>
              </div>
              <div className="list-ticket-content">
                <h3 className="list-ticket-title">{ticket.title}</h3>
                <p className="list-ticket-description">
                  {ticket.description.length > 100 
                    ? ticket.description.substring(0, 100) + '...'
                    : ticket.description
                  }
                </p>
              </div>
              <div className="list-ticket-meta">
                <span className={`badge ${status.class}`}>
                  {status.label}
                </span>
                <span className={`badge priority-badge-${priorityClass}`}>
                  <Zap size={12} />
                  {priorityLabel}
                </span>
                {ticket.category && (
                  <span className="badge category-badge">
                    <Tag size={12} />
                    {TICKET_CATEGORY_LABELS[ticket.category]}
                  </span>
                )}
              </div>
              <div className="list-ticket-info">
                <div className="info-item">
                  <User size={14} />
                  <span>Reporter: {ticket.user_email.split('@')[0]}</span>
                </div>
                {ticket.assigned_to && (
                  <div className="info-item assignee">
                    <User size={14} />
                    <span>Assignee: {getAssigneeName(ticket.assigned_to)}</span>
                  </div>
                )}
                <div className="info-item">
                  <Calendar size={14} />
                  <span>{formatDate(ticket.created_at)}</span>
                </div>
              </div>
              <div className="list-ticket-actions">
                {canViewChatHistory() && (
                  <button onClick={() => handleViewChatHistory(ticket)} className="icon-btn" title="View chat history">
                    <History size={16} />
                  </button>
                )}
                {canEditTicket(ticket) && (
                  <button onClick={() => handleEditTicket(ticket)} className="icon-btn">
                    <Edit2 size={16} />
                  </button>
                )}
                {canDeleteTicket(ticket) && (
                  <button onClick={() => handleDeleteTicket(ticket.id)} className="icon-btn delete">
                    <Trash2 size={16} />
                  </button>
                )}
                {!canViewChatHistory() && !canEditTicket(ticket) && !canDeleteTicket(ticket) && (
                  <span className="no-actions" title="No actions available">
                    <Lock size={16} />
                  </span>
                )}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )

  // Table view render
  const renderTableView = () => (
    <div className="jira-table-container">
      <table className="jira-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Status</th>
            <th>Priority</th>
            <th>Category</th>
            <th>Reporter</th>
            <th>Assignee</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredTickets.map(ticket => {
            const status = getStatusBadge(ticket.status)
            const priorityClass = getPriorityClass(ticket.priority)
            const priorityLabel = getPriorityLabel(ticket.priority)

            return (
              <tr key={ticket.id} className="table-row">
                <td className="table-id">#{ticket.id}</td>
                <td className="table-title">
                  <div className="title-cell">
                    <span>{ticket.title}</span>
                  </div>
                </td>
                <td>
                  <span className={`badge ${status.class}`}>
                    {status.label}
                  </span>
                </td>
                <td>
                  <span className={`badge priority-badge-${priorityClass}`}>
                    <Zap size={12} />
                    {priorityLabel}
                  </span>
                </td>
                <td>
                  {ticket.category && (
                    <span className="badge category-badge">
                      {TICKET_CATEGORY_LABELS[ticket.category]}
                    </span>
                  )}
                </td>
                <td>
                  <div className="user-cell">
                    <User size={14} />
                    <span>{ticket.user_email.split('@')[0]}</span>
                  </div>
                </td>
                <td>
                  <div className="user-cell assignee">
                    {ticket.assigned_to ? (
                      <>
                        <User size={14} />
                        <span>{getAssigneeName(ticket.assigned_to)}</span>
                      </>
                    ) : (
                      <span className="text-muted">Unassigned</span>
                    )}
                  </div>
                </td>
                <td>{formatDate(ticket.created_at)}</td>
                <td>
                  <div className="table-actions">
                    {canViewChatHistory() && (
                      <button onClick={() => handleViewChatHistory(ticket)} className="icon-btn" title="View chat history">
                        <History size={14} />
                      </button>
                    )}
                    {canEditTicket(ticket) && (
                      <button onClick={() => handleEditTicket(ticket)} className="icon-btn">
                        <Edit2 size={14} />
                      </button>
                    )}
                    {canDeleteTicket(ticket) && (
                      <button onClick={() => handleDeleteTicket(ticket.id)} className="icon-btn delete">
                        <Trash2 size={14} />
                      </button>
                    )}
                    {!canViewChatHistory() && !canEditTicket(ticket) && !canDeleteTicket(ticket) && (
                      <span className="no-actions" title="No actions available">
                        <Lock size={14} />
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )

  return (
    <div className="ticket-list-container jira-style">
      {/* Jira-style Header */}
      <div className="jira-header">
        <div className="jira-header-left">
          <h1>Issues</h1>
          <div className="header-stats">
            <span className="stat-item">
              {filteredTickets.length} issues
            </span>
          </div>
        </div>
        <div className="jira-header-right">
          {hasPermission('ticket:create') ? (
            <button onClick={() => setShowCreateModal(true)} className="btn-primary">
              <Plus size={18} />
              <span>Create</span>
            </button>
          ) : (
            <button disabled className="btn-primary" title="You don't have permission to create tickets">
              <Lock size={18} />
              <span>Create</span>
            </button>
          )}
        </div>
      </div>

      {/* Toolbar */}
      <div className="jira-toolbar">
        <div className="toolbar-left">
          <div className="search-box">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search issues..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="filter-group">
            <button 
              className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All
            </button>
            <button 
              className={`filter-btn ${filter === 'open' ? 'active' : ''}`}
              onClick={() => setFilter('open')}
            >
              Open
            </button>
            <button 
              className={`filter-btn ${filter === 'in_progress' ? 'active' : ''}`}
              onClick={() => setFilter('in_progress')}
            >
              In Progress
            </button>
            <button 
              className={`filter-btn ${filter === 'critical' ? 'active' : ''}`}
              onClick={() => setFilter('critical')}
            >
              <Zap size={14} />
              Critical
            </button>
          </div>
        </div>
        <div className="toolbar-right">
          <div className="view-switcher">
            <button 
              className={`view-btn ${viewMode === 'board' ? 'active' : ''}`}
              onClick={() => setViewMode('board')}
              title="Board view"
            >
              <LayoutGrid size={18} />
            </button>
            <button 
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
              title="List view"
            >
              <List size={18} />
            </button>
            <button 
              className={`view-btn ${viewMode === 'table' ? 'active' : ''}`}
              onClick={() => setViewMode('table')}
              title="Table view"
            >
              <Table size={18} />
            </button>
          </div>
          <button onClick={fetchTickets} className="refresh-btn">
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {/* Content Area */}
      {filteredTickets.length === 0 ? (
        <div className="empty-state">
          <XCircle className="empty-icon" size={64} />
          <h3>No issues found</h3>
          <p>No issues match your search or filter criteria</p>
        </div>
      ) : (
        <>
          {viewMode === 'board' && renderBoardView()}
          {viewMode === 'list' && renderListView()}
          {viewMode === 'table' && renderTableView()}
        </>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Ticket</h2>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleCreateTicket} className="ticket-form">
              <div className="form-group">
                <label htmlFor="title">Title *</label>
                <input
                  id="title"
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  required
                  placeholder="Brief description of the issue"
                />
              </div>
              <div className="form-group">
                <label htmlFor="description">Description *</label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  required
                  placeholder="Detailed description of the issue"
                  rows="5"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="priority">Priority</label>
                  <select
                    id="priority"
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: parseInt(e.target.value)})}
                  >
                    <option value={TICKET_PRIORITY.LOW}>Low</option>
                    <option value={TICKET_PRIORITY.MEDIUM}>Medium</option>
                    <option value={TICKET_PRIORITY.HIGH}>High</option>
                    <option value={TICKET_PRIORITY.CRITICAL}>Critical</option>
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="category">Category</label>
                  <select
                    id="category"
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                  >
                    {Object.entries(TICKET_CATEGORY_LABELS).map(([value, label]) => (
                      <option key={value} value={value}>{label}</option>
                    ))}
                  </select>
                </div>
              </div>
              {myDevices.length > 0 && (
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="device_id">Which machine? (optional)</label>
                    <select
                      id="device_id"
                      value={formData.device_id}
                      onChange={(e) => setFormData({...formData, device_id: e.target.value})}
                    >
                      <option value="">Not about a specific machine</option>
                      {myDevices.map((device) => (
                        <option key={device.device_id} value={device.device_id}>
                          {device.name || device.hostname || device.device_id}
                          {device.online === false ? ' \u2014 not responding' : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="user_email">Reporter Email *</label>
                  <input
                    id="user_email"
                    type="email"
                    value={formData.user_email}
                    onChange={(e) => setFormData({...formData, user_email: e.target.value})}
                    required
                    placeholder="user@example.com"
                    readOnly
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="assignee">Assignee</label>
                  {canAssignTicket() ? (
                    <select
                      id="assignee"
                      value={formData.assigned_to}
                      onChange={(e) => setFormData({...formData, assigned_to: e.target.value})}
                    >
                      <option value="">Unassigned</option>
                      {loadingAssignableUsers ? (
                        <option disabled>Loading users...</option>
                      ) : (
                        assignableUsers.map(user => (
                          <option key={user.id} value={user.email}>
                            {formatUserForDisplay(user)}
                          </option>
                        ))
                      )}
                    </select>
                  ) : (
                    <select id="assignee" disabled>
                      <option>No permission to assign</option>
                    </select>
                  )}
                </div>
              </div>
              <div className="form-actions">
                <button type="button" onClick={() => setShowCreateModal(false)} className="btn-cancel">
                  Cancel
                </button>
                <button type="submit" disabled={creating} className="btn-submit">
                  {creating ? 'Creating...' : 'Create Issue'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showEditModal && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Edit Ticket #{editingTicket?.id}</h2>
              <button className="modal-close" onClick={() => setShowEditModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleUpdateTicket} className="ticket-form">
              <div className="form-group">
                <label htmlFor="edit-title">Title *</label>
                <input
                  id="edit-title"
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  required
                  placeholder="Brief description of the issue"
                />
              </div>
              <div className="form-group">
                <label htmlFor="edit-description">Description *</label>
                <textarea
                  id="edit-description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  required
                  placeholder="Detailed description of the issue"
                  rows="5"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit-priority">Priority</label>
                  <select
                    id="edit-priority"
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: parseInt(e.target.value)})}
                  >
                    <option value={TICKET_PRIORITY.LOW}>Low</option>
                    <option value={TICKET_PRIORITY.MEDIUM}>Medium</option>
                    <option value={TICKET_PRIORITY.HIGH}>High</option>
                    <option value={TICKET_PRIORITY.CRITICAL}>Critical</option>
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="edit-status">Status</label>
                  <select
                    id="edit-status"
                    value={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.value})}
                  >
                    <option value={TICKET_STATUS.OPEN}>Open</option>
                    <option value={TICKET_STATUS.IN_PROGRESS}>In Progress</option>
                    <option value={TICKET_STATUS.ASSIGNED_TO_HUMAN}>Assigned to Human</option>
                    <option value={TICKET_STATUS.RESOLVED}>Resolved</option>
                    <option value={TICKET_STATUS.CLOSED}>Closed</option>
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit-category">Category</label>
                  <select
                    id="edit-category"
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                  >
                    {Object.entries(TICKET_CATEGORY_LABELS).map(([value, label]) => (
                      <option key={value} value={value}>{label}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group"></div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit-user_email">Reporter Email *</label>
                  <input
                    id="edit-user_email"
                    type="email"
                    value={formData.user_email}
                    onChange={(e) => setFormData({...formData, user_email: e.target.value})}
                    required
                    placeholder="user@example.com"
                    readOnly
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="edit-assignee">Assignee</label>
                  {canAssignTicket() ? (
                    <select
                      id="edit-assignee"
                      value={formData.assigned_to || ''}
                      onChange={(e) => setFormData({...formData, assigned_to: e.target.value})}
                    >
                      <option value="">Unassigned</option>
                      {loadingAssignableUsers ? (
                        <option disabled>Loading users...</option>
                      ) : (
                        assignableUsers.map(user => (
                          <option key={user.id} value={user.email}>
                            {formatUserForDisplay(user)}
                          </option>
                        ))
                      )}
                    </select>
                  ) : (
                    <select id="edit-assignee" disabled>
                      <option>No permission to assign</option>
                    </select>
                  )}
                </div>
              </div>
              <div className="form-actions">
                <button type="button" onClick={() => setShowEditModal(false)} className="btn-cancel">
                  Cancel
                </button>
                <button type="submit" disabled={updating} className="btn-submit">
                  {updating ? 'Updating...' : 'Update Issue'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Chat History Modal */}
      {showChatHistory && (
        <div className="modal-overlay" onClick={closeChatHistory}>
          <div className="modal-content chat-history-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="chat-history-header-info">
                <History size={20} />
                <h2>Chat History - Ticket #{selectedTicketForChat?.id}</h2>
              </div>
              <button className="modal-close" onClick={closeChatHistory}>
                <X size={20} />
              </button>
            </div>
            
            <div className="chat-history-ticket-info">
              <h3>{selectedTicketForChat?.title}</h3>
              <div className="ticket-meta-row">
                <span className={`badge priority-badge-${getPriorityClass(selectedTicketForChat?.priority)}`}>
                  <Zap size={12} />
                  {getPriorityLabel(selectedTicketForChat?.priority)}
                </span>
                <span className={`badge ${getStatusBadge(selectedTicketForChat?.status).class}`}>
                  {getStatusBadge(selectedTicketForChat?.status).label}
                </span>
              </div>
            </div>

            <div className="chat-history-content">
              {loadingChatHistory ? (
                <div className="chat-loading">
                  <Loader className="spinner" size={30} />
                  <p>Loading chat history...</p>
                </div>
              ) : chatHistory.length === 0 ? (
                <div className="chat-empty">
                  <Bot size={48} />
                  <p>No chat history found for this ticket</p>
                  <small>This ticket was created manually. Start a conversation with the AI bot to troubleshoot and resolve this issue.</small>
                  {selectedTicketForChat?.status !== 'resolved' && selectedTicketForChat?.status !== 'closed' && (
                    <button 
                      className="btn-fix-with-bot"
                      onClick={() => handleFixWithBot(selectedTicketForChat)}
                    >
                      <Bot size={18} />
                      Fix with AI Bot
                    </button>
                  )}
                </div>
              ) : (
                <div className="chat-messages-list">
                  {chatHistory.map((msg, index) => (
                    <div key={msg.id || index} className={`chat-message-item ${msg.role}`}>
                      <div className="chat-message-header">
                        <span className="chat-role">
                          {msg.role === 'user' ? (
                            <>
                              <User size={14} />
                              User
                            </>
                          ) : (
                            <>
                              <MessageSquare size={14} />
                              AI Assistant
                            </>
                          )}
                        </span>
                        <span className="chat-time">{formatMessageTime(msg.created_at)}</span>
                      </div>
                      <div className="chat-message-body">
                        {msg.content}
                        {msg.image_filename && (
                          <div className="chat-image-indicator">
                            📷 Image attached: {msg.image_filename}
                          </div>
                        )}
                        {msg.image_analysis && (
                          <div className="chat-image-analysis">
                            <strong>Image Analysis:</strong> {msg.image_analysis}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {/* Action buttons at bottom of modal */}
            {!loadingChatHistory && chatHistory.length > 0 && 
             selectedTicketForChat?.status !== 'resolved' && 
             selectedTicketForChat?.status !== 'closed' && (
              <div className="chat-history-actions">
                <button 
                  className="btn-continue-chat"
                  onClick={() => handleContinueChat(selectedTicketForChat, chatHistory)}
                >
                  <PlayCircle size={18} />
                  Continue Chat
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default TicketList
