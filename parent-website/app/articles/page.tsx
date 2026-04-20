'use client'

import Link from 'next/link'
import { useEffect, useMemo, useState } from 'react'
import './article-theme.css'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

type ArticleCategory = 'cardio' | 'neuro' | 'ortho' | 'derm' | 'pedia' | 'general'
type TopFilter = 'all' | 'new' | 'popular' | 'bookmarked'
type SortMode = 'recent' | 'popular' | 'likes' | 'az'

type ArticleItem = {
  id: string
  slug?: string
  title: string
  summary?: string
  category?: string
  tags?: string[]
  author_name?: string
  created_at?: string
  views?: number
  likes?: number
  read_time_minutes?: number
  hero_image_url?: string
}

const categoryMap: Record<ArticleCategory, string> = {
  cardio: 'קרדיולוגיה',
  neuro: 'נוירולוגיה',
  ortho: 'אורתופדיה',
  derm: 'דרמטולוגיה',
  pedia: 'רפואת ילדים',
  general: 'רפואה כללית',
}

function normalizeCategory(raw: string | undefined): ArticleCategory {
  const val = (raw || '').toLowerCase().trim()
  if (val.includes('cardio') || val.includes('לב') || val.includes('קרד')) return 'cardio'
  if (val.includes('neuro') || val.includes('נויר')) return 'neuro'
  if (val.includes('ortho') || val.includes('אורתו') || val.includes('עצם')) return 'ortho'
  if (val.includes('derm') || val.includes('עור') || val.includes('דרמט')) return 'derm'
  if (val.includes('pedia') || val.includes('ילד')) return 'pedia'
  return 'general'
}

function articleDate(date: string | undefined): string {
  if (!date) return '-'
  const d = new Date(date)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('he-IL')
}

function initials(name: string | undefined): string {
  if (!name) return 'MD'
  const p = name.trim().split(/\s+/).filter(Boolean)
  if (p.length === 0) return 'MD'
  return (p[0][0] + (p[1]?.[0] || '')).toUpperCase()
}

