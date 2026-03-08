'use client'

import { useState } from 'react'
import Link from 'next/link'
import Header from '@/components/Header'

const PATIENTS = [
  { id: 1, name: 'יוסי כהן', age: 54, diagnosis: 'יתר לחץ דם', lastVisit: '22.02.2026', status: 'active' },
  { id: 2, name: 'מרים לוי', age: 67, diagnosis: 'סוכרת סוג 2', lastVisit: '20.02.2026', status: 'pending' },
  { id: 3, name: 'דוד אברהם', age: 43, diagnosis: 'כאבי גב כרוניים', lastVisit: '19.02.2026', status: 'active' },
  { id: 4, name: 'שרה גולדברג', age: 71, diagnosis: 'אי ספיקת לב', lastVisit: '18.02.2026', status: 'active' },
  { id: 5, name: 'אחמד חסן', age: 38, diagnosis: 'אסתמה', lastVisit: '17.02.2026', status: 'pending' },
  { id: 6, name: 'רחל שמיר', age: 59, diagnosis: 'ארתריטיס', lastVisit: '16.02.2026', status: 'active' },
]

const STATS = [
  { label: 'ביקורים היום', value: '12', icon: '🩺', color: '#38bdf8' },
  { label: 'מטופלים פעילים', value: '148', icon: '👥', color: '#34d399' },
  { label: 'תמלולים הושלמו', value: '9', icon: '📝', color: '#a78bfa' },
  { label: 'ממתינים לסקירה', value: '3', icon: '⏳', color: '#fb923c' },
]

const SAMPLE_TRANSCRIPT = `שלום, אני ד"ר כהן. המטופל יוסי כהן, בן 54, מגיע עם תלונות על כאבי ראש וסחרחורות לאחרונה. לחץ הדם היום 148/92. המטופל מדווח על שינה לקויה ומתח מוגבר בעבודה. מומלץ להגביר מינון אמלודיפין ל-10 מ"ג, לבצע ניטור לחץ דם ביתי פעמיים ביום, ולחזור לביקור עוד 3 שבועות.`

