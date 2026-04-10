'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import '../community-theme.css'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

type Sort = 'hot' | 'new' | 'unanswered' | 'top'

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
  created_at: string
}

interface HotTag {
  name: string
  count: number
}

const STATUS_MAP: Record<string, { text: string; color: string; bg: string; border: string }> = {
  answered: { text: '✓ נענה',     color: '#065f46', bg: 'rgba(16,185,129,0.1)',  border: 'rgba(16,185,129,0.3)'  },
  open:     { text: '❓ ללא מענה', color: '#9f1239', bg: 'rgba(244,63,94,0.08)', border: 'rgba(244,63,94,0.25)'  },
  closed:   { text: '🔒 סגור',    color: '#6b7280', bg: 'rgba(107,114,128,0.1)', border: 'rgba(107,114,128,0.3)' },
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60)    return `לפני ${mins} דקות`
  const hours = Math.floor(mins / 60)
  if (hours < 24)   return `לפני ${hours} שעות`
  const days = Math.floor(hours / 24)
  if (days < 7)     return `לפני ${days} ימים`
  const weeks = Math.floor(days / 7)
  return `לפני ${weeks} שבועות`
}

function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('access_token')
}

export default function ForumPage() {
  const [search,    setSearch]    = useState('')
  const [sort,      setSort]      = useState<Sort>('new')
  const [activeTag, setActiveTag] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [posts,     setPosts]     = useState<Post[]>([])
  const [total,     setTotal]     = useState(0)
  const [hotTags,   setHotTags]   = useState<HotTag[]>([])
  const [stats,     setStats]     = useState<any>(null)
  const [loading,   setLoading]   = useState(true)

  // New post form
  const [newTitle, setNewTitle] = useState('')
  const [newBody,  setNewBody]  = useState('')
  const [newTag,   setNewTag]   = useState('')

  const loadPosts = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.set('sort', sort)
      params.set('per_page', '12')
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
  }, [sort, search, activeTag])

  const loadStats = useCallback(async () => {
    try {
      const res = await fetch(`${API}/forum/stats`)
      if (res.ok) {
        const data = await res.json()
        setStats(data)
        setHotTags(data.hot_tags || [])
      }
    } catch {}
  }, [])

  useEffect(() => { loadPosts() }, [loadPosts])
  useEffect(() => { loadStats() }, [loadStats])

  const handleCreatePost = async () => {
    const token = getToken()
    if (!token) { alert('יש להתחבר כדי לפרסם שאלה'); return }
    if (newTitle.length < 5) { alert('כותרת חייבת להכיל לפחות 5 תווים'); return }
    if (newBody.length < 10) { alert('תוכן חייב להכיל לפחות 10 תווים'); return }

    try {
      const res = await fetch(`${API}/forum/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
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
    } catch { alert('שגיאת רשת — נסה שוב') }
  }

  const handleVote = async (postId: string, value: number) => {
    const token = getToken()
    if (!token) { alert('יש להתחבר כדי להצביע'); return }
    try {
      const res = await fetch(`${API}/forum/posts/${postId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
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

        {/* Filter pills */}
        <div className="com-pills">
          {(['hot','new','unanswered','top'] as Sort[]).map(s => (
            <button
              key={s}
              onClick={() => setSort(s)}
              className={`com-pill${sort === s ? ' com-pill-active' : ''}`}
            >
              {{ hot: '🔥 חם', new: '🆕 חדש', unanswered: '❓ ללא מענה', top: '⭐ מובילים' }[s]}
            </button>
          ))}
          <span className="com-count">{loading ? '...' : `${total} שאלות`}</span>
        </div>

        {/* Main layout — posts + sidebar */}
        <div className="com-layout">

          {/* Post list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {loading && (
              <div className="com-card" style={{ textAlign: 'center', padding: 48, color: '#888' }}>
                טוען שאלות...
              </div>
            )}
            {!loading && posts.length === 0 && (
              <div className="com-card" style={{ textAlign: 'center', padding: 48, color: '#888' }}>
                לא נמצאו שאלות מתאימות
              </div>
            )}
            {posts.map(post => {
              const s = STATUS_MAP[post.status] || STATUS_MAP.open
              const tags = post.tags ? post.tags.split(',').map(t => t.trim()).filter(Boolean) : []
              return (
                <article key={post.id} className="com-card" style={{ cursor: 'pointer' }}>
                  <Link href={`/forum/${post.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                    <div className="fr-post">

                      {/* Stats column */}
                      <div className="fr-stats-col">
                        <div className="fr-stat-box">
                          <div className="fr-stat-n">{post.replies_count}</div>
                          <div className="fr-stat-l">תגובות</div>
                        </div>
                        <div className="fr-stat-box">
                          <div className="fr-stat-n">{post.views}</div>
                          <div className="fr-stat-l">צפיות</div>
                        </div>
                        <div className="fr-stat-box" onClick={e => { e.preventDefault(); handleVote(post.id, 1) }} style={{ cursor: 'pointer' }}>
                          <div className="fr-stat-n">+{post.votes}</div>
                          <div className="fr-stat-l">הצבעות</div>
                        </div>
                      </div>

                      {/* Content */}
                      <div className="fr-post-content">
                        <h3 className="fr-post-title">{post.title}</h3>
                        <div className="fr-post-meta">
                          <span
                            className="fr-status"
                            style={{ color: s.color, background: s.bg, border: `1px solid ${s.border}` }}
                          >
                            {s.text}
                          </span>
                          {tags.map(tag => (
                            <button
                              key={tag}
                              onClick={e => { e.preventDefault(); setActiveTag(activeTag === tag ? '' : tag) }}
                              className={`com-tag${activeTag === tag ? ' com-tag-active' : ''}`}
                            >
                              {tag}
                            </button>
                          ))}
                          <span className="fr-post-author">{post.author_name} · {timeAgo(post.created_at)}</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                </article>
              )
            })}
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
                    className={`com-tag${activeTag === t.name ? ' com-tag-active' : ''}`}
                  >
                    {t.name}
                    <span style={{ marginRight: 5, fontWeight: 900, color: '#888' }}>{t.count}</span>
                  </button>
                ))}
                {hotTags.length === 0 && <span style={{ color: '#888', fontSize: 13 }}>אין תגיות עדיין</span>}
              </div>
            </div>

            {/* Keyboard hint */}
            <div style={{ textAlign: 'center', fontSize: 12, color: '#888' }}>
              <span className="com-kbd">/</span> לחיפוש · <span className="com-kbd">Esc</span> לסגירה
            </div>

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
