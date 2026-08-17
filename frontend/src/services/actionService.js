/**
 * Action Service - Handles automated remediation actions
 */
import { API_CONFIG } from '../config/constants';
import { httpClient } from './httpClient';

const API_BASE_URL = API_CONFIG.BASE_URL;

/**
 * Get all available actions
 * @param {string} category - Optional category filter
 * @returns {Promise<Object>}
 */
export async function getAvailableActions(category = null) {
  try {
    const url = category 
      ? `${API_BASE_URL}/actions/available?category=${category}`
      : `${API_BASE_URL}/actions/available`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch actions');
    return response.json();
  } catch (error) {
    console.error('Error fetching actions:', error);
    throw error;
  }
}

/**
 * Get suggested actions based on issue description
 * @param {string} issueDescription - Description of the issue
 * @returns {Promise<Object>}
 */
export async function getSuggestedActions(issueDescription) {
  try {
    const response = await fetch(`${API_BASE_URL}/actions/suggest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ issue_description: issueDescription })
    });
    if (!response.ok) throw new Error('Failed to get suggestions');
    return response.json();
  } catch (error) {
    console.error('Error getting suggestions:', error);
    throw error;
  }
}

/**
 * Create an action request (pending approval)
 * @param {string} actionId - The action to execute
 * @param {Object} parameters - Action parameters
 * @param {string} userEmail - User's email
 * @param {number} ticketId - Optional ticket ID
 * @returns {Promise<Object>}
 */
export async function createActionRequest(actionId, parameters, userEmail, ticketId = null) {
  try {
    const payload = {
      action_id: actionId,
      parameters: parameters || {},
      user_email: userEmail
    };
    // Only include ticket_id if it's a valid number
    if (ticketId !== null && ticketId !== undefined) {
      payload.ticket_id = ticketId;
    }
    
    console.log('[ActionService] Creating action request:', payload);
    
    const response = await fetch(`${API_BASE_URL}/actions/request`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      const error = await response.json();
      console.error('[ActionService] Request failed:', error);
      throw new Error(error.detail || 'Failed to create action request');
    }
    return response.json();
  } catch (error) {
    console.error('Error creating action request:', error);
    throw error;
  }
}

/**
 * Approve or cancel an action
 * @param {string} requestId - The action request ID
 * @param {string} userEmail - User's email
 * @param {boolean} approved - Whether to approve or cancel
 * @returns {Promise<Object>}
 */
export async function approveAction(requestId, userEmail, approved = true) {
  try {
    const response = await fetch(`${API_BASE_URL}/actions/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request_id: requestId,
        user_email: userEmail,
        approved
      })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to approve action');
    }
    return response.json();
  } catch (error) {
    console.error('Error approving action:', error);
    throw error;
  }
}

/**
 * Execute a low-risk action directly (no approval needed)
 * @param {string} actionId - The action to execute
 * @param {Object} parameters - Action parameters
 * @param {string} userEmail - User's email
 * @returns {Promise<Object>}
 */
