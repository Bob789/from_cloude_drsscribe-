'use client'

import { useState, useEffect, useRef, useCallback } from 'react'

export interface FeedItem {
  id: number
  title: string
  meta: string
  tag: string
  gradient: [string, string]
  icon: string
}

interface Props {
  items: FeedItem[]
  visibleCount?: number
  intervalMs?: number
  label?: string
}

const ITEM_HEIGHT = 74

export default function ScrollingFeed({ items, visibleCount = 7, intervalMs = 2800, label = 'Feed' }: Props) {
  const [startIdx, setStartIdx] = useState(0)
  const [sliding, setSliding] = useState(false)
  const isRunning = useRef(false)

  const advance = useCallback(() => {
    if (isRunning.current) return
    isRunning.current = true
    setSliding(true)
    setTimeout(() => {
      setStartIdx(prev => {
        const next = (prev + 1) % items.length
        console.debug(`[ScrollingFeed:${label}] slide → idx ${next}`)
        return next
      })
      setSliding(false)
      isRunning.current = false
    }, 480)
  }, [items.length, label])

  useEffect(() => {
    if (items.length < 2) {
      console.warn(`[ScrollingFeed:${label}] need at least 2 items`)
      return
    }
    console.debug(`[ScrollingFeed:${label}] mounted, ${items.length} items, interval ${intervalMs}ms`)
    const id = setInterval(advance, intervalMs)
    return () => {
      clearInterval(id)
      console.debug(`[ScrollingFeed:${label}] unmounted`)
    }
  }, [advance, intervalMs, items.length, label])

  const renderCount = Math.min(visibleCount + 1, items.length)
  const visible = Array.from({ length: renderCount }, (_, i) => {
    const idx = (startIdx + i) % items.length
    return { item: items[idx], uid: `${idx}-${i}` }
  })

  return (
    <div style={{ overflow: 'hidden', height: ITEM_HEIGHT * visibleCount, position: 'relative' }}>
      <div
        style={{
          transform: sliding ? `translateY(-${ITEM_HEIGHT}px)` : 'translateY(0)',
          transition: sliding ? 'transform 0.48s cubic-bezier(0.4,0,0.2,1)' : 'none',
          willChange: 'transform',
        }}
      >
        {visible.map(({ item, uid }) => (
          <div
            key={uid}
            className="list-item"
            style={{ height: ITEM_HEIGHT, cursor: 'pointer', alignItems: 'center', padding: '0 12px', gap: 12 }}
          >
            <div style={{
              width: 50,
              height: 50,
              borderRadius: 12,
              background: `linear-gradient(135deg, ${item.gradient[0]}, ${item.gradient[1]})`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 24,
              flexShrink: 0,
              boxShadow: `0 4px 12px ${item.gradient[0]}55`,
            }}>
              {item.icon}
            </div>
            <div className="list-item-content" style={{ minWidth: 0 }}>
              <div className="list-item-title" style={{ fontSize: 13, lineHeight: 1.3, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {item.title}
              </div>
              <div className="list-item-meta" style={{ marginTop: 3 }}>{item.meta}</div>
            </div>
            <span className="tag" style={{ flexShrink: 0 }}>{item.tag}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
