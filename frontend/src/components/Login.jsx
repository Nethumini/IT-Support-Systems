import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot, Mail, Lock, LogIn, AlertTriangle, CheckCircle } from 'lucide-react'
import { authService } from '../services/authService'
import '../styles/components/Auth.css'

function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const data = await authService.login({ email, password })
      
      // Store token and user info
      console.log('✓ Login successful:', data)
      localStorage.setItem('token', data.access_token)
      console.log('✓ Token stored in localStorage')
      localStorage.setItem('user', JSON.stringify(data.user))
      console.log('✓ User data stored')
      
      // Verify token was stored
      const storedToken = localStorage.getItem('token')
      console.log('✓ Verification - Token in storage:', storedToken ? 'YES' : 'NO')
      
      onLogin(data.user)
      navigate('/')
      
    } catch (err) {
      console.error('✗ Login error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
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

        {/* Right Side - Login Form */}
        <div className="auth-card">
          <div className="auth-card-header">
            <h2>Welcome Back</h2>
            <p>Sign in to your account to continue</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            {error && (
              <div className="error-alert">
                <AlertTriangle size={20} />
                <span>{error}</span>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="email">
                <Mail size={18} />
                <span>Email Address</span>
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                required
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">
                <Lock size={18} />
                <span>Password</span>
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                autoComplete="current-password"
              />
            </div>

            <button type="submit" className="auth-btn" disabled={loading}>
              {loading ? (
                <>
                  <div className="spinner"></div>
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <LogIn size={20} />
                  <span>Sign In</span>
                </>
              )}
            </button>

            <div className="auth-switch">
              Don't have an account? 
              <button type="button" onClick={() => navigate('/register')} className="link-btn">
                Create one here
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Login
