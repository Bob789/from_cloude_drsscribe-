'use client'

import { useState } from 'react'
import Header from '@/components/Header'

type Category = 'all' | 'cardiology' | 'neurology' | 'orthopedics' | 'nutrition' | 'sleep' | 'mental'
type Sort = 'hot' | 'new' | 'popular'

interface Article {
  id: number
  title: string
  summary: string
  category: Exclude<Category, 'all'>
  tags: string[]
  author: string
  authorTitle: string
  readTime: number
  date: string
  icon: string
  views: number
  likes: number
}

const CATEGORY_META: Record<Exclude<Category, 'all'>, { label: string; color: string; bg: string }> = {
  cardiology:   { label: 'לב וכלי דם',  color: '#fca5a5', bg: 'rgba(239,68,68,0.1)'   },
  neurology:    { label: 'נוירולוגיה',  color: '#a78bfa', bg: 'rgba(139,92,246,0.1)'  },
  orthopedics:  { label: 'אורתופדיה',   color: '#93c5fd', bg: 'rgba(59,130,246,0.1)'  },
  nutrition:    { label: 'תזונה',        color: '#6ee7b7', bg: 'rgba(16,185,129,0.1)'  },
  sleep:        { label: 'שינה',         color: '#fde68a', bg: 'rgba(245,158,11,0.1)'  },
  mental:       { label: 'בריאות נפש',  color: '#f9a8d4', bg: 'rgba(236,72,153,0.1)'  },
}

const TABS: { id: Category; label: string }[] = [
  { id: 'all',          label: '📋 הכל'      },
  { id: 'cardiology',   label: '❤️ לב'       },
  { id: 'neurology',    label: '🧠 נוירו'    },
  { id: 'orthopedics',  label: '🦴 אורתו'    },
  { id: 'nutrition',    label: '🥗 תזונה'    },
  { id: 'sleep',        label: '😴 שינה'     },
  { id: 'mental',       label: '🧘 נפש'      },
]

