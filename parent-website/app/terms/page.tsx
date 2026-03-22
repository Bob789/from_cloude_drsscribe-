import Link from 'next/link'
import '../articles/article-theme.css'

export const metadata = {
  title: 'תנאי שימוש | Medical Hub',
  description: 'תנאי השימוש של Medical Hub ו-Doctor Scribe AI — תנאים והגבלות לשימוש בשירות.',
  openGraph: {
    title: 'תנאי שימוש | Medical Hub',
    description: 'תנאי השימוש של Medical Hub ו-Doctor Scribe AI',
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

export default function TermsPage() {
  return (
    <>
      <div className="article-block">

        <div className="page-header-bar">
          <Link href="/" className="back-btn">→</Link>
          <div>
            <div className="page-title">Medical Hub · תנאי שימוש</div>
            <div className="page-subtitle">עדכון אחרון: פברואר 2026</div>
          </div>
        </div>

        <div className="title-lines">
          <div className="title-line"></div>
          <div className="title-line"></div>
        </div>

        <div className="article-hero">
          <span className="hero-badge">מסמך משפטי</span>
          <h1 className="hero-title">תנאי שימוש</h1>
          <p className="hero-subtitle">תנאי השימוש של Medical Hub ו-Doctor Scribe AI — אנא קראו בעיון לפני השימוש בשירות</p>
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

          <h2>1. הסכמה לתנאים</h2>
          <p>השימוש באתר Doctor Scribe ובשירותי Medical Hub (להלן: "השירות") מהווה הסכמה מלאה לתנאי שימוש אלה. אם אינך מסכים לתנאים, הנך מתבקש להימנע משימוש בשירות. הנהלת האתר רשאית לעדכן תנאים אלה מעת לעת, והשימוש לאחר עדכון מהווה הסכמה לתנאים המעודכנים.</p>

          <h2>2. תיאור השירות</h2>
          <p>השירות כולל:</p>
          <ul>
            <li>פלטפורמת תוכן רפואי (מאמרים, מידע מקצועי ופורומים)</li>
            <li>מערכת תמלול וסיכום אוטומטי של מפגשים רפואיים (Doctor Scribe AI)</li>
          </ul>
          <p>השירות ניתן לצורכי עזר בלבד ואינו מחליף שיקול דעת מקצועי של גורם רפואי מוסמך.</p>

          <h2>3. שימוש רפואי – הבהרה</h2>
          <p>המידע המוצג באתר אינו מהווה ייעוץ רפואי, אבחנה או טיפול. אין להסתמך על המידע לצורך קבלת החלטות רפואיות. כל החלטה רפואית חייבת להתבצע בהתייעצות עם רופא מוסמך.</p>

          <h2>4. חשבון משתמש</h2>
          <p>בעת הרשמה לשירות:</p>
          <ul>
            <li>המשתמש אחראי לשמירת סודיות פרטי ההתחברות</li>
            <li>חל איסור להעביר או לשתף חשבון עם אחרים</li>
            <li>יש לספק מידע נכון, מדויק ומעודכן</li>
            <li>השימוש מותר למשתמשים מעל גיל 18 בלבד</li>
          </ul>

          <h2>5. שימוש מותר ואסור</h2>
          <h3>שימוש מותר:</h3>
          <ul>
            <li>שימוש אישי ולגיטימי בשירות</li>
            <li>פרסום תוכן ענייני ומבוסס</li>
            <li>השתתפות בפורומים ושאלות</li>
          </ul>
          <h3>שימוש אסור:</h3>
          <ul>
            <li>פרסום מידע רפואי שגוי או מטעה</li>
            <li>הפצת ספאם או תוכן פרסומי ללא אישור</li>
            <li>הטרדה, פגיעה או הפרת זכויות אחרים</li>
            <li>שימוש מסחרי ללא אישור מראש ובכתב</li>
          </ul>

          <h2>6. קניין רוחני</h2>
          <p>כל זכויות הקניין הרוחני באתר, לרבות טקסטים, עיצוב, קוד ומערכות, שייכות ל-Medical Hub. אין להעתיק, להפיץ, לשכפל או לעשות שימוש מסחרי ללא אישור מפורש בכתב.</p>

          <h2>7. הגבלת אחריות</h2>
          <p>השירות ניתן "כפי שהוא" (AS-IS). הנהלת האתר אינה אחראית לכל נזק ישיר או עקיף, לרבות:</p>
          <ul>
            <li>הסתמכות על מידע רפואי</li>
            <li>תקלות טכנולוגיות</li>
            <li>שימוש במערכות AI</li>
          </ul>
          <p>האחריות לשימוש במידע היא על המשתמש בלבד.</p>

          <h2>8. הפסקת שירות וסגירת חשבון</h2>
          <p>הנהלת האתר רשאית:</p>
          <ul>
            <li>להשעות או לסגור חשבון במקרה של הפרת תנאים</li>
            <li>להגביל גישה לשירות לפי שיקול דעתה</li>
          </ul>
          <p>המשתמש רשאי להפסיק שימוש בכל עת.</p>

          <h2>9. יצירת קשר</h2>
          <p>לשאלות או בירורים: <a href="mailto:legal@medicalhub.co.il">legal@medicalhub.co.il</a></p>

        </div>

        <LegalNav active="terms" />

      </div>
      <div className="main-footer">Doctor Scribe AI · Medical Hub · כל הזכויות שמורות</div>
    </>
  )
}