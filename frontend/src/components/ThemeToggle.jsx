import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import '../styles/components/ThemeToggle.css'

function ThemeToggle() {
  const { theme, toggleTheme, isDark } = useTheme()

  return (
    <button 
      onClick={toggleTheme}
      className="theme-toggle"
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      <div className="theme-toggle-icon">
        {isDark ? <Sun size={20} /> : <Moon size={20} />}
      </div>
      <span className="theme-toggle-text">
        {isDark ? 'Light' : 'Dark'}
      </span>
    </button>
  )
}

export default ThemeToggle
