import Link from 'next/link'
import '../articles/article-theme.css'

export const metadata = {
  title: 'הצהרת שימוש רפואי | Medical Hub',
  description: 'הצהרת שימוש ואחריות רפואית — המידע באתר אינו מהווה ייעוץ רפואי.',
  openGraph: {
    title: 'הצהרת שימוש רפואי | Medical Hub',
    description: 'הצהרת שימוש ואחריות רפואית של Medical Hub ו-Doctor Scribe AI',
    type: 'website',
  },
}

const LegalNav = ({ active }: { active: string }) => (
  <div style={{ padding: '0 24px 28px', borderTop: '1px solid rgba(0,51,153,0.2)', marginTop: 8 }}>
    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', paddingTop: 18, justifyContent: 'center', alignItems: 'center' }}>
      <Link href="/terms" style={{ fontWeight: active === 'terms' ? 800 : 600, color: active === 'terms' ? '#001f6b' : '#1a56db', textDecoration: 'none', padding: '8px 18px', background: active === 'terms' ? 'rgba(26,86,219,0.12)' : 'rgba(26,86,219,0.04)', border: active === 'terms' ? '2px solid #1a56db' : '1px solid rgba(26,86,219,0.25)', borderRadius: 10, fontSize: 14 }}>תנאי שימוש</Link>
      <span style={{ color: '#b0b8c8', fontSize: 18, userSelect: 'none' }}>|</span>
      <Link href="/privacy" style={{ fontWeight: active === 'privacy' ? 800 : 600, color: active === 'privacy' ? '#001f6b' : '#1a56db', textDecoration: 'none', padding: '8px 18px', background: active === 'privacy' ? 'rgba(26,86,219,0.12)' : 'rgba(26,86,219,0.04)', border: active === 'privacy' ? '2px solid #1a56db' : '1px solid rgba(26,86,219,0.25)', borderRadius: 10, fontSize: 14 }}>מדיניות פרטיות</Link>
      <span style={{ color: '#b0b8c8', fontSize: 18, userSelect: 'none' }}>|</span>
      <Link href="/medical-disclaimer" style={{ fontWeight: active === 'medical' ? 800 : 600, color: active === 'medical' ? '#001f6b' : '#1a56db', textDecoration: 'none', padding: '8px 18px', background: active === 'medical' ? 'rgba(26,86,219,0.12)' : 'rgba(26,86,219,0.04)', border: active === 'medical' ? '2px solid #1a56db' : '1px solid rgba(26,86,219,0.25)', borderRadius: 10, fontSize: 14 }}>הצהרת שימוש רפואי</Link>
    </div>
  </div>
)

export default function MedicalDisclaimerPage() {
  return (
    <>
      <div className="article-block">

        <div className="page-header-bar">
          <Link href="/" className="back-btn">→</Link>
          <div>
            <div className="page-title">Medical Hub · הצהרת שימוש רפואי</div>
            <div className="page-subtitle">תוכן האתר אינו מהווה ייעוץ רפואי</div>
          </div>
        </div>

        <div className="title-lines">
          <div className="title-line"></div>
          <div className="title-line"></div>
        </div>

        <div className="article-hero">
          <span className="hero-badge">הצהרה רפואית</span>
          <h1 className="hero-title">הצהרת שימוש ואחריות רפואית</h1>
          <p className="hero-subtitle">חשוב לקרוא — השימוש במידע הרפואי באתר כפוף לתנאים אלה</p>
        </div>

        <div className="divider-section">
          <div className="arch arch-right"></div>
          <div className="dark-lines-wrapper">
            <div className="dark-line"></div>
            <div className="dark-line"></div>
          </div>
          <div className="arch arch-left"></div>
        </div>

        <div className="article-body">

          <p>התוכן המוצג באתר זה, לרבות מאמרים, סקירות מקצועיות, פורום שאלות ותשובות, המלצות על רופאים, תמלולים וסיכומים אוטומטיים וכל מידע אחר, נועד למטרות מידע כללי והעשרה בלבד.</p>

          <h2>אין לראות בתוכן זה:</h2>
          <ul>
            <li>ייעוץ רפואי</li>
            <li>חוות דעת מקצועית</li>
            <li>אבחנה רפואית</li>
            <li>המלצה טיפולית</li>
          </ul>

          <h2>על שירותי AI ואוטומציה</h2>
          <p>השירותים המוצעים באתר, כולל Doctor Scribe AI, מבוססים בין היתר על מערכות אוטומטיות ובינה מלאכותית, ועל כן ייתכנו אי-דיוקים, השמטות או טעויות.</p>

          <h2>אין להסתמך על המידע לצורך:</h2>
          <ul>
            <li>קבלת החלטות רפואיות</li>
            <li>התחלת טיפול</li>
            <li>שינוי טיפול קיים</li>
          </ul>

          <p><strong>כל החלטה רפואית חייבת להתקבל על ידי רופא או איש מקצוע מוסמך בלבד.</strong></p>

          <h2>התחייבות המשתמש</h2>
          <p>המשתמש מתחייב:</p>
          <ul>
            <li>להשתמש במידע בזהירות ובשיקול דעת</li>
            <li>להתאים את המידע למצבו האישי</li>
            <li>לא לראות במידע תחליף לייעוץ רפואי</li>
          </ul>

          <h2>הגבלת אחריות</h2>
          <p>השימוש באתר ובתוכן נעשה באחריות המשתמש בלבד.</p>
          <p>הנהלת האתר, עובדיה וספקיה אינם אחראים לכל:</p>
          <ul>
            <li>נזק רפואי או בריאותי</li>
            <li>החמרת מצב</li>
            <li>תוצאה ישירה או עקיפה משימוש במידע</li>
          </ul>

          <div className="info-box">
            <h3>⚕️ לפני כל פעולה רפואית</h3>
            <p>יש לפנות לרופא מוסמך. המידע באתר אינו מחליף אבחנה, טיפול, או ייעוץ מקצועי.</p>
          </div>

        </div>

        <LegalNav active="medical" />

      </div>
      <div className="main-footer">Doctor Scribe AI · Medical Hub · כל הזכויות שמורות</div>
    </>
  )
}