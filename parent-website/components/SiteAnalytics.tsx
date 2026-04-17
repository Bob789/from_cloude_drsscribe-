'use client'

import { useEffect, useRef } from 'react'
import { usePathname, useSearchParams } from 'next/navigation'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

/** Persistent visitor ID — survives browser restarts (localStorage) */
function getVisitorId(): string {
  if (typeof window === 'undefined') return ''
  let vid = localStorage.getItem('mh_vid')
  if (!vid) {
    vid = crypto.randomUUID()
    localStorage.setItem('mh_vid', vid)
  }
  return vid
}

/** Per-tab session ID — resets when tab/browser closes (sessionStorage) */
function getSessionId(): string {
  if (typeof window === 'undefined') return ''
  let sid = sessionStorage.getItem('mh_sid')
  if (!sid) {
    // New session: stamp the start time
    sid = crypto.randomUUID()
    sessionStorage.setItem('mh_sid', sid)
    sessionStorage.setItem('mh_sid_start', Date.now().toString())
  }
  return sid
}

function getDeviceType(): string {
  if (typeof window === 'undefined') return 'desktop'
  const w = window.innerWidth
  if (w < 768) return 'mobile'
  if (w < 1024) return 'tablet'
  return 'desktop'
}

function getUtmParams(): { utm_source?: string; utm_medium?: string; utm_campaign?: string } {
  if (typeof window === 'undefined') return {}
  const params = new URLSearchParams(window.location.search)
  const result: Record<string, string> = {}
  for (const key of ['utm_source', 'utm_medium', 'utm_campaign']) {
    const val = params.get(key)
    if (val) result[key] = val
  }
  return result
}

function extractArticleSlug(path: string): string | null {
  const match = path.match(/^\/articles\/([^/?]+)/)
  return match ? match[1] : null
}

/** Fire-and-forget beacon to analytics API */
function sendAnalytics(endpoint: string, data: Record<string, unknown>) {
  try {
    const body = JSON.stringify(data)
    if (navigator.sendBeacon) {
      navigator.sendBeacon(`${API}/analytics/${endpoint}`, new Blob([body], { type: 'application/json' }))
    } else {
      fetch(`${API}/analytics/${endpoint}`, { method: 'POST', body, headers: { 'Content-Type': 'application/json' }, keepalive: true })
    }
  } catch { /* silent — analytics should never break the site */ }
}

export function trackSearch(query: string, resultsCount: number, clickedSlug?: string) {
  sendAnalytics('search', {
    session_id: getSessionId(),
    visitor_id: getVisitorId(),
    query,
    results_count: resultsCount,
    clicked_article_slug: clickedSlug || null,
  })
}

export function trackEvent(eventType: string, eventData?: Record<string, unknown>, pagePath?: string) {
  sendAnalytics('event', {
    session_id: getSessionId(),
    visitor_id: getVisitorId(),
    event_type: eventType,
    event_data: eventData || null,
    page_path: pagePath || (typeof window !== 'undefined' ? window.location.pathname : null),
  })
}

export default function SiteAnalytics() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const enterTime = useRef<number>(Date.now())

  useEffect(() => {
    enterTime.current = Date.now()

    const sid = getSessionId()
    const vid = getVisitorId()
    if (!sid) return

    sendAnalytics('pageview', {
      session_id: sid,
      visitor_id: vid,
      page_path: pathname,
      article_slug: extractArticleSlug(pathname),
      referrer: document.referrer || null,
      device_type: getDeviceType(),
      ...getUtmParams(),
    })

    // Send duration when user leaves the page
    return () => {
      const duration = Math.round((Date.now() - enterTime.current) / 1000)
      if (duration > 0 && duration < 3600) {
        sendAnalytics('pageview', {
          session_id: sid,
          visitor_id: vid,
          page_path: pathname,
          article_slug: extractArticleSlug(pathname),
          duration_seconds: duration,
          device_type: getDeviceType(),
        })
      }
    }
  }, [pathname, searchParams])

  return null
}
