'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useEffect } from 'react'

export default function Header() {
  const pathname   = usePathname() ?? '/'
  const isArticles = pathname.startsWith('/articles')
  const isForum    = pathname.startsWith('/forum')
  const isExperts  = pathname.startsWith('/experts')
  const isHome     = pathname === '/'
  const [menuOpen, setMenuOpen] = useState(false)
  const close = () => setMenuOpen(false)

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

  const navLinks = (
    <>
      <Link href="/"         className={`gh-link${isHome     ? ' gh-link-active' : ''}`} onClick={close}>דף הבית</Link>
      <Link href="/articles" className={`gh-link${isArticles ? ' gh-link-active' : ''}`} onClick={close}>מאמרים</Link>
      <Link href="/forum"    className={`gh-link${isForum    ? ' gh-link-active' : ''}`} onClick={close}>פורום</Link>
      <Link href="/experts"  className={`gh-link${isExperts  ? ' gh-link-active' : ''}`} onClick={close}>מומחים</Link>
      <Link href="/about"    className="gh-link" onClick={close}>אודות</Link>
      <Link href="/login"    className="gh-btn gh-btn-login" onClick={close}>התחברות</Link>
      <Link href="/product"  className="gh-btn gh-btn-cta" onClick={close}>Doctor Scribe AI</Link>
    </>
  )

  return (
    /* sticky wrapper — grows with content, pushes page down.
       Loses sticky state when open to prevent taking up half the screen while scrolling */
    <div className={`gh-sticky-wrapper${menuOpen ? ' gh-sticky-wrapper--open' : ''}`}>
      <header className="gh-header">
        {/* Brand */}
        <Link href="/" className="gh-brand">
          <div className="gh-logo">MH</div>
          <div className="gh-brand-name">MedicalHub</div>
        </Link>

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
