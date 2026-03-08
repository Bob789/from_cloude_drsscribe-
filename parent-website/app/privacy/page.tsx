import Header from '@/components/Header'
import Link from 'next/link'

export const metadata = {
  title: 'מדיניות פרטיות | Medical Hub',
  description: 'מדיניות הפרטיות של Medical Hub ו-MedScribe AI — כיצד אנו אוספים, משתמשים ומגנים על המידע שלך בהתאם ל-GDPR.',
  openGraph: {
    title: 'מדיניות פרטיות | Medical Hub',
    description: 'מדיניות הפרטיות של Medical Hub ו-MedScribe AI',
    type: 'website',
  },
}

export default function PrivacyPage() {
  return (
    <>
      <Header />
      <main>
        <div style={{ maxWidth: 800, margin: '48px auto', padding: '0 20px' }}>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: '#e0f2fe', marginBottom: 8 }}>
            מדיניות פרטיות
          </h1>
          <p style={{ color: 'var(--muted)', marginBottom: 40, fontSize: 14 }}>
            עדכון אחרון: פברואר 2026
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>1. כללי</h2>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8 }}>
                Medical Hub ו-MedScribe AI ("אנחנו", "השירות") מכבדים את פרטיותך ומחויבים להגנה על המידע האישי שלך.
                מדיניות זו מסבירה כיצד אנו אוספים, משתמשים, ומגנים על המידע שלך בהתאם לתקנות GDPR ולחקיקת הגנת הפרטיות הישראלית.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>2. מידע שאנו אוספים</h2>
              <ul style={{ color: 'var(--muted)', lineHeight: 1.8, paddingRight: 20 }}>
                <li><strong style={{ color: 'var(--text)' }}>מידע שמסרת:</strong> שם, כתובת אימייל, סיסמה בעת הרשמה</li>
                <li><strong style={{ color: 'var(--text)' }}>מידע שימוש:</strong> דפים שנצפו, שאלות שנשאלו בפורום, מאמרים שנקראו</li>
                <li><strong style={{ color: 'var(--text)' }}>מידע טכני:</strong> כתובת IP, סוג דפדפן, מכשיר</li>
                <li><strong style={{ color: 'var(--text)' }}>עוגיות (Cookies):</strong> ראה סעיף 5</li>
              </ul>
            </section>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>3. שימוש במידע</h2>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8 }}>
                אנו משתמשים במידע שלך כדי לספק ולשפר את השירות, לתקשר איתך, לנתח שימוש, ולעמוד בחובות חוקיות.
                לא נמכור או נשתף את המידע האישי שלך עם צדדים שלישיים לצרכי שיווק.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>4. זכויותיך</h2>
              <ul style={{ color: 'var(--muted)', lineHeight: 1.8, paddingRight: 20 }}>
                <li>זכות לגישה למידע האישי שלך</li>
                <li>זכות לתיקון מידע שגוי</li>
                <li>זכות למחיקה ("הזכות להישכח")</li>
                <li>זכות להתנגד לעיבוד</li>
                <li>זכות לניידות נתונים</li>
              </ul>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8, marginTop: 12 }}>
                לממש זכויות אלה, צור קשר: <a href="mailto:privacy@medicalhub.co.il" style={{ color: '#38bdf8' }}>privacy@medicalhub.co.il</a>
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>5. עוגיות</h2>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8 }}>
                אנו משתמשים בעוגיות הכרחיות לתפעול האתר ועוגיות אנליטיקה לשיפור השירות.
                ניתן לנהל העדפות עוגיות דרך הגדרות הדפדפן שלך.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>6. אבטחת מידע</h2>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8 }}>
                אנו נוקטים באמצעי אבטחה טכניים וארגוניים מתאימים להגנה על המידע שלך, כולל הצפנת SSL, אחסון מאובטח, וגישה מוגבלת למידע.
              </p>
            </section>

            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', paddingTop: 16 }}>
              <Link href="/terms" className="btn btn-secondary" style={{ padding: '12px 24px' }}>
                תנאי שימוש
              </Link>
              <Link href="/" className="btn btn-primary" style={{ padding: '12px 24px' }}>
                חזרה לדף הבית
              </Link>
            </div>
          </div>
        </div>
      </main>
      <footer className="site-footer">
        <p>© 2026 Medical Hub • מדיניות פרטיות • תנאי שימוש</p>
      </footer>
    </>
  )
}
