'use client'

import { useState } from 'react'
import Link from 'next/link'
import '../community-theme.css'

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
  answered:   { text: '✓ נענה',     color: '#065f46', bg: 'rgba(16,185,129,0.1)',  border: 'rgba(16,185,129,0.3)'  },
  waiting:    { text: '⏳ ממתין',   color: '#92400e', bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.3)'  },
  unanswered: { text: '❓ ללא מענה', color: '#9f1239', bg: 'rgba(244,63,94,0.08)', border: 'rgba(244,63,94,0.25)'  },
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
    <div id="forum-page-root">

      {/* ── BLOCK HEADER ── */}
      <div className="com-block-header">
        <div>
          <div className="com-block-title">💬 פורום רפואי</div>
          <div className="com-block-count">1,248 שאלות · 342 נוספו היום · 48 מומחים פעילים</div>
        </div>
        <button onClick={() => setShowModal(true)} className="com-cta-btn" style={{ width: 'auto', padding: '10px 22px' }}>
          ✏️ שאל שאלה
        </button>
      </div>

      {/* ── TITLE LINES ── */}
      <div className="com-title-lines">
        <div className="com-title-line"></div>
        <div className="com-title-line"></div>
      </div>

      {/* ── BODY ── */}
      <div className="com-body">

        {/* Search */}
        <div className="com-search-bar">
          <span style={{ fontSize: 16, color: '#999' }}>🔍</span>
          <input
            type="text"
            className="com-search-input"
            placeholder="חפש שאלה, תגית או נושא..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <span className="com-kbd">/</span>
        </div>

        {/* Filter pills */}
        <div className="com-pills">
          {(['hot','new','unanswered','top'] as Sort[]).map(s => (
            <button
              key={s}
              onClick={() => setSort(s)}
              className={`com-pill${sort === s ? ' com-pill-active' : ''}`}
            >
              {{ hot: '🔥 חם', new: '🆕 חדש', unanswered: '❓ ללא מענה', top: '⭐ מובילים' }[s]}
            </button>
          ))}
          <span className="com-count">{filtered.length} שאלות</span>
        </div>

        {/* Main layout — posts + sidebar */}
        <div className="com-layout">

          {/* Post list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {filtered.length === 0 && (
              <div className="com-card" style={{ textAlign: 'center', padding: 48, color: '#888' }}>
                לא נמצאו שאלות מתאימות
              </div>
            )}
            {filtered.map(post => {
              const s = STATUS_LABEL[post.status]
              return (
                <article key={post.id} className="com-card">
                  <div className="fr-post">

                    {/* Stats column */}
                    <div className="fr-stats-col">
                      <div className="fr-stat-box">
                        <div className="fr-stat-n">{post.replies}</div>
                        <div className="fr-stat-l">תגובות</div>
                      </div>
                      <div className="fr-stat-box">
                        <div className="fr-stat-n">{post.views}</div>
                        <div className="fr-stat-l">צפיות</div>
                      </div>
                      <div className="fr-stat-box">
                        <div className="fr-stat-n">+{post.votes}</div>
                        <div className="fr-stat-l">הצבעות</div>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="fr-post-content">
                      <h3 className="fr-post-title">{post.title}</h3>
                      <div className="fr-post-meta">
                        <span
                          className="fr-status"
                          style={{ color: s.color, background: s.bg, border: `1px solid ${s.border}` }}
                        >
                          {s.text}
                        </span>
                        {post.tags.map(tag => (
                          <button
                            key={tag}
                            onClick={() => setActiveTag(activeTag === tag ? '' : tag)}
                            className={`com-tag${activeTag === tag ? ' com-tag-active' : ''}`}
                          >
                            {tag}
                          </button>
                        ))}
                        <span className="fr-post-author">{post.author} · {post.time}</span>
                      </div>
                    </div>
                  </div>
                </article>
              )
            })}
          </div>

          {/* Sidebar */}
          <aside className="com-sidebar">

            {/* CTA card */}
            <div className="com-cta-card">
              <div className="com-cta-title">🙋 שאל את הקהילה</div>
              <div className="com-cta-sub">שאל שאלה רפואית ותקבל מענה ממומחים ורופאים תוך שעות ספורות.</div>
              <div className="com-mini-stats">
                <div className="com-mini-stat">
                  <div className="com-mini-n">48</div>
                  <div className="com-mini-l">מומחים פעילים</div>
                </div>
                <div className="com-mini-stat">
                  <div className="com-mini-n">~3 שע׳</div>
                  <div className="com-mini-l">זמן תגובה</div>
                </div>
              </div>
              <button onClick={() => setShowModal(true)} className="com-cta-btn">
                ✏️ פתח טופס שאלה
              </button>
            </div>

            {/* Hot tags */}
            <div className="com-card">
              <div className="com-sidebar-title">🔥 תגיות חמות</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {HOT_TAGS.map(t => (
                  <button
                    key={t.label}
                    onClick={() => setActiveTag(activeTag === t.label ? '' : t.label)}
                    className={`com-tag${activeTag === t.label ? ' com-tag-active' : ''}`}
                  >
                    {t.label}
                    <span style={{ marginRight: 5, fontWeight: 900, color: '#888' }}>{t.count}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Top contributors */}
            <div className="com-card">
              <div className="com-sidebar-title">🏆 תורמים מובילים</div>
              <div>
                {[
                  { name: 'פרופ׳ לוי',  answers: 78,  votes: 1240, badge: 'מומחה', bc: '#059669' },
                  { name: 'ד"ר כהן',    answers: 52,  votes: 820,  badge: 'מאומת', bc: '#b45309' },
                  { name: 'ד"ר שרה א',  answers: 34,  votes: 570,  badge: 'מאומת', bc: '#b45309' },
                ].map(c => (
                  <div key={c.name} className="fr-contrib-row">
                    <div>
                      <div className="fr-contrib-name">{c.name}</div>
                      <div className="fr-contrib-sub">{c.answers} תשובות · {c.votes} הצבעות</div>
                    </div>
                    <span style={{
                      fontSize: 11, fontWeight: 700, padding: '3px 10px', borderRadius: 999,
                      color: c.bc, background: `${c.bc}18`, border: `1px solid ${c.bc}44`,
                    }}>
                      {c.badge}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Keyboard hint */}
            <div style={{ textAlign: 'center', fontSize: 12, color: '#888' }}>
              <span className="com-kbd">/</span> לחיפוש · <span className="com-kbd">Esc</span> לסגירה
            </div>

          </aside>
        </div>
      </div>

      {/* Footer bar */}
      <div className="com-footer-bar">Doctor Scribe AI · Medical Hub · כל הזכויות שמורות</div>

      {/* ── MODAL ── */}
      {showModal && (
        <div
          className="com-modal-overlay"
          onClick={e => { if (e.target === e.currentTarget) setShowModal(false) }}
        >
          <div className="com-modal">
            <div className="com-modal-head">
              <h3 className="com-modal-head-title">✏️ שאל שאלה</h3>
              <button onClick={() => setShowModal(false)} className="com-modal-close">✕ סגור</button>
            </div>
            <div className="com-modal-body">
              <div>
                <label className="com-modal-label">כותרת השאלה</label>
                <input className="com-modal-input" placeholder="לדוגמה: כאב גב תחתון אחרי אימון – מה הסימנים המסוכנים?" />
              </div>
              <div>
                <label className="com-modal-label">תגית ראשית</label>
                <select className="com-modal-input">
                  {HOT_TAGS.map(t => <option key={t.label}>{t.label}</option>)}
                </select>
              </div>
              <div>
                <label className="com-modal-label">פירוט (גיל, רקע, מה ניסית)</label>
                <textarea className="com-modal-input" rows={4} style={{ resize: 'vertical' }} placeholder="כתוב פרטים קצרים..." />
              </div>
            </div>
            <div className="com-modal-foot">
              <button onClick={() => setShowModal(false)} className="com-btn-cancel">ביטול</button>
              <button onClick={() => { setShowModal(false); alert('דמו: השאלה פורסמה!') }} className="com-btn-submit">
                פרסם שאלה →
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
