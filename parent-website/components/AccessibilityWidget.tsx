'use client'

import { useState, useEffect } from 'react'

type AccessSettings = {
  fontSize: number       // 0=normal, 1=large, 2=xlarge
  highContrast: boolean
  grayscale: boolean
  highlightLinks: boolean
  bigCursor: boolean
  stopAnimations: boolean
  readingGuide: boolean
}

const DEFAULTS: AccessSettings = {
  fontSize: 0,
  highContrast: false,
  grayscale: false,
  highlightLinks: false,
  bigCursor: false,
  stopAnimations: false,
  readingGuide: false,
}

const STORAGE_KEY = 'mh-accessibility'

export default function AccessibilityWidget() {
  const [open, setOpen] = useState(false)
  const [s, setS] = useState<AccessSettings>(DEFAULTS)
  const [guideY, setGuideY] = useState(-100)

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored) as AccessSettings
        setS(parsed)
        applyAll(parsed)
      }
    } catch {}
  }, [])

  // Track mouse for reading guide
  useEffect(() => {
    if (!s.readingGuide) return
    const handler = (e: MouseEvent) => setGuideY(e.clientY)
    window.addEventListener('mousemove', handler)
    return () => window.removeEventListener('mousemove', handler)
  }, [s.readingGuide])

  function applyAll(settings: AccessSettings) {
    const root = document.documentElement

    // Font size
    const sizes = ['', 'access-font-large', 'access-font-xlarge']
    root.classList.remove('access-font-large', 'access-font-xlarge')
    if (settings.fontSize > 0) root.classList.add(sizes[settings.fontSize])

    // Toggles
    root.classList.toggle('access-high-contrast', settings.highContrast)
    root.classList.toggle('access-grayscale', settings.grayscale)
    root.classList.toggle('access-highlight-links', settings.highlightLinks)
    root.classList.toggle('access-big-cursor', settings.bigCursor)
    root.classList.toggle('access-stop-animations', settings.stopAnimations)
  }

  function update(patch: Partial<AccessSettings>) {
    const next = { ...s, ...patch }
    setS(next)
    applyAll(next)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  }

  function reset() {
    setS(DEFAULTS)
    applyAll(DEFAULTS)
    localStorage.removeItem(STORAGE_KEY)
  }

  const fontLabels = ['רגיל', 'גדול', 'גדול מאוד']

  return (
    <>
      {/* Reading guide line */}
      {s.readingGuide && (
        <div
          aria-hidden="true"
          style={{
            position: 'fixed',
            top: guideY - 22,
            left: 0,
            right: 0,
            height: 44,
            background: 'rgba(255,230,0,0.18)',
            borderTop: '2px solid rgba(255,220,0,0.6)',
            borderBottom: '2px solid rgba(255,220,0,0.6)',
            pointerEvents: 'none',
            zIndex: 99998,
          }}
        />
      )}

      {/* Floating toggle button */}
      <button
        onClick={() => setOpen(o => !o)}
        aria-label="פתח תפריט נגישות"
        aria-expanded={open}
        style={{
          position: 'fixed',
          left: 0,
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 99999,
          background: open ? '#1d4ed8' : 'linear-gradient(135deg,#1e40af,#2563eb)',
          border: 'none',
          borderRadius: '0 10px 10px 0',
          width: 48,
          height: 56,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '2px 0 18px rgba(37,99,235,0.55)',
          transition: 'background 0.2s',
        }}
        title="נגישות"
      >
        {/* Wheelchair / accessibility icon */}
        <svg width="24" height="24" viewBox="0 0 24 24" fill="white" aria-hidden="true">
          <circle cx="12" cy="3.5" r="2"/>
          <path d="M9 8h4.5l2.5 5H20v2h-5l-2-4H9v3l3.5 7H10l-3-6.5V8H9zm0 0"/>
          <path d="M8.5 19.5A5.5 5.5 0 1 0 14 14h-2a3.5 3.5 0 1 1-3.5 3.5v-2h-2v2c0 3.04 2.46 5.5 5.5 5.5z" opacity=".7"/>
        </svg>
      </button>

      {/* Panel */}
      {open && (
        <div
          role="dialog"
          aria-label="תפריט נגישות"
          style={{
            position: 'fixed',
            left: 52,
            top: '50%',
            transform: 'translateY(-50%)',
            zIndex: 99998,
            background: 'rgba(10,14,30,0.97)',
            border: '1px solid rgba(37,99,235,0.45)',
            borderRadius: 14,
            padding: '20px 18px',
            width: 230,
            boxShadow: '0 8px 40px rgba(0,0,0,0.6)',
            backdropFilter: 'blur(16px)',
            display: 'flex',
            flexDirection: 'column',
            gap: 6,
            direction: 'rtl',
            maxHeight: '90vh',
            overflowY: 'auto',
          }}
        >
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
            <span style={{ fontWeight: 700, fontSize: 15, color: '#e0f2fe' }}>נגישות</span>
            <button
              onClick={() => setOpen(false)}
              aria-label="סגור"
              style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: 20, lineHeight: 1 }}
            >×</button>
          </div>

          {/* Font size */}
          <SectionLabel>גודל טקסט</SectionLabel>
          <div style={{ display: 'flex', gap: 6, marginBottom: 4 }}>
            {[0, 1, 2].map(lvl => (
              <button
                key={lvl}
                onClick={() => update({ fontSize: lvl })}
                aria-pressed={s.fontSize === lvl}
                style={{
                  flex: 1,
                  padding: '7px 4px',
                  fontSize: 11 + lvl * 2,
                  background: s.fontSize === lvl ? '#2563eb' : 'rgba(255,255,255,0.07)',
                  border: s.fontSize === lvl ? '1px solid #3b82f6' : '1px solid rgba(255,255,255,0.1)',
                  borderRadius: 8,
                  color: '#e0f2fe',
                  cursor: 'pointer',
                  transition: 'background 0.15s',
                }}
              >
                {fontLabels[lvl]}
              </button>
            ))}
          </div>

          {/* Toggles */}
          <SectionLabel>הגדרות תצוגה</SectionLabel>
          {[
            { key: 'highContrast' as const,   icon: '◑', label: 'ניגוד גבוה' },
            { key: 'grayscale' as const,       icon: '▨', label: 'גווני אפור' },
            { key: 'highlightLinks' as const,  icon: '🔗', label: 'הדגש קישורים' },
            { key: 'bigCursor' as const,       icon: '⬆', label: 'סמן גדול' },
            { key: 'stopAnimations' as const,  icon: '⏸', label: 'עצור אנימציות' },
            { key: 'readingGuide' as const,    icon: '📏', label: 'מדריך קריאה' },
          ].map(({ key, icon, label }) => (
            <ToggleRow
              key={key}
              icon={icon}
              label={label}
              active={s[key] as boolean}
              onToggle={() => update({ [key]: !s[key] })}
            />
          ))}

          {/* Reset */}
          <button
            onClick={reset}
            style={{
              marginTop: 10,
              padding: '9px',
              background: 'rgba(239,68,68,0.13)',
              border: '1px solid rgba(239,68,68,0.35)',
              borderRadius: 8,
              color: '#fca5a5',
              cursor: 'pointer',
              fontSize: 13,
              fontFamily: 'Rubik, Heebo, sans-serif',
              transition: 'background 0.15s',
            }}
            onMouseOver={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.25)')}
            onMouseOut={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.13)')}
          >
            ↺ איפוס הגדרות
          </button>

          {/* Statement link */}
          <a
            href="/accessibility"
            style={{ textAlign: 'center', marginTop: 6, fontSize: 11, color: '#64748b', textDecoration: 'underline' }}
          >
            הצהרת נגישות
          </a>
        </div>
      )}
    </>
  )
}

