'use client'

import { useEffect } from 'react'
import Link from 'next/link'

export default function GlobalRouteError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Always log full error to console for debugging
    // (visible in browser DevTools → Console)
    // eslint-disable-next-line no-console
    console.error('[client-error]', {
      name: error.name,
      message: error.message,
      digest: error.digest,
      stack: error.stack,
      url: typeof window !== 'undefined' ? window.location.href : '',
    })

    // Best-effort: send to backend log endpoint (silent if not present)
    try {
      const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'
      fetch(`${API}/site/client-error`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: error.name,
          message: error.message,
          digest: error.digest,
          stack: (error.stack || '').slice(0, 4000),
          url: typeof window !== 'undefined' ? window.location.href : '',
          ua: typeof navigator !== 'undefined' ? navigator.userAgent : '',
          ts: new Date().toISOString(),
        }),
        keepalive: true,
      }).catch(() => {})
    } catch {}
  }, [error])

  const isDev = process.env.NODE_ENV !== 'production'

  return (
    <main
      dir="rtl"
      style={{
        minHeight: '70vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 16,
        padding: 24,
        color: 'white',
        textAlign: 'center',
      }}
    >
      <h1 style={{ fontSize: 28, margin: 0 }}>אופס — משהו השתבש בטעינת הדף</h1>
      <p style={{ color: 'rgba(255,255,255,0.75)', maxWidth: 600 }}>
        קרתה תקלה בצד הלקוח. הצוות יקבל דיווח אוטומטי. ניתן לנסות לרענן.
      </p>

      {error.digest && (
        <code
          style={{
            background: 'rgba(255,255,255,0.08)',
            padding: '6px 12px',
            borderRadius: 8,
            fontSize: 12,
          }}
        >
          digest: {error.digest}
        </code>
      )}

      {isDev && (
        <pre
          style={{
            maxWidth: '90vw',
            overflow: 'auto',
            background: 'rgba(0,0,0,0.6)',
            padding: 16,
            borderRadius: 10,
            fontSize: 12,
            textAlign: 'left',
            direction: 'ltr',
            color: '#fcd34d',
          }}
        >
          {error.name}: {error.message}
          {'\n\n'}
          {error.stack}
        </pre>
      )}

      <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
        <button
          onClick={() => reset()}
          style={{
            background: '#2563eb',
            color: 'white',
            border: 'none',
            borderRadius: 10,
            padding: '10px 22px',
            fontSize: 15,
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          נסה שוב
        </button>
        <Link
          href="/"
          style={{
            background: 'rgba(255,255,255,0.1)',
            color: 'white',
            borderRadius: 10,
            padding: '10px 22px',
            fontSize: 15,
            fontWeight: 600,
            textDecoration: 'none',
          }}
        >
          חזרה לעמוד הראשי
        </Link>
      </div>
    </main>
  )
}
