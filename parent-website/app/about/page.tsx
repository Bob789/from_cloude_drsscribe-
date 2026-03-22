
import Link from 'next/link'
import '../community-theme.css'

export const metadata = {
  title: 'אודות | Medical Hub',
  description: 'אודות Medical Hub — פלטפורמה רפואית מקיפה המשלבת מאמרים, פורום, מומחים ותמלול רפואי חכם.',
  openGraph: { title: 'אודות | Medical Hub', description: 'אודות Medical Hub', type: 'website' },
}

export default function AboutPage() {
  return (
    <div className="about-page">

      {/* ── HERO ── */}
      <div className="about-hero">
        <div className="about-badge">
          <span className="about-badge-dot"></span>
          Medical Hub — מרכז הידע הרפואי
        </div>
        <h1 className="about-hero-title">
          אנחנו <em>Medical Hub</em>
        </h1>
        <p className="about-hero-sub">
          פלטפורמה רפואית מקיפה המשלבת מאמרים מקצועיים, פורום קהילתי, מומחים מאומתים<br />
          ותמלול רפואי חכם — הכל במקום אחד, בעברית.
        </p>
        <div className="about-hero-btns">
          <Link href="/product" className="about-btn-gold">אודות Doctor Scribe AI ←</Link>
          <Link href="/articles" className="about-btn-ghost">גלה מאמרים</Link>
        </div>
      </div>

      {/* ── STATS STRIP ── */}
      <div className="about-stats-strip">
        {[
          { n: '12,000+', l: 'מאמרים רפואיים'   },
          { n: '48',      l: 'מומחים מאומתים'    },
          { n: '1,200+',  l: 'שאלות בפורום'      },
          { n: '8',       l: 'שפות נתמכות'        },
        ].map(s => (
          <div key={s.l} className="about-stat-cell">
            <div className="about-stat-n">{s.n}</div>
            <div className="about-stat-l">{s.l}</div>
          </div>
        ))}
      </div>

      {/* ── TITLE LINES ── */}
      <div className="com-title-lines">
        <div className="com-title-line"></div>
        <div className="com-title-line"></div>
      </div>

      {/* ── BODY ── */}
      <div className="about-body">

        {/* Mission */}
        <div className="about-section-heading">
          <span className="about-section-icon">🎯</span>
          <h2 className="about-section-title">המשימה שלנו</h2>
        </div>
        <p style={{ color: '#444', fontSize: 15, lineHeight: 1.75, marginBottom: 36, maxWidth: 720 }}>
          אנחנו מאמינים שכל אדם זכאי לגישה מהירה, מהימנה ופשוטה למידע רפואי איכותי.
          Medical Hub נוצרה כדי לגשר על הפער בין הרופא למטופל — ולהפוך את הידע הרפואי
          לנגיש, ברור ומדויק עבור כל מי שזקוק לו.
        </p>

        {/* Features */}
        <div className="about-section-heading">
          <span className="about-section-icon">⚡</span>
          <h2 className="about-section-title">מה תמצא כאן</h2>
        </div>
        <div className="about-features">
          {[
            { icon: '📚', title: 'מאמרים רפואיים',     text: 'מעל 12,000 מאמרים בנושאים רפואיים מגוונים, כתובים על ידי מומחים ומעודכנים באופן שוטף.' },
            { icon: '💬', title: 'פורום קהילתי',        text: 'שאל שאלות, שתף ניסיון וקבל מענה מרופאים ומומחים רפואיים תוך שעות ספורות.' },
            { icon: '👨‍⚕️', title: 'מומחים מאומתים',   text: '48 מומחים בתחומים שונים — מאורתופדיה ועד פסיכיאטריה — זמינים לייעוץ מקצועי.' },
            { icon: '🤖', title: 'תמלול רפואי חכם',    text: 'Doctor Scribe AI מתמלל ומסכם ביקורים רפואיים בדיוק מרבי, וחוסך שעות עבודה יקרות.' },
            { icon: '🌍', title: '8 שפות נתמכות',      text: 'ממשק מלא בעברית, אנגלית, ערבית, ועוד 5 שפות — כי בריאות לא מכירת גבולות.' },
            { icon: '🔒', title: 'פרטיות ואבטחה',      text: 'כל המידע הרפואי מוצפן ומאובטח בתקן הגבוה ביותר. אנחנו לא מוכרים נתונים אישיים.' },
          ].map(f => (
            <div key={f.title} className="about-feat-card">
              <div className="about-feat-icon">{f.icon}</div>
              <div className="about-feat-title">{f.title}</div>
              <div className="about-feat-text">{f.text}</div>
            </div>
          ))}
        </div>

        {/* Values */}
        <div className="about-section-heading">
          <span className="about-section-icon">💎</span>
          <h2 className="about-section-title">הערכים שלנו</h2>
        </div>
        <div className="about-values">
          {[
            { icon: '🎓', title: 'מהימנות מדעית', text: 'כל תוכן עובר בקרת איכות על ידי אנשי מקצוע. אנחנו לא מפרסמים מידע שאינו מבוסס ראיות.' },
            { icon: '🤝', title: 'נגישות לכולם',  text: 'ידע רפואי הוא זכות בסיסית. אנחנו מחויבים לשמור על הפלטפורמה חינמית ופתוחה לציבור הרחב.' },
            { icon: '⚡', title: 'חדשנות מתמדת',  text: 'אנחנו משלבים בינה מלאכותית מתקדמת כדי לשפר ולהאיץ את השירות שאנחנו מציעים.' },
            { icon: '❤️', title: 'אנשים קודם',    text: 'כל החלטה שאנחנו מקבלים — טכנולוגית, עיצובית או תוכנית — מתחילה ומסתיימת בשאלה: מה טוב למשתמש?' },
          ].map(v => (
            <div key={v.title} className="about-value-card">
              <div className="about-value-icon">{v.icon}</div>
              <div className="about-value-title">{v.title}</div>
              <div className="about-value-text">{v.text}</div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="about-cta-box">
          <div className="about-cta-title">מוכן להתחיל?</div>
          <div className="about-cta-sub">
            הצטרף לאלפי אנשים שכבר משתמשים ב-Medical Hub כדי לקבל מידע רפואי מהיר ומהימן.
          </div>
          <div className="about-cta-btns">
            <Link href="/forum" className="about-btn-gold">הצטרף לפורום ←</Link>
            <Link href="/experts" className="about-btn-ghost">מצא מומחה</Link>
          </div>
        </div>

      </div>

      {/* Footer bar */}
      <div className="com-footer-bar">Doctor Scribe AI · Medical Hub · כל הזכויות שמורות</div>

    </div>
  )
}
