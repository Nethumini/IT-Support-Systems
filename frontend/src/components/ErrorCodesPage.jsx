import { useState, useMemo } from 'react'
import { Search, AlertCircle, Info, Wrench, Monitor, Apple, Terminal } from 'lucide-react'
import { errorCodes, searchErrorCodes } from '../data/errorCodes'
import '../styles/components/ErrorCodesPage.css'

function ErrorCodesPage() {
  const [activeTab, setActiveTab] = useState('windows')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedError, setSelectedError] = useState(null)

  // Filter error codes based on search query
  const filteredErrors = useMemo(() => {
    if (!searchQuery.trim()) {
      return errorCodes[activeTab] || []
    }
    return searchErrorCodes(searchQuery, activeTab)
  }, [searchQuery, activeTab])

  const handleErrorSelect = (error) => {
    setSelectedError(error)
  }

  const handleSearch = (e) => {
    setSearchQuery(e.target.value)
    setSelectedError(null)
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'severity-critical'
      case 'high':
        return 'severity-high'
      case 'medium':
        return 'severity-medium'
      case 'low':
        return 'severity-low'
      default:
        return 'severity-medium'
    }
  }

  const getSeverityLabel = (severity) => {
    return severity.charAt(0).toUpperCase() + severity.slice(1)
  }

  const tabs = [
    { id: 'windows', label: 'Windows', icon: Monitor },
    { id: 'mac', label: 'macOS', icon: Apple },
    { id: 'linux', label: 'Linux', icon: Terminal }
  ]

  return (
    <div className="error-codes-container">
      <div className="error-codes-header">
        <div className="header-content">
          <div className="header-icon">
            <AlertCircle size={32} />
          </div>
          <div>
            <h1>Error Codes Reference</h1>
            <p>Common system error codes with potential causes and mitigation steps</p>
          </div>
        </div>
      </div>

      <div className="error-codes-content">
        {/* Search Bar */}
        <div className="search-section">
          <div className="search-input-wrapper">
            <Search size={20} className="search-icon" />
            <input
              type="text"
              placeholder={`Search error codes in ${tabs.find(t => t.id === activeTab)?.label}...`}
              value={searchQuery}
              onChange={handleSearch}
              className="search-input"
            />
            {searchQuery && (
              <button
                onClick={() => {
                  setSearchQuery('')
                  setSelectedError(null)
                }}
                className="clear-search-btn"
              >
                Clear
              </button>
            )}
          </div>
          {searchQuery && (
            <div className="search-results-count">
              Found {filteredErrors.length} result{filteredErrors.length !== 1 ? 's' : ''}
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="tabs-container">
          {tabs.map(tab => {
            const Icon = tab.icon
            const errorCount = errorCodes[tab.id]?.length || 0
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id)
                  setSelectedError(null)
                  setSearchQuery('')
                }}
                className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              >
                <Icon size={18} />
                <span>{tab.label}</span>
                <span className="tab-count">{errorCount}</span>
              </button>
            )
          })}
        </div>

        <div className="error-codes-layout">
          {/* Error List */}
          <div className="error-list-panel">
            <div className="panel-header">
              <h2>
                {searchQuery 
                  ? `Search Results (${filteredErrors.length})`
                  : `${tabs.find(t => t.id === activeTab)?.label} Error Codes (${filteredErrors.length})`
                }
              </h2>
            </div>
            <div className="error-list">
              {filteredErrors.length === 0 ? (
                <div className="empty-state">
                  <Info size={48} />
                  <p>No error codes found</p>
                  <span>Try adjusting your search query</span>
                </div>
              ) : (
                filteredErrors.map((error, index) => (
                  <div
                    key={index}
                    onClick={() => handleErrorSelect(error)}
                    className={`error-item ${selectedError?.code === error.code ? 'selected' : ''}`}
                  >
                    <div className="error-item-header">
                      <div className="error-code-badge">
                        <code>{error.code}</code>
                      </div>
                      <span className={`severity-badge ${getSeverityColor(error.severity)}`}>
                        {getSeverityLabel(error.severity)}
                      </span>
                    </div>
                    <div className="error-item-name">{error.name}</div>
                    <div className="error-item-description">
                      {error.description.substring(0, 100)}
                      {error.description.length > 100 ? '...' : ''}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Error Details */}
          <div className="error-details-panel">
            {selectedError ? (
              <div className="error-details">
                <div className="details-header">
                  <div className="details-code-section">
                    <code className="details-code">{selectedError.code}</code>
                    <span className={`details-severity ${getSeverityColor(selectedError.severity)}`}>
                      {getSeverityLabel(selectedError.severity)} Severity
                    </span>
                  </div>
                  <h2 className="details-name">{selectedError.name}</h2>
                </div>

                <div className="details-section">
                  <h3 className="section-title">
                    <Info size={18} />
                    Description
                  </h3>
                  <p className="section-content">{selectedError.description}</p>
                </div>

                <div className="details-section">
                  <h3 className="section-title">
                    <AlertCircle size={18} />
                    Potential Reason
                  </h3>
                  <p className="section-content">{selectedError.potentialReason}</p>
                </div>

                <div className="details-section">
                  <h3 className="section-title">
                    <Wrench size={18} />
                    Mitigation Steps
                  </h3>
                  <ol className="mitigation-steps">
                    {selectedError.mitigationSteps.map((step, index) => (
                      <li key={index} className="mitigation-step">
                        {step}
                      </li>
                    ))}
                  </ol>
                </div>
              </div>
            ) : (
              <div className="empty-details">
                <Info size={64} />
                <h3>Select an error code</h3>
                <p>Click on an error code from the list to view detailed information, potential causes, and mitigation steps.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ErrorCodesPage

