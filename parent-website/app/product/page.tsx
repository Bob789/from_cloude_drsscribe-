import Link from 'next/link'
import './product-theme.css'

export const metadata = {
  title: 'Doctor Scribe AI — תמלול רפואי חכם | Medical Hub',
  description: 'מערכת SaaS לתמלול וסיכום אוטומטי של ביקורים רפואיים בעברית. לקליניקות פרטיות ורופאים עצמאיים.',
  openGraph: {
    title: 'Doctor Scribe AI — תמלול רפואי חכם',
    description: 'מערכת SaaS לתמלול וסיכום אוטומטי של ביקורים רפואיים בעברית',
    url: 'https://medicalhub.co.il/product',
    type: 'website',
  },
}

export default function AboutMedScribeAIPage() {
  return (
    <div id="product-page">

      {/* ══════════════════════════════════════
          HERO
      ══════════════════════════════════════ */}
      <div className="prod-hero">
        <img src="/logo.png" alt="Doctor Scribe AI" className="prod-hero-logo" />

        <div className="prod-hero-badge">
          <span className="prod-hero-badge-dot"></span>
          SaaS רפואי חכם — עכשיו בעברית
        </div>

        <h1 className="prod-hero-title">
          <em>Doctor Scribe AI</em>
        </h1>
        <p className="prod-hero-sub">
          מסיים את הבירוקרטיה הרפואית תוך דקות.<br />
          הקלטה → תמלול → סיכום — אוטומטי לחלוטין.
        </p>

        {/* Flow diagram */}
        <div className="prod-hero-flow">
          <div className="prod-flow-step">
            <span className="prod-flow-icon">🎤</span>
            <span className="prod-flow-label">הקלטה בדפדפן</span>
          </div>
          <span className="prod-flow-arrow">←</span>
          <div className="prod-flow-step">
            <span className="prod-flow-icon">🤖</span>
            <span className="prod-flow-label">תמלול Whisper</span>
          </div>
          <span className="prod-flow-arrow">←</span>
          <div className="prod-flow-step">
            <span className="prod-flow-icon">🧠</span>
            <span className="prod-flow-label">סיכום GPT-4</span>
          </div>
          <span className="prod-flow-arrow">←</span>
          <div className="prod-flow-step">
            <span className="prod-flow-icon">💾</span>
            <span className="prod-flow-label">שמירה בתיק</span>
          </div>
        </div>

        <div className="prod-hero-btns">
          <a href="https://app.drsscribe.com" className="prod-btn-primary">
            🚀 כניסה למערכת תמלול
          </a>
          <a href="#demo" className="prod-btn-ghost">
            📹 צפה בדמו
          </a>
        </div>
      </div>

      {/* ══════════════════════════════════════
          TRUST BAR
      ══════════════════════════════════════ */}
      <div className="prod-trust-bar">
        {[
          { n: '80%',   l: 'חיסכון בזמן תיעוד'    },
          { n: '3 דק׳', l: 'זמן סיכום ממוצע'       },
          { n: '98%+',  l: 'דיוק תמלול בעברית'     },
          { n: '8',     l: 'שפות נתמכות'           },
        ].map(s => (
          <div key={s.l} className="prod-trust-cell">
            <div className="prod-trust-n">{s.n}</div>
            <div className="prod-trust-l">{s.l}</div>
          </div>
        ))}
      </div>

      {/* ══════════════════════════════════════
          TITLE LINES
      ══════════════════════════════════════ */}
      <div className="prod-title-lines">
        <div className="prod-title-line"></div>
        <div className="prod-title-line"></div>
      </div>

      {/* ══════════════════════════════════════
          HOW IT WORKS
      ══════════════════════════════════════ */}
      <div className="prod-section">
        <div className="prod-section-heading">
          <span className="prod-section-icon">🔄</span>
          <div>
            <h2 className="prod-section-title">איך זה עובד?</h2>
            <p className="prod-section-sub">שלושה שלבים פשוטים — הכל אוטומטי ברקע</p>
          </div>
        </div>

        <div className="prod-steps">
          {[
            { num: '1', icon: '🎤', title: 'הקלטה במקליט', desc: 'רופא לוחץ "התחל הקלטה" בדפדפן. לא צריך אפליקציה, לא צריך מיקרופון חיצוני. הקול עובר ישירות לענן.' },
            { num: '2', icon: '🤖', title: 'תמלול + סיכום AI', desc: 'Whisper מתמלל בדיוק גבוה, GPT-4.1 יוצר סיכום רפואי מובנה עם תגיות אבחנה ותוכנית טיפול.' },
            { num: '3', icon: '💾', title: 'שמירה ועריכה', desc: 'הסיכום נשמר בתיק המטופל. ניתן לעריכה ידנית, ייצוא PDF, ושליחה ישירה למטופל.' },
          ].map(step => (
            <div key={step.num} className="prod-step">
              <div className="prod-step-num">{step.num}</div>
              <div className="prod-step-icon">{step.icon}</div>
              <h3 className="prod-step-title">{step.title}</h3>
              <p className="prod-step-desc">{step.desc}</p>
            </div>
          ))}
        </div>

        <div className="prod-timing-box">
          <div className="prod-timing-n">⏱️ זמן כולל: 7–15 דקות</div>
          <div className="prod-timing-l">תלוי באורך ההקלטה — כל העיבוד אוטומטי ברקע בזמן שהרופא מטפל בחולה הבא</div>
        </div>
      </div>

      {/* ══════════════════════════════════════
          SUMMARY FIELDS
      ══════════════════════════════════════ */}
      <div className="prod-section-alt">
        <div className="prod-section-alt-inner">
          <div className="prod-section-heading">
            <span className="prod-section-icon">📝</span>
            <div>
              <h2 className="prod-section-title">מה כולל הסיכום האוטומטי?</h2>
              <p className="prod-section-sub">6 שדות רפואיים מובנים — נוצרים אוטומטית מהשיחה</p>
            </div>
          </div>

          <div className="prod-fields">
            {[
              { label: 'תלונה עיקרית',  example: '"כאבי גב תחתון במשך שבועיים"' },
              { label: 'ממצאים',         example: '"טווח תנועה מוגבל, רגישות L4-L5"' },
              { label: 'אבחנה',          example: '"Lumbar strain / פציעת שרירי גב"' },
              { label: 'תוכנית טיפול',  example: '"מנוחה 3 ימים, אדביל 600mg x3"' },
              { label: 'המלצות',         example: '"לשוב בעוד שבוע אם לא חל שיפור"' },
              { label: 'דחיפות',         example: 'רגיל · דחוף · קריטי' },
            ].map(f => (
              <div key={f.label} className="prod-field-card">
                <div className="prod-field-label">{f.label}</div>
                <p className="prod-field-example">{f.example}</p>
              </div>
            ))}
          </div>
          <p className="prod-editable-note">✏️ כל השדות ניתנים לעריכה ידנית לפני שמירה</p>
        </div>
      </div>

      {/* ══════════════════════════════════════
          FEATURES
      ══════════════════════════════════════ */}
      <div className="prod-section">
        <div className="prod-section-heading">
          <span className="prod-section-icon">⭐</span>
          <div>
            <h2 className="prod-section-title">תכונות עיקריות</h2>
            <p className="prod-section-sub">כלים מקצועיים שמשנים את חוויית הרפואה</p>
          </div>
        </div>

        <div className="prod-features">
          {[
            { icon: '👥', title: 'ניהול מטופלים',   items: ['רשימת מטופלים + חיפוש מהיר', 'היסטוריית ביקורים מלאה', 'מפתח ראשי גמיש (ת"ז / טלפון / אימייל)'] },
            { icon: '🎙️', title: 'תמלול מתקדם',    items: ['זיהוי דוברים (רופא vs מטופל)', 'דיוק גבוה בעברית', 'עריכת תמלול ידנית'] },
            { icon: '🧠', title: 'AI חכם',            items: ['סיכום רפואי מובנה', 'נורמליזציה של אבחנות', 'חילוץ תגיות אוטומטי'] },
            { icon: '🔍', title: 'חיפוש מתקדם',     items: ['Full-text search', 'חיפוש סמנטי', 'סינון לפי תאריכים ותגיות'] },
            { icon: '🌍', title: '8 שפות',            items: ['עברית (RTL)', 'אנגלית, גרמנית, ספרדית', 'צרפתית, פורטוגזית, קוריאנית, איטלקית'] },
            { icon: '🔒', title: 'אבטחה ופרטיות',   items: ['הצפנת PII (AES-256)', 'Google OAuth + JWT', 'Audit log מלא'] },
          ].map(f => (
            <div key={f.title} className="prod-feat-card">
              <div className="prod-feat-icon">{f.icon}</div>
              <h3 className="prod-feat-title">{f.title}</h3>
              <ul className="prod-feat-list">
                {f.items.map(item => <li key={item}>{item}</li>)}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* ══════════════════════════════════════
          BENEFITS
      ══════════════════════════════════════ */}
      <div className="prod-section-alt">
        <div className="prod-section-alt-inner">
          <div className="prod-section-heading">
            <span className="prod-section-icon">💡</span>
            <div>
              <h2 className="prod-section-title">למה Doctor Scribe AI?</h2>
              <p className="prod-section-sub">היתרונות לשני הצדדים של השיחה הרפואית</p>
            </div>
          </div>

          <div className="prod-benefits">
            <div className="prod-benefit-card">
              <div className="prod-benefit-head">👨‍⚕️ לרופא</div>
              <ul className="prod-benefit-list">
                {[
                  'חיסכון 80% בזמן תיעוד',
                  'סיכומים מקצועיים ואחידים',
                  'חיפוש מהיר בכל הביקורים',
                  'גרפים וסטטיסטיקות מלאים',
                  'גישה מכל מקום — רק דפדפן',
                ].map(i => <li key={i}>{i}</li>)}
              </ul>
            </div>
            <div className="prod-benefit-card">
              <div className="prod-benefit-head">🤕 למטופל</div>
              <ul className="prod-benefit-list">
                {[
                  'יותר זמן פנים אל פנים עם הרופא',
                  'סיכום ברור ומובן לקחת הביתה',
                  'פרטיות מוגנת — הצפנה מלאה',
                  'גישה למידע רפואי מסודר',
                  'אין צורך לחזור על המידע',
                ].map(i => <li key={i}>{i}</li>)}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* ══════════════════════════════════════
          DEMO
      ══════════════════════════════════════ */}
      <div className="prod-section" id="demo">
        <div className="prod-section-heading">
          <span className="prod-section-icon">📹</span>
          <div>
            <h2 className="prod-section-title">צפה איך זה עובד</h2>
            <p className="prod-section-sub">הדגמה חיה של כל שלב בתהליך</p>
          </div>
        </div>
        <div className="prod-demo-box">
          <div className="prod-demo-icon">🎬</div>
          <div className="prod-demo-title">סרטון הדגמה</div>
          <div className="prod-demo-sub">ניתן להוסיף סרטון YouTube / Vimeo כאן</div>
        </div>
      </div>

      {/* ══════════════════════════════════════
          FINAL CTA
      ══════════════════════════════════════ */}
      <div className="prod-cta">
        <div className="prod-cta-tag">► התחל עכשיו — חינם</div>
        <h2 className="prod-cta-title">מוכן לסיים את הבירוקרטיה?</h2>
        <p className="prod-cta-sub">
          התחבר עם Google ותתחיל להשתמש במערכת התמלול תוך דקות.
          לא צריך כרטיס אשראי.
        </p>
        <div className="prod-cta-btns">
          <a href="https://app.drsscribe.com" className="prod-btn-primary">
            🚀 כניסה למערכת המלאה
          </a>
          <Link href="/articles" className="prod-btn-ghost">
            📚 קרא מאמרים רפואיים
          </Link>
        </div>
        <p className="prod-cta-note">💡 מצב דמו: 10 מטופלים + 10 דקות תמלול לכל מטופל</p>
      </div>

      <div className="prod-footer-bar">Doctor Scribe AI · Medical Hub · כל הזכויות שמורות</div>

    </div>
  )
}
