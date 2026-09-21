import { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import {
  Monitor,
  Plus,
  RefreshCw,
  ShieldOff,
  AlertTriangle,
  Copy,
  Check,
  Wifi,
  WifiOff
} from 'lucide-react'
import deviceService from '../services/deviceService'
import '../styles/components/Devices.css'

/**
 * The machines running the AutoOps agent: who owns each one, and whether it is
 * still reporting in.
 *
 * Registering a device grants that machine the right to run approved
 * remediation actions on itself, so this page is for administrators and every
 * change here is audited on the server.
 */

/** A machine seen within this many minutes is treated as online. */
const ONLINE_WINDOW_MINUTES = 5

function lastSeenLabel(iso) {
  if (!iso) return { text: 'Never', online: false }

  const seen = new Date(iso)
  const minutes = Math.floor((Date.now() - seen.getTime()) / 60000)

  if (minutes < 1) return { text: 'Just now', online: true }
  if (minutes < ONLINE_WINDOW_MINUTES) return { text: `${minutes} min ago`, online: true }
  if (minutes < 60) return { text: `${minutes} min ago`, online: false }

  const hours = Math.floor(minutes / 60)
  if (hours < 24) return { text: `${hours} h ago`, online: false }
  return { text: `${Math.floor(hours / 24)} d ago`, online: false }
}

export default function Devices({ user }) {
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showRevoked, setShowRevoked] = useState(false)

  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', ownerEmail: '', osName: 'Windows', osVersion: '' })
  const [saving, setSaving] = useState(false)

  // Shown once, after registering. Never fetched again - the server keeps only
  // a hash, so if the administrator loses it the device must be re-registered.
  const [newSecret, setNewSecret] = useState(null)
  const [copied, setCopied] = useState(false)

  const isAdmin = user?.role === 'system_admin' || user?.role === 'it_admin'

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      setDevices(await deviceService.listAll(showRevoked))
    } catch (err) {
      setError(err?.message || 'Could not load devices')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showRevoked])

  const submit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const result = await deviceService.register(form)
      setNewSecret({ device: result.device, secret: result.secret })
      setForm({ name: '', ownerEmail: '', osName: 'Windows', osVersion: '' })
      setShowForm(false)
      await load()
    } catch (err) {
      setError(err?.message || 'Could not register the device')
    } finally {
      setSaving(false)
    }
  }

  const revoke = async (device) => {
    const ok = window.confirm(
      `Revoke ${device.name}?\n\nThis cannot be undone. The agent on that machine ` +
      `will stop receiving work immediately, and the machine must be registered ` +
      `again with a new secret to come back.`
    )
    if (!ok) return

    try {
      await deviceService.revoke(device.device_id)
      await load()
    } catch (err) {
      setError(err?.message || 'Could not revoke the device')
    }
  }

  const copySecret = async () => {
    try {
      await navigator.clipboard.writeText(newSecret.secret)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard can be blocked; the secret is on screen to copy by hand.
    }
  }

  if (!isAdmin) {
    return (
      <div className="devices-page">
        <div className="devices-empty">
          <ShieldOff size={32} />
          <p>Only administrators can manage endpoint devices.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="devices-page">
      <header className="devices-header">
        <div>
          <h1><Monitor size={22} /> Endpoint Devices</h1>
          <p className="devices-subtitle">
            Machines running the AutoOps agent. A remediation can target any of
            these, and the action runs there instead of on the server.
          </p>
        </div>
        <div className="devices-actions">
          <button className="devices-btn" onClick={load} disabled={loading}>
            <RefreshCw size={15} className={loading ? 'spin' : ''} /> Refresh
          </button>
          <button className="devices-btn primary" onClick={() => setShowForm(!showForm)}>
            <Plus size={15} /> Register device
          </button>
        </div>
      </header>

      {error && (
        <div className="devices-error"><AlertTriangle size={15} /> {error}</div>
      )}

      {newSecret && (
        <div className="devices-secret">
          <h3>Registered {newSecret.device.name}</h3>
          <p>
            This secret is shown <strong>once</strong>. Put it in the agent&apos;s
            configuration now — the server keeps only a hash and cannot show it
            again.
          </p>
          <div className="devices-secret-row">
            <code>AUTOOPS_DEVICE_ID={newSecret.device.device_id}</code>
          </div>
          <div className="devices-secret-row">
            <code>AUTOOPS_DEVICE_SECRET={newSecret.secret}</code>
            <button className="devices-btn" onClick={copySecret}>
              {copied ? <Check size={15} /> : <Copy size={15} />}
              {copied ? 'Copied' : 'Copy secret'}
            </button>
          </div>
          <button className="devices-btn" onClick={() => setNewSecret(null)}>
            I have saved it
          </button>
        </div>
      )}

      {showForm && (
        <form className="devices-form" onSubmit={submit}>
          <label>
            Machine name
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="WIN-LAB-01"
              required
            />
          </label>
          <label>
            Owner email
            <input
              type="email"
              value={form.ownerEmail}
              onChange={(e) => setForm({ ...form, ownerEmail: e.target.value })}
              placeholder="malith@acme.com"
              required
            />
          </label>
          <label>
            Operating system
            <input
              value={form.osName}
              onChange={(e) => setForm({ ...form, osName: e.target.value })}
              placeholder="Windows"
            />
          </label>
          <label>
            Version
            <input
              value={form.osVersion}
              onChange={(e) => setForm({ ...form, osVersion: e.target.value })}
              placeholder="11"
            />
          </label>
          <button className="devices-btn primary" type="submit" disabled={saving}>
            {saving ? 'Registering…' : 'Register'}
          </button>
        </form>
      )}

      <label className="devices-toggle">
        <input
          type="checkbox"
          checked={showRevoked}
          onChange={(e) => setShowRevoked(e.target.checked)}
        />
        Show revoked machines
      </label>

      {loading ? (
        <div className="devices-empty"><RefreshCw size={22} className="spin" /><p>Loading…</p></div>
      ) : devices.length === 0 ? (
        <div className="devices-empty">
          <Monitor size={32} />
          <p>No machines registered yet.</p>
          <p className="devices-hint">
            Register one here, then run the agent on it. See <code>agent/README.md</code>.
          </p>
        </div>
      ) : (
        <div className="devices-table-wrap">
          <table className="devices-table">
            <thead>
              <tr>
                <th>Machine</th>
                <th>Owner</th>
                <th>System</th>
                <th>Last seen</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {devices.map((d) => {
                const seen = lastSeenLabel(d.last_seen_at)
                return (
                  <tr key={d.device_id} className={d.is_active ? '' : 'revoked'}>
                    <td>
                      <div className="devices-name">{d.name}</div>
                      <code className="devices-id">{d.device_id}</code>
                    </td>
                    <td>{d.owner_email}</td>
                    <td>{[d.os_name, d.os_version].filter(Boolean).join(' ') || '—'}</td>
                    <td>
                      <span className={`devices-seen ${seen.online ? 'online' : ''}`}>
                        {seen.online ? <Wifi size={14} /> : <WifiOff size={14} />}
                        {seen.text}
                      </span>
                    </td>
                    <td>
                      <span className={`devices-status ${d.is_active ? 'active' : 'revoked'}`}>
                        {d.is_active ? 'Active' : 'Revoked'}
                      </span>
                    </td>
                    <td>
                      {d.is_active && (
                        <button className="devices-btn danger" onClick={() => revoke(d)}>
                          <ShieldOff size={14} /> Revoke
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

Devices.propTypes = {
  user: PropTypes.shape({ role: PropTypes.string })
}
