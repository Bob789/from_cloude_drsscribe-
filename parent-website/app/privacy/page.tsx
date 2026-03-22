import Link from 'next/link'
import '../articles/article-theme.css'

export const metadata = {
  title: 'מדיניות פרטיות | Medical Hub',
  description: 'מדיניות הפרטיות של Medical Hub ו-Doctor Scribe AI — הגנה על מידע אישי ונתוני Google.',
  openGraph: {
    title: 'מדיניות פרטיות | Medical Hub',
    description: 'מדיניות הפרטיות של Medical Hub ו-Doctor Scribe AI, כולל הצהרת שימוש ב-Google API.',
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

export default function PrivacyPage() {
  return (
    <>
      <div className="article-block">

        <div className="page-header-bar">
          <Link href="/" className="back-btn">→</Link>
          <div>
            <div className="page-title">Medical Hub · מדיניות פרטיות</div>
            <div className="page-subtitle">עדכון אחרון: פברואר 2026</div>
          </div>
        </div>

        <div className="title-lines">
          <div className="title-line"></div>
          <div className="title-line"></div>
        </div>

        <div className="article-hero">
          <span className="hero-badge">מסמך משפטי</span>
          <h1 className="hero-title">מדיניות פרטיות</h1>
          <p className="hero-subtitle">הגנה על מידע אישי ופרטיות המשתמשים — המידע שאנו אוספים וכיצד אנו משתמשים בו</p>
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

          <div className="info-box">
            <h3>🔑 הצהרת שימוש ב-Google API</h3>
            <p>השימוש ב-Doctor Scribe AI במידע שהתקבל מ-Google APIs יעמוד בדרישות מדיניות נתוני המשתמש של Google, כולל דרישות השימוש המוגבל. אנו לא מוכרים, לא מעבירים ולא משתמשים בנתוני Google לצרכי פרסום. הגישה לנתוני Google (כגון כתובת מייל ופרופיל) משמשת אך ורק לצורך אימות מזהות המשתמש.</p>
          </div>

          <h2>1. מבוא</h2>
          <p>Medical Hub ו-Doctor Scribe AI מחויבים לשמירה על פרטיות המשתמשים. מדיניות זו מפרטת כיצד אנו אוספים, משתמשים ומגנים על המידע האישי שלך.</p>

          <h2>2. המידע שאנו אוספים</h2>
          <ul>
            <li>פרטי חשבון: שם, כתובת מייל, תפקיד מקצועי</li>
            <li>נתוני Google OAuth: מזהה ייחודי, שם תצוגה, כתובת מייל</li>
            <li>תוכן מקצועי: הקלטות, תמלולים וסיכומים שנוצרו בשירות</li>
            <li>נתוני שימוש: עמודים שנצפו, פעולות בממשק</li>
            <li>נתונים טכניים: כתובת IP, סוג דפדפן</li>
          </ul>

          <h2>3. מטרות השימוש במידע</h2>
          <ul>
            <li>מתן השירות והפעלתו התקינה</li>
            <li>אימות זהות המשתמש ואבטחת החשבון</li>
            <li>שיפור השירות ופיתוח תכונות חדשות</li>
            <li>תמיכה טכנית ומענה לפניות</li>
          </ul>

          <h2>4. מידע רפואי ורגיש</h2>
          <p>תוכן רפואי (הקלטות, תמלולים, סיכומי מפגשים) מוצפן ב-AES-256 ומאוחסן בבידוד מלא. אנו לא מוכרים ולא משתפים מידע רפואי עם צדדים שלישיים ללא הסכמה מפורשת.</p>

          <h2>5. צדדים שלישיים</h2>
          <ul>
            <li>Google OAuth — אימות זהות בלבד</li>
            <li>OpenAI / Whisper — עיבוד תמלול וסיכום (בכפוף להסכם עיבוד נתונים)</li>
            <li>ספקי תשתית — אחסון וגיבוי מאובטח</li>
          </ul>
          <p>אנו לא מוכרים מידע אישי לצדדים שלישיים לצורכי פרסום.</p>

          <h2>6. אבטחת מידע</h2>
          <p>מידע אישי מוגן באמצעות הצפנת TLS 1.3 בתעבורה ו-AES-256 באחסון. גישה למידע מוגבלת לעובדים המורשים בלבד, ומבוקרת ב-Audit Log.</p>

          <h2>7. עוגיות (Cookies)</h2>
          <p>אנו משתמשים ב-Cookies לצורך ניהול סשן, העדפות שפה ואנליטיקה בסיסית. ניתן לנהל עוגיות דרך הגדרות הדפדפן שלך.</p>

          <h2>8. זכויות המשתמש</h2>
          <ul>
            <li>גישה למידע האישי — בכל עת לפי בקשה</li>
            <li>תיקון מידע שגוי</li>
            <li>מחיקת החשבון וכל הנתונים</li>
            <li>ייצוא הנתונים בפורמט נגיש</li>
          </ul>

          <h2>9. שמירת מידע</h2>
          <p>מידע משתמש נשמר כל עוד החשבון פעיל. לאחר בקשת מחיקה, המידע יוסר תוך 30 יום, למעט מידע הנדרש לצרכים משפטיים.</p>

          <h2>10. יצירת קשר</h2>
          <p>לשאלות בנושא פרטיות: <a href="mailto:privacy@medicalhub.co.il">privacy@medicalhub.co.il</a></p>

        </div>

        <LegalNav active="privacy" />

      </div>
      <div className="main-footer">Doctor Scribe AI · Medical Hub · כל הזכויות שמורות</div>
    </>
  )
}