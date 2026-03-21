'use client'

import { useState, useEffect } from 'react'
import './article-theme.css'
import { Category, Sort, Author } from './constants'
import Header           from '../../components/Header'
import ArticleFilters   from './ArticleFilters'
import ArticleCard      from './ArticleCard'
import ArticlesSidebar  from './ArticlesSidebar'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

export default function ArticlesPage() {
  const [search,     setSearch]     = useState('')
  const [category,   setCategory]   = useState<Category>('all')
  const [sort,       setSort]       = useState<Sort>('new')
  const [activeTag,  setActiveTag]  = useState('')
  const [articles,   setArticles]   = useState<any[]>([])
  const [loading,    setLoading]    = useState(true)
  const [totalCount, setTotalCount] = useState(0)

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const params = new URLSearchParams()
        if (category !== 'all') params.set('category', category)
        if (search)    params.set('search', search)
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


      <div className="page-wrap">
        <div className="block">

          <div className="block-header">
            <div>
              <div className="block-title">📰 מאמרים רפואיים</div>
              <div className="block-count">{totalCount} מאמרים מפורסמים</div>
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
                <div style={{ textAlign: 'center', color: '#888', padding: 48 }}>טוען מאמרים...</div>
              )}
              {!loading && articles.length === 0 && (
                <div style={{ textAlign: 'center', padding: 48, color: '#888', background: 'rgba(255,255,255,0.65)', borderRadius: 14 }}>
                  לא נמצאו מאמרים מתאימים
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
            </div>

            <ArticlesSidebar
              category={category}  catCounts={catCounts}
              allTags={allTags}    topAuthors={topAuthors}
              activeTag={activeTag}
              onCategory={setCategory} onTag={handleTag}
            />
          </div>
        </div>
      </div>

    </div>
  )
}
