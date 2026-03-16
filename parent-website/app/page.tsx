import Link from 'next/link'
import Header from '@/components/Header'
import ScrollingFeed, { FeedItem } from '@/components/ScrollingFeed'

const ARTICLES: FeedItem[] = [
  { id: 1,  title: 'כאבי גב כרוניים – מדריך מקיף',         meta: '4 דקות קריאה', tag: 'מאמר', gradient: ['#0ea5e9', '#2563eb'], icon: '📖' },
  { id: 2,  title: 'עייפות מתמשכת – מה לבדוק?',             meta: '6 דקות קריאה', tag: 'מאמר', gradient: ['#8b5cf6', '#6d28d9'], icon: '🔋' },
  { id: 3,  title: 'יתר לחץ דם – טיפול טבעי',               meta: '5 דקות קריאה', tag: 'מאמר', gradient: ['#ef4444', '#dc2626'], icon: '❤️' },
  { id: 4,  title: 'סוכרת סוג 2 – מניעה ושליטה',            meta: '8 דקות קריאה', tag: 'מאמר', gradient: ['#f97316', '#ea580c'], icon: '🩸' },
  { id: 5,  title: 'שינה בריאה – המדריך השלם',               meta: '3 דקות קריאה', tag: 'מאמר', gradient: ['#06b6d4', '#0891b2'], icon: '😴' },
  { id: 6,  title: 'דיאטה ים תיכונית – עדויות מדעיות',      meta: '7 דקות קריאה', tag: 'מאמר', gradient: ['#10b981', '#059669'], icon: '🥗' },
  { id: 7,  title: 'ספורט ובריאות לבני 50+',                 meta: '4 דקות קריאה', tag: 'מאמר', gradient: ['#f59e0b', '#d97706'], icon: '🏃' },
  { id: 8,  title: 'מחלות לב – גורמי סיכון מרכזיים',        meta: '9 דקות קריאה', tag: 'מאמר', gradient: ['#ec4899', '#db2777'], icon: '🫀' },
  { id: 9,  title: 'בריאות נפשית בעידן הדיגיטלי',           meta: '5 דקות קריאה', tag: 'מאמר', gradient: ['#a78bfa', '#7c3aed'], icon: '🧠' },
  { id: 10, title: 'אלרגיות עונתיות – מדריך מלא',           meta: '3 דקות קריאה', tag: 'מאמר', gradient: ['#34d399', '#10b981'], icon: '🌸' },
]

const FORUM_POSTS: FeedItem[] = [
  { id: 1,  title: 'כאב גב תחתון אחרי אימון',               meta: '12 תגובות • רופא ענה', tag: 'פורום', gradient: ['#6366f1', '#4f46e5'], icon: '💬' },
  { id: 2,  title: 'האם צריך MRI לכאבי ראש?',               meta: '7 תגובות',               tag: 'פורום', gradient: ['#8b5cf6', '#7c3aed'], icon: '🧩' },
  { id: 3,  title: 'תופעות לוואי של מטפורמין',              meta: '15 תגובות • רופא ענה', tag: 'פורום', gradient: ['#f43f5e', '#e11d48'], icon: '💊' },
  { id: 4,  title: 'דיאטה vs תרופות לסוכרת',                meta: '23 תגובות',              tag: 'פורום', gradient: ['#0ea5e9', '#0284c7'], icon: '⚖️' },
  { id: 5,  title: 'כאבי ברכיים בריצה',                     meta: '9 תגובות',               tag: 'פורום', gradient: ['#14b8a6', '#0d9488'], icon: '🦵' },
  { id: 6,  title: 'שיטות להפחתת לחץ דם',                  meta: '18 תגובות • רופא ענה', tag: 'פורום', gradient: ['#f97316', '#ea580c'], icon: '📊' },
  { id: 7,  title: 'אנמיה – תוספי ברזל',                    meta: '11 תגובות',              tag: 'פורום', gradient: ['#ec4899', '#db2777'], icon: '🩸' },
  { id: 8,  title: 'נדודי שינה – פתרונות',                  meta: '31 תגובות',              tag: 'פורום', gradient: ['#a78bfa', '#8b5cf6'], icon: '🌙' },
  { id: 9,  title: 'רפואת ספורט – שאלות',                   meta: '6 תגובות',               tag: 'פורום', gradient: ['#34d399', '#059669'], icon: '🏅' },
  { id: 10, title: 'תזונה לילדים – עצות',                   meta: '14 תגובות • רופא ענה', tag: 'פורום', gradient: ['#fbbf24', '#f59e0b'], icon: '🥦' },
]

