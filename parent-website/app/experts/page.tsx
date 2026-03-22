'use client'

import { useState } from 'react'
import '../community-theme.css'


type Specialty = 'all' | 'orthopedics' | 'neurology' | 'cardiology' | 'internal' | 'endocrinology' | 'psychiatry' | 'nephrology' | 'oncology'

interface Expert {
  id: number
  name: string
  title: string
  initials: string
  specialty: Exclude<Specialty, 'all'>
  hospital: string
  city: string
  rating: number
  reviews: number
  bio: string
  tags: string[]
  answers: number
  verified: boolean
  available: boolean
  color: string
}

const SPECIALTY_TABS: { id: Specialty; label: string }[] = [
  { id: 'all',           label: '👨‍⚕️ כולם'         },
  { id: 'cardiology',    label: '❤️ לב'            },
  { id: 'neurology',     label: '🧠 נוירולוגיה'    },
  { id: 'orthopedics',   label: '🦴 אורתופדיה'     },
  { id: 'internal',      label: '🏥 רפואה פנימית'  },
  { id: 'endocrinology', label: '🔬 אנדו'          },
  { id: 'psychiatry',    label: '🧘 פסיכיאטריה'    },
]

const ALL_EXPERTS: Expert[] = [
  {
    id: 1, name: 'ד"ר דניאל כהן',      title: 'מומחה אורתופדיה',      initials: 'דכ',
    specialty: 'orthopedics',   hospital: 'מרכז רפואי שיבא',   city: 'תל אביב',
    rating: 4.9, reviews: 128,
    bio: 'מומחה בכיר באורתופדיה ספורטיבית עם 15 שנות ניסיון. מתמחה בטיפול ללא ניתוח ובשיקום לאחר פציעות ספורט.',
    tags: ['כאבי גב','ספורט','שיקום'], answers: 234, verified: true, available: true,  color: '#0ea5e9',
  },
  {
    id: 2, name: 'פרופ׳ מרים לוי',      title: 'פרופסור נוירולוגיה',   initials: 'מל',
    specialty: 'neurology',     hospital: 'בית חולים הדסה',    city: 'ירושלים',
    rating: 4.8, reviews: 214,
    bio: 'פרופסור נוירולוגיה קלינית, מומחית בכאבי ראש, מיגרנה ואפילפסיה. חוקרת בכירה בתחום הנוירולוגיה.',
    tags: ['מיגרנה','נוירולוגיה','עייפות'], answers: 412, verified: true, available: false, color: '#8b5cf6',
  },
  {
    id: 3, name: 'ד"ר שרה אברמוביץ',   title: 'קרדיולוגית',            initials: 'שא',
    specialty: 'cardiology',    hospital: 'רמב"ם',               city: 'חיפה',
    rating: 4.9, reviews: 189,
    bio: 'קרדיולוגית מומחית בדימות לב וקרדיולוגיה מניעתית. מרצה בכירה בפקולטה לרפואה בטכניון.',
    tags: ['לב','כולסטרול','לחץ דם'], answers: 178, verified: true, available: true,  color: '#ef4444',
  },
  {
    id: 4, name: 'ד"ר יוסי מזרחי',     title: 'אנדוקרינולוג',          initials: 'ימ',
    specialty: 'endocrinology', hospital: 'איכילוב',             city: 'תל אביב',
    rating: 4.7, reviews: 97,
    bio: 'מומחה בסוכרת, בלוטת תריס ומחלות הורמונליות. פיתח פרוטוקולים לטיפול בסוכרת סוג 2 ללא תרופות.',
    tags: ['סוכרת','תריס','תזונה'], answers: 156, verified: true, available: true,  color: '#10b981',
  },
  {
    id: 5, name: 'פרופ׳ ריבה שמש',      title: 'מומחית רפואה פנימית',  initials: 'רש',
    specialty: 'internal',      hospital: 'סורוקה',              city: 'באר שבע',
    rating: 4.8, reviews: 143,
    bio: 'פרופסור ברפואה פנימית עם 20 שנות ניסיון. עוסקת בטיפול במחלות כרוניות ובמניעת מחלות קרדיווסקולריות.',
    tags: ['פנימית','מחלות כרוניות','מניעה'], answers: 321, verified: true, available: true,  color: '#f97316',
  },
  {
    id: 6, name: 'ד"ר אמיר זקן',       title: 'פסיכיאטר',              initials: 'אז',
    specialty: 'psychiatry',    hospital: 'גהה',                 city: 'רמת גן',
    rating: 4.6, reviews: 78,
    bio: 'פסיכיאטר מוסמך עם ניסיון רב בחרדה, דיכאון ו-CBT. מתמחה בהשפעת הדיגיטל על בריאות הנפש.',
    tags: ['חרדה','דיכאון','CBT'], answers: 98,  verified: true, available: false, color: '#a78bfa',
  },
  {
    id: 7, name: 'ד"ר נעמה כץ',        title: 'נפרולוגית',             initials: 'נכ',
    specialty: 'nephrology',    hospital: 'וולפסון',             city: 'פתח תקווה',
    rating: 4.7, reviews: 62,
    bio: 'מומחית בנפרולוגיה ומחלות כליות, עם ניסיון בדיאליזה והשתלת כליות. מרצה בבית הספר לרפואה.',
    tags: ['כליות','יתר לחץ דם','בדיקות'], answers: 74,  verified: true, available: true,  color: '#06b6d4',
  },
  {
    id: 8, name: 'פרופ׳ רון בן-דוד',   title: 'פרופסור אונקולוגיה',   initials: 'רב',
    specialty: 'oncology',      hospital: 'שיבא',                city: 'תל אביב',
    rating: 4.9, reviews: 231,
    bio: 'אחד המומחים המובילים בישראל באונקולוגיה. מתמחה בגידולים סולידיים, אימונותרפיה וטיפולים ביולוגיים.',
    tags: ['סרטן','אימונו','גנטיקה'], answers: 287, verified: true, available: false, color: '#ec4899',
  },
]

