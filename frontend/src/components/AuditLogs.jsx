import { useState, useEffect } from 'react';
import { 
  Shield, 
  Search, 
  Filter, 
  RefreshCw,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
  User,
  FileText,
  Activity,
  Download
} from 'lucide-react';
import auditService from '../services/auditService';
import '../styles/components/AuditLogs.css';

const ACTION_TYPES = [
  'USER_LOGIN',
  'USER_LOGOUT',
  'USER_ROLE_CHANGE',
  'USER_UPDATE',
  'USER_DEACTIVATE',
  'TICKET_CREATE',
  'TICKET_UPDATE',
  'TICKET_DELETE',
  'TICKET_VIEW',
  'ACCESS_DENIED',
  'SYSTEM_CONFIG_CHANGE'
];

const RESOURCE_TYPES = [
  'user',
  'ticket',
  'system',
  'endpoint',
  'config'
];

function AuditLogs({ user }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAction, setFilterAction] = useState('');
  const [filterResource, setFilterResource] = useState('');
  const [filterSuccess, setFilterSuccess] = useState('');
  const [filterUser, setFilterUser] = useState('');
  const [viewMode, setViewMode] = useState('all'); // 'all' or 'my'
  const [failedAttempts, setFailedAttempts] = useState([]);

  const isAdmin = user?.role === 'system_admin' || user?.role === 'it_admin';

  useEffect(() => {
    if (viewMode === 'all' && isAdmin) {
      fetchAuditLogs();
    } else {
      fetchMyAuditLogs();
    }
  }, [filterAction, filterResource, filterSuccess, filterUser, viewMode]);

  useEffect(() => {
    if (isAdmin) {
      fetchFailedAttempts();
    }
  }, []);

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {};
      if (filterAction) params.action = filterAction;
      if (filterResource) params.resource_type = filterResource;
      if (filterSuccess) params.success = filterSuccess;
      if (filterUser) params.user_email = filterUser;
      
      const data = await auditService.getAuditLogs(params);
      setLogs(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch audit logs');
      console.error('Error fetching audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMyAuditLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await auditService.getMyAuditLogs(100);
      setLogs(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch your audit logs');
      console.error('Error fetching my audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchFailedAttempts = async () => {
    try {
      const data = await auditService.getFailedAccessAttempts(24);
      setFailedAttempts(data);
    } catch (err) {
      console.error('Error fetching failed attempts:', err);
    }
  };

  const handleRefresh = () => {
    if (viewMode === 'all' && isAdmin) {
      fetchAuditLogs();
      fetchFailedAttempts();
    } else {
      fetchMyAuditLogs();
    }
  };

  const exportLogs = () => {
    const csv = convertToCSV(logs);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-logs-${new Date().toISOString()}.csv`;
    a.click();
  };

  const convertToCSV = (data) => {
    const headers = ['Timestamp', 'User', 'Action', 'Resource', 'Status', 'Details', 'IP Address'];
    const rows = data.map(log => [
      new Date(log.timestamp).toLocaleString(),
      log.user_email,
      log.action,
      `${log.resource_type}${log.resource_id ? ':' + log.resource_id : ''}`,
      log.success,
      log.details || '',
      log.ip_address || ''
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  };

  const getActionIcon = (action) => {
    if (action.includes('LOGIN')) return <User size={16} />;
    if (action.includes('TICKET')) return <FileText size={16} />;
    if (action.includes('DENIED')) return <XCircle size={16} />;
    if (action.includes('ROLE')) return <Shield size={16} />;
    return <Activity size={16} />;
  };

  const getSuccessClass = (success) => {
    switch (success) {
      case 'success': return 'success';
      case 'failed': return 'failed';
      case 'denied': return 'denied';
      default: return 'pending';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    
    return date.toLocaleString();
  };

  const filteredLogs = (logs || []).filter(log => {
    const matchesSearch = 
      log.user_email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.action?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.details?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  return (
    <div className="audit-logs">
      <div className="page-header">
        <div className="header-content">
          <div>
            <h1>Audit Logs</h1>
            <p>Track user actions and system events</p>
          </div>
        </div>
        <div className="header-actions">
          {isAdmin && (
            <>
              <div className="view-toggle">
                <button
                  className={`toggle-btn ${viewMode === 'all' ? 'active' : ''}`}
                  onClick={() => setViewMode('all')}
                >
                  All Logs
                </button>
                <button
                  className={`toggle-btn ${viewMode === 'my' ? 'active' : ''}`}
                  onClick={() => setViewMode('my')}
                >
                  My Logs
                </button>
              </div>
              <button className="btn-export" onClick={exportLogs}>
                <Download size={18} />
                Export
              </button>
            </>
          )}
          <button className="btn-refresh" onClick={handleRefresh} disabled={loading}>
            <RefreshCw size={18} className={loading ? 'spinning' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {isAdmin && failedAttempts && failedAttempts.length > 0 && (
        <div className="alert alert-warning">
          <AlertCircle size={18} />
          <strong>{failedAttempts.length}</strong> failed access attempts in the last 24 hours
        </div>
      )}

      <div className="filters-section">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {viewMode === 'all' && isAdmin && (
          <div className="filter-group">
            <Filter size={18} />
            <input
              type="text"
              placeholder="Filter by user email..."
              value={filterUser}
              onChange={(e) => setFilterUser(e.target.value)}
              className="filter-input"
            />
            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
            >
              <option value="">All Actions</option>
              {ACTION_TYPES.map(action => (
                <option key={action} value={action}>{action}</option>
              ))}
            </select>

            <select
              value={filterResource}
              onChange={(e) => setFilterResource(e.target.value)}
            >
              <option value="">All Resources</option>
              {RESOURCE_TYPES.map(resource => (
                <option key={resource} value={resource}>{resource}</option>
              ))}
            </select>

            <select
              value={filterSuccess}
              onChange={(e) => setFilterSuccess(e.target.value)}
            >
              <option value="">All Status</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
              <option value="denied">Denied</option>
            </select>
          </div>
        )}
      </div>

      <div className="logs-container">
        {loading ? (
          <div className="loading-state">
            <RefreshCw className="spinning" size={32} />
            <p>Loading audit logs...</p>
          </div>
        ) : (
          <table className="logs-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>User</th>
                <th>Action</th>
                <th>Resource</th>
                <th>Status</th>
                <th>IP Address</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log, index) => (
                <tr key={index} className={`log-row ${getSuccessClass(log.success)}`}>
                  <td>{formatTimestamp(log.timestamp)}</td>
                  <td>{log.user_email}</td>
                  <td>
                    <div className="log-action">
                      {getActionIcon(log.action)}
                      <span>{log.action}</span>
                    </div>
                  </td>
                  <td>
                    {log.resource_type}
                    {log.resource_id && ` #${log.resource_id}`}
                  </td>
                  <td>
                    <span className={`status-badge ${getSuccessClass(log.success)}`}>
                      {log.success === 'success' && <CheckCircle size={14} />}
                      {log.success === 'failed' && <XCircle size={14} />}
                      {log.success === 'denied' && <AlertCircle size={14} />}
                      {log.success}
                    </span>
                  </td>
                  <td>{log.ip_address || '-'}</td>
                  <td>{log.details || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {!loading && filteredLogs.length === 0 && (
          <div className="empty-state">
            <Shield size={48} />
            <p>No audit logs found</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default AuditLogs;
