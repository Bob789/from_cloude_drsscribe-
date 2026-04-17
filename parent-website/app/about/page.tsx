
import Link from 'next/link'
import '../community-theme.css'
import { FEATURES } from '@/lib/featureFlags'

export const metadata = {
  title: 'אודות | Medical Hub',
  description: 'Medical Hub — קהילה רפואית דיגיטלית בעברית. מאמרים מבוססי מדע, ידע נגיש ומהימן לכל אדם.',
  openGraph: {
    title: 'אודות | Medical Hub',
    description: 'קהילה רפואית דיגיטלית בעברית — ידע רפואי מהימן ונגיש לכולם.',
    url: 'https://medicalhub.co.il/about',
    type: 'website',
  },
}

export default function AboutPage() {
  return (
    <div className="about-page">

      {/* ── HERO ── */}
      <div className="about-hero">
        <div className="about-badge">
          <span className="about-badge-dot"></span>
          Medical Hub — קהילה רפואית דיגיטלית
        </div>
        <h1 className="about-hero-title">
          ידע רפואי <em>שייך לכולם</em>
        </h1>
        <p className="about-hero-sub">
          אנחנו בונים את הקהילה הרפואית המובילה בישראל — מקום שבו מטופלים<br />
          מקבלים מידע מהימן, ואנשי מקצוע חולקים ידע שמציל חיים.
        </p>
        <div className="about-hero-btns">
          <Link href="/articles" className="about-btn-gold">גלה מאמרים ←</Link>
          <Link href="/about-medscribe" className="about-btn-ghost">הכירו את Doctor Scribe AI</Link>
        </div>
      </div>

      {/* ── TITLE LINES ── */}
      <div className="com-title-lines">
        <div className="com-title-line"></div>
        <div className="com-title-line"></div>
      </div>

      {/* ── BODY ── */}
      <div className="about-body">

        {/* The Problem */}
        <div className="about-section-heading">
          <span className="about-section-icon">💡</span>
          <h2 className="about-section-title">למה הקמנו את Medical Hub</h2>
        </div>
        <p style={{ color: '#444', fontSize: 15, lineHeight: 1.85, marginBottom: 16, maxWidth: 720 }}>
          כל אחד מאיתנו מכיר את הרגע הזה: יוצאים מהרופא עם אבחנה, ומיד פותחים את הטלפון לחפש.
          מה שמוצאים לרוב — אתרים ישנים, מידע סותר, מאמרים שלא נכתבו על ידי רופאים, ופורומים
          שמלאים בפחדים ובעצות לא מקצועיות.
        </p>
        <p style={{ color: '#444', fontSize: 15, lineHeight: 1.85, marginBottom: 36, maxWidth: 720 }}>
          Medical Hub נוצרה כדי לתת מענה אחר. מקום אחד, בעברית, שבו כל מאמר נכתב באחריות,
          כל פיסת מידע מבוססת על ידע רפואי עדכני, וכל תוכן עובר בקרת איכות לפני שהוא מגיע אליכם.
          לא עוד חיפוש בין עשרות אתרים — מרכז ידע אחד שאפשר לסמוך עליו.
        </p>

        {/* What We Offer */}
        <div className="about-section-heading">
          <span className="about-section-icon">⚡</span>
          <h2 className="about-section-title">מה תמצאו כאן</h2>
        </div>
        <div className="about-features">
          {[
            { icon: '📚', title: 'מאמרים רפואיים מקצועיים', text: 'מאמרים בנושאי בריאות מגוונים — מקרדיולוגיה ועד תזונה — שנכתבים בשפה ברורה ונסמכים על מקורות רפואיים עדכניים.' },
            { icon: '🔍', title: 'חיפוש חכם ומדויק', text: 'מנוע חיפוש שמבין מונחים רפואיים בעברית ומוביל ישירות לתוכן הרלוונטי — בלי לשוטט.' },
            { icon: '🏷️', title: 'תיוג לפי תחום ומצב רפואי', text: 'כל מאמר מתויג לפי תחום, סימפטומים ומצבים רפואיים — כך שקל למצוא בדיוק את מה שמחפשים.' },
            ...(FEATURES.forum ? [{ icon: '💬', title: 'פורום קהילתי', text: 'מקום לשאול שאלות, לשתף ניסיון ולקבל מענה מקהילת המשתמשים ומאנשי מקצוע.' }] : []),
            ...(FEATURES.experts ? [{ icon: '👨‍⚕️', title: 'מומחים מאומתים', text: 'רופאים ומומחים שזהותם אומתה, זמינים לייעוץ מקצועי בתחומם.' }] : []),
            { icon: '🔒', title: 'פרטיות ושקיפות', text: 'אנחנו לא מוכרים נתונים אישיים, לא מציגים פרסומות ולא מקדמים מוצרים רפואיים. המידע כאן — בשבילכם.' },
          ].map(f => (
            <div key={f.title} className="about-feat-card">
              <div className="about-feat-icon">{f.icon}</div>
              <div className="about-feat-title">{f.title}</div>
              <div className="about-feat-text">{f.text}</div>
            </div>
          ))}
        </div>

        {/* Vision */}
        <div className="about-section-heading">
          <span className="about-section-icon">🔭</span>
          <h2 className="about-section-title">החזון שלנו</h2>
        </div>
        <p style={{ color: '#444', fontSize: 15, lineHeight: 1.85, marginBottom: 16, maxWidth: 720 }}>
          אנחנו מאמינים שבריאות טובה מתחילה בידע. כשמטופל מבין את המצב שלו,
          הוא מקבל החלטות טובות יותר, שואל שאלות חכמות יותר, ומנהל את הבריאות שלו באחריות.
        </p>
        <p style={{ color: '#444', fontSize: 15, lineHeight: 1.85, marginBottom: 36, maxWidth: 720 }}>
          Medical Hub נבנית כקהילה — לא רק כאתר מאמרים. המטרה היא ליצור מרחב שבו
          מטופלים, רופאים ואנשי מקצוע בתחום הבריאות יכולים להיפגש סביב ידע משותף.
          מרחב שבו שאלה טובה חשובה לא פחות מתשובה טובה, ושבו כל אדם מרגיש בטוח לחפש מידע.
        </p>

        {/* Values */}
        <div className="about-section-heading">
          <span className="about-section-icon">💎</span>
          <h2 className="about-section-title">הערכים שלנו</h2>
        </div>
        <div className="about-values">
          {[
            { icon: '🎓', title: 'דיוק ומהימנות', text: 'כל מאמר נבדק לפני פרסום. אנחנו מעדיפים לפרסם פחות — אבל נכון. מידע רפואי שגוי עלול לגרום נזק, ואנחנו לוקחים את זה ברצינות.' },
            { icon: '🤝', title: 'נגישות בלי תנאים', text: 'ידע רפואי הוא זכות, לא מותרות. כל התוכן ב-Medical Hub חינמי ופתוח — ללא רישום, ללא תשלום, ללא חסמים.' },
            { icon: '🌍', title: 'עברית קודם', text: 'רוב המידע הרפואי האיכותי קיים באנגלית בלבד. אנחנו מחזירים את הידע הזה לעברית — בשפה ברורה, לא מתנשאת ולא טכנית מדי.' },
            { icon: '❤️', title: 'אמפתיה דיגיטלית', text: 'מי שמחפש מידע רפואי לרוב חושש או חרד. אנחנו מקפידים על טון רגיש, שפה נקייה ותוכן שמרגיע — לא מפחיד.' },
          ].map(v => (
            <div key={v.title} className="about-value-card">
              <div className="about-value-icon">{v.icon}</div>
              <div className="about-value-title">{v.title}</div>
              <div className="about-value-text">{v.text}</div>
            </div>
          ))}
        </div>

        {/* Roadmap teaser */}
        <div className="about-section-heading">
          <span className="about-section-icon">🛤️</span>
          <h2 className="about-section-title">מה בדרך</h2>
        </div>
        <p style={{ color: '#444', fontSize: 15, lineHeight: 1.85, marginBottom: 12, maxWidth: 720 }}>
          Medical Hub נמצא בתחילת הדרך, וזה בדיוק הזמן להצטרף. הנה מה שאנחנו בונים:
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 36, maxWidth: 720 }}>
          {[
            { status: '✅', text: 'מאמרים רפואיים מקצועיים בעברית' },
            { status: '✅', text: 'חיפוש חכם לפי תחום וסימפטום' },
            { status: '🔜', text: 'פורום קהילתי עם מענה של רופאים' },
            { status: '🔜', text: 'ספריית מומחים מאומתים לפי תחום ואזור' },
            { status: '🔜', text: 'ניוזלטר שבועי — סיכום רפואי חכם' },
            { status: '🔜', text: 'אפליקציה ייעודית לנייד' },
          ].map(item => (
            <div key={item.text} style={{ display: 'flex', gap: 10, alignItems: 'center', fontSize: 14, color: '#333' }}>
              <span style={{ fontSize: 16, width: 24, textAlign: 'center' }}>{item.status}</span>
              <span>{item.text}</span>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="about-cta-box">
          <div className="about-cta-title">הצטרפו לקהילה</div>
          <div className="about-cta-sub">
            Medical Hub גדלה בזכות אנשים כמוכם — שמאמינים שידע רפואי מהימן צריך להיות נגיש לכולם.<br />
            גלו את המאמרים שלנו, שתפו עם מי שצריך, ועזרו לנו לבנות את הקהילה הרפואית הגדולה בישראל.
          </div>
          <div className="about-cta-btns">
            <Link href="/articles" className="about-btn-gold">גלו את המאמרים ←</Link>
            <Link href="/about-medscribe" className="about-btn-ghost">הכירו את הטכנולוגיה שמאחורי הקלעים</Link>
          </div>
        </div>

      </div>

      {/* Footer bar */}
      <div className="com-footer-bar">Medical Hub · קהילה רפואית דיגיטלית · כל הזכויות שמורות</div>

    </div>
  )
}
