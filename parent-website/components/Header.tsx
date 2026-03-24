'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Header() {
  const pathname   = usePathname() ?? '/'
  const isArticles = pathname.startsWith('/articles')
  const isForum    = pathname.startsWith('/forum')
  const isExperts  = pathname.startsWith('/experts')
  const isHome     = pathname === '/'

  return (
    <header className="gh-header">
      {/* Brand floats absolutely, aligned to right edge of site-block */}
      <Link href="/" className="gh-brand">
        <div className="gh-logo">MH</div>
        <div className="gh-brand-name">MedicalHub</div>
      </Link>

      {/* Nav floats absolutely, aligned to left edge of site-block */}
      <nav className="gh-nav">
        <Link href="/"         className={`gh-link${isHome     ? ' gh-link-active' : ''}`}>דף הבית</Link>
        <Link href="/articles" className={`gh-link${isArticles ? ' gh-link-active' : ''}`}>מאמרים</Link>
        <Link href="/forum"    className={`gh-link${isForum    ? ' gh-link-active' : ''}`}>פורום</Link>
        <Link href="/experts"  className={`gh-link${isExperts  ? ' gh-link-active' : ''}`}>מומחים</Link>
        <Link href="/about"    className="gh-link">אודות</Link>
        <Link href="/login"    className="gh-btn gh-btn-login">התחברות</Link>
        <Link href="/product"  className="gh-btn gh-btn-cta">Doctor Scribe AI</Link>
      </nav>
    </header>
  )
}
