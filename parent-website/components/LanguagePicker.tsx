'use client'

import { useState, useRef, useEffect } from 'react'
import { useLanguage } from '@/components/LanguageProvider'
import type { LangCode } from '@/lib/translations'

export const LANGUAGES: { code: LangCode; cc: string; name: string; nativeName: string }[] = [
  { code: 'he',    cc: 'il', name: 'Hebrew',              nativeName: 'עברית'     },
  { code: 'en',    cc: 'us', name: 'English',             nativeName: 'English'   },
  { code: 'ar',    cc: 'sa', name: 'Arabic',              nativeName: 'العربية'   },
  { code: 'ru',    cc: 'ru', name: 'Russian',             nativeName: 'Русский'   },
  { code: 'de',    cc: 'de', name: 'German',              nativeName: 'Deutsch'   },
  { code: 'fr',    cc: 'fr', name: 'French',              nativeName: 'Français'  },
  { code: 'es',    cc: 'es', name: 'Spanish',             nativeName: 'Español'   },
  { code: 'pt',    cc: 'br', name: 'Portuguese',          nativeName: 'Português' },
  { code: 'it',    cc: 'it', name: 'Italian',             nativeName: 'Italiano'  },
  { code: 'zh',    cc: 'cn', name: 'Chinese',             nativeName: '中文'       },
  { code: 'zh-TW', cc: 'tw', name: 'Traditional Chinese', nativeName: '繁體中文'  },
  { code: 'ko',    cc: 'kr', name: 'Korean',              nativeName: '한국어'     },
  { code: 'hi',    cc: 'in', name: 'Hindi',               nativeName: 'हिन्दी'    },
  { code: 'vi',    cc: 'vn', name: 'Vietnamese',          nativeName: 'Tiếng Việt'},
]

function FlagImg({ cc, size = 20 }: { cc: string; size?: number }) {
  const h = Math.round(size * 0.75)
  return (
    <img
      src={`https://flagcdn.com/${size}x${h}/${cc}.png`}
      srcSet={`https://flagcdn.com/${size * 2}x${h * 2}/${cc}.png 2x`}
      width={size}
      height={h}
      alt={cc}
      style={{ flexShrink: 0, display: 'block', borderRadius: 2 }}
    />
  )
}

export default function LanguagePicker() {
  const { lang, setLang } = useLanguage()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  const current = LANGUAGES.find(l => l.code === lang) ?? LANGUAGES[0]

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <div ref={ref} style={{ position: 'relative', display: 'inline-block' }}>
      {/* Globe button — shows only icon, no current language text */}
      <button
        onClick={() => setOpen(o => !o)}
        title={`Language: ${current.nativeName}`}
        aria-label="Change language"
        aria-expanded={open}
        style={{
          background: open ? 'rgba(255,255,255,0.18)' : 'rgba(255,255,255,0.08)',
          border: '1px solid rgba(255,255,255,0.2)',
          borderRadius: 8,
          padding: '6px 9px',
          color: 'white',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'background 0.2s',
        }}
      >
        {/* Globe SVG */}
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <ellipse cx="12" cy="12" rx="4" ry="10"/>
          <line x1="2" y1="12" x2="22" y2="12"/>
        </svg>
      </button>

      {open && (
        <div style={{
          position: 'absolute',
          top: 'calc(100% + 6px)',
          right: 0,
          background: '#001a5c',
          border: '1px solid rgba(255,255,255,0.15)',
          borderRadius: 12,
          minWidth: 220,
          maxHeight: 340,
          overflowY: 'auto',
          zIndex: 9999,
          boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
          direction: 'ltr',
        }}>
          {LANGUAGES.map(l => {
            const isActive = l.code === lang
            return (
              <button
                key={l.code}
                onClick={() => { setLang(l.code); setOpen(false) }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  width: '100%',
                  padding: '9px 14px',
                  background: isActive ? 'rgba(100,160,255,0.18)' : 'transparent',
                  border: 'none',
                  borderBottom: '1px solid rgba(255,255,255,0.06)',
                  color: isActive ? '#93c5fd' : 'white',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontSize: 14,
                  fontWeight: isActive ? 700 : 400,
                  transition: 'background 0.15s',
                }}
                onMouseEnter={e => { if (!isActive) (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.07)' }}
                onMouseLeave={e => { if (!isActive) (e.currentTarget as HTMLButtonElement).style.background = 'transparent' }}
              >
                <span style={{ fontSize: 20, flexShrink: 0, lineHeight: 1 }}><FlagImg cc={l.cc} size={20} /></span>
                <span style={{ flex: 1 }}>{l.nativeName}</span>
                {isActive && (
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="#93c5fd" strokeWidth="2.5" strokeLinecap="round">
                    <polyline points="2,7 6,11 12,3" />
                  </svg>
                )}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
