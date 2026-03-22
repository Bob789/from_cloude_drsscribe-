
import Link from 'next/link'

export const metadata = {
  title: 'המלצות רופאים | Medical Hub',
  description: 'בקשו המלצות על רופאים מומחים מהקהילה ב-Medical Hub.',
  openGraph: { title: 'המלצות רופאים | Medical Hub', description: 'בקשות להמלצות רופאים מהקהילה', type: 'website' },
}

export default function RecommendationsPage() {
  return (
    <>
      <div style={{ padding: '48px 20px', textAlign: 'center' }}>
        <div style={{ fontSize: 64, marginBottom: 24 }}>⭐</div>
        <h2 style={{ fontSize: 32, fontWeight: 800, color: '#001f6b', marginBottom: 16 }}>בקשה להמלצות רופאים</h2>
        <p style={{ fontSize: 18, color: '#444', marginBottom: 32, lineHeight: 1.7 }}>
          מחפשים רופא מומחה? כאן תוכלו לבקש המלצות מהקהילה.<br />
          הדף בפיתוח — בקרוב!
        </p>
        <Link href="/" className="btn btn-primary" style={{ padding: '14px 32px', fontSize: 16 }}>
          חזרה לדף הבית
        </Link>
      </div>
    </>
  )
}
