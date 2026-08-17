import { httpClient } from './httpClient'
import { API_ENDPOINTS } from '../config/constants'

/**
 * Static Data Service
 * Handles fetching quick actions and error codes from backend
 */
export const staticDataService = {
  /**
   * Get all quick actions data
   * @returns {Promise<Object>} Quick actions and categories
   */
  async getQuickActions() {
    return httpClient.get(API_ENDPOINTS.STATIC_DATA.QUICK_ACTIONS)
  },

  /**
   * Get all error codes data
   * @returns {Promise<Object>} Error codes organized by platform
   */
  async getErrorCodes() {
    return httpClient.get(API_ENDPOINTS.STATIC_DATA.ERROR_CODES)
  },

  /**
   * Get error codes for a specific platform
   * @param {string} platform - One of 'windows', 'mac', or 'linux'
   * @returns {Promise<Object>} Error codes for the platform
   */
  async getErrorCodesByPlatform(platform) {
    return httpClient.get(API_ENDPOINTS.STATIC_DATA.ERROR_CODES_BY_PLATFORM(platform))
  }
}

