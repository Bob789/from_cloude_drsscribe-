'use client'

import { useState, FormEvent } from 'react'
import Link from 'next/link'

export default function RegisterPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    if (!name.trim()) { setError('יש להזין שם מלא'); return }
    if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('כתובת אימייל אינה תקינה'); return
    }
    if (!password.trim()) { setError('יש להזין סיסמה'); return }
    setError('הרשמה עדיין לא זמינה — מגיע בקרוב!')
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(180deg, #0b1020, #060a15)',
      padding: '20px',
    }}>
      <div style={{ width: '100%', maxWidth: 420 }}>
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <Link href="/"><img src="/logo.png" alt="Medical Hub" width={72} height={72}
            style={{ borderRadius: '50%', margin: '0 auto 16px', display: 'block', boxShadow: '0 0 24px rgba(56,189,248,0.4)' }} /></Link>
          <h1 style={{ fontSize: 26, fontWeight: 700, color: '#e0f2fe', marginBottom: 8 }}>הרשמה למערכת</h1>
          <p style={{ color: 'var(--muted)', fontSize: 14 }}>Medical Hub — צור חשבון חדש</p>
        </div>

        <div style={{ background: 'rgba(18,26,51,0.85)', border: '1px solid var(--border)', borderRadius: 24, padding: '36px 32px' }}>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

            {error && (
              <div role="alert" className="error-message" style={{
                padding: '12px 16px', borderRadius: 12,
                border: '1px solid rgba(239,68,68,0.4)', background: 'rgba(239,68,68,0.1)',
                color: '#fca5a5', fontSize: 14, textAlign: 'center',
              }}>{error}</div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <label style={{ fontSize: 14, fontWeight: 600, color: 'var(--text)' }}>שם מלא</label>
              <input type="text" name="name" value={name} onChange={e => setName(e.target.value)}
                placeholder="ד&quot;ר ישראל ישראלי" required className="search-input"
                style={{ padding: '14px 16px', fontSize: 15 }} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <label style={{ fontSize: 14, fontWeight: 600, color: 'var(--text)' }}>אימייל</label>
              <input type="email" name="email" value={email} onChange={e => setEmail(e.target.value)}
                placeholder="doctor@clinic.co.il" required className="search-input"
                style={{ padding: '14px 16px', fontSize: 15 }} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <label style={{ fontSize: 14, fontWeight: 600, color: 'var(--text)' }}>סיסמה</label>
              <input type="password" name="password" value={password} onChange={e => setPassword(e.target.value)}
                placeholder="••••••••" required className="search-input"
                style={{ padding: '14px 16px', fontSize: 15 }} />
            </div>

            <button type="submit" className="btn btn-primary"
              style={{ width: '100%', padding: '15px', fontSize: 16, fontWeight: 700, textAlign: 'center', border: 'none' }}>
              📝 צור חשבון
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: 24 }}>
            <Link href="/login" style={{ fontSize: 14, color: 'var(--muted)', textDecoration: 'none' }}>
              יש לך חשבון? כניסה למערכת
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