function SectionLabel({ children }: { children: string }) {
  return (
    <div style={{ fontSize: 11, color: '#64748b', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginTop: 4 }}>
      {children}
    </div>
  )
}

function ToggleRow({ icon, label, active, onToggle }: { icon: string; label: string; active: boolean; onToggle: () => void }) {
  return (
    <button
      onClick={onToggle}
      aria-pressed={active}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        padding: '9px 10px',
        background: active ? 'rgba(37,99,235,0.22)' : 'rgba(255,255,255,0.05)',
        border: active ? '1px solid rgba(59,130,246,0.55)' : '1px solid rgba(255,255,255,0.08)',
        borderRadius: 8,
        color: active ? '#93c5fd' : '#94a3b8',
        cursor: 'pointer',
        fontSize: 13,
        textAlign: 'right',
        transition: 'all 0.15s',
        fontFamily: 'Rubik, Heebo, sans-serif',
        width: '100%',
      }}
    >
      <span style={{ fontSize: 14, minWidth: 18 }}>{icon}</span>
      <span style={{ flex: 1 }}>{label}</span>
      {/* Toggle indicator */}
      <span style={{
        width: 30, height: 16, borderRadius: 8,
        background: active ? '#2563eb' : 'rgba(255,255,255,0.15)',
        position: 'relative', flexShrink: 0,
        transition: 'background 0.15s',
      }}>
        <span style={{
          position: 'absolute',
          top: 2, left: active ? 2 : 14,
          width: 12, height: 12,
          borderRadius: '50%',
          background: 'white',
          transition: 'left 0.15s',
        }} />
      </span>
    </button>
  )
}
