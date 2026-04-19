'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import './article-theme.css'
import { Category, Sort, Author } from './constants'
import Header           from '../../components/Header'
import ArticleFilters   from './ArticleFilters'
import ArticleCard      from './ArticleCard'
import ArticlesSidebar  from './ArticlesSidebar'
import { useLanguage } from '@/components/LanguageProvider'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'
const PAGE_SIZE = 10

export default function ArticlesPage() {
  const { t } = useLanguage()
  const [search,        setSearch]        = useState('')
  const [category,      setCategory]      = useState<Category>('all')
  const [sort,          setSort]          = useState<Sort>('new')
  const [activeTag,     setActiveTag]     = useState('')
  const [articles,      setArticles]      = useState<any[]>([])
  const [loading,       setLoading]       = useState(true)
  const [totalCount,    setTotalCount]    = useState(0)
  const [page,          setPage]          = useState(1)
  const [hasMore,       setHasMore]       = useState(true)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const sentinelRef = useRef<HTMLDivElement>(null)

  // Reset + initial load when filters change
  useEffect(() => {
    let cancelled = false
    setPage(1)
    setArticles([])
    setHasMore(true)
    setLoading(true)

    const params = new URLSearchParams()
    if (category !== 'all') params.set('category', category)
    if (search)    params.set('search', search)
    if (activeTag) params.set('tag', activeTag)
    params.set('sort', sort === 'hot' ? 'popular' : sort === 'new' ? 'newest' : 'views')
    params.set('per_page', String(PAGE_SIZE))
    params.set('page', '1')

    fetch(`${API}/articles?${params}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (!cancelled && data) {
          setArticles(data.items || [])
          setTotalCount(data.total || 0)
          setHasMore((data.items || []).length === PAGE_SIZE)
        }
      })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [category, sort, search, activeTag])

  const loadMore = useCallback(async () => {
    if (isLoadingMore || !hasMore) return
    setIsLoadingMore(true)
    const nextPage = page + 1

    try {
      const params = new URLSearchParams()
      if (category !== 'all') params.set('category', category)
      if (search)    params.set('search', search)
      if (activeTag) params.set('tag', activeTag)
      params.set('sort', sort === 'hot' ? 'popular' : sort === 'new' ? 'newest' : 'views')
      params.set('per_page', String(PAGE_SIZE))
      params.set('page', String(nextPage))

      const res = await fetch(`${API}/articles?${params}`)
      if (res.ok) {
        const data = await res.json()
        const items = data.items || []
        setArticles(prev => [...prev, ...items])
        setPage(nextPage)
        setHasMore(items.length === PAGE_SIZE)
      }
    } catch {}
    finally { setIsLoadingMore(false) }
  }, [page, isLoadingMore, hasMore, category, sort, search, activeTag])

  // IntersectionObserver for infinite scroll
  useEffect(() => {
    const sentinel = sentinelRef.current
    if (!sentinel) return
    const observer = new IntersectionObserver(
      entries => { if (entries[0].isIntersecting) loadMore() },
      { threshold: 0.1 }
    )
    observer.observe(sentinel)
    return () => observer.disconnect()
  }, [loadMore])

  // Derived data
  const allTags = [...new Set(articles.flatMap(a => a.tags || []))]

  const authorMap = new Map<string, Author>()
  articles.forEach(a => {
    if (a.author_name) {
      const e = authorMap.get(a.author_name)
      if (e) e.count++
      else authorMap.set(a.author_name, { name: a.author_name, title: a.author_title || '', count: 1 })
    }
  })
  const topAuthors = [...authorMap.values()].sort((a, b) => b.count - a.count).slice(0, 5)

  const catCounts: Record<string, number> = {}
  articles.forEach(a => { catCounts[a.category] = (catCounts[a.category] || 0) + 1 })

  const handleTag = (tag: string) => setActiveTag(prev => prev === tag ? '' : tag)

  return (
    <div id="article-page-root">

          <div className="block-header">
            <div>
              <div className="block-title">{t('articles_title')}</div>
              <div className="block-count">{t('articles_count', { n: totalCount })}</div>
            </div>
          </div>

          <div className="title-lines">
            <div className="title-line"></div>
            <div className="title-line"></div>
          </div>

          <ArticleFilters
            search={search}     category={category}  sort={sort}
            articleCount={articles.length}
            onSearch={setSearch} onCategory={setCategory} onSort={setSort}
          />

          <div className="content-grid">
            <div className="articles-list">
              {loading && (
                <div style={{ textAlign: 'center', color: '#888', padding: 48 }}>{t('articles_loading')}</div>
              )}
              {!loading && articles.length === 0 && (
                <div style={{ textAlign: 'center', padding: 48, color: '#888', background: 'rgba(255,255,255,0.65)', borderRadius: 14 }}>
                  {t('articles_empty')}
                </div>
              )}
              {articles.map((article, index) => (
                <ArticleCard
                  key={article.id}
                  article={article}
                  activeTag={activeTag}
                  onTagClick={handleTag}
                  showDivider={index > 0}
                />
              ))}

              {/* Infinite scroll sentinel */}
              {!loading && hasMore && (
                <div ref={sentinelRef} style={{ padding: '24px 0', textAlign: 'center', color: '#888', fontSize: 14 }}>
                  {isLoadingMore && t('articles_load_more')}
                </div>
              )}
              {!loading && !hasMore && articles.length > 0 && (
                <div style={{ padding: '24px 0', textAlign: 'center', color: '#aaa', fontSize: 13 }}>
                  {t('articles_all_shown', { n: articles.length })}
                </div>
              )}
            </div>

            <ArticlesSidebar
              category={category}  catCounts={catCounts}
              allTags={allTags}    topAuthors={topAuthors}
              activeTag={activeTag}
              onCategory={setCategory} onTag={handleTag}
            />
      </div>

    </div>
  )
}