export default function ProductPage() {
  const [search, setSearch] = useState('')
  const [recording, setRecording] = useState(false)
  const [selectedPatient, setSelectedPatient] = useState(PATIENTS[0])

  const filtered = PATIENTS.filter(p =>
    p.name.includes(search) || p.diagnosis.includes(search)
  )

  return (
    <>
      <Header />
      <main style={{ background: 'var(--bg)', minHeight: 'calc(100vh - 64px)', padding: '24px 20px' }}>
        <div style={{ maxWidth: 1400, margin: '0 auto' }}>

          {/* Page Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
            <div>
              <h1 style={{ fontSize: 26, fontWeight: 700, color: '#e0f2fe', marginBottom: 4 }}>
                🎤 MedScribe AI — לוח בקרה
              </h1>
              <p style={{ color: 'var(--muted)', fontSize: 14 }}>ניהול מטופלים ותמלול ביקורים רפואיים</p>
            </div>
            <button
              aria-label="record visit"
              data-testid="record-button"
              onClick={() => setRecording(r => !r)}
              className="btn btn-primary"
              style={{ padding: '12px 24px', fontSize: 16, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}
            >
              {recording ? '⏹ עצור' : '🔴 הקלט ביקור'}
            </button>
          </div>

          {/* Stats Cards */}
          <div className="summary-stats" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 24 }}>
            {STATS.map(s => (
              <div key={s.label} className="card stat-card" style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '20px 24px' }}>
                <span style={{ fontSize: 36 }}>{s.icon}</span>
                <div>
                  <div style={{ fontSize: 28, fontWeight: 800, color: s.color }}>{s.value}</div>
                  <div style={{ fontSize: 13, color: 'var(--muted)' }}>{s.label}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Main content: patient list + transcription */}
          <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 20, alignItems: 'start' }}>

            {/* Patient List */}
            <div className="card patient-section" style={{ padding: 0, overflow: 'hidden' }}>
              <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
                <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>👥 רשימת מטופלים</h3>
                <input
                  type="search"
                  placeholder="חיפוש מטופל..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  className="search-input"
                  style={{ width: '100%', padding: '10px 14px', fontSize: 14 }}
                />
              </div>
              <div className="patient-list" style={{ maxHeight: 500, overflowY: 'auto' }}>
                {filtered.map(p => (
                  <div
                    key={p.id}
                    className="patient-card list-item"
                    data-testid="patient-card"
                    onClick={() => setSelectedPatient(p)}
                    style={{
                      cursor: 'pointer',
                      borderRadius: 0,
                      borderLeft: 'none', borderRight: 'none', borderTop: 'none',
                      borderBottom: '1px solid var(--border)',
                      background: selectedPatient.id === p.id ? 'rgba(56,189,248,0.08)' : 'transparent',
                      padding: '14px 20px',
                    }}
                  >
                    <div className="list-item-content">
                      <div className="list-item-title">{p.name}</div>
                      <div className="list-item-meta">{p.diagnosis} · גיל {p.age}</div>
                      <div className="list-item-meta" style={{ marginTop: 3 }}>ביקור אחרון: {p.lastVisit}</div>
                    </div>
                    <span className="tag" style={{ background: p.status === 'active' ? 'rgba(52,211,153,0.1)' : 'rgba(251,146,60,0.1)', borderColor: p.status === 'active' ? 'rgba(52,211,153,0.4)' : 'rgba(251,146,60,0.4)', color: p.status === 'active' ? '#6ee7b7' : '#fdba74' }}>
                      {p.status === 'active' ? 'פעיל' : 'ממתין'}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Transcription & Summary */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

              {/* Patient Header */}
              <div className="card" style={{ padding: '20px 24px' }}>
                <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 4 }}>{selectedPatient.name}</h3>
                <p style={{ color: 'var(--muted)', fontSize: 14 }}>{selectedPatient.diagnosis} · גיל {selectedPatient.age} · ביקור אחרון: {selectedPatient.lastVisit}</p>
              </div>

              {/* Recording Status */}
              {recording && (
                <div className="card" style={{ padding: '16px 24px', border: '1px solid rgba(239,68,68,0.4)', background: 'rgba(239,68,68,0.05)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#ef4444', display: 'inline-block', animation: 'pulse 1s infinite' }} />
                    <span style={{ color: '#fca5a5', fontWeight: 600 }}>מקליט... מדבר בבירור</span>
                  </div>
                </div>
              )}

              {/* Transcription Area */}
              <div className="card transcript-section" data-testid="transcript-area">
                <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>📄 תמלול הביקור</h3>
                <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 12, padding: '16px', fontSize: 14, lineHeight: 1.7, color: 'var(--text)', minHeight: 120 }}>
                  {SAMPLE_TRANSCRIPT}
                </div>
              </div>

              {/* Medical Summary */}
              <div className="card summary-section">
                <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>🧠 סיכום רפואי</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  {[
                    { label: 'אבחנה', value: selectedPatient.diagnosis },
                    { label: 'ממצאים', value: 'ל"ד 148/92, ניטור ביתי נדרש' },
                    { label: 'המלצות', value: 'הגברת מינון אמלודיפין ל-10 מ"ג' },
                    { label: 'מעקב', value: 'ביקור חוזר בעוד 3 שבועות' },
                  ].map(item => (
                    <div key={item.label} className="summary-field">
                      <div className="summary-field-label">{item.label}</div>
                      <div style={{ color: 'var(--text)', fontSize: 14 }}>{item.value}</div>
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
                  <button className="btn btn-secondary" style={{ flex: 1 }} data-testid="export-pdf">
                    📥 ייצוא PDF
                  </button>
                  <button className="btn btn-primary" style={{ flex: 1 }}>
                    ✉️ שלח לרשומה
                  </button>
                </div>
              </div>

            </div>
          </div>

        </div>
      </main>
    </>
  )
}
