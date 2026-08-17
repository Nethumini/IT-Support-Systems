import { httpClient } from './httpClient'
import { API_ENDPOINTS } from '../config/constants'

/**
 * Dashboard Service
 * Handles dashboard-related API calls
 */
export const dashboardService = {
  /**
   * Get dashboard statistics
   */
  async getStats() {
    return httpClient.get(API_ENDPOINTS.DASHBOARD.STATS)
  },

  /**
   * Get recent issues
   * @param {number} limit - Number of issues to fetch
   */
  async getRecentIssues(limit = 10) {
    return httpClient.get(API_ENDPOINTS.DASHBOARD.RECENT_ISSUES, { limit })
  }
}