export default function ArticlesPage() {
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<'all' | ArticleCategory>('all')
  const [activeTag, setActiveTag] = useState('')
  const [topFilter, setTopFilter] = useState<TopFilter>('all')
  const [sortMode, setSortMode] = useState<SortMode>('recent')
  const [articles, setArticles] = useState<ArticleItem[]>([])
  const [loading, setLoading] = useState(true)
  const [fetchError, setFetchError] = useState('')
  const [totalCount, setTotalCount] = useState(0)
  const [liked, setLiked] = useState<Set<string>>(new Set())
  const [bookmarked, setBookmarked] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (typeof window === 'undefined') return
    try {
      const l = JSON.parse(localStorage.getItem('mh_liked') || '[]')
      const b = JSON.parse(localStorage.getItem('mh_bookmark') || '[]')
      setLiked(new Set((l || []).map((x: any) => String(x))))
      setBookmarked(new Set((b || []).map((x: any) => String(x))))
    } catch {
      setLiked(new Set())
      setBookmarked(new Set())
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    const controller = new AbortController()
    setLoading(true)
    setFetchError('')

    const params = new URLSearchParams()
    if (selectedCategory !== 'all') params.set('category', selectedCategory)
    if (search) params.set('search', search)
    if (activeTag) params.set('tag', activeTag)
    params.set('sort', sortMode === 'popular' ? 'popular' : 'newest')
    params.set('per_page', '50')
    params.set('page', '1')

    const endpointCandidates = [
      API,
      'http://localhost:8000/api',
      'https://app.drsscribe.com/api',
    ].filter((value, index, all) => Boolean(value) && all.indexOf(value) === index)

    ;(async () => {
      for (const base of endpointCandidates) {
        try {
          const response = await fetch(`${base}/articles?${params}`, { signal: controller.signal })
          if (!response.ok) continue

          const data = await response.json()
          const items = Array.isArray(data?.items) ? data.items : []
          const total = Number(data?.total) || items.length

          if (!cancelled) {
            setArticles(items)
            setTotalCount(total)
            setFetchError('')
          }
          return
        } catch (error) {
          const maybeError = error as { name?: string }
          if (maybeError?.name === 'AbortError') return
        }
      }

      if (!cancelled) {
        setArticles([])
        setTotalCount(0)
        setFetchError('שגיאה בטעינת המאמרים מהשרת. נסה רענון או בדוק שה־API פעיל.')
      }
    })()
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
      controller.abort()
    }
  }, [selectedCategory, search, activeTag, sortMode])

  const allTags = useMemo(() => {
    return [...new Set(articles.flatMap(a => a.tags || []))].slice(0, 24)
  }, [articles])

  const categoryCounts = useMemo(() => {
    const m: Record<ArticleCategory, number> = {
      cardio: 0,
      neuro: 0,
      ortho: 0,
      derm: 0,
      pedia: 0,
      general: 0,
    }
    articles.forEach(a => {
      m[normalizeCategory(a.category)] += 1
    })
    return m
  }, [articles])

  const topAuthors = useMemo(() => {
    const map = new Map<string, number>()
    articles.forEach(a => {
      const n = a.author_name || 'צוות MedicalHub'
      map.set(n, (map.get(n) || 0) + 1)
    })
    return [...map.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([name, count]) => ({ name, count }))
  }, [articles])

  const decorated = useMemo(() => {
    const now = Date.now()
    return articles.map(a => {
      const created = a.created_at ? new Date(a.created_at).getTime() : 0
      const days = created > 0 ? (now - created) / (1000 * 60 * 60 * 24) : 999
      return {
        ...a,
        id: String(a.id),
        categoryKey: normalizeCategory(a.category),
        categoryLabel: categoryMap[normalizeCategory(a.category)],
        isNew: days <= 14,
        isHot: (a.views || 0) >= 500,
      }
    })
  }, [articles])

  const filtered = useMemo(() => {
    let out = [...decorated]
    if (topFilter === 'new') out = out.filter(a => a.isNew)
    if (topFilter === 'popular') out = out.filter(a => a.isHot)
    if (topFilter === 'bookmarked') out = out.filter(a => bookmarked.has(a.id))

    if (sortMode === 'popular') out.sort((a, b) => (b.views || 0) - (a.views || 0))
    else if (sortMode === 'likes') out.sort((a, b) => (b.likes || 0) - (a.likes || 0))
    else if (sortMode === 'az') out.sort((a, b) => a.title.localeCompare(b.title, 'he'))
    else out.sort((a, b) => (new Date(b.created_at || '').getTime() || 0) - (new Date(a.created_at || '').getTime() || 0))

    return out
  }, [decorated, topFilter, sortMode, bookmarked])

  const featured = filtered[0]
  const feed = filtered.slice(1)

  function toggleSetValue(current: Set<string>, id: string): Set<string> {
    const next = new Set(current)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    return next
  }

  function onLike(id: string) {
    const next = toggleSetValue(liked, id)
    setLiked(next)
    localStorage.setItem('mh_liked', JSON.stringify([...next]))
  }

  function onBookmark(id: string) {
    const next = toggleSetValue(bookmarked, id)
    setBookmarked(next)
    localStorage.setItem('mh_bookmark', JSON.stringify([...next]))
  }

  function handleTagClick(tag: string) {
    setActiveTag(prev => (prev === tag ? '' : tag))
    setSearch(tag)
  }

  return (
    <div id="article-page-root">
      <div className="hero">
        <div className="hero-inner">
          <div className="crumbs">
            <a href="/">דף הבית</a>
            <span className="crumbs-sep">›</span>
            <span>ספריית תוכן</span>
            <span className="crumbs-sep">›</span>
            <span>מאמרים רפואיים</span>
          </div>

          <h1>
            <span className="hero-icon" aria-hidden="true">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              </svg>
            </span>
            מאמרים רפואיים
          </h1>
          <p className="subtitle">ספרייה של מאמרים מקצועיים, כתובים על ידי רופאים מובילים. חיפוש מתקדם, קטגוריות רפואיות וטאגים לאבחון מהיר.</p>

          <div className="hero-stats">
            <div className="stat"><div className="stat-num">{totalCount}</div><div className="stat-label">מאמרים פעילים</div></div>
            <div className="stat"><div className="stat-num">{topAuthors.length}</div><div className="stat-label">רופאים כותבים</div></div>
            <div className="stat"><div className="stat-num">{Object.values(categoryCounts).filter(Boolean).length}</div><div className="stat-label">קטגוריות</div></div>
            <div className="stat"><div className="stat-num">{decorated.reduce((s, a) => s + (a.views || 0), 0).toLocaleString('he-IL')}</div><div className="stat-label">קריאות מצטברות</div></div>
          </div>

          <div className="searchbar">
            <span className="searchbar-icon" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.3-4.3"></path>
              </svg>
            </span>
            <input
              id="searchInput"
              type="text"
              placeholder="חיפוש לפי שם מאמר, נושא, רופא או מילות מפתח..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            <button type="button">חיפוש</button>
          </div>
        </div>
      </div>

      <main className="page-bg">
        <div className="page-inner">
          <aside className="sidebar">
            <div className="panel">
              <div className="panel-title">קטגוריות</div>
              <ul className="cat-list">
                <li className={`cat-item ${selectedCategory === 'all' ? 'active' : ''}`} onClick={() => setSelectedCategory('all')}>
                  <span className="cat-label"><span className="cat-swatch"></span>כל המאמרים</span>
                  <span className="cat-count">{totalCount}</span>
                </li>
                {(Object.keys(categoryMap) as ArticleCategory[]).map(cat => (
                  <li
                    key={cat}
                    className={`cat-item ${selectedCategory === cat ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    <span className="cat-label"><span className="cat-swatch"></span>{categoryMap[cat]}</span>
                    <span className="cat-count">{categoryCounts[cat]}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="panel">
              <div className="panel-title">תגיות חמות</div>
              <div className="tag-cloud">
                {allTags.map(tag => (
                  <span key={tag} className={`tag ${activeTag === tag ? 'active' : ''}`} onClick={() => handleTagClick(tag)}>{tag}</span>
                ))}
              </div>
            </div>

            <div className="panel">
              <div className="panel-title">כותבים מובילים</div>
              <div className="doctors-list">
                {topAuthors.map(a => (
                  <div key={a.name} className="doctor">
                    <div className="doctor-avatar">{initials(a.name)}</div>
                    <div className="doctor-info">
                      <div className="doctor-name">{a.name}</div>
                      <div className="doctor-role">רופא מומחה</div>
                    </div>
                    <div className="doctor-count">{a.count} מאמרים</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="scribe-card">
              <div className="scribe-chip">Doctor Scribe AI</div>
              <h3>תיעוד רפואי חכם, אוטומטי ומדויק</h3>
              <p>הפוך את הביקור של המטופל לסיכום רפואי מלא תוך שניות. ניסיון חינם ל-14 יום.</p>
              <a className="scribe-cta" href="/cpanel">התחלה חינם ›</a>
            </div>
          </aside>

          <section>
            <div className="toolbar">
              <div className="tabs">
                <button className={`tab ${topFilter === 'all' ? 'active' : ''}`} onClick={() => setTopFilter('all')}>הכל <span className="tab-count">{decorated.length}</span></button>
                <button className={`tab ${topFilter === 'new' ? 'active' : ''}`} onClick={() => setTopFilter('new')}>חדשים <span className="tab-count">{decorated.filter(a => a.isNew).length}</span></button>
                <button className={`tab ${topFilter === 'popular' ? 'active' : ''}`} onClick={() => setTopFilter('popular')}>פופולריים <span className="tab-count">{decorated.filter(a => a.isHot).length}</span></button>
                <button className={`tab ${topFilter === 'bookmarked' ? 'active' : ''}`} onClick={() => setTopFilter('bookmarked')}>שמורים <span className="tab-count">{bookmarked.size}</span></button>
              </div>
              <div className="sort-group">
                <label>מיון:</label>
                <select id="sortSelect" value={sortMode} onChange={e => setSortMode(e.target.value as SortMode)}>
                  <option value="recent">חדש ביותר</option>
                  <option value="popular">הכי פופולרי</option>
                  <option value="likes">הכי אהובים</option>
                  <option value="az">א-ב</option>
                </select>
              </div>
            </div>

            <div className="results-count">מציג <strong>{filtered.length}</strong> מתוך <strong>{totalCount}</strong> מאמרים</div>

            {featured && (
              <article className="featured" data-cat={featured.categoryKey}>
                <div
                  className="featured-img"
                  style={featured.hero_image_url ? { backgroundImage: `url(${featured.hero_image_url})`, backgroundSize: 'cover', backgroundPosition: 'center' } : undefined}
                ></div>
                <div className="featured-body">
                  <div className="featured-meta">
                    <span className="category-chip" data-cat={featured.categoryKey}><span className="chip-dot"></span>{featured.categoryLabel}</span>
                    {featured.isNew && <span className="badge-new">חדש</span>}
                    <span className="meta-item">⏱ {featured.read_time_minutes || 5} דקות קריאה</span>
                  </div>
                  <h2>{featured.title}</h2>
                  <p>{featured.summary || 'ללא תקציר זמין כרגע.'}</p>
                  <div className="featured-footer">
                    <div className="author-row">
                      <div className="author-avatar">{initials(featured.author_name)}</div>
                      <div>
                        <div style={{ color: 'var(--navy-900)', fontWeight: 600 }}>{featured.author_name || 'צוות MedicalHub'}</div>
                        <div style={{ fontSize: 12, color: 'var(--ink-400)' }}>{articleDate(featured.created_at)} · {(featured.views || 0).toLocaleString('he-IL')} קריאות</div>
                      </div>
                    </div>
                    <Link className="read-more" href={featured.slug ? `/articles/${featured.slug}` : '/articles'}>קרא את המאמר המלא</Link>
                  </div>
                </div>
              </article>
            )}

            <div className="articles">
              {loading && <div className="empty-state">טוען מאמרים...</div>}
              {!loading && fetchError && <div className="empty-state">{fetchError}</div>}
              {!loading && !fetchError && filtered.length === 0 && <div className="empty-state">לא נמצאו מאמרים מתאימים.</div>}

              {!loading && !fetchError && feed.map(a => (
                <article className="card" key={a.id} data-cat={a.categoryKey}>
                  <div className="card-body">
                    <div className="card-meta-row">
                      <span className="category-chip" data-cat={a.categoryKey}><span className="chip-dot"></span>{a.categoryLabel}</span>
                      {a.isNew && <span className="badge-new">חדש</span>}
                      {a.isHot && <span className="badge-hot">פופולרי</span>}
                      <span className="meta-item">⏱ {a.read_time_minutes || 5} דק׳</span>
                      <span className="meta-item">{articleDate(a.created_at)}</span>
                      <span className="meta-item">{a.author_name || 'צוות MedicalHub'}</span>
                    </div>

                    <h3>{a.title}</h3>
                    <p>{a.summary || 'ללא תקציר זמין כרגע.'}</p>

                    <div className="card-footer">
                      <div className="tags">
                        {(a.tags || []).slice(0, 5).map(tag => (
                          <span key={tag} className="tag" onClick={() => handleTagClick(tag)}>{tag}</span>
                        ))}
                      </div>

                      <div className="card-actions">
                        <button className={`icon-btn ${liked.has(a.id) ? 'liked' : ''}`} onClick={() => onLike(a.id)}>❤ {(a.likes || 0) + (liked.has(a.id) ? 1 : 0)}</button>
                        <button className={`icon-btn ${bookmarked.has(a.id) ? 'bookmarked' : ''}`} onClick={() => onBookmark(a.id)}>🔖</button>
                        <Link className="read-more" href={a.slug ? `/articles/${a.slug}` : '/articles'}>קרא עוד</Link>
                      </div>
                    </div>
                  </div>

                  <div
                    className="card-thumb"
                    data-label={a.categoryLabel}
                    style={a.hero_image_url ? { backgroundImage: `url(${a.hero_image_url})`, backgroundSize: 'cover', backgroundPosition: 'center' } : undefined}
                  ></div>
                </article>
              ))}
            </div>

            <nav className="pagination">
              <button className="page-btn active">1</button>
            </nav>
          </section>
        </div>
      </main>
    </div>
  )
}
