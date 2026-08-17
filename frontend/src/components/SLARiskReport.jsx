import React, { useState, useEffect } from 'react';
import { Clock, AlertTriangle, CheckCircle, Loader } from 'lucide-react';
import { API_CONFIG } from '../config/constants';
import '../styles/components/SLARiskReport.css';

const SLARiskReport = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_CONFIG.BASE_URL}/analytics/sla-risk`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch');
        return res.json();
      })
      .then(data => {
        setTickets(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load SLA report", err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return (
    <div className="sla-report-container">
      <div className="sla-loading">
        <Loader className="animate-spin" size={24} />
        <span>Analyzing Ticket Risk...</span>
      </div>
    </div>
  );

  if (error) return (
    <div className="sla-report-container">
      <div className="sla-error">
        <AlertTriangle size={24} />
        <span>Failed to load SLA predictions</span>
      </div>
    </div>
  );

  return (
    <div className="sla-report-container">
      <div className="sla-header">
        <div className="sla-icon">
          <Clock size={20} />
        </div>
        <div className="sla-title-section">
          <h4 className="sla-title">AI SLA Breach Prediction</h4>
          <p className="sla-subtitle">
            Analyzing {tickets.length} open ticket{tickets.length !== 1 ? 's' : ''} for potential delays.
          </p>
        </div>
      </div>

      <div className="sla-table-wrapper">
        <table className="sla-table">
          <thead>
            <tr>
              <th className="sla-th">Ticket Issue</th>
              <th className="sla-th">Priority</th>
              <th className="sla-th">AI Prediction</th>
              <th className="sla-th">Risk Status</th>
            </tr>
          </thead>
          <tbody>
            {tickets.length === 0 ? (
              <tr>
                <td colSpan="4" className="sla-no-data">
                  <div className="sla-empty-state">
                    <CheckCircle size={32} />
                    <p>No open tickets found to analyze.</p>
                  </div>
                </td>
              </tr>
            ) : (
              tickets.map(t => {
                const isRisk = t.predicted_hours > t.sla_limit;
                return (
                  <tr key={t.id} className="sla-row">
                    <td className="sla-td">
                      <div className="sla-ticket-info">
                        <div className="sla-ticket-title">{t.title}</div>
                        <div className="sla-ticket-id">ID: #{t.id}</div>
                      </div>
                    </td>
                    <td className="sla-td">
                      <span className={`sla-priority ${
                        t.priority === 'critical' ? 'critical' :
                        t.priority === 'high' ? 'high' : 
                        t.priority === 'medium' ? 'medium' : 
                        'low'
                      }`}>
                        {t.priority}
                      </span>
                    </td>
                    <td className="sla-td">
                      <div className="sla-prediction">
                        <div className="sla-predicted-hours">{t.predicted_hours}h</div>
                        <div className="sla-limit">Limit: {t.sla_limit}h</div>
                      </div>
                    </td>
                    <td className="sla-td">
                      {isRisk ? (
                        <div className="sla-status risk">
                          <AlertTriangle size={14} />
                          <span>High Risk</span>
                        </div>
                      ) : (
                        <div className="sla-status safe">
                          <CheckCircle size={14} />
                          <span>On Track</span>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SLARiskReport;
