'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import '../community-theme.css'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

type Sort = 'new' | 'unanswered' | 'top'

interface Post {
  id: string
  title: string
  body: string
  status: string
  author_name: string
  tags: string | null
  replies_count: number
  views: number
  votes: number
  first_reply: { body: string; author_name: string } | null
  created_at: string
}

interface HotTag {
  name: string
  count: number
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1)     return 'עכשיו'
  if (mins < 60)    return `לפני ${mins} דקות`
  const hours = Math.floor(mins / 60)
  if (hours < 24)   return `לפני ${hours} שעות`
  const days = Math.floor(hours / 24)
  if (days < 7)     return `לפני ${days} ימים`
  const weeks = Math.floor(days / 7)
  if (weeks < 5)    return `לפני ${weeks} שבועות`
  const months = Math.floor(days / 30)
  if (months < 12)  return `לפני ${months} חודשים`
  const years = Math.floor(days / 365)
  return `לפני ${years} שנים`
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('he-IL', { day: 'numeric', month: 'short', year: 'numeric' })
}

function formatViews(n: number): string {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}m`
  if (n >= 1000) return `${(n / 1000).toFixed(0)}k`
  return String(n)
}

function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('access_token')
}

async function refreshToken(): Promise<string | null> {
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) return null
  try {
    const res = await fetch(`${API}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
    })
    if (!res.ok) return null
    const data = await res.json()
    localStorage.setItem('access_token', data.access_token)
    if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
    return data.access_token
  } catch { return null }
}

async function authFetch(url: string, options: RequestInit): Promise<Response> {
  let token = getToken()
  if (!token) throw new Error('no_token')
  options.headers = { ...options.headers as Record<string,string>, Authorization: `Bearer ${token}` }
  let res = await fetch(url, options)
  if (res.status === 401) {
    const newToken = await refreshToken()
    if (!newToken) throw new Error('token_expired')
    options.headers = { ...options.headers as Record<string,string>, Authorization: `Bearer ${newToken}` }
    res = await fetch(url, options)
  }
  return res
}

const PER_PAGE = 15

