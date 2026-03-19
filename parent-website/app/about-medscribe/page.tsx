import Link from 'next/link'
import Header from '@/components/Header'

export const metadata = {
  title: 'MedScribe AI — תמלול רפואי חכם | Medical Hub',
  description: 'מערכת SaaS לתמלול וסיכום אוטומטי של ביקורים רפואיים בעברית. לקליניקות פרטיות ורופאים עצמאיים.',
  openGraph: {
    title: 'MedScribe AI — תמלול רפואי חכם',
    description: 'מערכת SaaS לתמלול וסיכום אוטומטי של ביקורים רפואיים בעברית',
    url: 'https://medicalhub.co.il/about-medscribe',
    type: 'website',
  },
}

export default function AboutMedScribePage() {
  return (
    <>
      <Header page="about" />

      {/* Hero */}
      <div className="hero" style={{ maxWidth: 1200, margin: '0 auto', padding: '48px 20px', textAlign: 'center' }}>
        <img src="/logo.png" alt="MedScribe AI" width={160} height={160} className="logo-animated" style={{ margin: '0 auto 32px', display: 'block' }} />
        <h2 style={{ fontSize: 56, fontWeight: 700, marginBottom: 24, background: 'linear-gradient(to left, #22d3ee, #3b82f6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
          MedScribe AI
        </h2>
        <p style={{ fontSize: 28, fontWeight: 600, marginBottom: 16 }}>מערכת SaaS לתמלול וסיכום אוטומטי</p>
        <p style={{ fontSize: 24, color: 'var(--muted)', marginBottom: 0 }}>של ביקורים רפואיים בעברית</p>

        <div style={{ maxWidth: 900, margin: '32px auto', padding: 32, borderRadius: 24, border: '1px solid rgba(56,189,248,0.3)', background: 'rgba(18,26,51,0.5)' }}>
          <p style={{ fontSize: 18, color: 'var(--muted)', lineHeight: 1.8 }}>
            רופא מקליט את השיחה עם המטופל בזמן אמת{' '}
            <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>→</span>{' '}
            המערכת מתמללת אוטומטית{' '}
            <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>→</span>{' '}
            יוצרת סיכום רפואי מובנה{' '}
            <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>→</span>{' '}
            שומרת בתיק המטופל
          </p>
        </div>

        <div style={{ marginTop: 32, display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
          <a href={process.env.NEXT_PUBLIC_MEDSCRIBE_URL || 'http://localhost:3000'} className="btn btn-primary" style={{ padding: '16px 40px', fontSize: 20 }}>
            🚀 כניסה למערכת המלאה
          </a>
          <a href="#demo" className="btn btn-secondary" style={{ padding: '16px 40px', fontSize: 20 }}>
            📹 צפה בדמו
          </a>
        </div>
      </div>

      {/* How It Works */}
      <div className="section">
        <h2 className="section-title">איך זה עובד? 🔄</h2>
        <div className="steps-grid">
          {[
            { num: '1', icon: '🎤', title: 'הקלטה', desc: 'רופא מקליט את השיחה עם המטופל ישירות מהדפדפן. לא צריך אפליקציה.' },
            { num: '2', icon: '🤖', title: 'תמלול + סיכום', desc: 'Whisper API מתמלל את השיחה, GPT-4.1 יוצר סיכום רפואי מובנה עם תגיות אבחנה.' },
            { num: '3', icon: '💾', title: 'שמירה', desc: 'הסיכום נשמר בתיק המטופל, ניתן לעריכה ולייצוא ל-PDF.' },
          ].map((step) => (
            <div key={step.num} className="step-card">
              <div className="step-number">{step.num}</div>
              <div className="step-icon">{step.icon}</div>
              <h3 className="step-title">{step.title}</h3>
              <p className="step-desc">{step.desc}</p>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 32, padding: 32, borderRadius: 24, border: '1px dashed rgba(56,189,248,0.5)', background: 'rgba(56,189,248,0.05)', textAlign: 'center' }}>
          <p style={{ fontSize: 20, fontWeight: 600, marginBottom: 8, color: '#e0f2fe' }}>⏱️ זמן כולל: 7-15 דקות</p>
          <p style={{ color: 'var(--muted)' }}>(תלוי באורך ההקלטה - כל העיבוד אוטומטי ברקע)</p>
        </div>
      </div>

      {/* Summary Fields */}
      <div className="section">
        <h2 className="section-title">מה כולל הסיכום האוטומטי? 📝</h2>
        <div className="summary-grid">
          <div className="fields-grid">
            {[
              { label: 'תלונה עיקרית', example: '"כאבי גב תחתון במשך שבועיים"' },
              { label: 'ממצאים', example: '"טווח תנועה מוגבל, רגישות L4-L5"' },
              { label: 'אבחנה', example: '"Lumbar strain / פציעת שרירי גב"' },
              { label: 'תוכנית טיפול', example: '"מנוחה 3 ימים, אדביל 600mg x3"' },
              { label: 'המלצות', example: '"לשוב בעוד שבוע אם לא חל שיפור"' },
              { label: 'דחיפות', example: 'רגיל / דחוף / קריטי' },
            ].map((field) => (
              <div key={field.label} className="summary-field">
                <div className="summary-field-label">{field.label}</div>
                <p className="summary-field-example">{field.example}</p>
              </div>
            ))}
          </div>
          <p style={{ textAlign: 'center', marginTop: 24, color: 'var(--muted)' }}>✏️ כל השדות ניתנים לעריכה ידנית</p>
        </div>
      </div>

      {/* Features */}
      <div className="section">
        <h2 className="section-title">תכונות עיקריות ⭐</h2>
        <div className="features-grid">
          {[
            { icon: '👥', title: 'ניהול מטופלים', items: ['רשימת מטופלים + חיפוש מהיר', 'היסטוריית ביקורים מלאה', 'מפתח ראשי גמיש (ת"ז/טלפון/אימייל)'] },
            { icon: '🎙️', title: 'תמלול מתקדם', items: ['זיהוי דוברים (רופא vs מטופל)', 'דיוק גבוה בעברית', 'עריכת תמלול ידנית'] },
            { icon: '🧠', title: 'AI חכם', items: ['סיכום רפואי מובנה', 'נורמליזציה של אבחנות', 'חילוץ תגיות אוטומטי'] },
            { icon: '🔍', title: 'חיפוש מתקדם', items: ['Full-text search', 'חיפוש סמנטי', 'סינון לפי תאריכים ותגיות'] },
            { icon: '🌍', title: '8 שפות', items: ['עברית (RTL)', 'אנגלית, גרמנית, ספרדית', 'צרפתית, פורטוגזית, קוריאנית, איטלקית'] },
            { icon: '🔒', title: 'אבטחה', items: ['הצפנת PII (AES-256)', 'Google OAuth + JWT', 'Audit log מלא'] },
          ].map((feature) => (
            <div key={feature.title} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <ul className="feature-list">
                {feature.items.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Benefits */}
      <div className="section">
        <h2 className="section-title">למה MedScribe? 💡</h2>
        <div className="benefits-grid">
          <div className="benefit-card">
            <h3>👨‍⚕️ לרופא</h3>
            <ul className="benefit-list">
              {['חיסכון 80% בזמן תיעוד', 'סיכומים מקצועיים ואחידים', 'חיפוש מהיר בכל הביקורים', 'גרפים וסטטיסטיקות', 'גישה מכל מקום (רק דפדפן)'].map(i => <li key={i}>{i}</li>)}
            </ul>
          </div>
          <div className="benefit-card">
            <h3>🤕 למטופל</h3>
            <ul className="benefit-list">
              {['יותר זמן פנים אל פנים עם הרופא', 'סיכום ברור ומובן לקחת הביתה', 'פרטיות מוגנת (הצפנה מלאה)', 'גישה למידע רפואי מסודר', 'אין צורך לחזור על המידע'].map(i => <li key={i}>{i}</li>)}
            </ul>
          </div>
        </div>
      </div>

      {/* Technology */}
      <div className="section">
        <h2 className="section-title">הטכנולוגיה מאחורי MedScribe 🛠️</h2>
        <div className="tech-grid">
          {[
            { label: 'Frontend', name: 'Flutter Web', desc: 'Material 3 Design' },
            { label: 'Backend', name: 'Python FastAPI', desc: 'Async + Celery' },
            { label: 'AI', name: 'OpenAI APIs', desc: 'Whisper + GPT-4.1' },
            { label: 'Database', name: 'PostgreSQL', desc: '+ Redis + MinIO' },
          ].map((tech) => (
            <div key={tech.name} className="tech-item">
              <div className="tech-item-label">{tech.label}</div>
              <div className="tech-item-name">{tech.name}</div>
              <div className="tech-item-desc">{tech.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="cta-section">
        <h2>מוכנים להתחיל? 🚀</h2>
        <p>התחבר עם Google והתחל להשתמש במערכת התמלול</p>
        <a href={process.env.NEXT_PUBLIC_MEDSCRIBE_URL || 'http://localhost:3000'} className="btn btn-primary">כניסה למערכת המלאה</a>
        <p style={{ marginTop: 24, fontSize: 14, color: 'var(--muted)' }}>
          💡 מצב דמו: 10 מטופלים + 10 דקות תמלול לכל מטופל
        </p>
      </div>

      {/* Demo */}
      <div className="section" id="demo">
        <h2 className="section-title">צפה איך זה עובד 📹</h2>
        <div style={{ aspectRatio: '16/9', borderRadius: 24, border: '2px solid var(--border)', background: 'rgba(18,26,51,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <p style={{ fontSize: 48, marginBottom: 16 }}>🎬</p>
            <p style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>סרטון הדגמה</p>
            <p style={{ color: 'var(--muted)' }}>(ניתן להוסיף סרטון YouTube / Vimeo כאן)</p>
          </div>
        </div>
      </div>

      <footer className="site-footer">
        <p>© 2026 Medical Hub • מדיניות פרטיות • תנאי שימוש</p>
        <p style={{ marginTop: 8 }}>
          <Link href="/" style={{ color: 'var(--accent)' }}>← חזרה לדף הבית</Link>
        </p>
      </footer>
    </>
  )
}
