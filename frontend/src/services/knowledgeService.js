import { httpClient } from './httpClient'

/**
 * Knowledge learned from verified fixes.
 *
 * A fix that was verified, and that no existing article covered, becomes a
 * draft. A draft is never searched or cited until a reviewer approves it, so
 * approving here changes what the assistant tells every future user. The
 * server enforces who may approve; the page only hides buttons that would fail.
 */
const knowledgeService = {
  /** Drafts still waiting for a reviewer. */
  async pending() {
    return httpClient.get('/knowledge/drafts?pending_only=true')
  },

  /** Every draft, reviewed or not, newest first. */
  async history() {
    return httpClient.get('/knowledge/drafts?pending_only=false')
  },

  /** Approved articles, in the shape the retriever searches. */
  async learned() {
    return httpClient.get('/knowledge/learned')
  },

  async stats() {
    return httpClient.get('/knowledge/stats')
  },

  /** Approve, optionally with the reviewer's corrections to the text. */
  async approve(draftId, { note, edits } = {}) {
    return httpClient.post('/knowledge/drafts/approve', {
      draft_id: draftId,
      note: note || null,
      edits: edits || null
    })
  },

  /** Decline. The draft stays on record and never becomes searchable. */
  async reject(draftId, reason) {
    return httpClient.post('/knowledge/drafts/reject', { draft_id: draftId, reason })
  }
}

export default knowledgeService
