
import Link from 'next/link'

export const metadata = {
  title: 'אודות | Medical Hub',
  description: 'אודות Medical Hub — פלטפורמה רפואית מקיפה המשלבת מאמרים, פורום, מומחים ותמלול רפואי חכם.',
  openGraph: { title: 'אודות | Medical Hub', description: 'אודות Medical Hub', type: 'website' },
}

export default function AboutPage() {
  return (
    <>
      <div style={{ padding: '48px 20px', textAlign: 'center' }}>
        <div style={{ fontSize: 64, marginBottom: 24 }}>ℹ️</div>
        <h2 style={{ fontSize: 32, fontWeight: 800, color: '#001f6b', marginBottom: 16 }}>אודות Medical Hub</h2>
        <p style={{ fontSize: 18, color: '#444', marginBottom: 32, lineHeight: 1.7 }}>
          Medical Hub היא פלטפורמה רפואית מקיפה המשלבת מאמרים, פורום, מומחים ותמלול רפואי חכם.<br />
          הדף בפיתוח — בקרוב!
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/product" className="btn btn-primary" style={{ padding: '14px 32px', fontSize: 16 }}>
            אודות Doctor Scribe AI
          </Link>
          <Link href="/" className="btn btn-secondary" style={{ padding: '14px 32px', fontSize: 16 }}>
            חזרה לדף הבית
          </Link>
        </div>
      </div>
    </>
  )
}
