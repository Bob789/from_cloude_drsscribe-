'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Header from '@/components/Header'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

type Category = 'all' | 'cardiology' | 'neurology' | 'orthopedics' | 'nutrition' | 'sleep' | 'mental' | 'general' | 'dermatology' | 'gastroenterology' | 'urology'
type Sort = 'hot' | 'new' | 'popular'

const CATEGORY_META: Record<string, { label: string; color: string; bg: string }> = {
  cardiology:        { label: 'לב וכלי דם',  color: '#fca5a5', bg: 'rgba(239,68,68,0.1)'   },
  neurology:         { label: 'נוירולוגיה',  color: '#a78bfa', bg: 'rgba(139,92,246,0.1)'  },
  orthopedics:       { label: 'אורתופדיה',   color: '#93c5fd', bg: 'rgba(59,130,246,0.1)'  },
  nutrition:         { label: 'תזונה',        color: '#6ee7b7', bg: 'rgba(16,185,129,0.1)'  },
  sleep:             { label: 'שינה',         color: '#fde68a', bg: 'rgba(245,158,11,0.1)'  },
  mental:            { label: 'בריאות נפש',  color: '#f9a8d4', bg: 'rgba(236,72,153,0.1)'  },
  general:           { label: 'כללי',         color: '#94a3b8', bg: 'rgba(148,163,184,0.1)' },
  dermatology:       { label: 'עור',          color: '#fdba74', bg: 'rgba(251,146,60,0.1)'  },
  gastroenterology:  { label: 'גסטרו',       color: '#86efac', bg: 'rgba(34,197,94,0.1)'   },
  urology:           { label: 'אורולוגיה',   color: '#7dd3fc', bg: 'rgba(56,189,248,0.1)'  },
}

const CATEGORY_ICONS: Record<string, string> = {
  cardiology: '❤️', neurology: '🧠', orthopedics: '🦴', nutrition: '🥗',
  sleep: '😴', mental: '🧘', general: '📋', dermatology: '🧴',
  gastroenterology: '🫁', urology: '💊',
}

const TABS: { id: Category; label: string }[] = [
  { id: 'all',          label: '📋 הכל'      },
  { id: 'cardiology',   label: '❤️ לב'       },
  { id: 'neurology',    label: '🧠 נוירו'    },
  { id: 'orthopedics',  label: '🦴 אורתו'    },
  { id: 'nutrition',    label: '🥗 תזונה'    },
  { id: 'sleep',        label: '😴 שינה'     },
  { id: 'mental',       label: '🧘 נפש'      },
]

