import { httpClient } from './httpClient'
import { API_ENDPOINTS } from '../config/constants'

/**
 * Chat Service
 * Handles all chat-related API calls
 */
export const chatService = {
  /**
   * Send chat message
   * @param {Array} messages - Message history
   * @param {string} userEmail - User email
   * @param {string} ticketId - Optional ticket ID
   */
  async sendMessage(messages, userEmail, ticketId = null) {
    return httpClient.post(API_ENDPOINTS.CHAT.SEND_MESSAGE, {
      messages,
      user_email: userEmail,
      ticket_id: ticketId
    })
  },

  /**
   * Get chat history
   * @param {string} ticketId - Ticket ID
   */
  async getHistory(ticketId) {
    return httpClient.get(API_ENDPOINTS.CHAT.GET_HISTORY, { ticket_id: ticketId })
  }
}
