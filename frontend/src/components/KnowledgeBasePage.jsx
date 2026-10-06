import { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { BookOpen, Check, X, RefreshCw, Pencil, ShieldCheck } from 'lucide-react'
import knowledgeService from '../services/knowledgeService'
import '../styles/components/KnowledgeBasePage.css'

/**
 * Knowledge the system learned from verified fixes, and the review that lets it in.
 *
 * A fix that was verified, and that no existing article covered, becomes a
 * draft. Until a reviewer approves it, the draft is never searched or cited -
 * otherwise the assistant would ground its answers on its own unreviewed
 * guesses. Approval is restricted to the same roles the server checks.
 */

const REVIEWER_ROLES = ['support_l2', 'support_l3', 'it_admin', 'system_admin']

const TABS = [
  { id: 'pending', label: 'Waiting for review' },
  { id: 'reviewed', label: 'Reviewed' },
  { id: 'learned', label: 'Learned articles' }
]

function formatDate(iso) {
  return iso ? new Date(iso).toLocaleString() : ''
}

function Steps({ steps }) {
  if (!steps?.length) return null
  return (
    <ol className="kb-steps">
      {steps.map((step, i) => <li key={i}>{step}</li>)}
    </ol>
  )
}

Steps.propTypes = { steps: PropTypes.arrayOf(PropTypes.string) }

function DraftCard({ draft, canReview, onDone }) {
  const [editing, setEditing] = useState(false)
  const [edits, setEdits] = useState({
    title: draft.title || '',
    issue_pattern: draft.issue_pattern || '',
    summary: draft.summary || '',
    steps: (draft.resolution_steps || []).join('\n')
  })
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const approve = async () => {
    setBusy(true)
    setError(null)
    try {
      // Send corrections only when the reviewer opened the editor; otherwise
      // the machine-written text is approved exactly as shown.
      const payload = editing
        ? {
            title: edits.title.trim(),
            issue_pattern: edits.issue_pattern.trim(),
            summary: edits.summary.trim(),
            resolution_steps: edits.steps.split('\n').map((s) => s.trim()).filter(Boolean)
          }
        : null
      await knowledgeService.approve(draft.id, { note, edits: payload })
      onDone()
    } catch (err) {
      setError(err?.message || 'Could not approve')
    } finally {
      setBusy(false)
    }
  }

  const reject = async () => {
    const reason = window.prompt('Why is this draft being rejected?')
    if (!reason || !reason.trim()) return
    setBusy(true)
    setError(null)
    try {
      await knowledgeService.reject(draft.id, reason.trim())
      onDone()
    } catch (err) {
      setError(err?.message || 'Could not reject')
    } finally {
      setBusy(false)
    }
  }

  const field = (key) => ({
    value: edits[key],
    onChange: (e) => setEdits({ ...edits, [key]: e.target.value })
  })

  return (
    <article className="kb-card">
      <header className="kb-card-head">
        <h3>{draft.title}</h3>
        <span className="kb-badge">{draft.category}</span>
      </header>

      <p className="kb-meta">
        {draft.verification_status === 'verified_success' && (
          <span className="kb-verified"><ShieldCheck size={14} /> From a verified fix</span>
        )}
        {draft.remediation_id && <span>Remediation #{draft.remediation_id}</span>}
        {draft.ticket_id && <span>Ticket #{draft.ticket_id}</span>}
        <span>{draft.machine_generated ? 'Written by the system' : `Written by ${draft.proposed_by}`}</span>
        <span>{formatDate(draft.created_at)}</span>
      </p>

      {draft.source_problem && (
        <p className="kb-source"><strong>User reported:</strong> {draft.source_problem}</p>
      )}

      {editing ? (
        <div className="kb-edit">
          <label>Title<input {...field('title')} /></label>
          <label>When this applies<textarea rows={2} {...field('issue_pattern')} /></label>
          <label>Summary<textarea rows={2} {...field('summary')} /></label>
          <label>Steps, one per line<textarea rows={5} {...field('steps')} /></label>
        </div>
      ) : (
        <>
          {draft.issue_pattern && <p><strong>When this applies:</strong> {draft.issue_pattern}</p>}
          {draft.summary && <p>{draft.summary}</p>}
          <Steps steps={draft.resolution_steps} />
        </>
      )}

      {error && <p className="kb-error">{error}</p>}

      {canReview ? (
        <div className="kb-review">
          <input
            className="kb-note"
            placeholder="Note for the record (optional)"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
          <div className="kb-buttons">
            <button type="button" className="kb-btn" disabled={busy} onClick={() => setEditing(!editing)}>
              <Pencil size={14} /> {editing ? 'Stop editing' : 'Edit'}
            </button>
            <button type="button" className="kb-btn approve" disabled={busy} onClick={approve}>
              <Check size={14} /> Approve
            </button>
            <button type="button" className="kb-btn reject" disabled={busy} onClick={reject}>
              <X size={14} /> Reject
            </button>
          </div>
        </div>
      ) : (
        <p className="kb-hint">Only Support L2, L3 or an administrator can approve knowledge.</p>
      )}
    </article>
  )
}

DraftCard.propTypes = {
  draft: PropTypes.object.isRequired,
  canReview: PropTypes.bool,
  onDone: PropTypes.func.isRequired
}

function ReviewedRow({ draft }) {
  return (
    <article className="kb-card compact">
      <header className="kb-card-head">
        <h3>{draft.title}</h3>
        <span className={`kb-status ${draft.status}`}>{draft.status}</span>
      </header>
      <p className="kb-meta">
        {draft.article_id && <span>{draft.article_id}</span>}
        {draft.reviewed_by && <span>Reviewed by {draft.reviewed_by}</span>}
        <span>{formatDate(draft.reviewed_at || draft.created_at)}</span>
      </p>
      {draft.review_note && <p className="kb-source">{draft.review_note}</p>}
    </article>
  )
}

ReviewedRow.propTypes = { draft: PropTypes.object.isRequired }

function LearnedArticle({ article }) {
  return (
    <article className="kb-card">
      <header className="kb-card-head">
        <h3>{article.title}</h3>
        <span className="kb-badge">{article.id}</span>
      </header>
      {article.issue_pattern && <p><strong>When this applies:</strong> {article.issue_pattern}</p>}
      {article.summary && <p>{article.summary}</p>}
      <Steps steps={article.resolution_steps} />
    </article>
  )
}

LearnedArticle.propTypes = { article: PropTypes.object.isRequired }

export default function KnowledgeBasePage({ user }) {
  const [tab, setTab] = useState('pending')
  const [items, setItems] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const canReview = REVIEWER_ROLES.includes(user?.role)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [data, summary] = await Promise.all([
        tab === 'pending'
          ? knowledgeService.pending()
          : tab === 'reviewed'
            ? knowledgeService.history()
            : knowledgeService.learned(),
        knowledgeService.stats()
      ])
      if (tab === 'learned') {
        setItems(data.articles || [])
      } else if (tab === 'reviewed') {
        setItems((data.drafts || []).filter((d) => d.status !== 'pending'))
      } else {
        setItems(data.drafts || [])
      }
      setStats(summary)
    } catch (err) {
      setError(err?.message || 'Could not load knowledge')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab])

  const empty = {
    pending: 'Nothing is waiting for review. A draft appears here when a fix is verified and no article covered it.',
    reviewed: 'No drafts have been reviewed yet.',
    learned: 'No learned articles yet. Approved drafts appear here and are searched by the assistant.'
  }[tab]

  return (
    <div className="kb-page">
      <header className="kb-header">
        <div>
          <h1><BookOpen size={22} /> Knowledge Base</h1>
          <p className="kb-subtitle">
            Articles the system learned from verified fixes. A draft is never
            searched or cited until a reviewer approves it.
          </p>
        </div>
        <button type="button" className="kb-btn" onClick={load} disabled={loading}>
          <RefreshCw size={14} /> Refresh
        </button>
      </header>

      {stats && (
        <div className="kb-stats">
          <div><strong>{stats.pending}</strong><span>waiting</span></div>
          <div><strong>{stats.approved}</strong><span>approved</span></div>
          <div><strong>{stats.rejected}</strong><span>rejected</span></div>
        </div>
      )}

      <nav className="kb-tabs" role="tablist">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={tab === t.id}
            className={tab === t.id ? 'active' : ''}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {error && <p className="kb-error">{error}</p>}

      {loading ? (
        <p className="kb-hint">Loading…</p>
      ) : items.length === 0 ? (
        <p className="kb-empty">{empty}</p>
      ) : (
        <div className="kb-list">
          {tab === 'pending' && items.map((d) => (
            <DraftCard key={d.id} draft={d} canReview={canReview} onDone={load} />
          ))}
          {tab === 'reviewed' && items.map((d) => <ReviewedRow key={d.id} draft={d} />)}
          {tab === 'learned' && items.map((a) => <LearnedArticle key={a.id} article={a} />)}
        </div>
      )}
    </div>
  )
}

KnowledgeBasePage.propTypes = {
  user: PropTypes.shape({ role: PropTypes.string })
}
