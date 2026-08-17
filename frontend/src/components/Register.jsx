import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot, Mail, Lock, User, Shield, CheckCircle, AlertTriangle, UserPlus } from 'lucide-react'
import { authService } from '../services/authService'
import '../styles/components/Auth.css'

function Register() {
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    password: '',
    confirmPassword: '',
    tier: 'staff'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      setLoading(false)
      return
    }

    try {
      await authService.register({
        email: formData.email,
        name: formData.name,
        password: formData.password,
        tier: formData.tier
      })

      setSuccess(true)
      setTimeout(() => {
        navigate('/login')
      }, 2000)
      
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="success-message">
            <span className="success-icon">
              <CheckCircle size={64} strokeWidth={2} />
            </span>
            <h2>Registration Successful!</h2>
            <p>Your account has been created and is pending activation.</p>
            <p>An administrator will review and activate your account shortly.</p>
            <p style={{ marginTop: '1rem', fontSize: '0.9rem' }}>Redirecting to login...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-container">
      <div className="tech-background">
        <div className="grid-lines"></div>
        <div className="floating-particles">
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
        </div>
        <div className="scan-line"></div>
      </div>

      <div className="auth-content-wrapper">
        {/* Left Side - Branding */}
        <div className="auth-branding">
          <div className="branding-content">
            <div className="brand-icon">
              <Bot size={64} strokeWidth={2} />
            </div>
            <h1 className="brand-title">IT Support Systems</h1>
            <p className="brand-subtitle">AI-Powered IT Support Assistant</p>
            <div className="brand-features">
              <div className="feature-item">
                <CheckCircle size={20} />
                <span>Instant Support</span>
              </div>
              <div className="feature-item">
                <CheckCircle size={20} />
                <span>Smart Automation</span>
              </div>
              <div className="feature-item">
                <CheckCircle size={20} />
                <span>24/7 Availability</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Registration Form */}
        <div className="auth-card register-card">
          <div className="auth-card-header">
            <h2>Create Your Account</h2>
            <p>Join us to get started with AI-powered IT support</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form register-form">
            {error && (
              <div className="error-alert">
                <AlertTriangle size={20} />
                <span>{error}</span>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="name">
                <User size={18} />
                <span>Full Name</span>
              </label>
              <input
                id="name"
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Enter your full name"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">
                <Mail size={18} />
                <span>Email Address</span>
              </label>
              <input
                id="email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="you@company.com"
                required
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="tier">
                <Shield size={18} />
                <span>User Role</span>
              </label>
              <select
                id="tier"
                name="tier"
                value={formData.tier}
                onChange={handleChange}
                className="tier-select"
              >
                <option value="staff">Staff Member</option>
                <option value="manager">Manager</option>
                <option value="contractor">Contractor</option>
              </select>
              <small className="field-hint">Choose your role in the organization</small>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="password">
                  <Lock size={18} />
                  <span>Password</span>
                </label>
                <input
                  id="password"
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Create a password"
                  required
                  autoComplete="new-password"
                  minLength={6}
                />
                <small className="field-hint">At least 6 characters</small>
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">
                  <Lock size={18} />
                  <span>Confirm Password</span>
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Re-enter password"
                  required
                  autoComplete="new-password"
                />
              </div>
            </div>

            <button type="submit" className="auth-btn" disabled={loading}>
              {loading ? (
                <>
                  <div className="spinner"></div>
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <UserPlus size={20} />
                  <span>Create Account</span>
                </>
              )}
            </button>

            <div className="auth-switch">
              Already have an account? 
              <button type="button" onClick={() => navigate('/login')} className="link-btn">
                Sign in here
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Register
