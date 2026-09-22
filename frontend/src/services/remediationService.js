import { httpClient } from './httpClient'

/**
 * These two wait on something slower than an ordinary API call: a model, or an
 * agent on another machine. The server allows a device sixty seconds to
 * answer, so the browser has to allow more than that - a shorter limit reports
 * a failure for work that is still running.
 */
const SLOW_CALL_TIMEOUT_MS = 120000

/**
 * Risk-adaptive remediation.
 *
 * Every call here is authenticated: the approver is taken from the JWT on the
 * server, never sent from the browser. A token returned by approve() authorises
 * exactly one execution of exactly the action that was approved.
 */
const remediationService = {
  /** Requests waiting on a human decision. */
  async getPending(mineOnly = false) {
    return httpClient.get(`/remediation/pending?mine_only=${mineOnly}`)
  },

  /** Past remediations with their verification outcomes. */
  async getHistory(limit = 50, mineOnly = true) {
    return httpClient.get(`/remediation/history?limit=${limit}&mine_only=${mineOnly}`)
  },

  /** Full trail for one request: risk, evidence, checks, outcome. */
  async getById(remediationId) {
    return httpClient.get(`/remediation/${remediationId}`)
  },

  /**
   * Approve a request. Returns the request plus a single-use approval_token,
   * which must be passed straight to execute().
   */
  async approve(remediationId) {
    return httpClient.post('/remediation/approve', { remediation_id: remediationId })
  },

  /** Reject a request. It can never execute afterwards. */
  async reject(remediationId, reason) {
    return httpClient.post('/remediation/reject', {
      remediation_id: remediationId,
      reason
    })
  },

  /**
   * Run an approved or auto-eligible request, then verify the outcome.
   * `token` is required for anything that needed approval.
   */
  async execute(remediationId, token = null) {
    return httpClient.post(
      '/remediation/execute',
      { remediation_id: remediationId, token },
      { timeout: SLOW_CALL_TIMEOUT_MS }
    )
  },

  /** Approve and run in one step, for medium-risk actions the user confirms. */
  async approveAndExecute(remediationId) {
    const approved = await this.approve(remediationId)
    return this.execute(remediationId, approved.approval_token)
  },

  /**
   * What the action found, and what to do next, in plain words.
   *
   * One model request - a fifth of a chat turn in agent mode. Returns
   * { explanation: null } rather than failing when the model is unavailable,
   * because the measured figures are already on screen either way.
   */
  async explain(remediationId) {
    return httpClient.post(
      `/remediation/${remediationId}/explain`,
      {},
      { timeout: SLOW_CALL_TIMEOUT_MS }
    )
  },

  /** Counts for the evaluation chapter. */
  async getStats() {
    return httpClient.get('/remediation/stats/summary')
  },

  /** Actions that can be run through the verified path. */
  async getAvailableActions() {
    return httpClient.get('/remediation/actions')
  }
}

export default remediationService

export { remediationService }
