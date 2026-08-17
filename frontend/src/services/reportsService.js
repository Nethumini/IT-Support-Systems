import { httpClient } from './httpClient'
import { API_ENDPOINTS } from '../config/constants'

/**
 * Reports Service
 * Handles report generation, export, and analytics data
 */
export const reportsService = {
  /**
   * Generate report
   * @param {Object} params - Report parameters
   */
  async generate(params = {}) {
    return httpClient.post(API_ENDPOINTS.REPORTS.GENERATE, params)
  },

  /**
   * Export report
   * @param {string} format - Export format (pdf, csv, xlsx)
   * @param {Object} params - Export parameters
   */
  async export(format, params = {}) {
    return httpClient.post(API_ENDPOINTS.REPORTS.EXPORT, {
      format,
      ...params
    })
  },

  /**
   * Get ticket statistics summary
   */
  async getTicketStats() {
    return httpClient.get('/tickets/stats/summary')
  },

  /**
   * Get all tickets for analytics
   * @param {Object} params - Query parameters (limit, skip, filters)
   */
  async getTickets(params = {}) {
    return httpClient.get('/tickets', params)
  },

  /**
   * Get system health prediction
   * @param {Object} metrics - System metrics data
   */
  async predictHealth(metrics = {}) {
    return httpClient.post('/predict-health', metrics)
  },

  /**
   * Get real system metrics
   */
  async getSystemMetrics() {
    return httpClient.get('/system-metrics')
  },

  /**
   * Get system stats (CPU, RAM, Disk usage, etc.)
   */
  async getSystemStats() {
    return httpClient.get('/stats')
  },

  /**
   * Check system health
   */
  async checkSystemHealth() {
    return httpClient.post('/check-systems', {})
  }
}
