'use client'

import { useEffect, useState, useCallback } from 'react'

interface ElemInfo {
  selector: string
  width: number
  height: number
  left: number
  right: number
  paddingLeft: number
  paddingRight: number
  marginLeft: number
  marginRight: number
  overflow: string
  overflowX: string
  display: string
  position: string
  flexWrap: string
  isOverflowing: boolean
  childrenCount: number
  visibleChildren: number
}

const SELECTORS = [
  '.gh-header',
  '.gh-brand',
  '.gh-nav',
  '.gh-link',
  '.gh-btn',
  '.gh-btn-login',
  '.gh-btn-cta',
  'body',
]

function getInfo(sel: string, vw: number): ElemInfo[] {
  const els = document.querySelectorAll<HTMLElement>(sel)
  return Array.from(els).map((el) => {
    const rect = el.getBoundingClientRect()
    const cs = window.getComputedStyle(el)
    const isOverflowing = rect.right > vw + 1 || rect.left < -1
    const children = Array.from(el.children) as HTMLElement[]
    const visibleChildren = children.filter(c => {
      const cr = c.getBoundingClientRect()
      return cr.width > 0 && cr.right <= vw + 2 && cr.left >= -2
    }).length
    return {
      selector: sel,
      width: Math.round(rect.width),
      height: Math.round(rect.height),
      left: Math.round(rect.left),
      right: Math.round(rect.right),
      paddingLeft: Math.round(parseFloat(cs.paddingLeft)),
      paddingRight: Math.round(parseFloat(cs.paddingRight)),
      marginLeft: Math.round(parseFloat(cs.marginLeft)),
      marginRight: Math.round(parseFloat(cs.marginRight)),
      overflow: cs.overflow,
      overflowX: cs.overflowX,
      display: cs.display,
      position: cs.position,
      flexWrap: cs.flexWrap,
      isOverflowing,
      childrenCount: children.length,
      visibleChildren,
    }
  })
}

