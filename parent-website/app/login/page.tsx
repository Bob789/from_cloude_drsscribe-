'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function LoginPage() {
  const router = useRouter()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    if (!username.trim() || !password.trim()) {
      setError('יש למלא את כל השדות')
      return
    }
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(data?.detail || 'שם משתמש או סיסמה שגויים')
        return
      }

      const data = await res.json()
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))

      router.push('/product')
    } catch {
      setError('שגיאת חיבור לשרת — נסה שוב')
    } finally {
      setLoading(false)
    }
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

        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <Link href="/">
            <img
              src="/logo.png"
              alt="Medical Hub"
              width={72}
              height={72}
              style={{ borderRadius: '50%', margin: '0 auto 16px', display: 'block', boxShadow: '0 0 24px rgba(56,189,248,0.4)' }}
            />
          </Link>
          <h1 style={{ fontSize: 26, fontWeight: 700, color: '#e0f2fe', marginBottom: 8 }}>
            כניסה למערכת
          </h1>
          <p style={{ color: 'var(--muted)', fontSize: 14 }}>
            MedScribe AI — תמלול רפואי חכם
          </p>
        </div>

        {/* Card */}
        <div style={{
          background: 'rgba(18,26,51,0.85)',
          border: '1px solid var(--border)',
          borderRadius: 24,
          padding: '36px 32px',
        }}>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

            {/* Error */}
            {error && (
              <div role="alert" className="error-message" style={{
                padding: '12px 16px',
                borderRadius: 12,
                border: '1px solid rgba(239,68,68,0.4)',
                background: 'rgba(239,68,68,0.1)',
                color: '#fca5a5',
                fontSize: 14,
                textAlign: 'center',
              }}>
                {error}
              </div>
            )}

            {/* Username */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <label style={{ fontSize: 14, fontWeight: 600, color: 'var(--text)' }}>
                שם משתמש / אימייל
              </label>
              <input
                type="email"
                name="email"
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder="doctor@clinic.co.il"
                required
                autoComplete="username"
                className="search-input"
                style={{ padding: '14px 16px', fontSize: 15 }}
              />
            </div>

            {/* Password */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <label style={{ fontSize: 14, fontWeight: 600, color: 'var(--text)' }}>
                סיסמה
              </label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                autoComplete="current-password"
                className="search-input"
                style={{ padding: '14px 16px', fontSize: 15 }}
              />
            </div>

            {/* Forgot password */}
            <div style={{ textAlign: 'left' }}>
              <a href="#" style={{ fontSize: 13, color: 'var(--accent)', textDecoration: 'none' }}>
                שכחתי סיסמה
              </a>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{
                width: '100%',
                padding: '15px',
                fontSize: 16,
                fontWeight: 700,
                textAlign: 'center',
                opacity: loading ? 0.7 : 1,
                cursor: loading ? 'not-allowed' : 'pointer',
                border: 'none',
              }}
            >
              {loading ? '⏳ מתחבר...' : '🔐 כניסה למערכת'}
            </button>

          </form>

          {/* Divider */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '24px 0' }}>
            <div style={{ flex: 1, height: 1, background: 'var(--border)' }} />
            <span style={{ fontSize: 13, color: 'var(--muted)' }}>או</span>
            <div style={{ flex: 1, height: 1, background: 'var(--border)' }} />
          </div>

          {/* Back to home */}
          <div style={{ textAlign: 'center' }}>
            <Link
              href="/"
              style={{ fontSize: 14, color: 'var(--muted)', textDecoration: 'none' }}
            >
              ← חזרה לדף הבית
            </Link>
          </div>
        </div>

        {/* Footer note */}
        <p style={{ textAlign: 'center', marginTop: 24, fontSize: 12, color: 'var(--muted)' }}>
          © 2026 Medical Hub • מדיניות פרטיות
        </p>
      </div>
    </div>
  )
}
