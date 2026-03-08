import Header from '@/components/Header'
import Link from 'next/link'

export const metadata = {
  title: 'המלצות רופאים | Medical Hub',
  description: 'בקשו המלצות על רופאים מומחים מהקהילה ב-Medical Hub.',
  openGraph: { title: 'המלצות רופאים | Medical Hub', description: 'בקשות להמלצות רופאים מהקהילה', type: 'website' },
}

export default function RecommendationsPage() {
  return (
    <>
      <Header />
      <main>
      <div style={{ maxWidth: 900, margin: '64px auto', padding: '0 20px', textAlign: 'center' }}>
        <div style={{ fontSize: 64, marginBottom: 24 }}>⭐</div>
        <h2 style={{ fontSize: 32, fontWeight: 800, color: '#e0f2fe', marginBottom: 16 }}>בקשה להמלצות רופאים</h2>
        <p style={{ fontSize: 18, color: 'var(--muted)', marginBottom: 32, lineHeight: 1.7 }}>
          מחפשים רופא מומחה? כאן תוכלו לבקש המלצות מהקהילה.<br />
          הדף בפיתוח — בקרוב!
        </p>
        <Link href="/" className="btn btn-primary" style={{ padding: '14px 32px', fontSize: 16 }}>
          חזרה לדף הבית
        </Link>
      </div>
      </main>
      <footer className="site-footer">
        <p>© 2026 Medical Hub • מדיניות פרטיות • תנאי שימוש</p>
      </footer>
    </>
  )
}
