'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'

interface HeaderProps {
  page?: 'home' | 'about' | 'forum' | 'articles' | 'experts'
}

const MENU_ITEMS = [
  { href: '/experiences',    label: 'חוויות אישיות',           icon: '💬' },
  { href: '/recommendations', label: 'בקשה להמלצות רופאים',    icon: '⭐' },
  { href: '/about',          label: 'אודות',                    icon: 'ℹ️' },
]

export default function Header({ page = 'home' }: HeaderProps) {
  const isAbout    = page === 'about'
  const isForum    = page === 'forum'
  const isArticles = page === 'articles'
  const isExperts  = page === 'experts'
  const isHome     = page === 'home'

  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  // Close menu when clicking outside
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  return (
    <header className="site-header">
      <div className="header-container">
        <div className="header-top">
          <Link href="/" className="brand">
            <div className="logo-circle">MH</div>
            <div className="brand-text">
              <h1>Medical Hub</h1>
              <p>{isAbout ? 'חזרה לדף הבית' : 'מאמרים • פורום • מומחים • תמלול'}</p>
            </div>
          </Link>

          <div className="header-buttons">
            {isAbout ? (
              <>
                <a href="#demo" className="btn btn-secondary">צפה בדמו</a>
                <Link href="/product" className="btn btn-primary">כניסה למערכת</Link>
              </>
            ) : (
              <>
                <Link href="/login" className="btn btn-secondary">התחברות Medical Hub</Link>
                <Link href="/product" className="btn btn-primary">שירות תמלול לקליניקה</Link>
              </>
            )}

            {/* Hamburger button + dropdown */}
            <div ref={menuRef} style={{ position: 'relative' }}>
              <button
                onClick={() => setMenuOpen(v => !v)}
                aria-label="תפריט"
                className="hamburger-btn"
              >
                <svg width="22" height="22" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" clipRule="evenodd" d="M4.473 8.15263H23.5266C24.0643 8.15263 24.5 7.6777 24.5 7.09194C24.5 6.50618 24.0643 6.03174 23.5266 6.03174H4.473C3.93531 6.03174 3.5 6.50618 3.5 7.09194C3.5 7.6777 3.93531 8.15263 4.473 8.15263ZM19.0765 12.9327H4.25706C3.83886 12.9327 3.50028 13.4076 3.50028 13.9934C3.50028 14.5791 3.83886 15.0536 4.25706 15.0536H19.0765C19.4947 15.0536 19.8336 14.5791 19.8336 13.9934C19.8336 13.4076 19.4947 12.9327 19.0765 12.9327ZM4.47328 19.8337H23.5268C24.0645 19.8337 24.5003 20.3086 24.5003 20.8944C24.5003 21.4802 24.0645 21.9546 23.5268 21.9546H4.47328C3.9356 21.9546 3.50028 21.4802 3.50028 20.8944C3.50028 20.3086 3.9356 19.8337 4.47328 19.8337Z" fill="white"/>
                </svg>
              </button>

              {/* Dropdown */}
              {menuOpen && (
                <div style={{
                  position: 'absolute',
                  top: 'calc(100% + 8px)',
                  left: 0,
                  minWidth: 220,
                  background: 'rgba(11,18,38,0.97)',
                  border: '1px solid rgba(56,189,248,0.35)',
                  borderRadius: 16,
                  boxShadow: '0 16px 40px rgba(0,0,0,0.5)',
                  backdropFilter: 'blur(12px)',
                  overflow: 'hidden',
                  zIndex: 300,
                }}>
                  <div style={{ padding: '10px 14px 6px', borderBottom: '1px solid var(--border)' }}>
                    <p style={{ margin: 0, fontSize: 11, color: 'var(--muted)', fontWeight: 600, letterSpacing: '0.05em' }}>
                      תפריט נוסף
                    </p>
                  </div>

                  {MENU_ITEMS.map(item => (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMenuOpen(false)}
                      style={{
                        display: 'flex', alignItems: 'center', gap: 10,
                        padding: '12px 16px',
                        color: 'var(--text)', textDecoration: 'none', fontSize: 14, fontWeight: 600,
                        borderBottom: '1px solid rgba(255,255,255,0.04)',
                        transition: 'background 0.15s',
                      }}
                      onMouseEnter={e => (e.currentTarget.style.background = 'rgba(56,189,248,0.07)')}
                      onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                    >
                      <span style={{ fontSize: 18 }}>{item.icon}</span>
                      {item.label}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {!isAbout && (
          <nav className="nav">
            <Link href="/"         className={`nav-pill ${isHome     ? 'nav-pill-active' : 'nav-pill-default'}`}>דף הבית</Link>
            <Link href="/articles" className={`nav-pill ${isArticles ? 'nav-pill-active' : 'nav-pill-default'}`}>מאמרים</Link>
            <Link href="/forum"    className={`nav-pill ${isForum    ? 'nav-pill-active' : 'nav-pill-default'}`}>פורום</Link>
            <Link href="/experts"  className={`nav-pill ${isExperts  ? 'nav-pill-active' : 'nav-pill-default'}`}>מומחים</Link>
          </nav>
        )}
      </div>
    </header>
  )
}
