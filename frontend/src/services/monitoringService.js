import { httpClient } from './httpClient'
import { API_ENDPOINTS } from '../config/constants'

/**
 * Monitoring Service
 * Handles all system monitoring API calls
 */
export const monitoringService = {
  /**
   * Get current system metrics for real-time display
   */
  async getMetrics() {
    return httpClient.get(API_ENDPOINTS.MONITORING.SYSTEM_METRICS)
  },

  /**
   * Get real system stats using psutil (Task Manager data)
   */
  async getRealStats() {
    return httpClient.get(API_ENDPOINTS.MONITORING.STATS)
  },

  /**
   * Get services status
   */
  async getServices() {
    return httpClient.get(API_ENDPOINTS.MONITORING.SERVICES)
  },

  /**
   * Get system logs
   * @param {Object} params - Query parameters
   */
  async getLogs(params = {}) {
    return httpClient.get(API_ENDPOINTS.MONITORING.LOGS, params)
  },

  /**
   * Check system health
   */
  async checkSystemHealth(autoCreateTickets = true) {
    return httpClient.post(API_ENDPOINTS.MONITORING.CHECK_HEALTH, { 
      auto_create_tickets: autoCreateTickets 
    })
  }
}
