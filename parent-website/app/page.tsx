'use client'

import Link from 'next/link'
import './homepage.css'

export default function MedicalHub() {
  return (
    <div className="hp-wrapper">
      {/* TOP BAR */}
      <div className="hp-top-bar">
        <Link href="/product">חדש: תמלול רפואי אוטומטי לקליניקות — Doctor Scribe AI ←</Link>
      </div>

      {/* HEADER */}
      <header className="hp-header">
        <div className="hp-header-inner">
          <Link href="/" className="hp-brand">
            <div className="hp-logo-circle">MH</div>
            <div>
              <div className="hp-brand-name">MedicalHub</div>
              <div className="hp-brand-sub">מאמרים • פורום • מומחים</div>
            </div>
          </Link>
          <nav className="hp-nav">
            <Link href="/" className="hp-nav-link">דף הבית</Link>
            <Link href="/articles" className="hp-nav-link">מאמרים</Link>
            <Link href="/forum" className="hp-nav-link">פורום</Link>
            <Link href="/experts" className="hp-nav-link">מומחים</Link>
            <Link href="/about" className="hp-nav-link">אודות</Link>
            <Link href="/login" className="hp-btn hp-btn-login">התחברות</Link>
            <Link href="/product" className="hp-btn hp-btn-cta">Doctor Scribe AI</Link>
          </nav>
        </div>
      </header>

      {/* PAGE CONTENT */}
      <div className="hp-page-wrap">
        <div className="hp-block">

          {/* HERO */}
          <div className="hp-hero">
            <div className="hp-hero-badge">
              <span className="hp-hero-dot" />
              מרכז הידע הרפואי המוביל בישראל
            </div>
            <h1 className="hp-hero-title">
              כל הידע הרפואי<br />
              <span>במקום אחד</span>
            </h1>
            <p className="hp-hero-sub">מאמרים מקצועיים, פורום פעיל עם מענה רופאים ורשימת מומחים — ידע רפואי מקצועי</p>
            <div className="hp-hero-search">
              <input type="text" placeholder="חיפוש מאמרים, דיונים או מומחים..." />
              <button className="hp-search-btn">🔍 חיפוש</button>
            </div>
            <div className="hp-hero-stats">
              <div className="hp-stat"><div className="hp-stat-num">150+</div><div className="hp-stat-lbl">מאמרים מקצועיים</div></div>
              <div className="hp-stat"><div className="hp-stat-num">2,500+</div><div className="hp-stat-lbl">דיונים בפורום</div></div>
              <div className="hp-stat"><div className="hp-stat-num">85</div><div className="hp-stat-lbl">רופאים ומומחים</div></div>
            </div>
          </div>

          <div className="hp-title-lines"><div className="hp-title-line" /><div className="hp-title-line" /></div>

          {/* MAIN GRID */}
          <div className="hp-main-grid">

            {/* ARTICLES COLUMN */}
            <div className="hp-articles-col">
              <div className="hp-section-label">
                <div className="hp-section-title">📰 מאמרים אחרונים</div>
                <span className="hp-section-badge">מגזין בריאות</span>
              </div>

              {[
                { icon: '🦴', title: 'כאבי גב כרוניים – מדריך מקיף לאבחון וטיפול', desc: 'סקירה עדכנית של גורמי כאב גב, שיטות אבחון, טיפול פיזיותרפי ותרופתי, ומתי מתייעצים לגבי ניתוח', cat: 'אורתופדיה', catColor: '#2563eb', time: 'לפני 2 ימים · 4 דקות קריאה' },
                { icon: '❤️', title: 'יתר לחץ דם – טיפול ומענה בגיל 40+', desc: 'מה כדאי לדעת על תזונה, פעילות גופנית ותרופות בניהול לחץ דם גבוה', cat: 'קרדיולוגיה', catColor: '#e11d48', time: 'לפני 3 ימים · 5 דקות קריאה' },
                { icon: '🩸', title: 'סוכרת סוג 2 – מניעה, שליטה וחיים עם המחלה', desc: 'הסבר מעמיק על ניהול סוכרת, תרופות עדכניות ואסטרטגיות תזונה מבוססות מחקר', cat: 'אנדוקרינולוגיה', catColor: '#d97706', time: 'לפני שבוע · 8 דקות קריאה' },
                { icon: '😴', title: 'שינה בריאה – המדריך המלא לשיפור איכות השינה', desc: 'היגיינת שינה, הפרעות נפוצות, טיפול CBT-I ומתי לפנות למעבדת שינה לאבחון מתקדם', cat: 'רפואת שינה', catColor: '#7c3aed', time: 'לפני שבוע · 3 דקות קריאה' },
                { icon: '🥗', title: 'תזונה ים תיכונית – עדויות מדעיות ופרקטיקה', desc: 'מה המחקר אומר על הדיאטה הים-תיכונית, מחלות לב, סוכרת ודמנציה', cat: 'תזונה', catColor: '#0d9488', time: 'לפני 10 ימים · 7 דקות קריאה' },
              ].map((a, i) => (
                <div key={i}>
                  {i > 0 && (
                    <div className="hp-pipe hp-art-pipe">
                      <div className="hp-arch hp-arch-right" />
                      <div className="hp-pipe-lines"><div className="hp-pipe-line" /><div className="hp-pipe-line" /></div>
                      <div className="hp-arch hp-arch-left" />
                    </div>
                  )}
                  <article className="hp-article-card">
                    <div className="hp-card-inner">
                      <div className="hp-card-icon">{a.icon}</div>
                      <div className="hp-card-body">
                        <div className="hp-card-title">{a.title}</div>
                        <div className="hp-card-desc">{a.desc}</div>
                        <div className="hp-card-meta-row">
                          <span className="hp-cat-badge" style={{ color: a.catColor, background: `${a.catColor}18`, border: `1px solid ${a.catColor}40` }}>{a.cat}</span>
                          <span className="hp-card-time">{a.time}</span>
                        </div>
                        <Link href="/articles" className="hp-read-btn">קרא עוד →</Link>
                      </div>
                    </div>
                  </article>
                </div>
              ))}

              {/* Editorial box */}
              <div className="hp-editorial-box">
                <span className="hp-ed-tag">✍️ מדורור רופא</span>
                <div className="hp-ed-title">רוצים לכתוב עבור Medical Hub?</div>
                <div className="hp-ed-text">אם אתם רופאים, אחיות או מטפלים מוסמכים, הצטרפו לצוות הכותבים שלנו ושתפו ידע מקצועי</div>
                <Link href="/join-writers" className="hp-ed-btn">להגשת מועמדות לכתיבה →</Link>
              </div>
            </div>

            {/* SIDEBAR */}
            <aside className="hp-sidebar">

              {/* Doctor Scribe AI */}
              <div className="hp-scribe-widget">
                <span className="hp-sponsored-tag">SPONSORED</span>
                <div className="hp-scribe-title">🎤 Doctor Scribe AI</div>
                <div className="hp-scribe-desc">המערכת החכמה לתמלול וסיכום ביקורים רפואיים בעברית. חוסכים 50% מזמן התיעוד</div>
                <ul className="hp-scribe-features">
                  <li>תמלול מדויק בעברית רפואית</li>
                  <li>סיכום אוטומטי לתיק הרפואי</li>
                  <li>הפקת הפניות ומכתבי שחרור</li>
                  <li>אבטחת מידע בתקן מחמיר</li>
                </ul>
                <Link href="/product" className="hp-scribe-btn">נסו חינם ל-14 יום</Link>
                <div className="hp-scribe-sub">אין צורך בכרטיס אשראי</div>
              </div>

              {/* Experts */}
              <div className="hp-side-card">
                <div className="hp-side-title">🩺 מומחים מובילים</div>
                <div className="hp-expert-list">
                  {[
                    { init: 'D', name: 'ד"ר דניאל כהן', spec: 'אורתופדיה • תל אביב' },
                    { init: 'M', name: 'פרופ׳ מרים לוי', spec: 'נוירולוגיה • ירושלים' },
                    { init: 'S', name: 'ד"ר שרה אברמוביץ', spec: 'קרדיולוגיה • חיפה' },
                    { init: 'Y', name: 'ד"ר יוסי מזרחי', spec: 'אנדוקרינולוגיה • ת"א' },
                  ].map(e => (
                    <div key={e.init} className="hp-expert-row">
                      <div className="hp-expert-avatar">{e.init}</div>
                      <div><div className="hp-expert-name">{e.name}</div><div className="hp-expert-spec">{e.spec}</div></div>
                    </div>
                  ))}
                </div>
                <Link href="/experts" className="hp-side-link">לכל המומחים →</Link>
              </div>

              {/* Forum */}
              <div className="hp-side-card">
                <div className="hp-side-title">💬 חם בפורום</div>
                <div className="hp-forum-list">
                  {[
                    { q: 'כאב גב תחתון אחרי אימון', replies: 12, dr: true },
                    { q: 'האם צריך MRI לכאבי ראש?', replies: 7, dr: false },
                    { q: 'תופעות לוואי של מטפורמין', replies: 15, dr: true },
                    { q: 'נדודי שינה כרוניים - עזרה', replies: 31, dr: false },
                    { q: 'שיטות להפחתת לחץ דם', replies: 18, dr: true },
                  ].map((f, i) => (
                    <div key={i} className="hp-forum-row">
                      <div className="hp-forum-q">{f.q}</div>
                      <div className="hp-forum-meta">
                        <span className="hp-forum-replies">{f.replies} תגובות</span>
                        {f.dr && <span className="hp-dr-badge">רופא השיב</span>}
                      </div>
                    </div>
                  ))}
                </div>
                <Link href="/forum" className="hp-side-link">לפורום המלא →</Link>
              </div>
            </aside>
          </div>

          {/* BOTTOM CTA */}
          <div className="hp-bottom-cta">
            <div className="hp-cta-eyebrow">DOCTOR SCRIBE AI</div>
            <h2 className="hp-cta-title">אתם מטפלים —<br /><span>ה-AI כותב</span></h2>
            <p className="hp-cta-sub">תמלול וסיכום אוטומטי של ביקורים רפואיים בעברית. לקליניקות פרטיות ורופאים עצמאיים</p>
            <div className="hp-cta-btns">
              <Link href="/product" className="hp-cta-primary">התחילו ניסיון חינם</Link>
              <Link href="/product" className="hp-cta-ghost">דמו אונליין</Link>
            </div>
          </div>

        </div>
      </div>

      {/* FOOTER */}
      <footer className="hp-footer">
        <div className="hp-footer-logo">MedicalHub</div>
        <div className="hp-footer-links">
          <Link href="/articles">מאמרים</Link>
          <Link href="/forum">פורום</Link>
          <Link href="/experts">מומחים</Link>
          <Link href="/product">Doctor Scribe AI</Link>
          <Link href="/privacy-policy">פרטיות</Link>
          <Link href="/terms">תנאי שימוש</Link>
        </div>
        <div className="hp-footer-copy">© 2026 Medical Hub</div>
      </footer>
    </div>
  )
}
