'use client'

import { useState } from 'react'
import Header from '@/components/Header'

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
    <>
      <Header page="experts" />

      <main>
      <div style={{ maxWidth: 1300, margin: '32px auto', padding: '0 20px' }}>

        {/* Title row */}
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0, color: '#e0f2fe' }}>👨‍⚕️ מומחים רפואיים</h2>
          <p style={{ color: 'var(--muted)', margin: '6px 0 0', fontSize: 14 }}>
            48 מומחים מאומתים · זמן תגובה ממוצע ~3 שעות · 1,800+ תשובות השבוע
          </p>
        </div>

        {/* Stats row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12, marginBottom: 20 }}>
          {[
            { n: '48', label: 'מומחים מאומתים', icon: '✓' },
            { n: '~3h', label: 'זמן תגובה ממוצע', icon: '⏱' },
            { n: '12K+', label: 'תשובות סה"כ', icon: '💬' },
            { n: '4.8', label: 'דירוג ממוצע', icon: '★' },
          ].map(s => (
            <div key={s.label} className="card" style={{ textAlign: 'center', padding: '16px 12px' }}>
              <div style={{ fontSize: 22, fontWeight: 900, color: '#38bdf8' }}>{s.icon} {s.n}</div>
              <div style={{ color: 'var(--muted)', fontSize: 12, marginTop: 4 }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Search */}
        <div className="card" style={{ padding: '16px 20px', marginBottom: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
          <input
            type="text"
            className="search-input"
            style={{ flex: 1, padding: '12px 16px' }}
            placeholder="חפש מומחה לפי שם, התמחות, או תגית..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <span className="kbd">/</span>
        </div>

        {/* Specialty tabs */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap', alignItems: 'center' }}>
          {SPECIALTY_TABS.map(t => (
            <button
              key={t.id}
              onClick={() => setSpecialty(t.id)}
              className={`nav-pill ${specialty === t.id ? 'nav-pill-active' : 'nav-pill-default'}`}
            >
              {t.label}
            </button>
          ))}
          <span style={{ marginRight: 'auto', color: 'var(--muted)', fontSize: 13 }}>
            {filtered.length} מומחים
          </span>
        </div>

        {/* Experts grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20 }}>
          {filtered.length === 0 && (
            <div className="card" style={{ textAlign: 'center', padding: 48, color: 'var(--muted)', gridColumn: '1/-1' }}>
              לא נמצאו מומחים מתאימים
            </div>
          )}

          {filtered.map(expert => (
            <article key={expert.id} className="expert-card card" data-testid="expert-card" style={{ padding: '24px 20px', display: 'flex', flexDirection: 'column', gap: 0 }}>

              {/* Available badge */}
              <div style={{ marginBottom: 12 }}>
                <span style={{
                  fontSize: 11, fontWeight: 700, padding: '3px 8px', borderRadius: 999,
                  color: expert.available ? '#a7f3d0' : 'var(--muted)',
                  background: expert.available ? 'rgba(52,211,153,0.1)' : 'rgba(0,0,0,0.2)',
                  border: `1px solid ${expert.available ? 'rgba(52,211,153,0.3)' : 'var(--border)'}`,
                }}>
                  {expert.available ? '🟢 זמין' : '⏸ לא זמין'}
                </span>
              </div>

              {/* Avatar + name */}
              <div style={{ textAlign: 'center', marginBottom: 14 }}>
                <div style={{
                  width: 72, height: 72, borderRadius: '50%',
                  background: `radial-gradient(circle at 30% 30%, ${expert.color}, #1e3a5f)`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'white', fontWeight: 800, fontSize: 22,
                  margin: '0 auto 12px',
                  border: `2px solid ${expert.color}55`,
                  boxShadow: `0 0 20px ${expert.color}33`,
                }}>
                  {expert.initials}
                </div>
                <h3 style={{ fontSize: 16, fontWeight: 800, margin: '0 0 3px', color: 'var(--text)' }}>
                  {expert.name}
                  {expert.verified && <span style={{ color: '#38bdf8', fontSize: 13, marginRight: 5 }}>✓</span>}
                </h3>
                <p style={{ color: 'var(--muted)', fontSize: 13, margin: '0 0 3px' }}>{expert.title}</p>
                <p style={{ color: 'var(--muted)', fontSize: 12, margin: 0 }}>🏥 {expert.hospital} · {expert.city}</p>
              </div>

              {/* Rating */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginBottom: 12 }}>
                <Stars rating={expert.rating} />
                <span style={{ fontSize: 14, fontWeight: 700 }}>{expert.rating}</span>
                <span style={{ color: 'var(--muted)', fontSize: 12 }}>({expert.reviews})</span>
              </div>

              {/* Bio */}
              <p style={{
                color: 'var(--muted)', fontSize: 13, lineHeight: 1.55, margin: '0 0 12px',
                maxHeight: '4em', overflow: 'hidden',
              }}>
                {expert.bio}
              </p>

              {/* Tags */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 14, justifyContent: 'center' }}>
                {expert.tags.map(tag => <span key={tag} className="tag">{tag}</span>)}
              </div>

              {/* Stats */}
              <div style={{ display: 'flex', gap: 0, justifyContent: 'center', marginBottom: 16, border: '1px solid var(--border)', borderRadius: 12, overflow: 'hidden' }}>
                <div style={{ flex: 1, textAlign: 'center', padding: '10px 8px', borderLeft: '1px solid var(--border)' }}>
                  <div style={{ fontWeight: 900, fontSize: 18, color: '#38bdf8' }}>{expert.answers}</div>
                  <div style={{ color: 'var(--muted)', fontSize: 11 }}>תשובות</div>
                </div>
                <div style={{ flex: 1, textAlign: 'center', padding: '10px 8px' }}>
                  <div style={{ fontWeight: 900, fontSize: 18, color: '#38bdf8' }}>{expert.reviews}</div>
                  <div style={{ color: 'var(--muted)', fontSize: 11 }}>ביקורות</div>
                </div>
              </div>

              {/* CTA */}
              <button
                onClick={() => openModal(expert)}
                className="btn btn-primary"
                style={{ width: '100%', padding: '12px', fontSize: 14, textAlign: 'center' }}
              >
                💬 שאל את המומחה
              </button>
            </article>
          ))}
        </div>
      </div>

      {/* Ask expert modal */}
      {showModal && selected && (
        <div
          onClick={e => { if (e.target === e.currentTarget) setShowModal(false) }}
          style={{
            position: 'fixed', inset: 0, zIndex: 300,
            background: 'rgba(0,0,0,0.65)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            padding: 20,
          }}
        >
          <div style={{
            width: '100%', maxWidth: 540,
            background: 'rgba(18,26,51,0.97)',
            border: '1px solid var(--border)',
            borderRadius: 24, overflow: 'hidden',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '18px 24px', borderBottom: '1px solid var(--border)' }}>
              <h3 style={{ margin: 0, fontSize: 17, fontWeight: 800 }}>
                💬 שאל את {selected.name}
              </h3>
              <button onClick={() => setShowModal(false)} className="btn btn-secondary" style={{ padding: '8px 14px', fontSize: 13 }}>✕</button>
            </div>
            <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 14 }}>
              <p style={{ color: 'var(--muted)', fontSize: 13, margin: 0 }}>
                {selected.title} · {selected.hospital} · {selected.city}
              </p>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--muted)', marginBottom: 6 }}>נושא השאלה</label>
                <input className="search-input" style={{ width: '100%', padding: '12px 14px' }} placeholder="לדוגמה: כאב ברך לאחר ריצה" />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--muted)', marginBottom: 6 }}>פרטים (גיל, רקע, מה ניסית)</label>
                <textarea className="search-input" rows={4} style={{ width: '100%', padding: '12px 14px', resize: 'vertical' }} placeholder="כתוב פרטים קצרים..." />
              </div>
            </div>
            <div style={{ display: 'flex', gap: 10, padding: '16px 24px', borderTop: '1px solid var(--border)' }}>
              <button onClick={() => setShowModal(false)} className="btn btn-secondary">ביטול</button>
              <button
                onClick={() => { setShowModal(false); alert('דמו: שאלתך נשלחה!') }}
                className="btn btn-primary"
                style={{ flex: 1 }}
              >
                שלח שאלה →
              </button>
            </div>
          </div>
        </div>
      )}

      </main>
    </>
  )
}
