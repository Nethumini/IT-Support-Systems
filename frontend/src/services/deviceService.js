import { httpClient } from './httpClient'

/**
 * Endpoint devices - the machines running the AutoOps agent.
 *
 * A remediation targets a device id, but the browser only knows who is logged
 * in. `listMine` is what joins the two: it answers "which machines belong to
 * me", so the chat can run an action on the user's own computer instead of on
 * whatever host the backend happens to be on.
 */
const deviceService = {
  /** Machines belonging to the logged-in user, most recently active first. */
  async listMine() {
    return httpClient.get('/devices/mine')
  },

  /** Every registered machine. Administrators only. */
  async listAll(includeRevoked = false) {
    return httpClient.get(`/devices?include_revoked=${includeRevoked}`)
  },

  /**
   * Register a machine. Administrators only.
   *
   * The response carries the device secret, and it is the only time it is ever
   * available - the server keeps a hash. Show it to the administrator once and
   * do not store it.
   */
  async register({ name, ownerEmail, osName, osVersion }) {
    return httpClient.post('/devices', {
      name,
      owner_email: ownerEmail,
      os_name: osName || null,
      os_version: osVersion || null
    })
  },

  /** Stop a machine receiving further work. Permanent. */
  async revoke(deviceId) {
    return httpClient.post(`/devices/${deviceId}/revoke`, {})
  }
}

export default deviceService

export { deviceService }
