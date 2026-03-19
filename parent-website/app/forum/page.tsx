'use client'

import { useState } from 'react'
import Link from 'next/link'
import Header from '@/components/Header'

type Status = 'answered' | 'waiting' | 'unanswered'
type Sort   = 'hot' | 'new' | 'unanswered' | 'top'

interface Post {
  id: number
  title: string
  status: Status
  author: string
  time: string
  tags: string[]
  replies: number
  views: number
  votes: number
}

const ALL_POSTS: Post[] = [
  { id: 1,  title: 'כאב גב תחתון אחרי אימון – מתי זה "דגל אדום"?',              status: 'answered',   author: 'משתמש_123',    time: 'לפני 2 שעות',    tags: ['כאבי גב','שיקום'],          replies: 18, views: 420, votes: 12 },
  { id: 2,  title: 'עייפות מתמשכת + סחרחורות קלות – אילו בדיקות בסיסיות?',       status: 'waiting',    author: 'רונית',        time: 'אתמול',          tags: ['עייפות','נוירולוגיה'],       replies: 6,  views: 190, votes: 3  },
  { id: 3,  title: 'איך מתעדים ביקור רפואי בצורה מסודרת וחוסכים זמן?',           status: 'unanswered', author: 'ד"ר X',         time: 'לפני 3 ימים',   tags: ['בירוקרטיה'],                 replies: 0,  views: 88,  votes: 0  },
  { id: 4,  title: 'מטפורמין ותופעות לוואי – האם להפסיק את הטיפול?',             status: 'answered',   author: 'אבי_ל',        time: 'לפני 5 שעות',   tags: ['סוכרת','תרופות'],           replies: 15, views: 340, votes: 22 },
  { id: 5,  title: 'כאבי ברכיים בריצה – ניהול שמרני מול ניתוח?',                status: 'answered',   author: 'ספורטיסט_99',  time: 'לפני 12 שעות',  tags: ['אורתופדיה','ספורט'],         replies: 9,  views: 215, votes: 7  },
  { id: 6,  title: 'שיטות להפחתת לחץ דם ללא תרופות – מה עובד?',                 status: 'waiting',    author: 'יוסי_מ',       time: 'לפני יומיים',   tags: ['לחץ דם','תזונה'],           replies: 18, views: 502, votes: 31 },
  { id: 7,  title: 'אנמיה מחוסר ברזל – מינון תוספים נכון לאישה בגיל 35',        status: 'answered',   author: 'שרה_כ',        time: 'לפני 3 ימים',   tags: ['דם','תוספים'],              replies: 11, views: 287, votes: 15 },
  { id: 8,  title: 'נדודי שינה כרוניים – מה עוזר באמת מעבר לתרופות?',           status: 'waiting',    author: 'עייף_מאוד',    time: 'לפני שבוע',     tags: ['שינה','בריאות נפש'],        replies: 31, views: 890, votes: 44 },
  { id: 9,  title: 'האם MRI ראש נחוץ לכאבי ראש חוזרים בגיל 40?',               status: 'answered',   author: 'דאגן',         time: 'לפני 4 ימים',   tags: ['נוירולוגיה','הדמיה'],        replies: 7,  views: 165, votes: 5  },
  { id: 10, title: 'תזונה לילדים עם אלרגיית חלב – תחליפים ומחסורים',             status: 'answered',   author: 'אמא_מודאגת',  time: 'לפני 6 ימים',   tags: ['ילדים','אלרגיה','תזונה'],   replies: 14, views: 380, votes: 27 },
  { id: 11, title: 'טיפול CBT לחרדה חברתית – האם זה עובד לטווח ארוך?',          status: 'waiting',    author: 'מרגיש_חרדה',   time: 'לפני שבועיים',  tags: ['בריאות נפש','טיפול'],       replies: 8,  views: 310, votes: 19 },
  { id: 12, title: 'ספורט עם מחלת לב כלילית – גבולות ואפשרויות',               status: 'answered',   author: 'ליאור_ב',      time: 'לפני 10 ימים',  tags: ['לב','ספורט'],               replies: 22, views: 671, votes: 38 },
]