export async function executeActionDirectly(actionId, parameters = {}, userEmail) {
  try {
    const params = new URLSearchParams({ user_email: userEmail });
    const response = await fetch(`${API_BASE_URL}/actions/execute/${actionId}?${params}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to execute action');
    }
    return response.json();
  } catch (error) {
    console.error('Error executing action:', error);
    throw error;
  }
}

/**
 * Get pending actions for a user
 * @param {string} userEmail - User's email
 * @returns {Promise<Object>}
 */
export async function getPendingActions(userEmail) {
  try {
    const response = await fetch(`${API_BASE_URL}/actions/pending?user_email=${encodeURIComponent(userEmail)}`);
    if (!response.ok) throw new Error('Failed to fetch pending actions');
    return response.json();
  } catch (error) {
    console.error('Error fetching pending actions:', error);
    throw error;
  }
}

/**
 * Get action history for a user
 * @param {string} userEmail - User's email
 * @param {number} limit - Max results
 * @returns {Promise<Object>}
 */
export async function getActionHistory(userEmail, limit = 20) {
  try {
    const response = await fetch(`${API_BASE_URL}/actions/history?user_email=${encodeURIComponent(userEmail)}&limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch action history');
    return response.json();
  } catch (error) {
    console.error('Error fetching action history:', error);
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Quick Diagnostics
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get top processes by CPU usage
 * @param {string} userEmail - User's email
 * @returns {Promise<Object>}
 */
export async function diagnoseProcesses(userEmail) {
  try {
    const response = await fetch(`${API_BASE_URL}/actions/diagnose/processes?user_email=${encodeURIComponent(userEmail)}`);
    if (!response.ok) throw new Error('Failed to diagnose processes');
    return response.json();
  } catch (error) {
    console.error('Error diagnosing processes:', error);
    throw error;
  }
}

/**
 * Get system health (CPU, Memory, Disk)
 * @param {string} userEmail - User's email
 * @returns {Promise<Object>}
 */
export async function diagnoseSystem(userEmail) {
  try {
    const response = await fetch(`${API_BASE_URL}/actions/diagnose/system?user_email=${encodeURIComponent(userEmail)}`);
    if (!response.ok) throw new Error('Failed to diagnose system');
    return response.json();
  } catch (error) {
    console.error('Error diagnosing system:', error);
    throw error;
  }
}

/**
 * Test network connectivity
 * @param {string} userEmail - User's email
 * @returns {Promise<Object>}
 */
export async function diagnoseNetwork(userEmail) {
  try {
    const response = await fetch(`${API_BASE_URL}/actions/diagnose/network?user_email=${encodeURIComponent(userEmail)}`);
    if (!response.ok) throw new Error('Failed to diagnose network');
    return response.json();
  } catch (error) {
    console.error('Error diagnosing network:', error);
    throw error;
  }
}

/**
 * Check disk space
 * @param {string} userEmail - User's email
 * @returns {Promise<Object>}
 */
export async function diagnoseDisk(userEmail) {
  try {
    const response = await fetch(`${API_BASE_URL}/actions/diagnose/disk?user_email=${encodeURIComponent(userEmail)}`);
    if (!response.ok) throw new Error('Failed to diagnose disk');
    return response.json();
  } catch (error) {
    console.error('Error diagnosing disk:', error);
    throw error;
  }
}

/**
 * Analyze diagnostic output and get smart suggestions
 * @param {Object} diagnosticOutput - The output from a diagnostic action
 * @param {string} diagnosticType - Type: processes, system_health, disk, network
 * @param {string} userEmail - User's email
 * @returns {Promise<Object>}
 */
export async function analyzeAndSuggest(diagnosticOutput, diagnosticType, userEmail) {
  try {
    const response = await fetch(`${API_BASE_URL}/actions/analyze?user_email=${encodeURIComponent(userEmail)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        diagnostic_output: diagnosticOutput,
        diagnostic_type: diagnosticType
      })
    });
    if (!response.ok) throw new Error('Failed to analyze');
    return response.json();
  } catch (error) {
    console.error('Error analyzing:', error);
    throw error;
  }
}

/**
 * Execute a quick fix for common issues
 * @param {string} issueType - slow_computer, network_issues, disk_full, browser_slow
 * @param {string} userEmail - User's email
 * @returns {Promise<Object>}
 */
export async function quickFix(issueType, userEmail) {
  try {
    const response = await fetch(`${API_BASE_URL}/actions/quick-fix/${issueType}?user_email=${encodeURIComponent(userEmail)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to execute quick fix');
    return response.json();
  } catch (error) {
    console.error('Error executing quick fix:', error);
    throw error;
  }
}

export default {
  getAvailableActions,
  getSuggestedActions,
  createActionRequest,
  approveAction,
  executeActionDirectly,
  getPendingActions,
  getActionHistory,
  diagnoseProcesses,
  diagnoseSystem,
  diagnoseNetwork,
  diagnoseDisk,
  analyzeAndSuggest,
  quickFix
};
