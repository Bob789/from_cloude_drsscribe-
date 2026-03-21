'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const MENU_ITEMS = [
  { href: '/experiences',     label: 'חוויות אישיות',        icon: '💬' },
  { href: '/recommendations', label: 'בקשה להמלצות רופאים', icon: '⭐' },
  { href: '/about',           label: 'אודות',                icon: 'ℹ️' },
]

export default function Header() {
  const pathname   = usePathname() ?? '/'
  const isArticles = pathname.startsWith('/articles')
  const isForum    = pathname.startsWith('/forum')
  const isExperts  = pathname.startsWith('/experts')
  const isHome     = pathname === '/'

  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

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
    <header className="gh-header">
      <div className="gh-inner">
        <Link href="/" className="gh-brand">
          <div className="gh-logo">MH</div>
          <div className="gh-brand-name">MedicalHub</div>
        </Link>

        <nav className="gh-nav">
          <Link href="/"         className={`gh-link${isHome     ? ' gh-link-active' : ''}`}>דף הבית</Link>
          <Link href="/articles" className={`gh-link${isArticles ? ' gh-link-active' : ''}`}>מאמרים</Link>
          <Link href="/forum"    className={`gh-link${isForum    ? ' gh-link-active' : ''}`}>פורום</Link>
          <Link href="/experts"  className={`gh-link${isExperts  ? ' gh-link-active' : ''}`}>מומחים</Link>
          <Link href="/about"    className="gh-link">אודות</Link>
          <Link href="/login"    className="gh-btn gh-btn-login">התחברות</Link>
          <Link href="/product"  className="gh-btn gh-btn-cta">Doctor Scribe AI</Link>
        </nav>

        <div ref={menuRef} style={{ position: 'relative' }}>
          <button
            onClick={() => setMenuOpen(v => !v)}
            aria-label="תפריט"
            className="gh-hamburger"
          >
            <svg width="22" height="22" viewBox="0 0 28 28" fill="none">
              <path fillRule="evenodd" clipRule="evenodd" d="M4.473 8.15263H23.5266C24.0643 8.15263 24.5 7.6777 24.5 7.09194C24.5 6.50618 24.0643 6.03174 23.5266 6.03174H4.473C3.93531 6.03174 3.5 6.50618 3.5 7.09194C3.5 7.6777 3.93531 8.15263 4.473 8.15263ZM19.0765 12.9327H4.25706C3.83886 12.9327 3.50028 13.4076 3.50028 13.9934C3.50028 14.5791 3.83886 15.0536 4.25706 15.0536H19.0765C19.4947 15.0536 19.8336 14.5791 19.8336 13.9934C19.8336 13.4076 19.4947 12.9327 19.0765 12.9327ZM4.47328 19.8337H23.5268C24.0645 19.8337 24.5003 20.3086 24.5003 20.8944C24.5003 21.4802 24.0645 21.9546 23.5268 21.9546H4.47328C3.9356 21.9546 3.50028 21.4802 3.50028 20.8944C3.50028 20.3086 3.9356 19.8337 4.47328 19.8337Z" fill="white"/>
            </svg>
          </button>

          {menuOpen && (
            <div style={{
              position: 'absolute', top: 'calc(100% + 8px)', left: 0,
              minWidth: 220, background: 'rgba(0,16,48,0.97)',
              border: '1px solid rgba(200,160,0,0.4)', borderRadius: 14,
              boxShadow: '0 16px 40px rgba(0,0,0,0.5)',
              backdropFilter: 'blur(12px)', overflow: 'hidden', zIndex: 300,
            }}>
              <div style={{ padding: '10px 14px 6px', borderBottom: '1px solid rgba(200,160,0,0.2)' }}>
                <p style={{ margin: 0, fontSize: 11, color: 'rgba(255,255,255,0.5)', fontWeight: 600, letterSpacing: '0.05em' }}>תפריט נוסף</p>
              </div>
              {MENU_ITEMS.map(item => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMenuOpen(false)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '12px 16px', color: 'rgba(255,255,255,0.85)',
                    textDecoration: 'none', fontSize: 14, fontWeight: 600,
                    borderBottom: '1px solid rgba(255,255,255,0.04)',
                    transition: 'background 0.15s',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = 'rgba(200,160,0,0.1)')}
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
    </header>
  )
}
