import { httpClient } from './httpClient'
import { API_ENDPOINTS } from '../config/constants'

/**
 * Status Service
 * Handles backend status checks
 */
export const statusService = {
  /**
   * Check backend status
   */
  async check() {
    return httpClient.get(API_ENDPOINTS.STATUS)
  }
}
