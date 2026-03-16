import Header from '@/components/Header'
import Link from 'next/link'

export const metadata = {
  title: 'תנאי שימוש | Medical Hub',
  description: 'תנאי השימוש של Medical Hub ו-Doctor Scribe AI — תנאים והגבלות לשימוש בשירות.',
  openGraph: {
    title: 'תנאי שימוש | Medical Hub',
    description: 'תנאי השימוש של Medical Hub ו-Doctor Scribe AI',
    type: 'website',
  },
}

export default function TermsPage() {
  return (
    <>
      <Header />
      <main>
        <div style={{ maxWidth: 800, margin: '48px auto', padding: '0 20px' }}>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: '#e0f2fe', marginBottom: 8 }}>
            תנאי שימוש
          </h1>
          <p style={{ color: 'var(--muted)', marginBottom: 40, fontSize: 14 }}>
            עדכון אחרון: פברואר 2026
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>1. הסכמה לתנאים</h2>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8 }}>
                בשימוש בשירותי Medical Hub ו-Doctor Scribe AI, הנך מסכים לתנאים אלה. אם אינך מסכים, אנא הימנע משימוש בשירות.
                אנו שומרים הזכות לעדכן תנאים אלה בכל עת עם הודעה מוקדמת.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>2. השירות</h2>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8 }}>
                Medical Hub מספק פלטפורמת קהילה רפואית כולל מאמרים, פורום שאלות ותשובות, ורשימת מומחים.
                Doctor Scribe AI מספק שירות תמלול וסיכום אוטומטי של ביקורים רפואיים.
              </p>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8, marginTop: 12 }}>
                <strong style={{ color: '#ef4444' }}>אזהרה רפואית:</strong> המידע באתר הוא למטרות מידע כללי בלבד ואינו מהווה עצה רפואית.
                לא להסתמך על המידע לצורך אבחון, טיפול, או החלטות רפואיות. פנה לרופא מוסמך.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>3. חשבון משתמש</h2>
              <ul style={{ color: 'var(--muted)', lineHeight: 1.8, paddingRight: 20 }}>
                <li>אחראי לשמירת סיסמתך בסוד</li>
                <li>אסור לשתף חשבון עם אחרים</li>
                <li>חייב להיות בן 18+ לשימוש בשירות</li>
                <li>יש לספק פרטים נכונים ומדויקים בעת הרשמה</li>
              </ul>
            </section>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>4. שימוש מותר</h2>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8 }}>
                מותר: שימוש אישי לגיטימי, שיתוף תוכן מדויק ומועיל, שאלות ותשובות בפורום.
              </p>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8, marginTop: 8 }}>
                אסור: פרסום ספאם, תוכן מטעה, מידע רפואי שגוי, הטרדה, שימוש מסחרי ללא אישור.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>5. קניין רוחני</h2>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8 }}>
                כל התוכן באתר (למעט תוכן שפרסמו משתמשים) שייך ל-Medical Hub.
                אסור להעתיק, להפיץ, או להשתמש בתוכן ללא אישור מפורש בכתב.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>6. הגבלת אחריות</h2>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8 }}>
                השירות מסופק "כפי שהוא" (as-is). Medical Hub אינו אחראי לנזקים ישירים או עקיפים הנובעים מהשימוש בשירות.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>7. סיום חשבון</h2>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8 }}>
                Medical Hub רשאי להשעות או לסגור חשבון שהפר תנאים אלה. ניתן לבטל חשבון בכל עת דרך הגדרות הפרופיל.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e0f2fe', marginBottom: 12 }}>8. יצירת קשר</h2>
              <p style={{ color: 'var(--muted)', lineHeight: 1.8 }}>
                לשאלות בנוגע לתנאים אלה:{' '}
                <a href="mailto:legal@medicalhub.co.il" style={{ color: '#38bdf8' }}>legal@medicalhub.co.il</a>
              </p>
            </section>

            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', paddingTop: 16 }}>
              <Link href="/privacy" className="btn btn-secondary" style={{ padding: '12px 24px' }}>
                מדיניות פרטיות
              </Link>
              <Link href="/" className="btn btn-primary" style={{ padding: '12px 24px' }}>
                חזרה לדף הבית
              </Link>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}
