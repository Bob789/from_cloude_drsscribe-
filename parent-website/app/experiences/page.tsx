
import Link from 'next/link'

export const metadata = {
  title: 'חוויות אישיות | Medical Hub',
  description: 'שתפו וקראו חוויות אישיות של מטופלים ורופאים ב-Medical Hub.',
  openGraph: { title: 'חוויות אישיות | Medical Hub', description: 'חוויות אישיות של מטופלים ורופאים', type: 'website' },
}

export default function ExperiencesPage() {
  return (
    <>

      <main>
      <div style={{ maxWidth: 900, margin: '64px auto', padding: '0 20px', textAlign: 'center' }}>
        <div style={{ fontSize: 64, marginBottom: 24 }}>💬</div>
        <h2 style={{ fontSize: 32, fontWeight: 800, color: '#e0f2fe', marginBottom: 16 }}>חוויות אישיות</h2>
        <p style={{ fontSize: 18, color: 'var(--muted)', marginBottom: 32, lineHeight: 1.7 }}>
          כאן תוכלו לשתף ולקרוא חוויות אישיות של מטופלים ורופאים.<br />
          הדף בפיתוח — בקרוב!
        </p>
        <Link href="/" className="btn btn-primary" style={{ padding: '14px 32px', fontSize: 16 }}>
          חזרה לדף הבית
        </Link>
      </div>
      </main>
    </>
  )
}
