'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import '../../article-theme.css'
import { CATEGORY_META, CATEGORY_ICONS } from '../../constants'
import Header from '../../../../components/Header'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

export default function TagPage() {
  const { tag } = useParams<{ tag: string }>()
  const decodedTag = decodeURIComponent(tag)

  const [articles, setArticles] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)

  const PAGE_SIZE = 12

  useEffect(() => {
    setLoading(true)
    setArticles([])
    setPage(1)
    fetch(`${API}/articles?tag=${encodeURIComponent(decodedTag)}&per_page=${PAGE_SIZE}&page=1&sort=newest`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) {
          setArticles(data.items || [])
          setTotal(data.total || 0)
          setHasMore((data.items || []).length === PAGE_SIZE)
        }
      })
      .finally(() => setLoading(false))
  }, [decodedTag])

  const loadMore = () => {
    const nextPage = page + 1
    fetch(`${API}/articles?tag=${encodeURIComponent(decodedTag)}&per_page=${PAGE_SIZE}&page=${nextPage}&sort=newest`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) {
          setArticles(prev => [...prev, ...(data.items || [])])
          setHasMore((data.items || []).length === PAGE_SIZE)
          setPage(nextPage)
        }
      })
  }

  return (
    <>
      <div id="article-page-root" dir="rtl">
        <Header />

        <div className="page-wrap" style={{ maxWidth: 900, margin: '0 auto', padding: '24px 20px 48px' }}>

          {/* Breadcrumb */}
          <nav className="breadcrumb-bar" aria-label="breadcrumb" style={{ marginBottom: 16 }}>
            <Link href="/">ראשי</Link>
            <span className="bc-sep">›</span>
            <Link href="/articles">מאמרים</Link>
            <span className="bc-sep">›</span>
            <span className="bc-current">#{decodedTag}</span>
          </nav>

          {/* Header */}
          <div style={{
            background: 'linear-gradient(135deg, #001f6b, #1a56db)',
            borderRadius: 14, padding: '28px 28px 24px',
            marginBottom: 24, color: 'white',
          }}>
            <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.6)', marginBottom: 8 }}>תגית</div>
            <h1 style={{ fontSize: 28, fontWeight: 800, margin: 0, marginBottom: 8 }}>#{decodedTag}</h1>
            {!loading && (
              <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.7)' }}>
                {total} מאמר{total !== 1 ? 'ים' : ''} בנושא זה
              </div>
            )}
          </div>

          {/* Articles */}
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#888' }}>טוען מאמרים...</div>
          ) : articles.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#888' }}>
              לא נמצאו מאמרים עבור התגית #{decodedTag}
            </div>
          ) : (
            <div className="articles-list">
              {articles.map((article: any, i: number) => {
                const cat = CATEGORY_META[article.category] || CATEGORY_META.general
                const icon = CATEGORY_ICONS[article.category] || '📄'
                const publishDate = article.published_at
                  ? new Date(article.published_at).toLocaleDateString('he-IL') : ''
                return (
                  <div key={article.slug}>
                    {i > 0 && (
                      <div className="pipe" style={{ margin: '16px 0' }}>
                        <div className="arch arch-right"></div>
                        <div className="pipe-lines"><div className="pipe-line"></div><div className="pipe-line"></div></div>
                        <div className="arch arch-left"></div>
                      </div>
                    )}
                    <Link href={`/articles/${article.slug}`} className="article-card" style={{ display: 'block' }}>
                      <div className="card-inner">
                        <div className="card-thumb">
                          {article.hero_image_url
                            ? <img src={article.hero_image_url} alt={article.hero_image_alt || article.title} className="card-thumb-img" />
                            : <span className="card-thumb-icon">{icon}</span>
                          }
                        </div>
                        <div className="card-body">
                          <div className="card-title">{article.title}</div>
                          <div className="card-desc">{article.summary}</div>
                          <div className="card-meta-row">
                            <span className="cat-badge" style={{ color: cat.color, background: cat.bg, border: `1px solid ${cat.color}44` }}>
                              {cat.label}
                            </span>
                            {(article.tags || []).slice(0, 3).map((t: string) => (
                              <Link
                                key={t}
                                href={`/articles/tag/${encodeURIComponent(t)}`}
                                className={`tag-chip${t === decodedTag ? ' active' : ''}`}
                                onClick={e => e.stopPropagation()}
                              >
                                {t}
                              </Link>
                            ))}
                            <span className="card-author">{article.author_name} · {article.read_time_minutes} דק׳ · {publishDate}</span>
                          </div>
                          <div className="card-stats">
                            <span className="stat">👁️ {(article.views || 0).toLocaleString()}</span>
                            <span className="stat">❤️ {article.likes || 0}</span>
                            <span className="read-btn">קרא עוד →</span>
                          </div>
                        </div>
                      </div>
                    </Link>
                  </div>
                )
              })}
            </div>
          )}

          {hasMore && !loading && (
            <div style={{ textAlign: 'center', marginTop: 24 }}>
              <button onClick={loadMore} style={{
                padding: '12px 32px', borderRadius: 10,
                border: '1px solid rgba(26,86,219,0.35)',
                background: 'rgba(26,86,219,0.1)',
                color: '#003399', fontFamily: 'Rubik, sans-serif',
                fontSize: 14, fontWeight: 700, cursor: 'pointer',
              }}>
                טען עוד מאמרים
              </button>
            </div>
          )}

        </div>
      </div>
    </>
  )
}
