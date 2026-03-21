'use client'

import { useEffect } from 'react'
import Link from 'next/link'

export default function HomePage() {
  // Stars rising animation handled globally in StarsCanvas (layout.tsx)

  // Scroll reveal
  useEffect(() => {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target as HTMLElement
          el.style.opacity = '1'
          el.style.transform = 'translateY(0)'
          el.style.transition = 'opacity 0.5s, transform 0.5s'
          observer.unobserve(el)
        }
      })
    }, { threshold: 0.1 })

    const elements = document.querySelectorAll('.hp .article-card, .hp .side-card, .hp .scribe-widget, .hp .editorial-box')
    elements.forEach(el => {
      const htmlEl = el as HTMLElement
      htmlEl.style.opacity = '0'
      htmlEl.style.transform = 'translateY(24px)'
      observer.observe(el)
    })

    return () => observer.disconnect()
  }, [])

  return (
    <div className="hp">
        {/* PAGE CONTENT */}
        <div className="page-wrap">
          <div className="block">

            {/* HERO */}
            <div className="hero">
              <div className="hero-badge">
                <span className="hero-dot"></span>
                מרכז הידע הרפואי המוביל בישראל
              </div>
              <h1 className="hero-title">
                כל הידע הרפואי<br />
                <span>במקום אחד</span>
              </h1>
              <p className="hero-sub">מאמרים מקצועיים, פורום פעיל עם מענה רופאים ורשימת מומחים — ידע רפואי מקצועי</p>
              <div className="hero-search">
                <input type="text" placeholder="חיפוש מאמרים, דיונים או מומחים..." />
                <button className="search-btn"><i className="fas fa-search"></i> חיפוש</button>
              </div>
              <div className="hero-stats">
                <div className="stat-item">
                  <div className="stat-num">150+</div>
                  <div className="stat-lbl">מאמרים מקצועיים</div>
                </div>
                <div className="stat-item">
                  <div className="stat-num">2,500+</div>
                  <div className="stat-lbl">דיונים בפורום</div>
                </div>
                <div className="stat-item">
                  <div className="stat-num">85</div>
                  <div className="stat-lbl">רופאים ומומחים</div>
                </div>
              </div>
            </div>

            <div className="title-lines">
              <div className="title-line"></div>
              <div className="title-line"></div>
            </div>

            {/* MAIN GRID */}
            <div className="main-grid">

              {/* ARTICLES COLUMN */}
              <div className="articles-col">
                <div className="section-label">
                  <div className="section-title">
                    <i className="fas fa-newspaper"></i> מאמרים אחרונים
                  </div>
                  <span className="section-badge">מגזין בריאות</span>
                </div>

                {/* Article 1 */}
                <article className="article-card">
                  <div className="card-inner">
                    <div className="card-icon">🦴</div>
                    <div className="card-body">
                      <div className="card-title">כאבי גב כרוניים – מדריך מקיף לאבחון וטיפול</div>
                      <div className="card-desc">סקירה עדכנית של גורמי כאב גב, שיטות אבחון, טיפול פיזיותרפי ותרופתי, ומתי מתייעצים לגבי ניתוח</div>
                      <div className="card-meta-row">
                        <span className="cat-badge" style={{color:'#2563eb',background:'rgba(37,99,235,0.1)',border:'1px solid rgba(37,99,235,0.25)'}}>אורתופדיה</span>
                        <span className="card-time">לפני 2 ימים · 4 דקות קריאה</span>
                      </div>
                      <Link href="#" className="read-btn">קרא עוד →</Link>
                    </div>
                  </div>
                </article>

                <div className="pipe art-pipe">
                  <div className="arch arch-right"></div>
                  <div className="pipe-lines"><div className="pipe-line"></div><div className="pipe-line"></div></div>
                  <div className="arch arch-left"></div>
                </div>

                {/* Article 2 */}
                <article className="article-card">
                  <div className="card-inner">
                    <div className="card-icon">❤️</div>
                    <div className="card-body">
                      <div className="card-title">יתר לחץ דם – טיפול ומענה בגיל 40+</div>
                      <div className="card-desc">מה כדאי לדעת על תזונה, פעילות גופנית ותרופות בניהול לחץ דם גבוה</div>
                      <div className="card-meta-row">
                        <span className="cat-badge" style={{color:'#e11d48',background:'rgba(225,29,72,0.1)',border:'1px solid rgba(225,29,72,0.25)'}}>קרדיולוגיה</span>
                        <span className="card-time">לפני 3 ימים · 5 דקות קריאה</span>
                      </div>
                      <Link href="#" className="read-btn">קרא עוד →</Link>
                    </div>
                  </div>
                </article>

                <div className="pipe art-pipe">
                  <div className="arch arch-right"></div>
                  <div className="pipe-lines"><div className="pipe-line"></div><div className="pipe-line"></div></div>
                  <div className="arch arch-left"></div>
                </div>

                {/* Article 3 */}
                <article className="article-card">
                  <div className="card-inner">
                    <div className="card-icon">🩸</div>
                    <div className="card-body">
                      <div className="card-title">סוכרת סוג 2 – מניעה, שליטה וחיים עם המחלה</div>
                      <div className="card-desc">הסבר מעמיק על ניהול סוכרת, תרופות עדכניות ואסטרטגיות תזונה מבוססות מחקר</div>
                      <div className="card-meta-row">
                        <span className="cat-badge" style={{color:'#d97706',background:'rgba(217,119,6,0.1)',border:'1px solid rgba(217,119,6,0.25)'}}>אנדוקרינולוגיה</span>
                        <span className="card-time">לפני שבוע · 8 דקות קריאה</span>
                      </div>
                      <Link href="#" className="read-btn">קרא עוד →</Link>
                    </div>
                  </div>
                </article>

                <div className="pipe art-pipe">
                  <div className="arch arch-right"></div>
                  <div className="pipe-lines"><div className="pipe-line"></div><div className="pipe-line"></div></div>
                  <div className="arch arch-left"></div>
                </div>

                {/* Article 4 */}
                <article className="article-card">
                  <div className="card-inner">
                    <div className="card-icon">😴</div>
                    <div className="card-body">
                      <div className="card-title">שינה בריאה – המדריך המלא לשיפור איכות השינה</div>
                      <div className="card-desc">היגיינת שינה, הפרעות נפוצות, טיפול CBT-I ומתי לפנות למעבדת שינה לאבחון מתקדם</div>
                      <div className="card-meta-row">
                        <span className="cat-badge" style={{color:'#7c3aed',background:'rgba(124,58,237,0.1)',border:'1px solid rgba(124,58,237,0.25)'}}>רפואת שינה</span>
                        <span className="card-time">לפני שבוע · 3 דקות קריאה</span>
                      </div>
                      <Link href="#" className="read-btn">קרא עוד →</Link>
                    </div>
                  </div>
                </article>

                <div className="pipe art-pipe">
                  <div className="arch arch-right"></div>
                  <div className="pipe-lines"><div className="pipe-line"></div><div className="pipe-line"></div></div>
                  <div className="arch arch-left"></div>
                </div>

                {/* Article 5 */}
                <article className="article-card">
                  <div className="card-inner">
                    <div className="card-icon">🥗</div>
                    <div className="card-body">
                      <div className="card-title">תזונה ים תיכונית – עדויות מדעיות ופרקטיקה</div>
                      <div className="card-desc">מה המחקר אומר על הדיאטה הים-תיכונית, מחלות לב, סוכרת ודמנציה</div>
                      <div className="card-meta-row">
                        <span className="cat-badge" style={{color:'#0d9488',background:'rgba(13,148,136,0.1)',border:'1px solid rgba(13,148,136,0.25)'}}>תזונה</span>
                        <span className="card-time">לפני 10 ימים · 7 דקות קריאה</span>
                      </div>
                      <Link href="#" className="read-btn">קרא עוד →</Link>
                    </div>
                  </div>
                </article>

                {/* Editorial box */}
                <div className="editorial-box">
                  <span className="ed-tag">✍️ מדורור רופא</span>
                  <div className="ed-title">רוצים לכתוב עבור Medical Hub?</div>
                  <div className="ed-text">אם אתם רופאים, אחיות או מטפלים מוסמכים, הצטרפו לצוות הכותבים שלנו ושתפו ידע מקצועי</div>
                  <Link href="/join-writers" className="ed-btn">להגשת מועמדות לכתיבה →</Link>
                </div>
              </div>

              {/* SIDEBAR */}
              <aside className="sidebar">

                {/* Doctor Scribe AI */}
                <div className="scribe-widget">
                  <span className="sponsored-tag">SPONSORED</span>
                  <div className="scribe-title">🎤 Doctor Scribe AI</div>
                  <div className="scribe-desc">המערכת החכמה לתמלול וסיכום ביקורים רפואיים בעברית. חוסכים 50% מזמן התיעוד</div>
                  <ul className="scribe-features">
                    <li>תמלול מדויק בעברית רפואית</li>
                    <li>סיכום אוטומטי לתיק הרפואי</li>
                    <li>הפקת הפניות ומכתבי שחרור</li>
                    <li>אבטחת מידע בתקן מחמיר</li>
                  </ul>
                  <Link href="/product" className="scribe-btn">נסו חינם ל-14 יום</Link>
                  <div className="scribe-sub">אין צורך בכרטיס אשראי</div>
                </div>

                {/* Experts */}
                <div className="side-card">
                  <div className="side-title">🩺 מומחים מובילים</div>
                  <div className="expert-list">
                    <div className="expert-row">
                      <div className="expert-avatar">D</div>
                      <div>
                        <div className="expert-name">ד&quot;ר דניאל כהן</div>
                        <div className="expert-spec">אורתופדיה • תל אביב</div>
                      </div>
                    </div>
                    <div className="expert-row">
                      <div className="expert-avatar">M</div>
                      <div>
                        <div className="expert-name">פרופ׳ מרים לוי</div>
                        <div className="expert-spec">נוירולוגיה • ירושלים</div>
                      </div>
                    </div>
                    <div className="expert-row">
                      <div className="expert-avatar">S</div>
                      <div>
                        <div className="expert-name">ד&quot;ר שרה אברמוביץ</div>
                        <div className="expert-spec">קרדיולוגיה • חיפה</div>
                      </div>
                    </div>
                    <div className="expert-row">
                      <div className="expert-avatar">Y</div>
                      <div>
                        <div className="expert-name">ד&quot;ר יוסי מזרחי</div>
                        <div className="expert-spec">אנדוקרינולוגיה • ת&quot;א</div>
                      </div>
                    </div>
                  </div>
                  <Link href="/experts" className="side-link">לכל המומחים →</Link>
                </div>

                {/* Forum hot topics */}
                <div className="side-card">
                  <div className="side-title">💬 חם בפורום</div>
                  <div className="forum-list">
                    <div className="forum-row">
                      <div className="forum-q">כאב גב תחתון אחרי אימון</div>
                      <div className="forum-meta">
                        <span className="forum-replies">12 תגובות</span>
                        <span className="dr-badge">רופא השיב</span>
                      </div>
                    </div>
                    <div className="forum-row">
                      <div className="forum-q">האם צריך MRI לכאבי ראש?</div>
                      <div className="forum-meta">
                        <span className="forum-replies">7 תגובות</span>
                      </div>
                    </div>
                    <div className="forum-row">
                      <div className="forum-q">תופעות לוואי של מטפורמין</div>
                      <div className="forum-meta">
                        <span className="forum-replies">15 תגובות</span>
                        <span className="dr-badge">רופא השיב</span>
                      </div>
                    </div>
                    <div className="forum-row">
                      <div className="forum-q">נדודי שינה כרוניים - עזרה</div>
                      <div className="forum-meta">
                        <span className="forum-replies">31 תגובות</span>
                      </div>
                    </div>
                    <div className="forum-row">
                      <div className="forum-q">שיטות להפחתת לחץ דם</div>
                      <div className="forum-meta">
                        <span className="forum-replies">18 תגובות</span>
                        <span className="dr-badge">רופא השיב</span>
                      </div>
                    </div>
                  </div>
                  <Link href="/forum" className="side-link">לפורום המלא →</Link>
                </div>

              </aside>
            </div>

            {/* BOTTOM CTA */}
            <div className="bottom-cta">
              <div className="cta-eyebrow">DOCTOR SCRIBE AI</div>
              <h2 className="cta-title">אתם מטפלים —<br /><span>ה-AI כותב</span></h2>
              <p className="cta-sub">תמלול וסיכום אוטומטי של ביקורים רפואיים בעברית. לקליניקות פרטיות ורופאים עצמאיים</p>
              <div className="cta-btns">
                <Link href="/product" className="cta-primary">התחילו ניסיון חינם</Link>
                <Link href="/product" className="cta-ghost">דמו אונליין</Link>
              </div>
            </div>

          </div>
        </div>

      </div>
  )
}
