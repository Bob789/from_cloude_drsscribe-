'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import './search.css'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

function relativeTime(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return 'היום'
  if (days === 1) return 'אתמול'
  if (days < 7) return `לפני ${days} ימים`
  const weeks = Math.floor(days / 7)
  if (days < 30) return weeks === 1 ? 'לפני שבוע' : `לפני ${weeks} שבועות`
  const months = Math.floor(days / 30)
  return months === 1 ? 'לפני חודש' : `לפני ${months} חודשים`
}

type FilterType = 'all' | 'article' | 'forum'

export default function SearchPage() {
  return (
    <Suspense fallback={<div style={{ color: 'white', textAlign: 'center', padding: 60 }}>טוען...</div>}>
      <SearchContent />
    </Suspense>
  )
}

function SearchContent() {
  const searchParams = useSearchParams()
  const initialQuery = searchParams.get('q') || ''

  const [query, setQuery] = useState(initialQuery)
  const [inputValue, setInputValue] = useState(initialQuery)
  const [results, setResults] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [filter, setFilter] = useState<FilterType>('all')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)

  useEffect(() => {
    if (!query.trim()) return
    setLoading(true)
    const params = new URLSearchParams({ q: query, page: String(page), per_page: '20' })
    fetch(`${API}/site/search?${params}`)
      .then(r => r.json())
      .then(data => {
        setResults(data.items || [])
        setTotal(data.total || 0)
        setTotalPages(data.pages || 0)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [query, page])

  // Update query from URL changes
  useEffect(() => {
    const q = searchParams.get('q')
    if (q && q !== query) {
      setQuery(q)
      setInputValue(q)
      setPage(1)
    }
  }, [searchParams])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim().length >= 2) {
      setQuery(inputValue.trim())
      setPage(1)
      window.history.replaceState(null, '', `/search?q=${encodeURIComponent(inputValue.trim())}`)
    }
  }

  const filtered = filter === 'all' ? results : results.filter(r => r.type === filter)
  const articleCount = results.filter(r => r.type === 'article').length
  const forumCount = results.filter(r => r.type === 'forum').length

  return (
    <div className="search-page">
      <div className="search-header">
        <Link href="/" className="back-home">
          <i className="fas fa-arrow-right"></i> חזרה לדף הבית
        </Link>
        <h1 className="search-page-title">🔍 תוצאות חיפוש</h1>

        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
            placeholder="חיפוש מאמרים ודיונים..."
            className="search-input"
          />
          <button type="submit" className="search-submit">
            <i className="fas fa-search"></i> חיפוש
          </button>
        </form>

        {query && !loading && (
          <div className="search-meta">
            נמצאו <strong>{total}</strong> תוצאות עבור &ldquo;<strong>{query}</strong>&rdquo;
          </div>
        )}

        {total > 0 && (
          <div className="filter-tabs">
            <button className={`filter-tab ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>
              הכל ({total})
            </button>
            <button className={`filter-tab ${filter === 'article' ? 'active' : ''}`} onClick={() => setFilter('article')}>
              📰 מאמרים ({articleCount})
            </button>
            <button className={`filter-tab ${filter === 'forum' ? 'active' : ''}`} onClick={() => setFilter('forum')}>
              💬 פורום ({forumCount})
            </button>
          </div>
        )}
      </div>

      <div className="search-results">
        {loading && (
          <div className="search-loading">מחפש...</div>
        )}

        {!loading && query && filtered.length === 0 && (
          <div className="no-results">
            <div className="no-results-icon">🔍</div>
            <div className="no-results-text">לא נמצאו תוצאות עבור &ldquo;{query}&rdquo;</div>
            <div className="no-results-hint">נסו לחפש במילים אחרות או לבדוק את האיות</div>
          </div>
        )}

        {!loading && filtered.map(item => (
          <Link key={`${item.type}-${item.id}`} href={item.url} className="result-card">
            <div className="result-type-badge" data-type={item.type}>
              {item.type === 'article' ? '📰 מאמר' : '💬 דיון בפורום'}
            </div>
            <h3 className="result-title">{item.title}</h3>
            <p className="result-snippet">{item.snippet}</p>
            <div className="result-meta">
              {item.author_name && <span className="result-author">{item.author_name}</span>}
              {item.date && <span className="result-date">{relativeTime(item.date)}</span>}
              <span className="result-views">👁️ {item.views}</span>
              {item.likes > 0 && <span className="result-likes">❤️ {item.likes}</span>}
              {item.read_time_minutes && <span className="result-time">{item.read_time_minutes} דק׳ קריאה</span>}
              {item.category && <span className="result-category">{item.category}</span>}
            </div>
          </Link>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="search-pagination">
          <button disabled={page <= 1} onClick={() => setPage(p => p - 1)} className="page-btn">← הקודם</button>
          <span className="page-info">עמוד {page} מתוך {totalPages}</span>
          <button disabled={page >= totalPages} onClick={() => setPage(p => p + 1)} className="page-btn">הבא →</button>
        </div>
      )}
    </div>
  )
}