const ALL_ARTICLES: Article[] = [
  { id: 1,  title: 'כאבי גב כרוניים – מדריך מקיף לאבחון וטיפול',         summary: 'סקירה עדכנית של גורמי כאב גב, שיטות אבחון, טיפול פיזיותרפי ותרופתי, ומתי מתייעצים לגבי ניתוח. כל מה שצריך לדעת.', category: 'orthopedics', tags: ['כאבי גב','שיקום','פיזיותרפיה'],   author: 'ד"ר דניאל כהן',      authorTitle: 'אורתופד',          readTime: 4, date: 'לפני 2 ימים',    icon: '🦴', views: 1240, likes: 87  },
  { id: 2,  title: 'יתר לחץ דם – מה כדאי לדעת בגיל 40+',                 summary: 'גורמי סיכון, טיפול תרופתי לעומת שינוי אורח חיים, ומה החדשות האחרונות בנושא טיפול ביתר לחץ דם.', category: 'cardiology',   tags: ['לחץ דם','לב','מניעה'],           author: 'פרופ׳ ריבה שמש',     authorTitle: 'רפואה פנימית',     readTime: 5, date: 'לפני 3 ימים',    icon: '❤️', views: 2100, likes: 143 },
  { id: 3,  title: 'עייפות מתמשכת – מתי זה יותר מסתם עייפות?',           summary: 'מחלות שעומדות מאחורי עייפות כרונית: אנמיה, בעיות בלוטת תריס, דיכאון, ומחלות אוטואימוניות. כיצד מאבחנים ומטפלים.', category: 'neurology',    tags: ['עייפות','בלוטת תריס','דם'],      author: 'פרופ׳ מרים לוי',     authorTitle: 'נוירולוגית',       readTime: 6, date: 'לפני 5 ימים',    icon: '🔋', views: 3400, likes: 210 },
  { id: 4,  title: 'דיאטה ים תיכונית – עדויות מדעיות 2025',               summary: 'מה המחקר אומר על הדיאטה הים-תיכונית ומחלות לב, סוכרת, ודמנציה. נתונים עדכניים ומה לאכול בפועל.', category: 'nutrition',    tags: ['תזונה','לב','מניעה'],            author: 'ד"ר יוסי מזרחי',     authorTitle: 'אנדוקרינולוג',     readTime: 7, date: 'לפני שבוע',      icon: '🥗', views: 1890, likes: 124 },
  { id: 5,  title: 'שינה בריאה – המדריך המלא לשינה עמוקה',                summary: 'היגיינת שינה, הפרעות שינה נפוצות, טיפול CBT-I, ומתי מתייעצים עם מומחה שינה. כל מה שצריך לדעת.', category: 'sleep',        tags: ['שינה','CBT','נדודי שינה'],       author: 'ד"ר אמיר זקן',       authorTitle: 'פסיכיאטר',         readTime: 3, date: 'לפני שבועיים',   icon: '😴', views: 4200, likes: 312 },
  { id: 6,  title: 'חרדה חברתית – סימנים, גורמים, וטיפול יעיל',           summary: 'הבנת חרדה חברתית, ההבדל בינה לבין ביישנות, וטיפולים יעילים כולל CBT ותרופות. מדריך מלא.', category: 'mental',       tags: ['חרדה','CBT','בריאות נפש'],       author: 'ד"ר אמיר זקן',       authorTitle: 'פסיכיאטר',         readTime: 5, date: 'לפני 3 שבועות',  icon: '🧘', views: 2700, likes: 198 },
  { id: 7,  title: 'ספורט בגיל 50+ – כיצד להתאמן בבטחה ובחוכמה',         summary: 'איך לבנות תוכנית אימון מותאמת לגיל, אילו ספורטים כדאי לבחור ואילו להימנע מהם. טיפים מהשדה.', category: 'orthopedics',  tags: ['ספורט','שיקום','גיל מבוגר'],    author: 'ד"ר דניאל כהן',      authorTitle: 'אורתופד',          readTime: 4, date: 'לפני חודש',      icon: '🏃', views: 1560, likes: 96  },
  { id: 8,  title: 'סוכרת סוג 2 – מניעה ושליטה דרך תזונה נכונה',         summary: 'אסטרטגיות תזונתיות מבוססות מחקר, מדדים חשובים, ומתי תרופות הכרחיות. עדויות מהמחקרים.', category: 'nutrition',    tags: ['סוכרת','תזונה','מניעה'],         author: 'ד"ר יוסי מזרחי',     authorTitle: 'אנדוקרינולוג',     readTime: 8, date: 'לפני חודש',      icon: '🩸', views: 2240, likes: 167 },
  { id: 9,  title: 'כאבי ראש חוזרים – מיגרנה ומה מעבר לה',               summary: 'טריגרים נפוצים, אבחנה מבדלת, טיפולים מונעים, ומתי לפנות לבדיקת MRI. מדריך לסובלים מכאבי ראש.', category: 'neurology',    tags: ['מיגרנה','כאב ראש','הדמיה'],     author: 'פרופ׳ מרים לוי',     authorTitle: 'נוירולוגית',       readTime: 5, date: 'לפני חודשיים',   icon: '🧠', views: 3100, likes: 241 },
  { id: 10, title: 'מחלות לב – גורמי סיכון ובדיקות מומלצות',              summary: 'פרופיל שומנים, לחץ דם, סוכר בצום – מה לבדוק, מתי, ומה המשמעות של הנתונים. המלצות מעשיות.', category: 'cardiology',   tags: ['לב','כולסטרול','מניעה'],         author: 'ד"ר שרה אברמוביץ',   authorTitle: 'קרדיולוגית',       readTime: 9, date: 'לפני 3 חודשים',  icon: '🫀', views: 4800, likes: 356 },
  { id: 11, title: 'אלרגיות עונתיות – מדריך מלא לעונת האביב',             summary: 'אבחנה, טיפול תרופתי ואימונותרפיה, וטיפים מעשיים למחיה עם אלרגיות עונתיות ופרחי אביב.', category: 'neurology',    tags: ['אלרגיה','נשימה','אביב'],         author: 'ד"ר נעמה כץ',        authorTitle: 'נפרולוגית',        readTime: 3, date: 'לפני 4 חודשים',  icon: '🌸', views: 1380, likes: 78  },
  { id: 12, title: 'בריאות נפשית בעידן הדיגיטלי – FOMO ומדיה חברתית',    summary: 'השפעת מדיה חברתית על חרדה ודיכאון בקרב בני נוער ומבוגרים, וכלים פרקטיים להגנה על הנפש.', category: 'mental',       tags: ['בריאות נפש','דיגיטל','חרדה'],   author: 'ד"ר אמיר זקן',       authorTitle: 'פסיכיאטר',         readTime: 5, date: 'לפני 5 חודשים',  icon: '📱', views: 3700, likes: 289 },
]

const HOT_TAGS = ['כאבי גב','לחץ דם','תזונה','שינה','חרדה','לב','סוכרת','מיגרנה']