export default function ForumPage() {
  const [search,    setSearch]    = useState('')
  const [sort,      setSort]      = useState<Sort>('new')
  const [activeTag, setActiveTag] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [posts,     setPosts]     = useState<Post[]>([])
  const [total,     setTotal]     = useState(0)
  const [page,      setPage]      = useState(1)
  const [hotTags,   setHotTags]   = useState<HotTag[]>([])
  const [stats,     setStats]     = useState<any>(null)
  const [leaderboard, setLeaderboard] = useState<{name: string; score: number}[]>([])
  const [loading,   setLoading]   = useState(true)

  const [newTitle, setNewTitle] = useState('')
  const [newBody,  setNewBody]  = useState('')
  const [newTag,   setNewTag]   = useState('')

  const totalPages = Math.ceil(total / PER_PAGE)

  const loadPosts = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.set('sort', sort)
      params.set('per_page', String(PER_PAGE))
      params.set('page', String(page))
      if (search)    params.set('search', search)
      if (activeTag) params.set('tag', activeTag)
      if (sort === 'unanswered') params.set('status', 'open')

      const res = await fetch(`${API}/forum/posts?${params}`)
      if (res.ok) {
        const data = await res.json()
        setPosts(data.posts || [])
        setTotal(data.total || 0)
      }
    } catch {}
    finally { setLoading(false) }
  }, [sort, search, activeTag, page])

  const loadStats = useCallback(async () => {
    try {
      const [statsRes, lbRes] = await Promise.all([
        fetch(`${API}/forum/stats`),
        fetch(`${API}/forum/leaderboard?limit=10`),
      ])
      if (statsRes.ok) {
        const data = await statsRes.json()
        setStats(data)
        setHotTags(data.hot_tags || [])
      }
      if (lbRes.ok) {
        setLeaderboard(await lbRes.json())
      }
    } catch {}
  }, [])

  useEffect(() => { loadPosts() }, [loadPosts])
  useEffect(() => { loadStats() }, [loadStats])

  // Reset page on filter changes
  useEffect(() => { setPage(1) }, [sort, search, activeTag])

  const handleCreatePost = async () => {
    if (newTitle.length < 5) { alert('כותרת חייבת להכיל לפחות 5 תווים'); return }
    if (newBody.length < 10) { alert('תוכן חייב להכיל לפחות 10 תווים'); return }
    try {
      const res = await authFetch(`${API}/forum/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle, body: newBody, tags: newTag || null }),
      })
      if (res.ok) {
        setShowModal(false)
        setNewTitle(''); setNewBody(''); setNewTag('')
        loadPosts()
        loadStats()
      } else {
        const err = await res.json().catch(() => null)
        alert(err?.detail || 'שגיאה ביצירת השאלה')
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : ''
      if (msg === 'no_token' || msg === 'token_expired') {
        alert('יש להתחבר מחדש כדי לפרסם שאלה')
        window.location.href = '/login'
      } else { alert('שגיאת רשת — נסה שוב') }
    }
  }

  const handleVote = async (postId: string, value: number) => {
    try {
      const res = await authFetch(`${API}/forum/posts/${postId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value }),
      })
      if (res.ok) loadPosts()
    } catch {}
  }

  return (
    <div id="forum-page-root">

      {/* ── BLOCK HEADER ── */}
      <div className="com-block-header">
        <div>
          <div className="com-block-title">💬 פורום רפואי</div>
          <div className="com-block-count">
            {stats ? `${stats.total_posts} שאלות · ${stats.total_replies} תגובות · ${stats.active_users} משתמשים פעילים` : 'טוען...'}
          </div>
        </div>
        <button onClick={() => setShowModal(true)} className="com-cta-btn" style={{ width: 'auto', padding: '10px 22px' }}>
          ✏️ שאל שאלה
        </button>
      </div>

      {/* ── TITLE LINES ── */}
      <div className="com-title-lines">
        <div className="com-title-line"></div>
        <div className="com-title-line"></div>
      </div>

      {/* ── BODY ── */}
      <div className="com-body">

        {/* Search */}
        <div className="com-search-bar">
          <span style={{ fontSize: 16, color: '#999' }}>🔍</span>
          <input
            type="text"
            className="com-search-input"
            placeholder="חפש שאלה, תגית או נושא..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <span className="com-kbd">/</span>
        </div>

        {/* Filter pills + count */}
        <div className="so-toolbar">
          <div className="com-pills" style={{ marginBottom: 0 }}>
            {(['new','unanswered','top'] as Sort[]).map(s => (
              <button
                key={s}
                onClick={() => setSort(s)}
                className={`com-pill${sort === s ? ' com-pill-active' : ''}`}
              >
                {{ new: '🆕 חדש', unanswered: '❓ ללא מענה', top: '⭐ מובילים' }[s]}
              </button>
            ))}
          </div>
          {/* Medical disclaimer */}
          <div className="so-medical-disclaimer">⚕️ המידע באתר זה הוא כללי בלבד ואינו מהווה ייעוץ רפואי. בכל מצב רפואי — פנה לרופא.</div>
          <span className="so-results-count">{loading ? '...' : `${total} תוצאות`}</span>
        </div>

        {/* Main layout — posts + sidebar */}
        <div className="com-layout">

          {/* Post list — SO style */}
          <div className="so-question-list">
            {loading && (
              <div className="so-empty">טוען שאלות...</div>
            )}
            {!loading && posts.length === 0 && (
              <div className="so-empty">לא נמצאו שאלות מתאימות</div>
            )}
            {posts.map(post => {
              const tags = post.tags ? post.tags.split(',').map(t => t.trim()).filter(Boolean) : []
              const isAnswered = post.status === 'answered'
              const hasReplies = post.replies_count > 0
              return (
                <div key={post.id} className="so-question-row">
                  {/* Stats sidebar */}
                  <div className="so-stats-cell">
                    <div className="so-stat-item" title="הצבעות">
                      <span className="so-stat-num">{post.votes}</span>
                      <span className="so-stat-label">הצבעות</span>
                    </div>
                    <div className={`so-stat-item ${isAnswered ? 'so-stat-answered' : hasReplies ? 'so-stat-has-replies' : ''}`} title="תגובות">
                      {isAnswered && <span className="so-check">✓</span>}
                      <span className="so-stat-num">{post.replies_count}</span>
                      <span className="so-stat-label">{post.replies_count === 1 ? 'תגובה' : 'תגובות'}</span>
                    </div>
                    <div className="so-stat-item so-stat-views" title="צפיות">
                      <span className="so-stat-num">{formatViews(post.views)}</span>
                      <span className="so-stat-label">צפיות</span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="so-content-cell">
                    <h3 className="so-question-title">
                      {isAnswered && <span className="so-accepted-badge" title="נענה">✓</span>}
                      <Link href={`/forum/${post.id}`}>{post.title}</Link>
                    </h3>
                    <p className="so-question-excerpt">{post.body.length > 200 ? post.body.slice(0, 200) + '…' : post.body}</p>
                    <div className="so-question-meta">
                      <div className="so-tags-row">
                        {tags.map(tag => (
                          <button
                            key={tag}
                            onClick={() => setActiveTag(activeTag === tag ? '' : tag)}
                            className={`so-tag${activeTag === tag ? ' so-tag-active' : ''}`}
                          >
                            {tag}
                          </button>
                        ))}
                      </div>
                      <div className="so-user-card">
                        <div className="so-user-avatar">{post.author_name.charAt(0)}</div>
                        <span className="so-user-name">{post.author_name}</span>
                        <span className="so-time">{timeAgo(post.created_at)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="so-pagination">
                <button
                  className="so-page-btn"
                  disabled={page <= 1}
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                >
                  → הקודם
                </button>
                {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                  let p: number
                  if (totalPages <= 5) {
                    p = i + 1
                  } else if (page <= 3) {
                    p = i + 1
                  } else if (page >= totalPages - 2) {
                    p = totalPages - 4 + i
                  } else {
                    p = page - 2 + i
                  }
                  return (
                    <button
                      key={p}
                      className={`so-page-btn${page === p ? ' so-page-active' : ''}`}
                      onClick={() => setPage(p)}
                    >
                      {p}
                    </button>
                  )
                })}
                {totalPages > 5 && page < totalPages - 2 && (
                  <>
                    <span className="so-page-dots">...</span>
                    <button className="so-page-btn" onClick={() => setPage(totalPages)}>{totalPages}</button>
                  </>
                )}
                <button
                  className="so-page-btn"
                  disabled={page >= totalPages}
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                >
                  הבא ←
                </button>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <aside className="com-sidebar">

            {/* CTA card */}
            <div className="com-cta-card">
              <div className="com-cta-title">🙋 שאל את הקהילה</div>
              <div className="com-cta-sub">שאל שאלה רפואית ותקבל מענה ממומחים ורופאים תוך שעות ספורות.</div>
              <div className="com-mini-stats">
                <div className="com-mini-stat">
                  <div className="com-mini-n">{stats?.active_users || 0}</div>
                  <div className="com-mini-l">משתמשים פעילים</div>
                </div>
                <div className="com-mini-stat">
                  <div className="com-mini-n">{stats?.total_posts || 0}</div>
                  <div className="com-mini-l">שאלות</div>
                </div>
              </div>
              <button onClick={() => setShowModal(true)} className="com-cta-btn">
                ✏️ פתח טופס שאלה
              </button>
            </div>

            {/* Hot tags */}
            <div className="com-card">
              <div className="com-sidebar-title">🔥 תגיות חמות</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {hotTags.map(t => (
                  <button
                    key={t.name}
                    onClick={() => setActiveTag(activeTag === t.name ? '' : t.name)}
                    className={`so-tag${activeTag === t.name ? ' so-tag-active' : ''}`}
                  >
                    {t.name}
                    <span style={{ marginRight: 5, fontWeight: 400, color: '#848d97', fontSize: 11 }}>×{t.count}</span>
                  </button>
                ))}
                {hotTags.length === 0 && <span style={{ color: '#888', fontSize: 13 }}>אין תגיות עדיין</span>}
              </div>
            </div>

            {/* Leaderboard */}
            {leaderboard.length > 0 && (
              <div className="com-card">
                <div className="com-sidebar-title">🏆 דירוג משתמשים</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {leaderboard.map((u, i) => (
                    <div key={i} className="so-lb-row">
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span className="so-lb-rank">
                          {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}`}
                        </span>
                        <div className="so-user-avatar" style={{ width: 24, height: 24, fontSize: 11 }}>{u.name.charAt(0)}</div>
                        <span style={{ fontSize: 13, fontWeight: 600, color: '#3b4045' }}>{u.name}</span>
                      </div>
                      <span className="so-lb-score">
                        {u.score} נק׳
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </aside>
        </div>
      </div>

      {/* Footer bar */}
      <div className="com-footer-bar">Doctor Scribe AI · Medical Hub · כל הזכויות שמורות</div>

      {/* ── MODAL ── */}
      {showModal && (
        <div
          className="com-modal-overlay"
          onClick={e => { if (e.target === e.currentTarget) setShowModal(false) }}
        >
          <div className="com-modal">
            <div className="com-modal-head">
              <h3 className="com-modal-head-title">✏️ שאל שאלה</h3>
              <button onClick={() => setShowModal(false)} className="com-modal-close">✕ סגור</button>
            </div>
            <div className="com-modal-body">
              <div>
                <label className="com-modal-label">כותרת השאלה</label>
                <input
                  className="com-modal-input"
                  placeholder="לדוגמה: כאב גב תחתון אחרי אימון – מה הסימנים המסוכנים?"
                  value={newTitle}
                  onChange={e => setNewTitle(e.target.value)}
                />
              </div>
              <div>
                <label className="com-modal-label">תגית ראשית</label>
                <input
                  className="com-modal-input"
                  placeholder="לדוגמה: כאבי גב, נוירולוגיה"
                  value={newTag}
                  onChange={e => setNewTag(e.target.value)}
                />
              </div>
              <div>
                <label className="com-modal-label">פירוט (גיל, רקע, מה ניסית)</label>
                <textarea
                  className="com-modal-input"
                  rows={4}
                  style={{ resize: 'vertical' }}
                  placeholder="כתוב פרטים קצרים..."
                  value={newBody}
                  onChange={e => setNewBody(e.target.value)}
                />
              </div>
            </div>
            <div className="com-modal-foot">
              <button onClick={() => setShowModal(false)} className="com-btn-cancel">ביטול</button>
              <button onClick={handleCreatePost} className="com-btn-submit">
                פרסם שאלה →
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
