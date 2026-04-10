'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useState, useEffect, useRef } from 'react'

export default function Header() {
  const pathname   = usePathname() ?? '/'
  const router     = useRouter()
  const isArticles = pathname.startsWith('/articles')
  const isForum    = pathname.startsWith('/forum')
  const isExperts  = pathname.startsWith('/experts')
  const isHome     = pathname === '/'
  const [menuOpen, setMenuOpen] = useState(false)
  const [user, setUser] = useState<{ name?: string; nickname?: string; avatar_url?: string } | null>(null)
  const [profileOpen, setProfileOpen] = useState(false)
  const profileRef = useRef<HTMLDivElement>(null)
  const close = () => setMenuOpen(false)

  // Load user from localStorage on mount + listen for storage changes
  useEffect(() => {
    const loadUser = () => {
      try {
        const raw = localStorage.getItem('user')
        const token = localStorage.getItem('access_token')
        if (raw && token) {
          setUser(JSON.parse(raw))
        } else {
          setUser(null)
        }
      } catch { setUser(null) }
    }
    loadUser()
    window.addEventListener('storage', loadUser)
    // Custom event for same-tab login/logout
    window.addEventListener('auth-changed', loadUser)
    return () => {
      window.removeEventListener('storage', loadUser)
      window.removeEventListener('auth-changed', loadUser)
    }
  }, [pathname])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    setUser(null)
    window.dispatchEvent(new Event('auth-changed'))
    close()
    router.push('/')
  }

  // Close mobile menu automatically when window is resized to desktop width
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 820 && menuOpen) {
        setMenuOpen(false)
      }
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [menuOpen])

  // Close profile dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setProfileOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const displayName = user?.nickname || user?.name || 'משתמש'

  const authSection = user ? (
    <>
      <span className="gh-user-greeting">שלום, {displayName}</span>
      <button onClick={handleLogout} className="gh-btn gh-btn-login" style={{ cursor: 'pointer' }}>יציאה</button>
    </>
  ) : (
    <Link href="/login" className="gh-btn gh-btn-login" onClick={close}>התחברות</Link>
  )

  const brandSection = (
    <div className="gh-brand-wrapper" ref={profileRef}>
      <button
        className="gh-brand gh-brand-btn"
        onClick={() => setProfileOpen(o => !o)}
        aria-label="תפריט פרופיל"
        aria-expanded={profileOpen}
      >
        {user?.avatar_url ? (
          <img src={user.avatar_url} alt="" className="gh-logo gh-logo-avatar" />
        ) : (
          <div className="gh-logo">MH</div>
        )}
        <div className="gh-brand-name">MedicalHub</div>
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" style={{ marginRight: '2px', transition: 'transform 0.2s', transform: profileOpen ? 'rotate(180deg)' : 'rotate(0deg)' }}>
          <polyline points="2,4 6,8 10,4" />
        </svg>
      </button>
      {profileOpen && (
        <div className="gh-profile-dropdown">
          {user ? (
            <>
              <div className="gh-profile-dropdown-header">
                <div className="gh-profile-dropdown-name">{displayName}</div>
                <div className="gh-profile-dropdown-email">{(user as any).email || ''}</div>
              </div>
              <div className="gh-profile-dropdown-divider" />
              <Link href="/profile" className="gh-profile-dropdown-item" onClick={() => setProfileOpen(false)}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><circle cx="8" cy="5" r="3"/><path d="M2 14c0-3 2.5-5 6-5s6 2 6 5"/></svg>
                פרופיל
              </Link>
              <button className="gh-profile-dropdown-item" onClick={() => { handleLogout(); setProfileOpen(false); }}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><path d="M6 2H3a1 1 0 00-1 1v10a1 1 0 001 1h3"/><path d="M10 11l3-3-3-3"/><path d="M13 8H6"/></svg>
                יציאה
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="gh-profile-dropdown-item" onClick={() => setProfileOpen(false)}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><path d="M10 2h3a1 1 0 011 1v10a1 1 0 01-1 1h-3"/><path d="M6 11l-3-3 3-3"/><path d="M3 8h7"/></svg>
                התחברות
              </Link>
            </>
          )}
        </div>
      )}
    </div>
  )

  const navLinks = (
    <>
      <Link href="/"         className={`gh-link${isHome     ? ' gh-link-active' : ''}`} onClick={close}>דף הבית</Link>
      <Link href="/articles" className={`gh-link${isArticles ? ' gh-link-active' : ''}`} onClick={close}>מאמרים</Link>
      <Link href="/forum"    className={`gh-link${isForum    ? ' gh-link-active' : ''}`} onClick={close}>פורום</Link>
      <Link href="/experts"  className={`gh-link${isExperts  ? ' gh-link-active' : ''}`} onClick={close}>מומחים</Link>
      <Link href="/about"    className="gh-link" onClick={close}>אודות</Link>
      {authSection}
      <Link href="/product"  className="gh-btn gh-btn-cta" onClick={close}>Doctor Scribe AI</Link>
    </>
  )

  return (
    /* sticky wrapper — grows with content, pushes page down.
       Loses sticky state when open to prevent taking up half the screen while scrolling */
    <div className={`gh-sticky-wrapper${menuOpen ? ' gh-sticky-wrapper--open' : ''}`}>
      <header className="gh-header">
        {/* Brand with profile dropdown */}
        {brandSection}

        {/* Desktop nav — hidden on mobile via CSS */}
        <nav className="gh-nav">
          {navLinks}
        </nav>

        {/* Hamburger — shown on mobile via CSS */}
        <button
          className="gh-hamburger"
          onClick={() => setMenuOpen(o => !o)}
          aria-label={menuOpen ? 'סגור תפריט' : 'פתח תפריט'}
          aria-expanded={menuOpen}
        >
          {menuOpen
            ? <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round"><line x1="3" y1="3" x2="17" y2="17"/><line x1="17" y1="3" x2="3" y2="17"/></svg>
            : <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round"><line x1="3" y1="6" x2="17" y2="6"/><line x1="3" y1="10" x2="17" y2="10"/><line x1="3" y1="14" x2="17" y2="14"/></svg>
          }
        </button>
      </header>

      {/* Mobile drawer — sibling to header INSIDE sticky wrapper.
          When visible the wrapper grows, naturally pushing page content down. */}
      {menuOpen && (
        <nav className="gh-mobile-drawer">
          {navLinks}
        </nav>
      )}
    </div>
  )
}
