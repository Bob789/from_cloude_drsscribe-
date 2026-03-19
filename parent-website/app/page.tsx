'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'

const MENU_ITEMS = [
  { href: '/experiences',    label: 'חוויות אישיות',           icon: '💬' },
  { href: '/recommendations', label: 'בקשה להמלצות רופאים',    icon: '⭐' },
  { href: '/about',          label: 'אודות',                    icon: 'ℹ️' },
]

export default function MedicalHub() {
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false)
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const menuRef = useRef<HTMLDivElement>(null)

  // Close menu when clicking outside
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  // Particles
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let W = window.innerWidth
    let H = window.innerHeight
    let animationFrameId: number

    const resize = () => {
      W = canvas.width = window.innerWidth
      H = canvas.height = window.innerHeight
    }
    window.addEventListener('resize', resize)
    resize()

    const colors = ['rgba(96,165,250,', 'rgba(168,85,247,', 'rgba(20,184,166,', 'rgba(245,158,11,']
    const particles: any[] = []

    for (let i = 0; i < 55; i++) {
        particles.push({
            x: Math.random() * 1400,
            y: Math.random() * 900,
            r: Math.random() * 1.5 + 0.4,
            dx: (Math.random() - 0.5) * 0.3,
            dy: -Math.random() * 0.4 - 0.1,
            o: Math.random() * 0.5 + 0.15,
            c: colors[Math.floor(Math.random() * colors.length)]
        })
    }

    const draw = () => {
      ctx.clearRect(0, 0, W, H)
      particles.forEach(p => {
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = p.c + p.o + ')'
        ctx.fill()
        p.x += p.dx
        p.y += p.dy
        if (p.y < -10) { p.y = H + 10; p.x = Math.random() * W }
        if (p.x < -10) p.x = W + 10
        if (p.x > W + 10) p.x = -10
      })
      animationFrameId = requestAnimationFrame(draw)
    }
    draw()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animationFrameId)
    }
  }, [])

  // Magnetic Hover & Scroll Reveal
  useEffect(() => {
    // Magnetic Hover
    const cards = document.querySelectorAll('.article-card') as NodeListOf<HTMLElement>
    const handleMouseMove = (e: MouseEvent) => {
      const card = e.currentTarget as HTMLElement
      const r = card.getBoundingClientRect()
      const x = (e.clientX - r.left - r.width  / 2) / r.width  * 6
      const y = (e.clientY - r.top  - r.height / 2) / r.height * 4
      card.style.transform = `translateY(-6px) scale(1.012) rotateY(${x}deg) rotateX(${-y}deg)`
    }
    const handleMouseLeave = (e: MouseEvent) => {
      const card = e.currentTarget as HTMLElement
      card.style.transform = ''
      card.style.transition = 'transform .4s cubic-bezier(.34,1.56,.64,1), box-shadow .3s, border-color .3s'
    }
    const handleMouseEnter = (e: MouseEvent) => {
       const card = e.currentTarget as HTMLElement
       card.style.transition = 'transform .15s ease, box-shadow .3s, border-color .3s'
    }

    cards.forEach(card => {
      card.addEventListener('mousemove', handleMouseMove)
      card.addEventListener('mouseleave', handleMouseLeave)
      card.addEventListener('mouseenter', handleMouseEnter)
    })

    // Scroll Reveal
    const observer = new IntersectionObserver(entries => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
           (entry.target as HTMLElement).style.opacity = '1';
           (entry.target as HTMLElement).style.transform = 'translateY(0)';
           observer.unobserve(entry.target);
        }
      })
    }, { threshold: 0.1 })

    const elements = document.querySelectorAll('.article-card, .sidebar-card, .ds-widget, .editorial-promo')
    elements.forEach(el => {
       (el as HTMLElement).style.opacity = '0';
       (el as HTMLElement).style.transform = 'translateY(24px)';
       observer.observe(el)
    })

    return () => {
        cards.forEach(card => {
            card.removeEventListener('mousemove', handleMouseMove)
            card.removeEventListener('mouseleave', handleMouseLeave)
            card.removeEventListener('mouseenter', handleMouseEnter)
        })
        observer.disconnect()
    }
  }, [])

  return (
    <>
      {/* Background orbs */}
      <div className="bg-orbs" aria-hidden="true">
        <div className="orb orb1"></div>
        <div className="orb orb2"></div>
        <div className="orb orb3"></div>
      </div>

      {/* Floating particles */}
      <canvas ref={canvasRef} id="particleCanvas" className="particles" aria-hidden="true"></canvas>

      {/* TOP BAR */}
      <div className="top-bar">
        <strong>חדש:</strong> תמלול רפואי אוטומטי לקליניקות —{' '}
        <a href="https://drsscribe.com/product">Doctor Scribe AI ←</a>
      </div>

      {/* HEADER */}
      <header>
        <div 
          className="hamburger" 
          aria-label="תפריט"
          ref={menuRef}
          onClick={() => {
            if (typeof window !== 'undefined' && window.innerWidth <= 820) {
              setIsMobileNavOpen(!isMobileNavOpen)
            } else {
              setIsMenuOpen(!isMenuOpen)
            }
          }}
          style={{ position: 'relative' }}
        >
          <svg viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 7C4 6.44772 4.44772 6 5 6H23C23.5523 6 24 6.44772 24 7C24 7.55228 23.5523 8 23 8H5C4.44772 8 4 7.55228 4 7Z" fill="#E2E8F0"/>
            <path d="M4 14C4 13.4477 4.4477 13 5 13H23C23.5523 13 24 13.4477 24 14C24 14.5523 23.5523 15 23 15H5C4.4477 15 4 14.5523 4 14Z" fill="#E2E8F0"/>
            <path d="M4 21C4 20.4477 4.44772 20 5 20H23C23.5523 20 24 20.4477 24 21C24 21.5523 23.5523 22 23 22H5C4.44772 22 4 21.5523 4 21Z" fill="#E2E8F0"/>
          </svg>

          {/* Desktop Dropdown */}
          {isMenuOpen && (
            <div className="desktop-dropdown" style={{
              position: 'absolute',
              top: 'calc(100% + 12px)',
              right: -10,
              minWidth: 240,
              background: 'rgba(15,23,42,0.95)',
              border: '1px solid rgba(56,189,248,0.2)',
              borderRadius: 12,
              boxShadow: '0 20px 40px rgba(0,0,0,0.4)',
              backdropFilter: 'blur(12px)',
              zIndex: 300,
              overflow: 'hidden',
              textAlign: 'right',
              cursor: 'default'
            }} onClick={(e) => e.stopPropagation()}>
              <div style={{ padding: '12px 16px 8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                <p style={{ margin: 0, fontSize: 11, color: '#94a3b8', fontWeight: 600, letterSpacing: '0.05em' }}>
                  תפריט נוסף
                </p>
              </div>
              
              {MENU_ITEMS.map(item => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="dropdown-item"
                  style={{
                    display: 'flex', alignItems: 'center', gap: 12,
                    padding: '12px 16px',
                    color: '#f8fafc', textDecoration: 'none', fontSize: 14, fontWeight: 500,
                    borderBottom: '1px solid rgba(255,255,255,0.03)',
                    transition: 'background 0.2s',
                    direction: 'rtl'
                  }}
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span style={{ fontSize: 18 }}>{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </div>
          )}
        </div>
        <nav>
          <Link href="/" className="nav-home">דף הבית</Link>
          <Link href="/login" className="nav-login">התחברות Medical Hub</Link>
          <Link href="/articles">מאמרים</Link>
          <Link href="/forum">פורום</Link>
          <Link href="/experts">מומחים</Link>
          <Link href="/about">אודות</Link>
          <a href="https://drsscribe.com/product" className="header-cta">Doctor Scribe AI</a>
        </nav>
        <div className="logo">MedicalHub</div>
      </header>

      {/* MOBILE NAV DRAWER */}
      <nav className={`mobile-nav ${isMobileNavOpen ? 'open' : ''}`} id="mobileNav">
        <Link href="/">דף הבית</Link>
        <Link href="/login">התחברות Medical Hub</Link>
        <Link href="/articles">מאמרים</Link>
        <Link href="/forum">פורום</Link>
        <Link href="/experts">מומחים</Link>
        <Link href="/about">אודות</Link>
        <a href="https://drsscribe.com/product" className="mobile-cta">Doctor Scribe AI</a>
      </nav>

      <main>
        {/* HERO */}
        <section className="hero">
          <div className="hero-badge-wrap"><div className="hero-badge"><span className="pulse-dot"></span>מרכז הידע הרפואי המוביל בישראל</div></div>
          <h1 className="hero-title">כל הידע הרפואי<br /><span className="grad-text">במקום אחד</span></h1>
          <p className="hero-sub">מאמרים מקצועיים, פורום פעיל עם מענה רופאים ורשימת מומחים — ידע רפואי מקצועי</p>
          <div className="search-wrap">
            <input type="text" placeholder="חיפוש מאמרים, דיונים או מומחים..." />
            <button className="search-btn" aria-label="חיפוש">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </button>
          </div>
          <div className="hero-stats">
            <div className="hero-stat">
              <span className="num">150+</span>
              <span className="label">מאמרים מקצועיים</span>
            </div>
            <div className="hero-stat">
              <span className="num">2,500+</span>
              <span className="label">דיונים בפורום</span>
            </div>
            <div className="hero-stat">
              <span className="num">85</span>
              <span className="label">רופאים ומומחים</span>
            </div>
          </div>
        </section>

        {/* GRID */}
        <div className="page-grid">
          {/* MAIN */}
          <div>
            <div className="sec-head">
              <h2>מאמרים אחרונים</h2>
              <div className="line"></div>
              <span className="tag">מגזין בריאות</span>
            </div>

            {/* Articles */}
            <div className="article-card">
              <div className="article-img">🦴</div>
              <div className="article-body">
                <h3>כאבי גב כרוניים – מדריך מקיף לאבחון וטיפול</h3>
                <p>סקירה עדכנית של גורמי כאב גב, שיטות אבחון, טיפול פיזיותרפי ותרופתי, ומתי מתייעצים לגבי ניתוח.</p>
                <div className="article-meta">
                  <span className="cat-badge badge-blue">אורתופדיה</span>
                  <span>• לפני 2 ימים</span>
                  <span>• 4 דקות קריאה</span>
                </div>
              </div>
            </div>

            <div className="article-card">
              <div className="article-img">❤️</div>
              <div className="article-body">
                <h3>יתר לחץ דם – טיפול ומענה בגיל 40+</h3>
                <p>מה כדאי לדעת על תזונה, פעילות גופנית ותרופות בניהול לחץ דם גבוה. מדריך מונע למבוגרים.</p>
                <div className="article-meta">
                  <span className="cat-badge badge-rose">קרדיולוגיה</span>
                  <span>• לפני 3 ימים</span>
                  <span>• 5 דקות קריאה</span>
                </div>
              </div>
            </div>

            <div className="article-card">
              <div className="article-img">🩸</div>
              <div className="article-body">
                <h3>סוכרת סוג 2 – מניעה, שליטה וחיים עם המחלה</h3>
                <p>הסבר מעמיק על ניהול סוכרת, תרופות עדכניות ואסטרטגיות תזונה מבוססות מחקר.</p>
                <div className="article-meta">
                  <span className="cat-badge badge-amber">אנדוקרינולוגיה</span>
                  <span>• לפני שבוע</span>
                  <span>• 8 דקות קריאה</span>
                </div>
              </div>
            </div>

            <div className="article-card">
              <div className="article-img">😴</div>
              <div className="article-body">
                <h3>שינה בריאה – המדריך המלא לשיפור איכות השינה</h3>
                <p>היגיינת שינה, הפרעות נפוצות, טיפול CBT-I ומתי לפנות למעבדת שינה לאבחון מתקדם.</p>
                <div className="article-meta">
                  <span className="cat-badge badge-purp">רפואת שינה</span>
                  <span>• לפני שבוע</span>
                  <span>• 3 דקות קריאה</span>
                </div>
              </div>
            </div>

            <div className="article-card">
              <div className="article-img">🥗</div>
              <div className="article-body">
                <h3>תזונה ים תיכונית – עדויות מדעיות ופרקטיקה</h3>
                <p>מה המחקר אומר על הדיאטה הים-תיכונית, מחלות לב, סוכרת ודמנציה. תפריט שבועי מומלץ.</p>
                <div className="article-meta">
                  <span className="cat-badge badge-teal">תזונה</span>
                  <span>• לפני 10 ימים</span>
                  <span>• 7 דקות קריאה</span>
                </div>
              </div>
            </div>

            {/* Editorial Promo */}
            <div className="editorial-promo">
              <div className="icon">✍️</div>
              <div>
                <div className="promo-label">מדורור רופא</div>
                <h4>רוצים לכתוב עבור Medical Hub?</h4>
                <p>אם אתם רופאים, אחיות או מטפלים מוסמכים, הצטרפו לצוות הכותבים שלנו ושתפו ידע מקצועי.</p>
                <a href="/join-writers">להגשת מועמדות לכתיבה →</a>
              </div>
            </div>

          </div>

          {/* SIDEBAR */}
          <aside>
             {/* DR SCRIBE WIDGET */}
            <div className="ds-widget">
              <div className="ds-tag">SPONSORED</div>
              <h3>Doctor Scribe AI</h3>
              <p>המערכת החכמה לתמלול וסיכום ביקורים רפואיים בעברית. חוסכים 50% מזמן התיעוד.</p>
              <ul className="ds-features">
                 <li><span className="feat-dot"></span> תמלול מדויק בעברית רפואית</li>
                 <li><span className="feat-dot"></span> סיכום אוטומטי לתיק הרפואי</li>
                 <li><span className="feat-dot"></span> הפקת הפניות ומכתבי שחרור</li>
                 <li><span className="feat-dot"></span> אבטחת מידע בתקן מחמיר</li>
              </ul>
              <a href="https://drsscribe.com/product" className="ds-cta">נסו חינם ל-14 יום</a>
              <div className="ds-cta-sub">אין צורך בכרטיס אשראי</div>
            </div>

            {/* EXPERTS WIDGET */}
            <div className="sidebar-card card-experts">
               <div className="card-heading-experts">
                  <div className="ch-icon">🩺</div>
                  <div className="ch-label">מומחים מובילים</div>
               </div>
               
               <div className="expert-card">
                 <div className="expert-avatar">D</div>
                 <div>
                   <div className="expert-name">ד"ר דניאל כהן</div>
                   <div className="expert-spec">אורתופדיה • תל אביב</div>
                 </div>
               </div>
               <div className="expert-card">
                 <div className="expert-avatar">M</div>
                 <div>
                   <div className="expert-name">פרופ׳ מרים לוי</div>
                   <div className="expert-spec">נוירולוגיה • ירושלים</div>
                 </div>
               </div>
               <div className="expert-card">
                 <div className="expert-avatar">S</div>
                 <div>
                   <div className="expert-name">ד"ר שרה אברמוביץ</div>
                   <div className="expert-spec">קרדיולוגיה • חיפה</div>
                 </div>
               </div>
               <div className="expert-card">
                 <div className="expert-avatar">Y</div>
                 <div>
                   <div className="expert-name">ד"ר יוסי מזרחי</div>
                   <div className="expert-spec">אנדוקרינולוגיה • ת"א</div>
                 </div>
               </div>
               
               <div style={{marginTop: '20px', textAlign: 'center'}}>
                 <Link href="/experts" className="btn-ghost" style={{fontSize: '0.8rem', padding: '8px 20px'}}>לכל המומחים</Link>
               </div>
            </div>

            {/* POPULAR - FORUM */}
            <div className="sidebar-card card-popular">
               <div className="card-heading-popular">
                  <div className="ch-icon">💬</div>
                  <div className="ch-label">חם בפורום</div>
               </div>
               
               <a className="forum-row">
                 <div className="forum-title">כאב גב תחתון אחרי אימון</div>
                 <div className="forum-meta">12 תגובות <span className="forum-badge">רופא השיב</span></div>
               </a>
               <a className="forum-row">
                 <div className="forum-title">האם צריך MRI לכאבי ראש?</div>
                 <div className="forum-meta">7 תגובות</div>
               </a>
               <a className="forum-row">
                 <div className="forum-title">תופעות לוואי של מטפורמין</div>
                 <div className="forum-meta">15 תגובות <span className="forum-badge">רופא השיב</span></div>
               </a>
               <a className="forum-row">
                 <div className="forum-title">נדודי שינה כרוניים - עזרה</div>
                 <div className="forum-meta">31 תגובות</div>
               </a>
               <a className="forum-row">
                 <div className="forum-title">שיטות להפחתת לחץ דם</div>
                 <div className="forum-meta">18 תגובות <span className="forum-badge">רופא השיב</span></div>
               </a>
               
               <div style={{marginTop: '20px', textAlign: 'center'}}>
                 <Link href="/forum" className="btn-ghost" style={{fontSize: '0.8rem', padding: '8px 20px'}}>לפורום המלא</Link>
               </div>
            </div>

          </aside>
        </div>

        {/* BOTTOM CTA */}
        <section className="bottom-cta">
          <div className="eyebrow">Doctor Scribe AI</div>
          <h2><span className="grad-text">אתם מטפלים — ה-AI כותב</span></h2>
          <p>תמלול וסיכום אוטומטי של ביקורים רפואיים בעברית. לקליניקות פרטיות ורופאים עצמאיים.</p>
          <div className="cta-row">
            <a href="https://drsscribe.com/product" className="btn-primary">התחילו ניסיון חינם</a>
            <a href="https://drsscribe.com/demo" className="btn-ghost">דמו אונליין</a>
          </div>
        </section>
      </main>

      <footer>
        <div className="footer-logo">MedicalHub</div>
        <div className="footer-links">
          <Link href="/articles">מאמרים</Link>
          <Link href="/forum">פורום</Link>
          <Link href="/experts">מומחים</Link>
          <a href="https://drsscribe.com/product">Doctor Scribe AI</a>
          <Link href="/privacy-policy">פרטיות</Link>
          <Link href="/terms">תנאי שימוש</Link>
        </div>
        <div className="footer-copy">© 2026 Medical Hub</div>
      </footer>
    </>
  )
}
