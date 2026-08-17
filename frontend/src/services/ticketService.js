import { httpClient } from './httpClient'
import { API_ENDPOINTS } from '../config/constants'

/**
 * Ticket Service
 * Handles all ticket-related API calls
 */
export const ticketService = {
  /**
   * Get all tickets
   * @param {Object} params - Query parameters
   */
  async getAll(params = {}) {
    return httpClient.get(API_ENDPOINTS.TICKETS.GET_ALL, params)
  },

  /**
   * Get ticket by ID
   * @param {string} id - Ticket ID
   */
  async getById(id) {
    return httpClient.get(API_ENDPOINTS.TICKETS.GET_BY_ID(id))
  },

  /**
   * Create new ticket
   * @param {Object} ticketData - Ticket data
   */
  async create(ticketData) {
    return httpClient.post(API_ENDPOINTS.TICKETS.CREATE, ticketData)
  },

  /**
   * Update ticket
   * @param {string} id - Ticket ID
   * @param {Object} ticketData - Updated ticket data
   */
  async update(id, ticketData) {
    return httpClient.put(API_ENDPOINTS.TICKETS.UPDATE(id), ticketData)
  },

  /**
   * Delete ticket
   * @param {string} id - Ticket ID
   */
  async delete(id) {
    return httpClient.delete(API_ENDPOINTS.TICKETS.DELETE(id))
  }
}