const TOP_AUTHORS = [
  { name: 'ד"ר אמיר זקן',      articles: 3, specialty: 'פסיכיאטריה' },
  { name: 'ד"ר דניאל כהן',     articles: 2, specialty: 'אורתופדיה'   },
  { name: 'ד"ר יוסי מזרחי',    articles: 2, specialty: 'אנדוקרינולוגיה' },
  { name: 'פרופ׳ מרים לוי',     articles: 2, specialty: 'נוירולוגיה'  },
]

export default function ArticlesPage() {
  const [search,    setSearch]    = useState('')
  const [category,  setCategory]  = useState<Category>('all')
  const [sort,      setSort]      = useState<Sort>('hot')
  const [activeTag, setActiveTag] = useState('')

  const filtered = ALL_ARTICLES.filter(a => {
    const matchSearch = !search || a.title.includes(search) || a.tags.some(t => t.includes(search))
    const matchCat    = category === 'all' || a.category === category
    const matchTag    = !activeTag || a.tags.includes(activeTag)
    return matchSearch && matchCat && matchTag
  }).sort((a, b) => {
    if (sort === 'new')     return b.id - a.id
    if (sort === 'popular') return b.views - a.views
    return (b.likes + b.views * 0.01) - (a.likes + a.views * 0.01)
  })

  return (
    <>
      <Header page="articles" />

      <main>
      <div style={{ maxWidth: 1300, margin: '32px auto', padding: '0 20px' }}>

        {/* Title row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0, color: '#e0f2fe' }}>📰 מאמרים רפואיים</h2>
            <p style={{ color: 'var(--muted)', margin: '6px 0 0', fontSize: 14 }}>
              142 מאמרים · 12 חדשים השבוע · 28 רופאים כותבים
            </p>
          </div>
        </div>

        {/* Search */}
        <div className="card" style={{ padding: '16px 20px', marginBottom: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
          <input
            type="text"
            className="search-input"
            style={{ flex: 1, padding: '12px 16px' }}
            placeholder="חפש מאמר, תגית או כותב... (/ לקיצור)"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <span className="kbd">/</span>
        </div>

        {/* Category tabs */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
          {TABS.map(t => (
            <button
              key={t.id}
              onClick={() => setCategory(t.id)}
              className={`nav-pill ${category === t.id ? 'nav-pill-active' : 'nav-pill-default'}`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Sort */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
          {(['hot','new','popular'] as Sort[]).map(s => (
            <button
              key={s}
              onClick={() => setSort(s)}
              style={{
                padding: '6px 14px', borderRadius: 10, fontSize: 13, cursor: 'pointer',
                fontWeight: sort === s ? 700 : 400,
                border: sort === s ? '1px solid rgba(56,189,248,0.6)' : '1px solid var(--border)',
                background: sort === s ? 'rgba(56,189,248,0.08)' : 'transparent',
                color: sort === s ? '#e0f2fe' : 'var(--muted)',
              }}
            >
              {{ hot: '🔥 חם', new: '🆕 חדש', popular: '👁️ פופולרי' }[s]}
            </button>
          ))}
          <span style={{ marginRight: 'auto', color: 'var(--muted)', fontSize: 13 }}>
            {filtered.length} מאמרים
          </span>
        </div>

        {/* Main layout */}
        <div className="forum-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 20, alignItems: 'start' }}>

          {/* Article list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {filtered.length === 0 && (
              <div className="card" style={{ textAlign: 'center', padding: 48, color: 'var(--muted)' }}>
                לא נמצאו מאמרים מתאימים
              </div>
            )}

            {filtered.map(article => {
              const cat = CATEGORY_META[article.category]
              return (
                <article key={article.id} className="article-card card" data-testid="article-card">
                  <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>

                    {/* Emoji icon box */}
                    <div style={{
                      width: 56, height: 56, borderRadius: 16, flexShrink: 0,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: 'rgba(56,189,248,0.08)', border: '1px solid rgba(56,189,248,0.2)',
                      fontSize: 28,
                    }}>
                      {article.icon}
                    </div>

                    {/* Content */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <h3 style={{ fontSize: 15, fontWeight: 800, margin: '0 0 8px', lineHeight: 1.4, color: 'var(--text)' }}>
                        {article.title}
                      </h3>
                      <p style={{ color: 'var(--muted)', fontSize: 13, margin: '0 0 10px', lineHeight: 1.5, maxHeight: '2.8em', overflow: 'hidden' }}>
                        {article.summary}
                      </p>

                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center' }}>
                        {/* Category badge */}
                        <span style={{
                          fontSize: 12, fontWeight: 700, padding: '4px 10px', borderRadius: 999, whiteSpace: 'nowrap',
                          color: cat.color, background: cat.bg, border: `1px solid ${cat.color}44`,
                        }}>
                          {cat.label}
                        </span>
                        {/* Tags */}
                        {article.tags.slice(0, 2).map(tag => (
                          <button
                            key={tag}
                            onClick={() => setActiveTag(activeTag === tag ? '' : tag)}
                            className="tag"
                            style={{ cursor: 'pointer', background: activeTag === tag ? 'rgba(56,189,248,0.18)' : undefined, border: activeTag === tag ? '1px solid rgba(56,189,248,0.6)' : undefined }}
                          >
                            {tag}
                          </button>
                        ))}
                        <span style={{ color: 'var(--muted)', fontSize: 12, marginRight: 'auto' }}>
                          {article.author} · {article.readTime} דק׳ · {article.date}
                        </span>
                      </div>

                      <div style={{ display: 'flex', gap: 16, marginTop: 10, alignItems: 'center' }}>
                        <span style={{ fontSize: 12, color: 'var(--muted)' }}>👁️ {article.views.toLocaleString()}</span>
                        <span style={{ fontSize: 12, color: 'var(--muted)' }}>❤️ {article.likes}</span>
                        <button className="btn btn-primary" style={{ marginRight: 'auto', padding: '6px 16px', fontSize: 12 }}>
                          קרא עוד →
                        </button>
                      </div>
                    </div>
                  </div>
                </article>
              )
            })}
          </div>

          {/* Sidebar */}
          <aside style={{ position: 'sticky', top: 88, display: 'flex', flexDirection: 'column', gap: 16 }}>

            {/* Categories */}
            <div className="card">
              <h4 style={{ margin: '0 0 12px' }}>📂 קטגוריות</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {(Object.entries(CATEGORY_META) as [Exclude<Category,'all'>, typeof CATEGORY_META[keyof typeof CATEGORY_META]][]).map(([id, meta]) => (
                  <button
                    key={id}
                    onClick={() => setCategory(id)}
                    style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      padding: '8px 12px', borderRadius: 10, cursor: 'pointer', fontSize: 13,
                      border: category === id ? `1px solid ${meta.color}44` : '1px solid var(--border)',
                      background: category === id ? meta.bg : 'transparent',
                      color: 'var(--text)',
                    }}
                  >
                    <span>{meta.label}</span>
                    <span style={{ color: meta.color, fontWeight: 700, fontSize: 12 }}>
                      {ALL_ARTICLES.filter(a => a.category === id).length}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Hot tags */}
            <div className="card">
              <h4 style={{ margin: '0 0 12px' }}>🔥 תגיות חמות</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {HOT_TAGS.map(tag => (
                  <button
                    key={tag}
                    onClick={() => setActiveTag(activeTag === tag ? '' : tag)}
                    className="tag"
                    style={{ cursor: 'pointer', background: activeTag === tag ? 'rgba(56,189,248,0.18)' : undefined, border: activeTag === tag ? '1px solid rgba(56,189,248,0.6)' : undefined }}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>

            {/* Top authors */}
            <div className="card">
              <h4 style={{ margin: '0 0 12px' }}>✍️ כותבים מובילים</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {TOP_AUTHORS.map(a => (
                  <div key={a.name} className="forum-mini" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 13 }}>{a.name}</div>
                      <div style={{ color: 'var(--muted)', fontSize: 11, marginTop: 2 }}>{a.specialty}</div>
                    </div>
                    <span style={{ fontSize: 11, color: '#93c5fd', fontWeight: 700 }}>{a.articles} מאמרים</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Doctor Scribe AI CTA */}
            <div className="card cta-card">
              <h4 style={{ margin: '0 0 8px' }}>🎤 Doctor Scribe AI</h4>
              <p style={{ color: 'var(--muted)', fontSize: 13, lineHeight: 1.5, margin: '0 0 12px' }}>
                תמלול וסיכום אוטומטי של ביקורים רפואיים לקליניקות פרטיות.
              </p>
              <a href="/product" className="btn btn-primary" style={{ display: 'block', textAlign: 'center', padding: '10px' }}>
                למד עוד →
              </a>
            </div>

            <p style={{ fontSize: 12, color: 'var(--muted)', textAlign: 'center' }}>
              <span className="kbd">/</span> לחיפוש
            </p>
          </aside>
        </div>
      </div>

      </main>
    </>
  )
}