export default function NavDebugger() {
  const [vw, setVw] = useState(0)
  const [infos, setInfos] = useState<ElemInfo[]>([])
  const [open, setOpen] = useState(true)
  const [highlight, setHighlight] = useState(false)

  const collect = useCallback(() => {
    const w = window.innerWidth
    setVw(w)
    const all: ElemInfo[] = []
    for (const sel of SELECTORS) {
      all.push(...getInfo(sel, w))
    }
    setInfos(all)
  }, [])

  useEffect(() => {
    collect()
    window.addEventListener('resize', collect)
    return () => window.removeEventListener('resize', collect)
  }, [collect])

  // Add red outline to overflowing elements
  useEffect(() => {
    if (!highlight) {
      document.querySelectorAll<HTMLElement>('[data-dbg-outlined]').forEach(el => {
        el.style.outline = ''
        el.removeAttribute('data-dbg-outlined')
      })
      return
    }
    const vw2 = window.innerWidth
    for (const sel of SELECTORS) {
      document.querySelectorAll<HTMLElement>(sel).forEach(el => {
        const r = el.getBoundingClientRect()
        if (r.right > vw2 + 1 || r.left < -1) {
          el.style.outline = '3px solid red'
          el.setAttribute('data-dbg-outlined', '1')
        } else {
          el.style.outline = '1px solid #00ff88'
          el.setAttribute('data-dbg-outlined', '1')
        }
      })
    }
    return () => {
      document.querySelectorAll<HTMLElement>('[data-dbg-outlined]').forEach(el => {
        el.style.outline = ''
        el.removeAttribute('data-dbg-outlined')
      })
    }
  }, [highlight, vw])

  const bad = infos.filter(i => i.isOverflowing)
  const near820 = vw >= 780 && vw <= 880

  return (
    <div style={{
      position: 'fixed', bottom: 12, left: 12, zIndex: 99999,
      fontFamily: 'monospace', fontSize: '11px',
      maxWidth: open ? 420 : 44, maxHeight: open ? '80vh' : 44,
      overflow: 'hidden',
      background: 'rgba(0,0,0,0.92)', color: '#e0e0e0',
      border: `2px solid ${bad.length ? '#ff4444' : near820 ? '#ffaa00' : '#00cc66'}`,
      borderRadius: 10, transition: 'all 0.2s',
    }}>
      {/* Header bar */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '6px 10px', background: 'rgba(255,255,255,0.07)',
        cursor: 'pointer', gap: 8,
      }} onClick={() => setOpen(o => !o)}>
        <span style={{ color: bad.length ? '#ff6666' : near820 ? '#ffcc55' : '#55ff99', fontWeight: 700 }}>
          {open ? '▼' : '▶'} NAV DEBUG {vw}px {bad.length ? `⚠ ${bad.length} overflow` : '✓'}
        </span>
        {open && (
          <label style={{ cursor: 'pointer', color: '#aaa', fontSize: 10 }} onClick={e => e.stopPropagation()}>
            <input type="checkbox" checked={highlight} onChange={e => setHighlight(e.target.checked)} style={{ marginLeft: 4 }} />
            {' '}outline
          </label>
        )}
      </div>

      {open && (
        <div style={{ overflowY: 'auto', maxHeight: 'calc(80vh - 36px)', padding: '6px 0' }}>

          {/* 820 warning */}
          {near820 && (
            <div style={{ background: '#443300', padding: '4px 10px', margin: '2px 6px', borderRadius: 6, color: '#ffcc55' }}>
              ⚠ ב-820px breakpoint — בדוק overflow!
            </div>
          )}

          {/* Overflowing elements highlighted */}
          {bad.length > 0 && (
            <div style={{ background: '#440000', padding: '4px 10px', margin: '4px 6px', borderRadius: 6 }}>
              <div style={{ color: '#ff8888', fontWeight: 700 }}>גולשים מחוץ ל-viewport:</div>
              {bad.map((b, i) => (
                <div key={i} style={{ color: '#ffaaaa', paddingTop: 2 }}>
                  {b.selector} → left:{b.left} right:{b.right} (vw:{vw})
                </div>
              ))}
            </div>
          )}

          {/* Per-element table */}
          {SELECTORS.map(sel => {
            const items = infos.filter(i => i.selector === sel)
            if (!items.length) return (
              <div key={sel} style={{ padding: '2px 10px', color: '#555' }}>{sel} — לא נמצא</div>
            )
            return items.map((info, idx) => (
              <div key={`${sel}-${idx}`} style={{
                margin: '3px 6px', padding: '5px 8px', borderRadius: 6,
                background: info.isOverflowing ? 'rgba(180,0,0,0.25)' : 'rgba(255,255,255,0.04)',
                borderLeft: `3px solid ${info.isOverflowing ? '#ff4444' : '#334'}`,
              }}>
                <div style={{ color: info.isOverflowing ? '#ff8888' : '#88ccff', fontWeight: 700 }}>
                  {sel}{items.length > 1 ? ` [${idx}]` : ''}
                  {info.isOverflowing ? ' ← OVERFLOWS!' : ''}
                </div>
                <div style={{ color: '#aaa', lineHeight: 1.7 }}>
                  <span style={{ color: '#fff' }}>w:</span>{info.width}
                  {'  '}<span style={{ color: '#fff' }}>l:</span>{info.left}
                  {'  '}<span style={{ color: '#fff' }}>r:</span>
                  <span style={{ color: info.right > vw ? '#ff6666' : '#88ff99' }}>{info.right}</span>
                  {'  '}vw:{vw}
                  <br />
                  <span style={{ color: '#fff' }}>pad:</span>⬅{info.paddingLeft} ➡{info.paddingRight}
                  {'  '}<span style={{ color: '#fff' }}>mar:</span>⬅{info.marginLeft} ➡{info.marginRight}
                  <br />
                  <span style={{ color: '#fff' }}>display:</span>{info.display}
                  {'  '}<span style={{ color: '#fff' }}>pos:</span>{info.position}
                  {'  '}<span style={{ color: '#fff' }}>wrap:</span>{info.flexWrap}
                  <br />
                  <span style={{ color: '#fff' }}>overflow:</span>{info.overflow}/{info.overflowX}
                  {'  '}
                  <span style={{ color: info.visibleChildren < info.childrenCount ? '#ff8844' : '#88ff99' }}>
                    children: {info.visibleChildren}/{info.childrenCount} visible
                  </span>
                </div>
              </div>
            ))
          })}

          <div style={{ padding: '4px 10px', color: '#555', fontSize: 10 }}>
            לחץ Ctrl+R אחרי שינוי גודל לרענון
          </div>
        </div>
      )}
    </div>
  )
}