const EXPERTS: FeedItem[] = [
  { id: 1, title: 'ד"ר דניאל כהן',       meta: 'אורתופדיה • תל אביב',        tag: 'מומחה', gradient: ['#0ea5e9', '#2563eb'], icon: '🦴' },
  { id: 2, title: 'פרופ׳ מרים לוי',       meta: 'נוירולוגיה • ירושלים',       tag: 'מומחה', gradient: ['#8b5cf6', '#6d28d9'], icon: '🧠' },
  { id: 3, title: 'ד"ר שרה אברמוביץ',    meta: 'קרדיולוגיה • חיפה',          tag: 'מומחה', gradient: ['#ef4444', '#dc2626'], icon: '❤️' },
  { id: 4, title: 'ד"ר יוסי מזרחי',      meta: 'אנדוקרינולוגיה • תל אביב',  tag: 'מומחה', gradient: ['#10b981', '#059669'], icon: '🔬' },
  { id: 5, title: 'פרופ׳ ריבה שמש',       meta: 'רפואה פנימית • באר שבע',    tag: 'מומחה', gradient: ['#f97316', '#ea580c'], icon: '🏥' },
  { id: 6, title: 'ד"ר אמיר זקן',        meta: 'פסיכיאטריה • רמת גן',       tag: 'מומחה', gradient: ['#a78bfa', '#7c3aed'], icon: '🧘' },
  { id: 7, title: 'ד"ר נעמה כץ',         meta: 'נפרולוגיה • פתח תקווה',     tag: 'מומחה', gradient: ['#06b6d4', '#0891b2'], icon: '💉' },
  { id: 8, title: 'פרופ׳ רון בן-דוד',    meta: 'אונקולוגיה • תל אביב',      tag: 'מומחה', gradient: ['#ec4899', '#db2777'], icon: '🔭' },
]

