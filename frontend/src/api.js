// API utility for backend integration
import { API_CONFIG } from './config/constants.js';

const API_BASE_URL = API_CONFIG.BASE_URL;

export async function fetchBackendStatus(options = {}) {
  const { signal, timeout = 5000 } = options;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(`${API_BASE_URL}/status`, { signal: signal || controller.signal });
    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(`Backend responded with ${response.status} ${response.statusText} ${text}`);
    }
    return response.json();
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Request timed out');
    }
    throw new Error(err.message || 'Network error');
  } finally {
    clearTimeout(timer);
  }
}

export async function sendChatMessage(messages, userEmail, ticketId = null, sessionId = null, agentMode = false) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: messages.map(m => ({
          role: m.role,
          content: m.content
        })),
        user_email: userEmail,
        ticket_id: ticketId,
        session_id: sessionId,
        agent_mode: agentMode
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Server error: ${response.status}`);
    }

    return response.json();
  } catch (err) {
    throw new Error(err.message || 'Failed to send message');
  }
}

export async function resetChatConversation(userEmail) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_email: userEmail
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Server error: ${response.status}`);
    }

    return response.json();
  } catch (err) {
    console.warn('Failed to reset conversation:', err.message);
    // Don't throw - this is a background operation
    return null;
  }
}

/**
 * Send a chat message with an image attachment
 * @param {File} file - The image file to upload
 * @param {string} message - Optional text message to accompany the image
 * @param {string} userEmail - User email for context
 * @param {number|null} ticketId - Optional existing ticket ID
 * @param {string|null} sessionId - Optional session ID
 * @returns {Promise<Object>} Chat response with image analysis
 */
export async function sendChatMessageWithImage(file, message, userEmail, ticketId = null, sessionId = null) {
  try {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('message', message || '');
    formData.append('user_email', userEmail || 'anonymous@autoops.ai');
    if (ticketId) {
      formData.append('ticket_id', ticketId.toString());
    }
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    const response = await fetch(`${API_BASE_URL}/chat/image`, {
      method: 'POST',
      body: formData,
      // Note: Don't set Content-Type header - browser will set it with boundary for multipart
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      // Handle various error formats from FastAPI
      let errorMessage = `Server error: ${response.status}`;
      if (errorData) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          // Validation errors from FastAPI
          errorMessage = errorData.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
        } else if (typeof errorData.detail === 'object') {
          errorMessage = errorData.detail.msg || errorData.detail.message || JSON.stringify(errorData.detail);
        }
      }
      throw new Error(errorMessage);
    }

    return response.json();
  } catch (err) {
    throw new Error(err.message || 'Failed to send image');
  }
}

/**
 * Get chat history for a ticket
 * @param {number} ticketId - Ticket ID
 * @returns {Promise<Object>} Chat history with sessions
 */
export async function getTicketChatHistory(ticketId) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/history/${ticketId}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Server error: ${response.status}`);
    }
    
    return response.json();
  } catch (err) {
    throw new Error(err.message || 'Failed to get chat history');
  }
}

/**
 * Resume a previous chat session
 * @param {string} sessionId - Session ID to resume
 * @returns {Promise<Object>} Session info
 */
export async function resumeChatSession(sessionId) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/resume/${sessionId}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Server error: ${response.status}`);
    }
    
    return response.json();
  } catch (err) {
    throw new Error(err.message || 'Failed to resume session');
  }
}

/**
 * Get user's recent chat sessions
 * @param {string} userEmail - User email
 * @param {number} limit - Max sessions to return
 * @returns {Promise<Object>} Sessions list
 */
export async function getUserChatSessions(userEmail, limit = 10) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${encodeURIComponent(userEmail)}?limit=${limit}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Server error: ${response.status}`);
    }
    
    return response.json();
  } catch (err) {
    throw new Error(err.message || 'Failed to get sessions');
  }
}
