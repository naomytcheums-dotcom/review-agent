import { NavLink } from 'react-router-dom'
import './Layout.css'

function Layout({ children }) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand mono">
            <span className="brand-caret">&gt;_</span> review-agent
          </div>
          <nav className="topbar-nav">
            <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : '')}>
              Reviews
            </NavLink>
            <NavLink to="/settings" className={({ isActive }) => (isActive ? 'active' : '')}>
              Settings
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="app-main">{children}</main>
    </div>
  )
}

export default Layout