const HOT_TAGS = [
  { label: 'כאבי גב', count: 214 },
  { label: 'עייפות',  count: 98  },
  { label: 'שיקום',   count: 76  },
  { label: 'נוירולוגיה', count: 64 },
  { label: 'סוכרת',   count: 53  },
  { label: 'תזונה',   count: 48  },
  { label: 'בריאות נפש', count: 41 },
]

const STATUS_LABEL: Record<Status, { text: string; color: string; bg: string; border: string }> = {
  answered:   { text: 'נענה',       color: '#a7f3d0', bg: 'rgba(52,211,153,.1)',  border: 'rgba(52,211,153,.3)'  },
  waiting:    { text: 'ממתין',      color: '#fde68a', bg: 'rgba(251,191,36,.1)',  border: 'rgba(251,191,36,.3)'  },
  unanswered: { text: 'ללא מענה',   color: '#fecdd3', bg: 'rgba(251,113,133,.1)', border: 'rgba(251,113,133,.3)' },
}

export default function ForumPage() {
  const [search,    setSearch]    = useState('')
  const [sort,      setSort]      = useState<Sort>('hot')
  const [activeTag, setActiveTag] = useState('')
  const [showModal, setShowModal] = useState(false)

  const filtered = ALL_POSTS.filter(p => {
    const matchSearch = !search || p.title.toLowerCase().includes(search.toLowerCase()) || p.tags.some(t => t.includes(search))
    const matchTag    = !activeTag || p.tags.includes(activeTag)
    const matchSort   = sort !== 'unanswered' || p.status === 'unanswered'
    return matchSearch && matchTag && matchSort
  }).sort((a, b) => {
    if (sort === 'new')  return b.id - a.id
    if (sort === 'top')  return b.votes - a.votes
    return (b.replies + b.votes * 2) - (a.replies + a.votes * 2)
  })

  return (
    <>
      <Header page="forum" />

      <main>
      <div style={{ maxWidth: 1300, margin: '32px auto', padding: '0 20px' }}>

        {/* Page title row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0, color: '#e0f2fe' }}>💬 פורום רפואי</h2>
            <p style={{ color: 'var(--muted)', margin: '6px 0 0', fontSize: 14 }}>
              1,248 שאלות · 342 נוספו היום · 48 מומחים פעילים
            </p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="btn btn-primary"
            style={{ padding: '13px 24px', fontSize: 15, fontWeight: 700 }}
          >
            ✏️ שאל שאלה
          </button>
        </div>

        {/* Search */}
        <div className="card" style={{ padding: '16px 20px', marginBottom: 20, display: 'flex', gap: 12, alignItems: 'center' }}>
          <input
            type="text"
            className="search-input"
            style={{ flex: 1, padding: '12px 16px' }}
            placeholder="חפש שאלה, תגית או מומחה... (/ לקיצור)"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <span className="kbd">/</span>
        </div>

        {/* Filter tabs */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
          {(['hot','new','unanswered','top'] as Sort[]).map(s => (
            <button
              key={s}
              onClick={() => setSort(s)}
              className={`nav-pill ${sort === s ? 'nav-pill-active' : 'nav-pill-default'}`}
            >
              {{ hot: '🔥 חם', new: '🆕 חדש', unanswered: '❓ ללא מענה', top: '⭐ מובילים' }[s]}
            </button>
          ))}
          <span style={{ marginRight: 'auto', color: 'var(--muted)', fontSize: 13 }}>
            {filtered.length} שאלות
          </span>
        </div>

        {/* Main layout */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 20, alignItems: 'start' }} className="forum-grid">

          {/* Post list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {filtered.length === 0 && (
              <div className="card" style={{ textAlign: 'center', padding: 48, color: 'var(--muted)' }}>
                לא נמצאו שאלות מתאימות
              </div>
            )}
            {filtered.map(post => {
              const s = STATUS_LABEL[post.status]
              return (
                <article key={post.id} className="forum-post card" data-testid="question">
                  <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>

                    {/* Stats column */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, flexShrink: 0, minWidth: 64 }}>
                      <div className="forum-stat">
                        <div className="forum-stat-n">{post.replies}</div>
                        <div className="forum-stat-l">תגובות</div>
                      </div>
                      <div className="forum-stat">
                        <div className="forum-stat-n">{post.views}</div>
                        <div className="forum-stat-l">צפיות</div>
                      </div>
                      <div className="forum-stat">
                        <div className="forum-stat-n">+{post.votes}</div>
                        <div className="forum-stat-l">הצבעות</div>
                      </div>
                    </div>

                    {/* Content */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <h3 style={{ fontSize: 15, fontWeight: 800, margin: '0 0 10px', lineHeight: 1.35, color: 'var(--text)' }}>
                        {post.title}
                      </h3>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center' }}>
                        {/* Status badge */}
                        <span style={{
                          fontSize: 12, fontWeight: 700,
                          padding: '4px 10px', borderRadius: 999,
                          color: s.color, background: s.bg, border: `1px solid ${s.border}`,
                          whiteSpace: 'nowrap',
                        }}>
                          {s.text}
                        </span>
                        {/* Tags */}
                        {post.tags.map(tag => (
                          <button
                            key={tag}
                            onClick={() => setActiveTag(activeTag === tag ? '' : tag)}
                            className="tag"
                            style={{
                              cursor: 'pointer',
                              background: activeTag === tag ? 'rgba(56,189,248,0.18)' : undefined,
                              border: activeTag === tag ? '1px solid rgba(56,189,248,0.6)' : undefined,
                            }}
                          >
                            {tag}
                          </button>
                        ))}
                        <span style={{ color: 'var(--muted)', fontSize: 12, marginRight: 'auto' }}>
                          {post.author} · {post.time}
                        </span>
                      </div>
                    </div>
                  </div>
                </article>
              )
            })}
          </div>

          {/* Sidebar */}
          <aside style={{ position: 'sticky', top: 88, display: 'flex', flexDirection: 'column', gap: 16 }}>

            {/* CTA */}
            <div className="card cta-card">
              <h4 style={{ margin: '0 0 8px' }}>🙋 שאל את הקהילה</h4>
              <p style={{ color: 'var(--muted)', fontSize: 13, lineHeight: 1.5, margin: '0 0 14px' }}>
                שאל שאלה רפואית ותקבל מענה ממומחים ומרופאים תוך שעות ספורות.
              </p>
              <div className="forum-mini-grid">
                <div className="forum-mini">
                  <div style={{ color: 'var(--muted)', fontSize: 11 }}>מומחים פעילים</div>
                  <div style={{ fontWeight: 900, fontSize: 18, marginTop: 4 }}>48</div>
                </div>
                <div className="forum-mini">
                  <div style={{ color: 'var(--muted)', fontSize: 11 }}>זמן תגובה</div>
                  <div style={{ fontWeight: 900, fontSize: 18, marginTop: 4 }}>~3 שע׳</div>
                </div>
              </div>
              <button
                onClick={() => setShowModal(true)}
                className="btn btn-primary"
                style={{ width: '100%', textAlign: 'center', marginTop: 14, padding: '12px' }}
              >
                ✏️ פתח טופס שאלה
              </button>
            </div>

            {/* Hot tags */}
            <div className="card">
              <h4 style={{ margin: '0 0 12px' }}>🔥 תגיות חמות</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {HOT_TAGS.map(t => (
                  <button
                    key={t.label}
                    onClick={() => setActiveTag(activeTag === t.label ? '' : t.label)}
                    className="tag"
                    style={{
                      cursor: 'pointer',
                      background: activeTag === t.label ? 'rgba(56,189,248,0.18)' : undefined,
                      border: activeTag === t.label ? '1px solid rgba(56,189,248,0.6)' : undefined,
                    }}
                  >
                    {t.label}
                    <span style={{ color: 'var(--muted)', fontWeight: 700, marginRight: 4 }}>{t.count}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Top contributors */}
            <div className="card">
              <h4 style={{ margin: '0 0 12px' }}>🏆 תורמים מובילים</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {[
                  { name: 'פרופ׳ לוי',  answers: 78,  votes: 1240, badge: 'מומחה',  bColor: '#a7f3d0' },
                  { name: 'ד"ר כהן',    answers: 52,  votes: 820,  badge: 'מאומת',  bColor: '#fde68a' },
                  { name: 'ד"ר שרה א', answers: 34,  votes: 570,  badge: 'מאומת',  bColor: '#fde68a' },
                ].map(c => (
                  <div key={c.name} className="forum-mini" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 800, fontSize: 14 }}>{c.name}</div>
                      <div style={{ color: 'var(--muted)', fontSize: 12, marginTop: 2 }}>{c.answers} תשובות · {c.votes} הצבעות</div>
                    </div>
                    <span style={{
                      fontSize: 11, fontWeight: 700, padding: '3px 8px', borderRadius: 999,
                      color: c.bColor, background: 'rgba(255,255,255,0.06)', border: `1px solid ${c.bColor}55`,
                    }}>
                      {c.badge}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <p style={{ fontSize: 12, color: 'var(--muted)', textAlign: 'center' }}>
              <span className="kbd">/</span> לחיפוש · <span className="kbd">Esc</span> לסגירה
            </p>
          </aside>
        </div>
      </div>

      {/* Ask question modal */}
      {showModal && (
        <div
          onClick={e => { if (e.target === e.currentTarget) setShowModal(false) }}
          style={{
            position: 'fixed', inset: 0, zIndex: 200,
            background: 'rgba(0,0,0,0.65)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            padding: 20,
          }}
        >
          <div style={{
            width: '100%', maxWidth: 600,
            background: 'rgba(18,26,51,0.97)',
            border: '1px solid var(--border)',
            borderRadius: 24,
            overflow: 'hidden',
          }}>
            {/* Modal header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '18px 24px', borderBottom: '1px solid var(--border)' }}>
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 800 }}>✏️ שאל שאלה</h3>
              <button onClick={() => setShowModal(false)} className="btn btn-secondary" style={{ padding: '8px 14px', fontSize: 13 }}>✕ סגור</button>
            </div>

            {/* Modal body */}
            <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--muted)', marginBottom: 6 }}>כותרת השאלה</label>
                <input className="search-input" style={{ width: '100%', padding: '12px 14px' }} placeholder="לדוגמה: כאב גב תחתון אחרי אימון – מה הסימנים המסוכנים?" />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--muted)', marginBottom: 6 }}>תגית ראשית</label>
                <select className="search-input" style={{ width: '100%', padding: '12px 14px' }}>
                  {HOT_TAGS.map(t => <option key={t.label}>{t.label}</option>)}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--muted)', marginBottom: 6 }}>פירוט (גיל, רקע, מה ניסית)</label>
                <textarea
                  className="search-input"
                  rows={5}
                  style={{ width: '100%', padding: '12px 14px', resize: 'vertical' }}
                  placeholder="כתוב פרטים קצרים..."
                />
              </div>
            </div>

            {/* Modal footer */}
            <div style={{ display: 'flex', gap: 10, padding: '16px 24px', borderTop: '1px solid var(--border)' }}>
              <button onClick={() => setShowModal(false)} className="btn btn-secondary">ביטול</button>
              <button onClick={() => { setShowModal(false); alert('דמו: השאלה פורסמה!') }} className="btn btn-primary" style={{ flex: 1 }}>
                פרסם שאלה →
              </button>
            </div>
          </div>
        </div>
      )}

      </main>
    </>
  )
}
