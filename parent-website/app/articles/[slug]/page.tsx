'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import '../article-theme.css'
import { useLanguage } from '@/components/LanguageProvider'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

interface GlossaryEntry { id: string; term: string; definition: string; category: string | null }
interface TocItem { id: string; text: string; level: number; num: string }

function injectGlossaryTooltips(html: string, terms: GlossaryEntry[]): string {
  if (typeof window === 'undefined' || terms.length === 0) return html
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const sorted = [...terms].sort((a, b) => b.term.length - a.term.length)
    const skipTags = new Set(['SCRIPT', 'STYLE', 'CODE', 'PRE', 'A', 'BUTTON'])

    function walkText(node: Node) {
      if (node.nodeType === 3) {
        const text = node.textContent || ''
        for (const { term } of sorted) {
          const idx = text.indexOf(term)
          if (idx < 0) continue
          const parent = node.parentNode
          if (!parent) break
          let p: Element | null = parent as Element
          while (p) {
            if (skipTags.has(p.nodeName) || p.classList?.contains('gloss-term')) return
            p = p.parentElement
          }
          const frag = doc.createDocumentFragment()
          if (idx > 0) frag.appendChild(doc.createTextNode(text.slice(0, idx)))
          const span = doc.createElement('span')
          span.className = 'gloss-term'
          span.setAttribute('data-term', term)
          span.setAttribute('tabindex', '0')
          span.textContent = term
          frag.appendChild(span)
          if (idx + term.length < text.length) frag.appendChild(doc.createTextNode(text.slice(idx + term.length)))
          parent.replaceChild(frag, node)
          return
        }
      } else if (node.nodeType === 1) {
        const el = node as Element
        if (skipTags.has(el.tagName) || el.classList?.contains('gloss-term')) return
        Array.from(node.childNodes).forEach(walkText)
      }
    }

    walkText(doc.body)
    return doc.body.innerHTML
  } catch {
    return html
  }
}

function extractToc(html: string): TocItem[] {
  if (typeof window === 'undefined') return []
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const headings = Array.from(doc.querySelectorAll('h2, h3'))
  return headings.map((el, i) => ({
    id: el.id || `section-${i}`,
    text: el.textContent?.trim() || '',
    level: parseInt(el.tagName[1]),
    num: String(i + 1).padStart(2, '0'),
  })).filter(h => h.text)
}