function Stars({ rating }: { rating: number }) {
  const full = Math.floor(rating)
  const half = rating - full >= 0.5
  return (
    <span style={{ color: '#fbbf24', fontSize: 15, letterSpacing: 1 }}>
      {'★'.repeat(full)}{half ? '½' : ''}{'☆'.repeat(5 - full - (half ? 1 : 0))}
    </span>
  )
}

export default function ExpertsPage() {
  const [search,    setSearch]    = useState('')
  const [specialty, setSpecialty] = useState<Specialty>('all')
  const [showModal, setShowModal] = useState(false)
  const [selected,  setSelected]  = useState<Expert | null>(null)

  const filtered = ALL_EXPERTS.filter(e => {
    const matchSearch = !search || e.name.includes(search) || e.bio.includes(search) || e.tags.some(t => t.includes(search))
    const matchSpec   = specialty === 'all' || e.specialty === specialty
    return matchSearch && matchSpec
  })

  function openModal(expert: Expert) {
    setSelected(expert)
    setShowModal(true)
  }

  return (
    <div id="experts-page-root">

      {/* ── BLOCK HEADER ── */}
      <div className="com-block-header">
        <div>
          <div className="com-block-title">👨‍⚕️ מומחים רפואיים</div>
          <div className="com-block-count">48 מומחים מאומתים · זמן תגובה ~3 שעות · 12K+ תשובות</div>
        </div>
      </div>

      {/* ── TITLE LINES ── */}
      <div className="com-title-lines">
        <div className="com-title-line"></div>
        <div className="com-title-line"></div>
      </div>

      {/* ── BODY ── */}
      <div className="com-body">

        {/* Stats bar */}
        <div className="com-stats-bar">
          {[
            { n: '48',   l: 'מומחים מאומתים', icon: '✓'  },
            { n: '~3h',  l: 'זמן תגובה ממוצע', icon: '⏱' },
            { n: '12K+', l: 'תשובות סה"כ',     icon: '💬' },
            { n: '4.8',  l: 'דירוג ממוצע',      icon: '★'  },
          ].map(s => (
            <div key={s.l} className="com-stat-tile">
              <div className="ex-stat-n">{s.icon} {s.n}</div>
              <div className="ex-stat-l">{s.l}</div>
            </div>
          ))}
        </div>

        {/* Search */}
        <div className="com-search-bar">
          <span style={{ fontSize: 16, color: '#999' }}>🔍</span>
          <input
            type="text"
            className="com-search-input"
            placeholder="חפש מומחה לפי שם, התמחות, או תגית..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <span className="com-kbd">/</span>
        </div>

        {/* Specialty pills */}
        <div className="com-pills">
          {SPECIALTY_TABS.map(t => (
            <button
              key={t.id}
              onClick={() => setSpecialty(t.id)}
              className={`com-pill${specialty === t.id ? ' com-pill-active' : ''}`}
            >
              {t.label}
            </button>
          ))}
          <span className="com-count">{filtered.length} מומחים</span>
        </div>

        {/* Experts grid */}
        <div className="ex-grid">
          {filtered.length === 0 && (
            <div className="com-card" style={{ textAlign: 'center', padding: 48, color: '#888', gridColumn: '1/-1' }}>
              לא נמצאו מומחים מתאימים
            </div>
          )}
          {filtered.map(expert => (
            <article key={expert.id} className="ex-card" data-testid="expert-card">

              {/* Availability + verified */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <span className={`ex-avail ${expert.available ? 'ex-avail-yes' : 'ex-avail-no'}`}>
                  {expert.available ? '🟢 זמין' : '⏸ לא זמין'}
                </span>
                {expert.verified && (
                  <span style={{ fontSize: 11, fontWeight: 700, color: '#1a56db', background: 'rgba(26,86,219,0.08)', padding: '3px 8px', borderRadius: 999, border: '1px solid rgba(26,86,219,0.2)' }}>
                    ✓ מאומת
                  </span>
                )}
              </div>

              {/* Avatar */}
              <div
                className="ex-avatar"
                style={{
                  background: `radial-gradient(circle at 30% 30%, ${expert.color}, #1e3a5f)`,
                  border: `2px solid ${expert.color}55`,
                  boxShadow: `0 0 20px ${expert.color}33`,
                }}
              >
                {expert.initials}
              </div>

              {/* Name + role */}
              <div className="ex-name">{expert.name}</div>
              <div className="ex-job">{expert.title}</div>
              <div className="ex-hosp">🏥 {expert.hospital} · {expert.city}</div>

              {/* Rating */}
              <div className="ex-rating-row">
                <Stars rating={expert.rating} />
                <span style={{ fontWeight: 700 }}>{expert.rating}</span>
                <span style={{ color: '#888', fontSize: 12 }}>({expert.reviews})</span>
              </div>

              {/* Bio */}
              <p className="ex-bio">{expert.bio}</p>

              {/* Tags */}
              <div className="ex-tags">
                {expert.tags.map(tag => <span key={tag} className="com-tag">{tag}</span>)}
              </div>

              {/* Stats */}
              <div className="ex-stats-row">
                <div className="ex-stat-cell">
                  <div className="ex-stat-n">{expert.answers}</div>
                  <div className="ex-stat-l">תשובות</div>
                </div>
                <div className="ex-stat-cell">
                  <div className="ex-stat-n">{expert.reviews}</div>
                  <div className="ex-stat-l">ביקורות</div>
                </div>
              </div>

              {/* CTA button */}
              <button onClick={() => openModal(expert)} className="ex-ask-btn">
                💬 שאל את המומחה
              </button>

            </article>
          ))}
        </div>
      </div>

      {/* Footer bar */}
      <div className="com-footer-bar">Doctor Scribe AI · Medical Hub · כל הזכויות שמורות</div>

      {/* ── MODAL ── */}
      {showModal && selected && (
        <div
          className="com-modal-overlay"
          onClick={e => { if (e.target === e.currentTarget) setShowModal(false) }}
        >
          <div className="com-modal">
            <div className="com-modal-head">
              <h3 className="com-modal-head-title">💬 שאל את {selected.name}</h3>
              <button onClick={() => setShowModal(false)} className="com-modal-close">✕ סגור</button>
            </div>
            <div className="com-modal-body">
              <p style={{ color: '#666', fontSize: 13, margin: 0 }}>
                {selected.title} · {selected.hospital} · {selected.city}
              </p>
              <div>
                <label className="com-modal-label">נושא השאלה</label>
                <input className="com-modal-input" placeholder="לדוגמה: כאב ברך לאחר ריצה" />
              </div>
              <div>
                <label className="com-modal-label">פרטים (גיל, רקע, מה ניסית)</label>
                <textarea className="com-modal-input" rows={4} style={{ resize: 'vertical' }} placeholder="כתוב פרטים קצרים..." />
              </div>
            </div>
            <div className="com-modal-foot">
              <button onClick={() => setShowModal(false)} className="com-btn-cancel">ביטול</button>
              <button onClick={() => { setShowModal(false); alert('דמו: שאלתך נשלחה!') }} className="com-btn-submit">
                שלח שאלה →
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
