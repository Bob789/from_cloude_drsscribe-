'use client'

import React, { useState } from 'react'
import Link from 'next/link'

export default function GlucoseArticlePage() {
  const [likes, setLikes] = useState(0)

  // Mock data matching the requested article
  const article = {
    title: 'חוסר איזון ברמות הגלוקוז: מה חשוב לדעת וכיצד להתמודד',
    subtitle: 'הבנת חוסר איזון ברמות הגלוקוז ואיך לשמור על איזון בריא',
    author: 'צוות Medical Hub · צוות התוכן הרפואי',
    date: '16.3.2026',
    readTime: 2,
    views: 8,
    category: 'endocrinology',
    categoryLabel: 'אנדוקרינולוגיה',
    tags: ['גלוקוז', 'סוכרת', 'תזונה', 'בריאות'],
  }

  const handleLike = () => {
    setLikes(prev => prev + 1)
  }

  return (
    <>
      <head>
        <title>{article.title} | Medical Hub</title>
        <meta name="description" content={article.subtitle} />
        <meta name="keywords" content={article.tags.join(', ')} />
      </head>

      <main style={{ background: 'var(--bg)', minHeight: '100vh', paddingBottom: 80 }}>
        {/* Hero Section - Using a gradient placeholder since we don't have the original image */}
        <div style={{ 
          width: '100%', 
          height: 400, 
          position: 'relative',
          background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden'
        }}>
           {/* Abstract decorative elements */}
           <div style={{ position: 'absolute', width: 300, height: 300, background: 'rgba(56,189,248,0.1)', borderRadius: '50%', top: -50, right: 100, filter: 'blur(60px)' }}></div>
           <div style={{ position: 'absolute', width: 250, height: 250, background: 'rgba(168,85,247,0.1)', borderRadius: '50%', bottom: 50, left: 100, filter: 'blur(60px)' }}></div>
           
           <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '40px 20px 30px', background: 'linear-gradient(transparent, rgba(13,17,23,0.9))' }}>
              <div style={{ maxWidth: 800, margin: '0 auto' }}>
                <span style={{ 
                  padding: '6px 16px', 
                  borderRadius: 20, 
                  background: 'rgba(56,189,248,0.2)', 
                  color: '#38bdf8', 
                  fontSize: 13, 
                  fontWeight: 600,
                  backdropFilter: 'blur(4px)'
                }}>
                  {article.categoryLabel}
                </span>
              </div>
            </div>
        </div>

        <article style={{ maxWidth: 800, margin: '0 auto', padding: '0 20px', position: 'relative', top: -20 }} dir="rtl">
          {/* Title and Header */}
          <div style={{ marginBottom: 40 }}>
            <h1 style={{ 
              fontSize: 'clamp(2rem, 5vw, 2.5rem)', 
              fontWeight: 800, 
              lineHeight: 1.2, 
              color: '#f0f9ff', 
              marginBottom: 16,
              textShadow: '0 4px 20px rgba(0,0,0,0.5)'
            }}>
              {article.title}
            </h1>
            <p style={{ fontSize: '1.25rem', color: '#94a3b8', marginBottom: 24, lineHeight: 1.6 }}>
              {article.subtitle}
            </p>

            {/* Meta info */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 16, 
              flexWrap: 'wrap', 
              fontSize: '0.9rem', 
              color: '#64748b',
              borderBottom: '1px solid rgba(255,255,255,0.1)',
              paddingBottom: 24
            }}>
              <span style={{ color: '#e2e8f0', fontWeight: 500 }}>{article.author}</span>
              <span>•</span>
              <span>{article.readTime} דקות קריאה</span>
              <span>•</span>
              <span>{article.views} צפיות</span>
              <span>•</span>
              <span>{article.date}</span>
            </div>
          </div>

          {/* Article Content */}
          <div className="article-content" style={{ fontSize: '1.125rem', lineHeight: 1.8, color: '#d4d4d8' }}>
            
            <p style={{ marginBottom: 24 }}>
              חוסר איזון ברמות הגלוקוז בדם הוא מצב נפוץ המוביל לסיכונים בריאותיים משמעותיים,
              במיוחד בקרב מבוגרים מעל גיל 40. הבנת הגורמים לחוסר איזון זה וכיצד לשמור על רמות
              גלוקוז מאוזנות יכולה לשפר את איכות החיים ולמנוע מחלות כרוניות.
            </p>

            <h2 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#e0f2fe', marginTop: 48, marginBottom: 24 }}>
              מהו חוסר איזון ברמות הגלוקוז?
            </h2>
            <p style={{ marginBottom: 24 }}>
              חוסר איזון ברמות הגלוקוז מתייחס למצב שבו רמות הסוכר בדם אינן נשארות בטווח
              הנורמלי. מצב זה יכול להוביל להיפוגליקמיה (רמות נמוכות מדי של גלוקוז) או להיפרגליקמיה
              (רמות גבוהות מדי של גלוקוז), וכל אחד מהם מהווה סיכון לבריאות.
            </p>

            <h3 style={{ fontSize: '1.4rem', fontWeight: 600, color: '#bae6fd', marginTop: 32, marginBottom: 16 }}>
              היפוגליקמיה: סכנות ורמזים
            </h3>
            <ul style={{ listStyleType: 'disc', paddingRight: 24, marginBottom: 24, color: '#cbd5e1' }}>
              <li style={{ marginBottom: 8 }}><strong>סימפטומים:</strong> רעידות, זיעה מוגברת, חולשה, בלבול.</li>
              <li style={{ marginBottom: 8 }}><strong>סיבות נפוצות:</strong> צריכת יתר של אינסולין, דילוג על ארוחות, פעילות גופנית מופרזת ללא תזונה מספקת.</li>
            </ul>

            <h3 style={{ fontSize: '1.4rem', fontWeight: 600, color: '#bae6fd', marginTop: 32, marginBottom: 16 }}>
              היפרגליקמיה: הבנת ההשפעות
            </h3>
            <ul style={{ listStyleType: 'disc', paddingRight: 24, marginBottom: 24, color: '#cbd5e1' }}>
              <li style={{ marginBottom: 8 }}><strong>סימפטומים:</strong> צמא מוגבר, שתן תכוף, עייפות, ראייה מטושטשת.</li>
              <li style={{ marginBottom: 8 }}><strong>סיבות:</strong> תזונה עשירה בפחמימות, סטרס, מחסור בפעילות גופנית.</li>
            </ul>

            <h2 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#e0f2fe', marginTop: 48, marginBottom: 24 }}>
              גורמים לחוסר איזון בגלוקוז
            </h2>
            <p style={{ marginBottom: 24 }}>
              חוסר איזון בגלוקוז עלול להיגרם ממספר גורמים, כולל תזונה לא מאוזנת, חוסר פעילות
              גופנית, סטרס כרוני ומחלות מטבוליות כמו סוכרת.
            </p>

            <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 12, padding: 24, marginBottom: 32, border: '1px solid rgba(255,255,255,0.05)' }}>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 600, color: '#fff', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 10 }}>
                🥦 תזונה ותפקידה באיזון הגלוקוז
              </h3>
              <p style={{ marginBottom: 12 }}>
                <strong>שימו לב למה שאתם אוכלים:</strong> העדיפו מזונות עשירים בסיבים תזונתיים ודלים בסוכר.
              </p>
              <p style={{ marginBottom: 0 }}>
                <strong>ארוחות סדירות:</strong> אכלו ארוחות קטנות ומסודרות לאורך היום כדי לשמור על רמות גלוקוז יציבות.
              </p>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 12, padding: 24, marginBottom: 32, border: '1px solid rgba(255,255,255,0.05)' }}>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 600, color: '#fff', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 10 }}>
                🏃‍♂️ פעילות גופנית כמרכיב מפתח
              </h3>
              <p style={{ marginBottom: 12 }}>
                <strong>המלצות לפעילות:</strong> התעמלו באופן סדיר לפחות 150 דקות בשבוע.
              </p>
              <p style={{ marginBottom: 0 }}>
                <strong>יתרונות:</strong> פעילות גופנית תורמת לשיפור רגישות לאינסולין ומסייעת בשמירה על משקל בריא.
              </p>
            </div>

            <h2 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#e0f2fe', marginTop: 48, marginBottom: 24 }}>
              טיפים מעשיים לשמירה על איזון
            </h2>
            <p style={{ marginBottom: 24 }}>
              שמירה על איזון ברמות הגלוקוז דורשת מאמץ מתמשך ומודעות. הנה מספר טיפים מעשיים:
            </p>
            <ul style={{ listStyleType: 'none', padding: 0, display: 'grid', gap: 16, marginBottom: 32 }}>
              {[
                { title: 'מעקב אחר רמות הגלוקוז', text: 'השתמשו במד סוכר לניטור קבוע' },
                { title: 'ניהול סטרס', text: 'תרגלו טכניקות הרפיה כמו יוגה או מדיטציה' },
                { title: 'כמות סוכר מתונה', text: 'הימנעו מצריכה מוגזמת של משקאות ממותקים ומאפים מתוקים' }
              ].map((tip, i) => (
                <li key={i} style={{ background: 'rgba(56,189,248,0.05)', borderRight: '4px solid #38bdf8', padding: '16px 20px', borderRadius: '4px 8px 8px 4px' }}>
                  <strong style={{ display: 'block', color: '#7dd3fc', marginBottom: 4 }}>{tip.title}</strong>
                  <span style={{ color: '#cbd5e1' }}>{tip.text}</span>
                </li>
              ))}
            </ul>

            <h2 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#e0f2fe', marginTop: 48, marginBottom: 24 }}>
              סיכום והמלצה לפעולה
            </h2>
            <p style={{ marginBottom: 24 }}>
              חוסר איזון ברמות הגלוקוז הוא אתגר בריאותי שניתן לנהל בעזרת שינויי אורח חיים.
              חשוב להמשיך ללמוד על הנושא ולפנות לרופא לקבלת ייעוץ מותאם אישית. למידע נוסף, מומלץ
              לעיין בפורומים רפואיים ולקרוא עוד על הנושא.
            </p>
            
            <div style={{ background: 'rgba(253, 224, 71, 0.1)', border: '1px solid rgba(253, 224, 71, 0.2)', padding: 16, borderRadius: 8, fontSize: '0.9rem', color: '#fef08a', marginTop: 32 }}>
              <strong>הבהרה משפטית:</strong> מאמר זה נועד למטרות מידע כללי בלבד ואינו מהווה תחליף לייעוץ רפואי מקצועי.
            </div>

          </div>

          {/* Tags */}
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 48, paddingTop: 24, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
            {article.tags.map((tag) => (
              <span key={tag} style={{ 
                padding: '6px 14px', 
                borderRadius: 20, 
                background: 'rgba(56,189,248,0.1)', 
                color: '#38bdf8', 
                fontSize: 14,
                cursor: 'default' 
              }}>
                #{tag}
              </span>
            ))}
          </div>

          {/* Like Button */}
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: 40 }}>
            <button 
              onClick={handleLike} 
              style={{ 
                padding: '12px 32px', 
                borderRadius: 50, 
                border: '1px solid rgba(244,114,182,0.3)', 
                background: 'rgba(244,114,182,0.1)', 
                color: '#f472b6', 
                fontSize: 16, 
                fontWeight: 600,
                cursor: 'pointer', 
                display: 'flex', 
                alignItems: 'center', 
                gap: 10,
                transition: 'all 0.2s ease'
              }}
              onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(244,114,182,0.2)'; e.currentTarget.style.transform = 'scale(1.05)' }}
              onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(244,114,182,0.1)'; e.currentTarget.style.transform = 'scale(1)' }}
            >
              <span>❤️</span>
              <span>אהבתי ({likes})</span>
            </button>
          </div>
          
          {/* Related Articles Mockup */}
          <div style={{ marginTop: 64 }}>
            <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: 24, color: '#e0f2fe' }}>מאמרים נוספים שיעניינו אותך</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 24 }}>
                <Link href="#" style={{ textDecoration: 'none' }}>
                    <div style={{ background: 'rgba(30,41,59,0.5)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 16, padding: 20, height: '100%', transition: 'all 0.2s' }}>
                        <h4 style={{ color: '#f1f5f9', fontWeight: 600, marginBottom: 8 }}>תזונה נכונה לחולי סוכרת - המדריך המלא</h4>
                        <p style={{ fontSize: '0.9rem', color: '#94a3b8', margin: 0 }}>טיפים לבניית תפריט מאוזן ושמירה על רמות סוכר תקינות לאורך היום.</p>
                    </div>
                </Link>
                <Link href="#" style={{ textDecoration: 'none' }}>
                    <div style={{ background: 'rgba(30,41,59,0.5)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 16, padding: 20, height: '100%', transition: 'all 0.2s' }}>
                         <h4 style={{ color: '#f1f5f9', fontWeight: 600, marginBottom: 8 }}>חשיבות הפעילות הגופנית בגיל השלישי</h4>
                         <p style={{ fontSize: '0.9rem', color: '#94a3b8', margin: 0 }}>איך לשלב תנועה בחיי היומיום ולשפר את איכות החיים בקלות.</p>
                    </div>
                </Link>
            </div>
          </div>

        </article>
      </main>
    </>
  )
}
