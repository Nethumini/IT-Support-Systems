/**
 * System Information Service
 * Uses browser APIs to gather system information
 * Note: Browsers have security restrictions and cannot access full Task Manager data
 */

class SystemInfoService {
  constructor() {
    this.hasPermission = false
    this.systemInfo = null
  }

  /**
   * Request permission to access system information
   */
  async requestPermission() {
    try {
      // Note: Browsers don't have a direct permission API for system info
      // But we can check what's available and request user consent
      
      // Check if we can access performance API
      if (typeof performance !== 'undefined' && performance.memory) {
        this.hasPermission = true
        return { granted: true, message: 'System information access granted' }
      }
      
      // Check for device memory API
      if (navigator.deviceMemory) {
        this.hasPermission = true
        return { granted: true, message: 'System information access granted' }
      }
      
      // If no special APIs, still grant basic access
      this.hasPermission = true
      return { granted: true, message: 'Basic system information available' }
    } catch (error) {
      console.error('Permission request error:', error)
      return { granted: false, message: 'Unable to access system information' }
    }
  }

  /**
   * Get CPU information
   */
  getCPUInfo() {
    return {
      cores: navigator.hardwareConcurrency || 'Unknown',
      architecture: navigator.platform || 'Unknown',
      // Note: Real CPU usage % is not available in browsers
      // We can only get number of cores
    }
  }

  /**
   * Get Memory information
   */
  getMemoryInfo() {
    const info = {
      total: null,
      used: null,
      available: null,
      usagePercent: null
    }

    // Try to get device memory (Chrome/Edge only)
    if (navigator.deviceMemory) {
      info.total = navigator.deviceMemory * 1024 // Convert GB to MB
    }

    // Try to get JavaScript heap memory (Chrome/Edge only)
    if (typeof performance !== 'undefined' && performance.memory) {
      const memory = performance.memory
      info.used = Math.round(memory.usedJSHeapSize / 1048576) // Convert to MB
      info.total = Math.round(memory.totalJSHeapSize / 1048576) // Convert to MB
      info.available = Math.round(memory.jsHeapSizeLimit / 1048576) // Convert to MB
      
      if (info.total > 0) {
        info.usagePercent = Math.round((info.used / info.total) * 100)
      }
    }

    return info
  }

  /**
   * Get Network information
   */
  getNetworkInfo() {
    const info = {
      connectionType: 'Unknown',
      effectiveType: 'Unknown',
      downlink: null,
      rtt: null,
      saveData: false
    }

    // Network Information API (Chrome/Edge/Opera)
    if (navigator.connection || navigator.mozConnection || navigator.webkitConnection) {
      const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection
      
      info.connectionType = connection.type || 'Unknown'
      info.effectiveType = connection.effectiveType || 'Unknown'
      info.downlink = connection.downlink || null
      info.rtt = connection.rtt || null
      info.saveData = connection.saveData || false
    }

    return info
  }

  /**
   * Get Storage information
   */
  async getStorageInfo() {
    const info = {
      quota: null,
      usage: null,
      available: null,
      usagePercent: null
    }

    // Storage API (Chrome/Edge/Opera)
    if (navigator.storage && navigator.storage.estimate) {
      try {
        const estimate = await navigator.storage.estimate()
        if (estimate.quota && estimate.usage) {
          info.quota = Math.round(estimate.quota / 1048576) // Convert to MB
          info.usage = Math.round(estimate.usage / 1048576) // Convert to MB
          info.available = info.quota - info.usage
          
          if (info.quota > 0) {
            info.usagePercent = Math.round((info.usage / info.quota) * 100)
          }
        }
      } catch (error) {
        console.error('Storage estimate error:', error)
      }
    }

    return info
  }

  /**
   * Get Screen information
   */
  getScreenInfo() {
    return {
      resolution: `${window.screen.width}x${window.screen.height}`,
      availResolution: `${window.screen.availWidth}x${window.screen.availHeight}`,
      colorDepth: `${window.screen.colorDepth} bit`,
      pixelRatio: window.devicePixelRatio || 1
    }
  }

  /**
   * Get Browser information
   */
  getBrowserInfo() {
    const userAgent = navigator.userAgent
    let browser = 'Unknown'
    let version = 'Unknown'

    if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) {
      browser = 'Chrome'
      const match = userAgent.match(/Chrome\/(\d+)/)
      version = match ? match[1] : 'Unknown'
    } else if (userAgent.includes('Firefox')) {
      browser = 'Firefox'
      const match = userAgent.match(/Firefox\/(\d+)/)
      version = match ? match[1] : 'Unknown'
    } else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
      browser = 'Safari'
      const match = userAgent.match(/Version\/(\d+)/)
      version = match ? match[1] : 'Unknown'
    } else if (userAgent.includes('Edg')) {
      browser = 'Edge'
      const match = userAgent.match(/Edg\/(\d+)/)
      version = match ? match[1] : 'Unknown'
    }

    return { browser, version, userAgent }
  }

  /**
   * Get all system information
   */
  async getAllSystemInfo() {
    if (!this.hasPermission) {
      throw new Error('Permission not granted. Please request permission first.')
    }

    const [storageInfo] = await Promise.all([
      this.getStorageInfo()
    ])

    return {
      cpu: this.getCPUInfo(),
      memory: this.getMemoryInfo(),
      network: this.getNetworkInfo(),
      storage: storageInfo,
      screen: this.getScreenInfo(),
      browser: this.getBrowserInfo(),
      timestamp: new Date().toISOString()
    }
  }

  /**
   * Check if advanced APIs are available
   */
  checkAPIAvailability() {
    return {
      performanceMemory: typeof performance !== 'undefined' && !!performance.memory,
      deviceMemory: !!navigator.deviceMemory,
      networkInfo: !!(navigator.connection || navigator.mozConnection || navigator.webkitConnection),
      storageEstimate: !!(navigator.storage && navigator.storage.estimate),
      hardwareConcurrency: !!navigator.hardwareConcurrency
    }
  }
}

export const systemInfoService = new SystemInfoService()
export default SystemInfoService

