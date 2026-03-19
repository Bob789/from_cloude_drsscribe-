'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function CookieBanner() {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (!localStorage.getItem('cookie-consent')) {
      setVisible(true)
    }
  }, [])

  function accept() {
    localStorage.setItem('cookie-consent', '1')
    setVisible(false)
  }

  if (!visible) return null

  return (
    <div
      data-testid="cookie-banner"
      className="cookie-banner"
      style={{
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      zIndex: 500,
      background: 'rgba(11,16,32,0.97)',
      borderTop: '1px solid rgba(56,189,248,0.35)',
      backdropFilter: 'blur(12px)',
      padding: '18px 24px',
      display: 'flex',
      alignItems: 'center',
      gap: 20,
      flexWrap: 'wrap',
      justifyContent: 'space-between',
    }}>
      <p style={{ margin: 0, fontSize: 14, color: 'var(--muted)', lineHeight: 1.6, flex: 1, minWidth: 260 }}>
        חשוב לנו שתהיה לך חוויית גלישה מעולה. לכן, אנו נעזרים בעוגיות (Cookies) לצורך שיפור ביצועי האתר,
        התאמה אישית וסטטיסטיקה. בלחיצה על &#39;המשך&#39; או בהמשך הגלישה, הנך מסכים לשימוש זה בהתאם ל{' '}
        <Link href="/privacy" style={{ color: '#38bdf8', textDecoration: 'underline' }}>
          מדיניות הפרטיות
        </Link>
        .
      </p>
      <button
        onClick={accept}
        className="btn btn-primary"
        style={{ padding: '10px 28px', fontSize: 14, whiteSpace: 'nowrap', flexShrink: 0 }}
      >
        המשך
      </button>
    </div>
  )
}