export default function HomePage() {
  return (
    <>
      <Header />
      <main>

      {/* Hero */}
      <div style={{ position: 'relative' }}>
        {/* Logo only — floats up above the header. z-index 201 applies only to this 120x120 image, not to page content */}
        <div style={{
          position: 'absolute', top: -70, left: 0, right: 0,
          display: 'flex', justifyContent: 'center',
          zIndex: 201, pointerEvents: 'none',
        }}>
          <img src="/logo.png" alt="Doctor Scribe AI" width={120} height={120} className="logo-animated" style={{ pointerEvents: 'auto' }} />
        </div>

        {/* Text + buttons — normal z-index, never blocks nav */}
        <section style={{ maxWidth: 1400, margin: '0 auto', padding: '70px 20px 40px', textAlign: 'center' }}>
          <h2 className="hero-title" style={{ fontSize: 48, fontWeight: 700, marginBottom: 24, background: 'linear-gradient(to left, #22d3ee, #3b82f6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
            Medical Hub + Doctor Scribe AI
          </h2>
          <p style={{ fontSize: 24, marginBottom: 16, color: 'var(--text)' }}>
            פלטפורמה מקיפה: מאמרים • פורום • מומחים • תמלול רפואי חכם
          </p>
          <p style={{ fontSize: 18, color: 'var(--muted)', marginBottom: 32 }}>
            מערכת SaaS לתמלול וסיכום אוטומטי של ביקורים רפואיים בעברית
          </p>
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/product" className="btn btn-primary" style={{ padding: '16px 32px', fontSize: 18, lineHeight: 1.4 }}>
              <div style={{ fontSize: 18, fontWeight: 700 }}>🎤 גלה את Doctor Scribe AI</div>
              <div style={{ fontSize: 14, marginTop: 4, opacity: 0.85 }}>חדש: שירות תמלול לקליניקות</div>
            </Link>
          </div>
          <div style={{ marginTop: 18, fontSize: 14, color: 'var(--muted)' }}>
            <Link
              href="/privacy-policy"
              style={{ color: '#38bdf8', textDecoration: 'underline', textUnderlineOffset: 3 }}
            >
              Privacy Policy
            </Link>
            {' '}•{' '}
            <Link
              href="/privacy-policy"
              style={{ color: '#38bdf8', textDecoration: 'underline', textUnderlineOffset: 3 }}
            >
              מדיניות פרטיות
            </Link>
          </div>
        </section>
      </div>

      {/* Search bar */}
      <div style={{ maxWidth: 1400, margin: '0 auto 24px', padding: '0 20px' }}>
        <div className="card">
          <h3>חיפוש מהיר</h3>
          <div className="search-box">
            <input type="text" className="search-input" placeholder="חפש מאמר / פורום / מומחה / תמלול..." />
            <button className="btn btn-secondary">חפש</button>
          </div>
          <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 8 }}>
            טיפ: לחץ <span className="kbd">/</span> לקיצור מקלדת
          </p>
        </div>
      </div>

      {/* 3-column animated feeds */}
      <div className="feeds-grid" style={{ maxWidth: 1400, margin: '0 auto 24px', padding: '0 20px' }}>

        {/* Articles */}
        <div className="card" style={{ minWidth: 0 }}>
          <h4>📰 מאמרים פופולריים</h4>
          <ScrollingFeed items={ARTICLES} visibleCount={7} intervalMs={2800} label="articles" />
        </div>

        {/* Forum */}
        <div className="card" style={{ minWidth: 0 }}>
          <h4>💬 פורום פעיל</h4>
          <ScrollingFeed items={FORUM_POSTS} visibleCount={7} intervalMs={3200} label="forum" />
        </div>

        {/* Experts */}
        <div className="card" style={{ minWidth: 0 }}>
          <h4>👨‍⚕️ מומחים מומלצים</h4>
          <ScrollingFeed items={EXPERTS} visibleCount={7} intervalMs={3600} label="experts" />
        </div>

      </div>

      {/* Doctor Scribe AI – full-width horizontal CTA */}
      <div style={{ maxWidth: 1400, margin: '0 auto 48px', padding: '0 20px' }}>
        <div style={{
          padding: '32px 40px',
          borderRadius: 24,
          border: '1px solid rgba(56,189,248,0.6)',
          background: 'linear-gradient(135deg, rgba(18,26,51,0.95), rgba(6,10,21,0.95))',
          display: 'flex',
          alignItems: 'center',
          gap: 32,
          flexWrap: 'wrap',
        }}>
          <img
            src="/logo.png"
            alt="Doctor Scribe AI"
            width={72}
            height={72}
            style={{ borderRadius: '50%', flexShrink: 0, boxShadow: '0 0 24px rgba(56,189,248,0.4)' }}
          />
          <div style={{ flex: 1, minWidth: 200 }}>
            <h3 style={{ fontSize: 26, fontWeight: 700, marginBottom: 8, color: '#e0f2fe' }}>
              🎤 Doctor Scribe AI
            </h3>
            <p style={{ color: 'var(--text)', fontSize: 16, marginBottom: 6 }}>
              ניהול מטופלים + תמלול אוטומטי + סיכום ביקור + תגיות אבחנה
            </p>
            <p style={{ color: 'var(--muted)', fontSize: 14 }}>
              מערכת SaaS לתמלול וסיכום אוטומטי של ביקורים רפואיים בעברית — לקליניקות פרטיות ורופאים עצמאיים
            </p>
          </div>
          <div style={{ display: 'flex', gap: 12, flexShrink: 0, flexWrap: 'wrap' }}>
            <Link href="/product" className="btn btn-primary" style={{ padding: '14px 28px', fontSize: 16 }}>
              למד עוד
            </Link>
            <Link href="/product" className="btn btn-secondary" style={{ padding: '14px 28px', fontSize: 16 }}>
              כניסה למערכת
            </Link>
          </div>
        </div>
      </div>

      </main>

      {/* FOOTER - Google Verification Compliance */}
      <footer style={{ 
        borderTop: '1px solid var(--border)', 
        marginTop: 48, 
        padding: '32px 20px', 
        textAlign: 'center', 
        color: 'var(--muted)',
        backgroundColor: 'rgba(6, 10, 21, 0.5)' 
      }}>
        <div style={{ marginBottom: 16 }}>
          © 2026 Medical Hub • Doctor Scribe AI Privacy Policy • מדיניות פרטיות • תנאי שימוש
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 24, flexWrap: 'wrap' }}>
          <a href="/privacy-policy" style={{ color: 'var(--text)', textDecoration: 'none' }}>מדיניות פרטיות</a>
          <a href="/terms" style={{ color: 'var(--text)', textDecoration: 'none' }}>תנאי שימוש</a>
          <a href="/contact" style={{ color: 'var(--text)', textDecoration: 'none' }}>צור קשר</a>
        </div>
      </footer>
    </>
  )
}
