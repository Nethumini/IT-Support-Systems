import { API_CONFIG, ERROR_MESSAGES } from '../config/constants'
import { STORAGE_KEYS } from '../config/constants'

/**
 * Base HTTP client with error handling and authentication
 */
class HttpClient {
  constructor(baseURL = API_CONFIG.BASE_URL) {
    this.baseURL = baseURL
    this.timeout = API_CONFIG.TIMEOUT
  }

  getAuthToken() {
    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN)
    if (token) {
      console.debug('✓ Auth token found:', token.substring(0, 20) + '...')
    } else {
      console.debug('✗ No auth token in localStorage')
    }
    return token
  }

  getHeaders(customHeaders = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...customHeaders
    }

    const token = this.getAuthToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
      console.debug('✓ Authorization header set')
    } else {
      console.warn('⚠ No token available for Authorization header')
    }

    return headers
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      ...options,
      headers: this.getHeaders(options.headers)
    }

    console.debug(`📡 ${options.method || 'GET'} ${url}`, {
      headers: config.headers,
      body: options.body
    })

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), this.timeout)

      const response = await fetch(url, {
        ...config,
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        console.error(`❌ Request failed with status ${response.status}`)
        if (response.status === 401) {
          console.warn('⚠ Unauthorized (401) - Clearing token and redirecting to login')
          localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
        throw await this.handleErrorResponse(response)
      }

      // Handle empty responses (like 204 No Content for DELETE)
      const contentType = response.headers.get('content-type')
      if (response.status === 204 || !contentType || !contentType.includes('application/json')) {
        return null
      }

      return await response.json()
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async handleErrorResponse(response) {
    const error = new Error()
    error.status = response.status

    try {
      const data = await response.json()
      error.message = data.message || data.detail || ERROR_MESSAGES.SERVER_ERROR
    } catch {
      error.message = this.getDefaultErrorMessage(response.status)
    }

    return error
  }

  getDefaultErrorMessage(status) {
    switch (status) {
      case 401:
        return ERROR_MESSAGES.AUTH_ERROR
      case 404:
        return ERROR_MESSAGES.NOT_FOUND
      case 500:
        return ERROR_MESSAGES.SERVER_ERROR
      default:
        return ERROR_MESSAGES.NETWORK_ERROR
    }
  }

  handleError(error) {
    if (error.name === 'AbortError') {
      error.message = 'Request timeout'
    } else if (!error.message) {
      error.message = ERROR_MESSAGES.NETWORK_ERROR
    }
    return error
  }

  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const url = queryString ? `${endpoint}?${queryString}` : endpoint
    return this.request(url, { method: 'GET' })
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  async patch(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' })
  }
}

export const httpClient = new HttpClient()
