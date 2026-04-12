'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Script from 'next/script'

const GOOGLE_CLIENT_ID = '459295230393-a7tahndgdhses9shhg0oue74ealf009r.apps.googleusercontent.com'
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

export default function LoginPage() {
  const router = useRouter()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [gsiReady, setGsiReady] = useState(false)

  useEffect(() => {
    // Check if already loaded (e.g. cached)
    if ((window as any).google?.accounts?.oauth2) {
      setGsiReady(true)
    }
  }, [])

  async function handleGoogleLogin() {
    setError('')
    setLoading(true)

    try {
      // Load Google Identity Services
      let google = (window as any).google
      if (!google?.accounts?.oauth2) {
        // Try waiting a moment for script to finish loading
        await new Promise(r => setTimeout(r, 1500))
        google = (window as any).google
        if (!google?.accounts?.oauth2) {
          setError('שגיאה בטעינת שירות Google — נסה לרענן את הדף')
          setLoading(false)
          return
        }
      }

      const client = google.accounts.oauth2.initTokenClient({
        client_id: GOOGLE_CLIENT_ID,
        scope: 'email profile openid',
        callback: async (tokenResponse: any) => {
          if (tokenResponse.error) {
            setError('הכניסה עם Google נכשלה — נסה שוב')
            setLoading(false)
            return
          }

          try {
            const res = await fetch(`${API_URL}/auth/google`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                token: tokenResponse.access_token,
                token_type: 'access_token',
              }),
            })

            if (!res.ok) {
              setError('הכניסה נכשלה — נסה שוב')
              setLoading(false)
              return
            }

            const data = await res.json()
            localStorage.setItem('access_token', data.access_token)
            localStorage.setItem('refresh_token', data.refresh_token)
            localStorage.setItem('user', JSON.stringify(data.user))
            window.dispatchEvent(new Event('auth-changed'))

            router.push('/')
          } catch {
            setError('שגיאת חיבור לשרת — נסה שוב')
          } finally {
            setLoading(false)
          }
        },
      })

      client.requestAccessToken()
    } catch {
      setError('שגיאה בכניסה — נסה שוב')
      setLoading(false)
    }
  }

  return (
    <>
      {/* Load Google Identity Services */}
      <Script
        src="https://accounts.google.com/gsi/client"
        strategy="afterInteractive"
        onLoad={() => setGsiReady(true)}
      />

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
              כניסה למערכת מאמרים • פורום • מומחים
            </h1>
            <p style={{ color: 'var(--muted)', fontSize: 14 }}>
              כניסה באמצעות כתובת Gmail בלבד
            </p>
          </div>

          {/* Card */}
          <div style={{
            background: 'rgba(18,26,51,0.85)',
            border: '1px solid var(--border)',
            borderRadius: 24,
            padding: '36px 32px',
          }}>

            {/* Error */}
            {error && (
              <div role="alert" style={{
                padding: '12px 16px',
                borderRadius: 12,
                border: '1px solid rgba(239,68,68,0.4)',
                background: 'rgba(239,68,68,0.1)',
                color: '#fca5a5',
                fontSize: 14,
                textAlign: 'center',
                marginBottom: 20,
              }}>
                {error}
              </div>
            )}

            {/* Google Sign In Button */}
            <button
              onClick={handleGoogleLogin}
              disabled={loading}
              style={{
                width: '100%',
                padding: '15px 20px',
                fontSize: 16,
                fontWeight: 700,
                textAlign: 'center',
                background: '#ffffff',
                color: '#3c4043',
                border: '1px solid #dadce0',
                borderRadius: 12,
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 12,
                transition: 'box-shadow 0.2s',
              }}
              onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)')}
              onMouseLeave={e => (e.currentTarget.style.boxShadow = 'none')}
            >
              {!loading && (
                <svg width="20" height="20" viewBox="0 0 48 48">
                  <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
                  <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
                  <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
                  <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
                </svg>
              )}
              {loading ? '⏳ מתחבר...' : 'התחבר עם Google'}
            </button>

            {/* Divider */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '24px 0' }}>
              <div style={{ flex: 1, height: 1, background: 'var(--border)' }} />
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

          {/* Footer */}
          <p style={{ textAlign: 'center', marginTop: 24, fontSize: 12, color: 'var(--muted)' }}>
            © 2026 Medical Hub • מדיניות פרטיות
          </p>
        </div>
      </div>
    </>
  )
}
