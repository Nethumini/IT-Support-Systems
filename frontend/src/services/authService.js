import { httpClient } from './httpClient'
import { API_ENDPOINTS } from '../config/constants'

/**
 * Authentication Service
 * Handles all authentication-related API calls
 */
export const authService = {
  /**
   * Login user
   * @param {Object} credentials - User credentials
   * @param {string} credentials.email - User email
   * @param {string} credentials.password - User password
   */
  async login(credentials) {
    return httpClient.post(API_ENDPOINTS.AUTH.LOGIN, credentials)
  },

  /**
   * Register new user
   * @param {Object} userData - User registration data
   */
  async register(userData) {
    return httpClient.post(API_ENDPOINTS.AUTH.REGISTER, userData)
  },

  /**
   * Logout user
   */
  async logout() {
    return httpClient.post(API_ENDPOINTS.AUTH.LOGOUT)
  },

  /**
   * Refresh authentication token
   */
  async refreshToken() {
    return httpClient.post(API_ENDPOINTS.AUTH.REFRESH)
  }
}