export default function ArticlesPage() {
  const [search,    setSearch]    = useState('')
  const [category,  setCategory]  = useState<Category>('all')
  const [sort,      setSort]      = useState<Sort>('new')
  const [activeTag, setActiveTag] = useState('')
  const [articles, setArticles]   = useState<any[]>([])
  const [loading, setLoading]     = useState(true)
  const [totalCount, setTotalCount] = useState(0)

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const params = new URLSearchParams()
        if (category !== 'all') params.set('category', category)
        if (search) params.set('search', search)
        if (activeTag) params.set('tag', activeTag)
        params.set('sort', sort === 'hot' ? 'popular' : sort === 'new' ? 'newest' : 'views')
        params.set('per_page', '20')

        const res = await fetch(`${API}/articles?${params}`)
        if (res.ok) {
          const data = await res.json()
          setArticles(data.items || [])
          setTotalCount(data.total || 0)
        }
      } catch {}
      finally { setLoading(false) }
    }
    load()
  }, [category, sort, search, activeTag])

  // Collect all unique tags from loaded articles
  const allTags = [...new Set(articles.flatMap(a => a.tags || []))]

  // Collect authors
  const authorMap = new Map<string, { name: string; title: string; count: number }>()
  articles.forEach(a => {
    if (a.author_name) {
      const existing = authorMap.get(a.author_name)
      if (existing) existing.count++
      else authorMap.set(a.author_name, { name: a.author_name, title: a.author_title || '', count: 1 })
    }
  })
  const topAuthors = [...authorMap.values()].sort((a, b) => b.count - a.count).slice(0, 5)

  // Category counts
  const catCounts: Record<string, number> = {}
  articles.forEach(a => { catCounts[a.category] = (catCounts[a.category] || 0) + 1 })

  return (
    <>
      <Header page="articles" />

      <main>
      <div style={{ maxWidth: 1300, margin: '32px auto', padding: '0 20px' }}>

        {/* Title row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0, color: '#e0f2fe' }}>📰 מאמרים רפואיים</h2>
            <p style={{ color: 'var(--muted)', margin: '6px 0 0', fontSize: 14 }}>
              {totalCount} מאמרים מפורסמים
            </p>
          </div>
        </div>

        {/* Search */}
        <div className="card" style={{ padding: '16px 20px', marginBottom: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
          <input
            type="text"
            className="search-input"
            style={{ flex: 1, padding: '12px 16px' }}
            placeholder="חפש מאמר, תגית או כותב..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {/* Category tabs */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
          {TABS.map(t => (
            <button
              key={t.id}
              onClick={() => setCategory(t.id)}
              className={`nav-pill ${category === t.id ? 'nav-pill-active' : 'nav-pill-default'}`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Sort */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
          {(['hot','new','popular'] as Sort[]).map(s => (
            <button
              key={s}
              onClick={() => setSort(s)}
              style={{
                padding: '6px 14px', borderRadius: 10, fontSize: 13, cursor: 'pointer',
                fontWeight: sort === s ? 700 : 400,
                border: sort === s ? '1px solid rgba(56,189,248,0.6)' : '1px solid var(--border)',
                background: sort === s ? 'rgba(56,189,248,0.08)' : 'transparent',
                color: sort === s ? '#e0f2fe' : 'var(--muted)',
              }}
            >
              {{ hot: '🔥 חם', new: '🆕 חדש', popular: '👁️ פופולרי' }[s]}
            </button>
          ))}
          <span style={{ marginRight: 'auto', color: 'var(--muted)', fontSize: 13 }}>
            {articles.length} מאמרים
          </span>
        </div>

        {/* Main layout */}
        <div className="forum-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 20, alignItems: 'start' }}>

          {/* Article list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {loading && <div style={{ textAlign: 'center', color: 'var(--muted)', padding: 48 }}>טוען מאמרים...</div>}

            {!loading && articles.length === 0 && (
              <div className="card" style={{ textAlign: 'center', padding: 48, color: 'var(--muted)' }}>
                לא נמצאו מאמרים מתאימים
              </div>
            )}

            {articles.map(article => {
              const cat = CATEGORY_META[article.category] || CATEGORY_META.general
              const icon = CATEGORY_ICONS[article.category] || '📄'
              const publishDate = article.published_at ? new Date(article.published_at).toLocaleDateString('he-IL') : ''

              return (
                <article key={article.id} className="article-card card" data-testid="article-card">
                  <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>

                    {/* Image or emoji icon */}
                    {article.hero_image_url ? (
                      <img
                        src={article.hero_image_url}
                        alt={article.hero_image_alt || article.title}
                        style={{ width: 120, height: 80, borderRadius: 12, objectFit: 'cover', flexShrink: 0 }}
                      />
                    ) : (
                      <div style={{
                        width: 56, height: 56, borderRadius: 16, flexShrink: 0,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: 'rgba(56,189,248,0.08)', border: '1px solid rgba(56,189,248,0.2)',
                        fontSize: 28,
                      }}>
                        {icon}
                      </div>
                    )}

                    {/* Content */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <h3 style={{ fontSize: 15, fontWeight: 800, margin: '0 0 8px', lineHeight: 1.4, color: 'var(--text)' }}>
                        {article.title}
                      </h3>
                      <p style={{ color: 'var(--muted)', fontSize: 13, margin: '0 0 10px', lineHeight: 1.5, maxHeight: '2.8em', overflow: 'hidden' }}>
                        {article.summary}
                      </p>

                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center' }}>
                        {/* Category badge */}
                        <span style={{
                          fontSize: 12, fontWeight: 700, padding: '4px 10px', borderRadius: 999, whiteSpace: 'nowrap',
                          color: cat.color, background: cat.bg, border: `1px solid ${cat.color}44`,
                        }}>
                          {cat.label}
                        </span>
                        {/* Tags */}
                        {(article.tags || []).slice(0, 2).map((tag: string) => (
                          <button
                            key={tag}
                            onClick={() => setActiveTag(activeTag === tag ? '' : tag)}
                            className="tag"
                            style={{ cursor: 'pointer', background: activeTag === tag ? 'rgba(56,189,248,0.18)' : undefined, border: activeTag === tag ? '1px solid rgba(56,189,248,0.6)' : undefined }}
                          >
                            {tag}
                          </button>
                        ))}
                        <span style={{ color: 'var(--muted)', fontSize: 12, marginRight: 'auto' }}>
                          {article.author_name} · {article.read_time_minutes} דק׳ · {publishDate}
                        </span>
                      </div>

                      <div style={{ display: 'flex', gap: 16, marginTop: 10, alignItems: 'center' }}>
                        <span style={{ fontSize: 12, color: 'var(--muted)' }}>👁️ {(article.views || 0).toLocaleString()}</span>
                        <span style={{ fontSize: 12, color: 'var(--muted)' }}>❤️ {article.likes || 0}</span>
                        <Link href={`/articles/${article.slug}`} className="btn btn-primary" style={{ marginRight: 'auto', padding: '6px 16px', fontSize: 12, textDecoration: 'none' }}>
                          קרא עוד →
                        </Link>
                      </div>
                    </div>
                  </div>
                </article>
              )
            })}
          </div>

          {/* Sidebar */}
          <aside style={{ position: 'sticky', top: 88, display: 'flex', flexDirection: 'column', gap: 16 }}>

            {/* Categories */}
            <div className="card">
              <h4 style={{ margin: '0 0 12px' }}>📂 קטגוריות</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {Object.entries(CATEGORY_META).map(([id, meta]) => (
                  <button
                    key={id}
                    onClick={() => setCategory(id as Category)}
                    style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      padding: '8px 12px', borderRadius: 10, cursor: 'pointer', fontSize: 13,
                      border: category === id ? `1px solid ${meta.color}44` : '1px solid var(--border)',
                      background: category === id ? meta.bg : 'transparent',
                      color: 'var(--text)',
                    }}
                  >
                    <span>{meta.label}</span>
                    <span style={{ color: meta.color, fontWeight: 700, fontSize: 12 }}>
                      {catCounts[id] || 0}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Hot tags */}
            {allTags.length > 0 && (
              <div className="card">
                <h4 style={{ margin: '0 0 12px' }}>🔥 תגיות חמות</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {allTags.slice(0, 12).map(tag => (
                    <button
                      key={tag}
                      onClick={() => setActiveTag(activeTag === tag ? '' : tag)}
                      className="tag"
                      style={{ cursor: 'pointer', background: activeTag === tag ? 'rgba(56,189,248,0.18)' : undefined, border: activeTag === tag ? '1px solid rgba(56,189,248,0.6)' : undefined }}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Top authors */}
            {topAuthors.length > 0 && (
              <div className="card">
                <h4 style={{ margin: '0 0 12px' }}>✍️ כותבים מובילים</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {topAuthors.map(a => (
                    <div key={a.name} className="forum-mini" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 13 }}>{a.name}</div>
                        <div style={{ color: 'var(--muted)', fontSize: 11, marginTop: 2 }}>{a.title}</div>
                      </div>
                      <span style={{ fontSize: 11, color: '#93c5fd', fontWeight: 700 }}>{a.count} מאמרים</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Doctor Scribe AI CTA */}
            <div className="card cta-card">
              <h4 style={{ margin: '0 0 8px' }}>🎤 Doctor Scribe AI</h4>
              <p style={{ color: 'var(--muted)', fontSize: 13, lineHeight: 1.5, margin: '0 0 12px' }}>
                תמלול וסיכום אוטומטי של ביקורים רפואיים לקליניקות פרטיות.
              </p>
              <a href="/product" className="btn btn-primary" style={{ display: 'block', textAlign: 'center', padding: '10px' }}>
                למד עוד →
              </a>
            </div>
          </aside>
        </div>
      </div>

      </main>
    </>
  )
}