function ensureHeadingIds(html: string): string {
  if (typeof window === 'undefined') return html
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  let i = 0
  doc.querySelectorAll('h2, h3').forEach(el => {
    if (!el.id) el.id = `section-${i}`
    i++
  })
  return doc.body.innerHTML
}

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>()
  const searchParams = useSearchParams()
  const { t, lang } = useLanguage()
  const [article, setArticle] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [related, setRelated] = useState<any[]>([])
  const [processedHtml, setProcessedHtml] = useState<string>('')
  const [glossary, setGlossary] = useState<GlossaryEntry[]>([])
  const [toc, setToc] = useState<TocItem[]>([])
  const [activeToc, setActiveToc] = useState<string>('')
  const [readPct, setReadPct] = useState(0)
  const [liked, setLiked] = useState(false)
  const [saved, setSaved] = useState(false)
  const [feedbackVote, setFeedbackVote] = useState<'yes' | 'no' | null>(null)
  const bodyRef = useRef<HTMLDivElement>(null)

  const [prevArticle, setPrevArticle] = useState<any>(null)
  const [nextArticle, setNextArticle] = useState<any>(null)
  const [comments, setComments] = useState<any[]>([])
  const [commentBody, setCommentBody] = useState('')
  const [commentLoading, setCommentLoading] = useState(false)
  const [commentError, setCommentError] = useState('')
  const [currentUser, setCurrentUser] = useState<any>(null)

  useEffect(() => {
    try {
      const raw = localStorage.getItem('user')
      const token = localStorage.getItem('access_token')
      if (raw && token) setCurrentUser(JSON.parse(raw))
    } catch {}
    const onAuth = () => {
      try {
        const raw = localStorage.getItem('user')
        const token = localStorage.getItem('access_token')
        if (raw && token) setCurrentUser(JSON.parse(raw))
        else setCurrentUser(null)
      } catch {}
    }
    window.addEventListener('auth-changed', onAuth)
    return () => window.removeEventListener('auth-changed', onAuth)
  }, [])

  useEffect(() => {
    async function load() {
      try {
        const preview = searchParams.get('preview') ? '?preview=1' : ''
        const [res, glossRes, commentsRes] = await Promise.all([
          fetch(`${API}/articles/${slug}${preview}`),
          fetch(`${API}/glossary`),
          fetch(`${API}/articles/${slug}/comments`),
        ])
        const data = await res.json()
        const glossData: GlossaryEntry[] = glossRes.ok ? await glossRes.json() : []
        const commentsData = commentsRes.ok ? await commentsRes.json() : []
        setArticle(data)
        setGlossary(glossData)
        setComments(commentsData)

        if (data.category) {
          const relRes = await fetch(`${API}/articles?category=${data.category}&per_page=50`)
          const relData = await relRes.json()
          const allInCat: any[] = relData.items || []
          setRelated(allInCat.filter((a: any) => a.slug !== slug).slice(0, 3))
          const idx = allInCat.findIndex((a: any) => a.slug === slug)
          if (idx > 0) setPrevArticle(allInCat[idx - 1])
          if (idx >= 0 && idx < allInCat.length - 1) setNextArticle(allInCat[idx + 1])
        }
      } catch { setError(true) }
      finally { setLoading(false) }
    }
    load()
  }, [slug, searchParams])

  useEffect(() => {
    if (!article?.content_html) return
    let html = ensureHeadingIds(article.content_html)

    if (article.hero_image_url) {
      const alt = (article.hero_image_alt || article.title || '').replace(/"/g, '&quot;')
      const src = article.hero_image_url.replace(/"/g, '%22')
      const imgHtml = `<div class="article-accent-img"><img src="${src}" alt="${alt}" /></div>`
      if (/<\/h[123]>/i.test(html)) {
        html = html.replace(/<\/h[123]>/i, (m: string) => m + imgHtml)
      } else {
        html = html.replace(/<p/i, imgHtml + '<p')
      }
    }

    const withGloss = glossary.length > 0 ? injectGlossaryTooltips(html, glossary) : html
    setProcessedHtml(withGloss)
    setToc(extractToc(html))
  }, [article, glossary])

  // Reading progress & active TOC
  useEffect(() => {
    function onScroll() {
      const scrollTop = window.scrollY
      const docH = document.documentElement.scrollHeight - window.innerHeight
      setReadPct(Math.min(100, Math.max(0, Math.round((scrollTop / docH) * 100))))

      if (!bodyRef.current) return
      const scroll = scrollTop + 140
      const sections = toc.map(item => document.getElementById(item.id)).filter(Boolean) as HTMLElement[]
      let active = sections[0]?.id || ''
      for (const s of sections) {
        if (s.offsetTop <= scroll) active = s.id
      }
      setActiveToc(active)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [toc])

  // Glossary tooltip singleton
  useEffect(() => {
    if (!processedHtml || glossary.length === 0) return
    const glossMap: Record<string, string> = {}
    glossary.forEach(g => { glossMap[g.term] = g.definition })

    const tip = document.createElement('div')
    tip.className = 'gloss-tooltip'
    tip.innerHTML = '<div class="gt-head"><span class="gt-ico">ℹ</span><span class="gt-term"></span></div><div class="gt-body"></div><div class="gt-arrow"></div>'
    document.body.appendChild(tip)

    const tipTerm = tip.querySelector('.gt-term') as HTMLElement
    const tipBody = tip.querySelector('.gt-body') as HTMLElement

    function showTip(el: Element) {
      const t = el.getAttribute('data-term') || ''
      const def = glossMap[t]
      if (!def) return
      tipTerm.textContent = t
      tipBody.textContent = def
      tip.classList.add('show')
      const r = el.getBoundingClientRect()
      const tw = 320
      let left = r.left + r.width / 2 - tw / 2 + window.scrollX
      left = Math.max(12, Math.min(left, window.innerWidth - tw - 12))
      tip.style.left = left + 'px'
      tip.style.top = (r.top + window.scrollY - tip.offsetHeight - 12) + 'px'
      const arrow = tip.querySelector('.gt-arrow') as HTMLElement
      if (arrow) arrow.style.left = (r.left + r.width / 2 - left) + 'px'
    }
    function hideTip() { tip.classList.remove('show') }

    const onOver = (e: Event) => {
      const t = (e.target as Element).closest?.('.gloss-term')
      if (t) showTip(t)
    }
    const onOut = (e: Event) => {
      const t = (e.target as Element).closest?.('.gloss-term')
      if (t) hideTip()
    }
    const onFocusIn = (e: Event) => {
      const t = e.target as Element
      if (t.classList?.contains('gloss-term')) showTip(t)
    }
    const onFocusOut = (e: Event) => {
      const t = e.target as Element
      if (t.classList?.contains('gloss-term')) hideTip()
    }

    document.addEventListener('mouseover', onOver)
    document.addEventListener('mouseout', onOut)
    document.addEventListener('focusin', onFocusIn)
    document.addEventListener('focusout', onFocusOut)

    return () => {
      document.removeEventListener('mouseover', onOver)
      document.removeEventListener('mouseout', onOut)
      document.removeEventListener('focusin', onFocusIn)
      document.removeEventListener('focusout', onFocusOut)
      tip.remove()
    }
  }, [processedHtml, glossary])

  const scrollToSection = useCallback((id: string) => {
    const el = document.getElementById(id)
    if (el) window.scrollTo({ top: el.offsetTop - 100, behavior: 'smooth' })
  }, [])

  const handleLike = async () => {
    await fetch(`${API}/articles/${slug}/like`, { method: 'POST' })
    setLiked(l => !l)
  }

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!commentBody.trim()) return
    setCommentLoading(true)
    setCommentError('')
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(`${API}/articles/${slug}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ body: commentBody.trim() }),
      })
      if (!res.ok) throw new Error()
      const newComment = await res.json()
      setComments(prev => [...prev, newComment])
      setCommentBody('')
    } catch { setCommentError(t('comment_error')) } finally {
      setCommentLoading(false)
    }
  }

  if (loading) return (
    <main style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center', direction: 'rtl' }}>
      <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: 16 }}>{t('article_loading')}</div>
    </main>
  )

  if (error || !article) return (
    <main style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16, direction: 'rtl' }}>
      <h1 style={{ fontSize: 28, color: 'white' }}>{t('article_not_found')}</h1>
      <Link href="/articles" style={{ color: '#fcf9c6' }}>{t('article_back_to_list')}</Link>
    </main>
  )

  const categoryLabels: Record<string, string> = {
    cardiology: t('cat_cardiology'), neurology: t('cat_neurology'), orthopedics: t('cat_orthopedics'),
    nutrition: t('cat_nutrition'), sleep: t('cat_sleep'), mental: t('cat_mental'), general: t('cat_general'),
    dermatology: t('cat_dermatology'), gastroenterology: t('cat_gastroenterology'), urology: t('cat_urology'),
  }
  const categoryLabel = categoryLabels[article.category] || article.category
  const authorInitials = article.author_name
    ? article.author_name.split(' ').map((w: string) => w[0]).slice(0, 2).join('')
    : 'ד"ר'

  const publishDate = article.published_at
    ? new Date(article.published_at).toLocaleDateString('he-IL', { day: 'numeric', month: 'short', year: 'numeric' })
    : ''

  return (
    <>
      <head>
        <title>{article.seo_title || article.title} | Medical Hub</title>
        <meta name="description" content={article.seo_description || article.summary || ''} />
        {article.seo_keywords?.length > 0 && <meta name="keywords" content={article.seo_keywords.join(', ')} />}
        <meta property="og:title" content={article.title} />
        <meta property="og:description" content={article.summary || ''} />
        <meta property="og:type" content="article" />
        <meta property="og:url" content={`https://medicalhub.co.il/articles/${slug}`} />
        {article.hero_image_url && <meta property="og:image" content={article.hero_image_url} />}
        <meta name="robots" content="index, follow" />
        <link rel="canonical" href={`https://medicalhub.co.il/articles/${slug}`} />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Article',
              headline: article.title,
              description: article.seo_description || article.summary || '',
              image: article.hero_image_url || undefined,
              author: { '@type': 'Person', name: article.author_name },
              datePublished: article.published_at || article.created_at,
              dateModified: article.updated_at || article.created_at,
              publisher: { '@type': 'Organization', name: 'Medical Hub' },
              mainEntityOfPage: `https://medicalhub.co.il/articles/${slug}`,
            }),
          }}
        />
      </head>

      <div className="art-detail">

        {/* Crumb bar with prev/next */}
        <div className="crumb-bar">
          <div className="crumb-inner">
            <div className="crumbs">
              <Link href="/">דף הבית</Link>
              <span className="sep">›</span>
              <Link href="/articles">מאמרים</Link>
              <span className="sep">›</span>
              <Link href={`/articles?category=${article.category}`}>{categoryLabel}</Link>
              <span className="sep">›</span>
              <span className="current">{article.title.length > 40 ? article.title.slice(0, 40) + '…' : article.title}</span>
            </div>
            <div className="crumb-right">
              <Link href="/articles">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
                חזרה לרשימה
              </Link>
              {prevArticle && (
                <Link href={`/articles/${prevArticle.slug}`}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
                  מאמר קודם
                </Link>
              )}
              {nextArticle && (
                <Link href={`/articles/${nextArticle.slug}`}>
                  מאמר הבא
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
                </Link>
              )}
            </div>
          </div>
        </div>

        {/* Layout */}
        <div className="art-d-layout">

          {/* Sidebar */}
          <aside className="art-d-aside">

            {/* TOC */}
            {toc.length > 0 && (
              <div className="art-d-aside-card">
                <div className="art-d-aside-h">תוכן המאמר</div>
                <div className="art-d-aside-body">
                  <ul className="art-d-toc">
                    {toc.map(item => (
                      <li key={item.id}>
                        <a
                          href={`#${item.id}`}
                          className={activeToc === item.id ? 'toc-active' : ''}
                          onClick={e => { e.preventDefault(); scrollToSection(item.id) }}
                        >
                          <span className="toc-num">{item.num}</span>
                          {item.text.length > 40 ? item.text.slice(0, 40) + '…' : item.text}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Author */}
            <div className="art-d-aside-card">
              <div className="art-d-author-card">
                <div className="art-d-author-ava">{authorInitials}</div>
                <div className="art-d-author-name">{article.author_name}</div>
                {article.author_title && (
                  <div className="art-d-author-title">{article.author_title}</div>
                )}
                <div className="art-d-author-bio">מאמרים רפואיים מבוססי ראיות, מותאמים לקהל הרחב.</div>
              </div>
            </div>

            {/* Meta stats */}
            <div className="art-d-aside-card art-d-meta-card">
              {article.read_time_minutes && (
                <div className="art-d-meta-row">
                  <div className="ico">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                  </div>
                  <div><strong>{article.read_time_minutes} דקות</strong> קריאה</div>
                </div>
              )}
              {publishDate && (
                <div className="art-d-meta-row">
                  <div className="ico">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  </div>
                  <div>פורסם <strong>{publishDate}</strong></div>
                </div>
              )}
              {article.views > 0 && (
                <div className="art-d-meta-row">
                  <div className="ico">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  </div>
                  <div><strong>{article.views.toLocaleString()}</strong> צפיות</div>
                </div>
              )}
            </div>

          </aside>

          {/* Article */}
          <main>
            <article className="art-d-article">

              {/* Hero */}
              <div className="art-d-hero">
                <div className="art-d-cat">
                  <span className="dot"></span>
                  {categoryLabel}
                </div>
                <h1 className="art-d-title">{article.title}</h1>
                {(article.subtitle || article.summary) && (
                  <p className="art-d-sub">{article.subtitle || article.summary}</p>
                )}
                <div className="art-d-hero-meta">
                  <div className="art-d-hm-item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                    נכתב ע״י <strong>{article.author_name}</strong>
                    {article.author_title && <span style={{ opacity: .7 }}> · {article.author_title}</span>}
                  </div>
                  {article.read_time_minutes && (
                    <>
                      <div className="art-d-hm-sep"></div>
                      <div className="art-d-hm-item">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        <strong>{article.read_time_minutes} דקות</strong> קריאה
                      </div>
                    </>
                  )}
                  {publishDate && (
                    <>
                      <div className="art-d-hm-sep"></div>
                      <div className="art-d-hm-item">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                        {publishDate}
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Action strip */}
              <div className="art-d-strip">
                <div className="art-d-progress">
                  <span>התקדמות</span>
                  <div className="bar">
                    <span className="fill" style={{ width: `${readPct}%` }}></span>
                  </div>
                  <span>{readPct}%</span>
                </div>
                <div className="art-d-actions">
                  <button
                    className={`art-d-btn${liked ? ' liked' : ''}`}
                    onClick={handleLike}
                  >
                    <svg viewBox="0 0 24 24" fill={liked ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                    </svg>
                    {article.likes || 0}
                  </button>
                  <button
                    className={`art-d-btn${saved ? ' saved' : ''}`}
                    onClick={() => setSaved(s => !s)}
                  >
                    <svg viewBox="0 0 24 24" fill={saved ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
                    </svg>
                    {saved ? 'נשמר ✓' : 'שמור'}
                  </button>
                  <button
                    className="art-d-btn"
                    onClick={async () => {
                      try {
                        if (navigator.share) await navigator.share({ title: article.title, url: location.href })
                        else { await navigator.clipboard.writeText(location.href); alert('הקישור הועתק') }
                      } catch {}
                    }}
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
                      <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
                    </svg>
                    שתף
                  </button>
                  <button className="art-d-btn" onClick={() => window.print()}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="6 9 6 2 18 2 18 9"/>
                      <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
                      <rect x="6" y="14" width="12" height="8"/>
                    </svg>
                    הדפס
                  </button>
                </div>
              </div>

              {/* Body */}
              <div className="art-d-body" ref={bodyRef}>
                <div dangerouslySetInnerHTML={{ __html: processedHtml || article.content_html || '' }} />
              </div>

              {/* Author footer */}
              <div className="author-footer">
                <div className="af-ava">{authorInitials}</div>
                <div className="af-info">
                  <h5>{article.author_name}</h5>
                  {article.author_title && <div className="af-t">{article.author_title}</div>}
                  <p>מאמרים רפואיים מבוססי ראיות, מותאמים לקהל הרחב.</p>
                </div>
                <a href="#" className="af-cta">עקוב אחרי</a>
              </div>

              {/* Tags */}
              {article.tags?.length > 0 && (
                <div className="art-d-tags" style={{ marginTop: 8 }}>
                  <span className="art-d-tags-label">תגיות:</span>
                  {article.tags.map((tag: string) => (
                    <Link key={tag} href={`/articles/tag/${encodeURIComponent(tag)}`} className="art-d-tag">
                      #{tag}
                    </Link>
                  ))}
                </div>
              )}

              {/* Feedback */}
              <div className="art-d-feedback">
                <div className="art-d-feedback-inner">
                  <h4>האם המאמר הזה עזר לכם?</h4>
                  <div className="art-d-fb-btns">
                    <button
                      className={`art-d-fb-btn yes${feedbackVote === 'yes' ? ' voted' : ''}`}
                      onClick={() => setFeedbackVote('yes')}
                    >
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H7V10l4.34-8a1.45 1.45 0 0 1 2.64 1L15 5.88z"/></svg>
                      כן, עזר מאוד
                    </button>
                    <button
                      className={`art-d-fb-btn no${feedbackVote === 'no' ? ' voted' : ''}`}
                      onClick={() => setFeedbackVote('no')}
                    >
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H17v12l-4.34 8a1.45 1.45 0 0 1-2.64-1L9 18.12z"/></svg>
                      לא ממש
                    </button>
                    <button className="art-d-fb-btn">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                      הוסף תגובה
                    </button>
                  </div>
                </div>
              </div>

              {/* Comments */}
              <div className="art-d-comments">
                <div className="art-d-comments-title">
                  {t('comments_title', { n: comments.length })}
                </div>

                {comments.length === 0 && (
                  <p style={{ color: '#5a6d92', fontSize: 14, marginBottom: 20 }}>{t('comments_first')}</p>
                )}

                {comments.map((c: any) => (
                  <div key={c.id} style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
                    <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(13,35,82,0.1)', flexShrink: 0, overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      {c.author_avatar
                        ? <img src={c.author_avatar} alt={c.author_name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        : <span style={{ color: '#5a6d92', fontSize: 16 }}>👤</span>
                      }
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', marginBottom: 4 }}>
                        <span style={{ color: '#0d2352', fontWeight: 600, fontSize: 14 }}>{c.author_name}</span>
                        <span style={{ color: '#8693b0', fontSize: 12 }}>
                          {new Date(c.created_at).toLocaleDateString('he-IL', { day: 'numeric', month: 'short', year: 'numeric' })}
                        </span>
                      </div>
                      <p style={{ color: '#2a3f6b', fontSize: 15, lineHeight: 1.6, margin: 0, whiteSpace: 'pre-wrap' }}>{c.body}</p>
                    </div>
                  </div>
                ))}

                {currentUser ? (
                  <form onSubmit={handleAddComment} style={{ marginTop: 20 }}>
                    <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                      <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'rgba(13,35,82,0.1)', flexShrink: 0, overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {currentUser.avatar_url
                          ? <img src={currentUser.avatar_url} alt={currentUser.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                          : <span style={{ color: '#5a6d92', fontSize: 14 }}>👤</span>
                        }
                      </div>
                      <div style={{ flex: 1 }}>
                        <textarea
                          value={commentBody}
                          onChange={e => setCommentBody(e.target.value)}
                          placeholder={t('comment_placeholder')}
                          rows={3}
                          maxLength={2000}
                          style={{ width: '100%', background: 'rgba(13,35,82,0.05)', border: '1px solid rgba(13,35,82,0.15)', borderRadius: 10, padding: '10px 14px', color: '#0d2352', fontSize: 14, resize: 'vertical', fontFamily: 'inherit', boxSizing: 'border-box' }}
                        />
                        {commentError && <p style={{ color: '#e53947', fontSize: 13, margin: '4px 0 0' }}>{commentError}</p>}
                        <button
                          type="submit"
                          disabled={commentLoading || !commentBody.trim()}
                          style={{ marginTop: 8, background: '#123078', color: 'white', border: 'none', borderRadius: 8, padding: '8px 20px', fontSize: 14, fontWeight: 600, cursor: commentLoading || !commentBody.trim() ? 'not-allowed' : 'pointer', opacity: commentLoading || !commentBody.trim() ? 0.6 : 1 }}
                        >
                          {commentLoading ? t('comment_submitting') : t('comment_submit')}
                        </button>
                      </div>
                    </div>
                  </form>
                ) : (
                  <div style={{ marginTop: 16, padding: '14px 18px', background: 'rgba(13,35,82,0.05)', borderRadius: 10, border: '1px solid rgba(13,35,82,0.1)', textAlign: 'center' }}>
                    <span style={{ color: '#5a6d92', fontSize: 14 }}>
                      <Link href={`${process.env.NEXT_PUBLIC_MEDSCRIBE_URL || 'https://app.drsscribe.com'}/login`} style={{ color: '#123078', fontWeight: 600 }}>{t('comment_login_prompt')}</Link>
                      {' '}{t('comment_login_link')}
                    </span>
                  </div>
                )}
              </div>

            </article>

            {/* Related */}
            {related.length > 0 && (
              <section className="art-d-related">
                <div className="art-d-related-h">מאמרים דומים</div>
                <div className="art-d-related-grid">
                  {related.map((r: any) => (
                    <Link key={r.slug} href={`/articles/${r.slug}`} className="art-d-rel-card">
                      <div className="art-d-rel-thumb">
                        {r.hero_image_url
                          ? <img src={r.hero_image_url} alt={r.title} />
                          : <div className="no-img">{String(related.indexOf(r) + 1).padStart(2, '0')}</div>
                        }
                      </div>
                      <div className="art-d-rel-body">
                        <div className="art-d-rel-cat">{categoryLabels[r.category] || r.category}</div>
                        <div className="art-d-rel-title">{r.title}</div>
                        {r.summary && (
                          <div className="art-d-rel-desc">
                            {r.summary.length > 80 ? r.summary.slice(0, 80) + '...' : r.summary}
                          </div>
                        )}
                        <div className="art-d-rel-meta">
                          <span className="r">{r.author_name}</span>
                          {r.read_time_minutes && <span>{r.read_time_minutes} דק׳ קריאה</span>}
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* Disclaimer */}
            <div className="art-d-disclaimer">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              <div>
                <strong>{t('legal_title')}</strong>{' '}
                {t('legal_text1')} {t('legal_text2')}
              </div>
            </div>

          </main>
        </div>

        <div className="art-d-footer">
          Doctor Scribe AI · Medical Hub · כל הזכויות שמורות
        </div>

      </div>
    </>
  )
}
