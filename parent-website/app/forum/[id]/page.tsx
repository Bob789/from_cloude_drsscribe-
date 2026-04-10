'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import '../../community-theme.css'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

interface Post {
  id: string
  title: string
  body: string
  status: string
  author_id: string
  author_name: string
  tags: string | null
  replies_count: number
  views: number
  votes: number
  created_at: string
  updated_at: string | null
}

interface Reply {
  id: string
  post_id: string
  author_id: string
  author_name: string
  body: string
  votes: number
  is_accepted: boolean
  created_at: string
}

const STATUS_MAP: Record<string, { text: string; color: string; bg: string; border: string }> = {
  answered: { text: '✓ נענה',     color: '#065f46', bg: 'rgba(16,185,129,0.1)',  border: 'rgba(16,185,129,0.3)'  },
  open:     { text: '❓ פתוח',    color: '#9f1239', bg: 'rgba(244,63,94,0.08)', border: 'rgba(244,63,94,0.25)'  },
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

function getCurrentUserId(): string | null {
  if (typeof window === 'undefined') return null
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return user.id || null
  } catch { return null }
}

export default function ForumPostPage() {
  const { id } = useParams<{ id: string }>()
  const [post,    setPost]    = useState<Post | null>(null)
  const [replies, setReplies] = useState<Reply[]>([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(false)
  const [replyBody, setReplyBody] = useState('')

  const loadPost = useCallback(async () => {
    try {
      const res = await fetch(`${API}/forum/posts/${id}`)
      if (!res.ok) { setError(true); return }
      setPost(await res.json())
    } catch { setError(true) }
    finally { setLoading(false) }
  }, [id])

  const loadReplies = useCallback(async () => {
    try {
      const res = await fetch(`${API}/forum/posts/${id}/replies`)
      if (res.ok) setReplies(await res.json())
    } catch {}
  }, [id])

  useEffect(() => { loadPost() }, [loadPost])
  useEffect(() => { loadReplies() }, [loadReplies])

  const handleReply = async () => {
    const token = getToken()
    if (!token) { alert('יש להתחבר כדי להגיב'); return }
    if (replyBody.length < 2) return

    try {
      const res = await fetch(`${API}/forum/posts/${id}/replies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ body: replyBody }),
      })
      if (res.ok) {
        setReplyBody('')
        loadReplies()
        loadPost()
      } else {
        const err = await res.json().catch(() => null)
        alert(err?.detail || 'שגיאה בשליחת התגובה')
      }
    } catch { alert('שגיאת רשת — נסה שוב') }
  }

  const handleVotePost = async (value: number) => {
    const token = getToken()
    if (!token) { alert('יש להתחבר כדי להצביע'); return }
    try {
      const res = await fetch(`${API}/forum/posts/${id}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ value }),
      })
      if (res.ok) loadPost()
    } catch {}
  }

  const handleVoteReply = async (replyId: string, value: number) => {
    const token = getToken()
    if (!token) { alert('יש להתחבר כדי להצביע'); return }
    try {
      const res = await fetch(`${API}/forum/replies/${replyId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ value }),
      })
      if (res.ok) loadReplies()
    } catch {}
  }

  const handleAcceptReply = async (replyId: string) => {
    const token = getToken()
    if (!token) return
    try {
      const res = await fetch(`${API}/forum/replies/${replyId}/accept`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) { loadReplies(); loadPost() }
    } catch {}
  }

  if (loading) return (
    <div id="forum-page-root">
      <div className="com-body" style={{ textAlign: 'center', padding: 80, color: '#888' }}>טוען...</div>
    </div>
  )

  if (error || !post) return (
    <div id="forum-page-root">
      <div className="com-body" style={{ textAlign: 'center', padding: 80, color: '#888' }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>😕</div>
        <div>השאלה לא נמצאה</div>
        <Link href="/forum" style={{ color: '#10b981', marginTop: 16, display: 'inline-block' }}>
          ← חזרה לפורום
        </Link>
      </div>
    </div>
  )

  const s = STATUS_MAP[post.status] || STATUS_MAP.open
  const tags = post.tags ? post.tags.split(',').map(t => t.trim()).filter(Boolean) : []
  const currentUserId = getCurrentUserId()
  const isAuthor = currentUserId === post.author_id

  return (
    <div id="forum-page-root">

      {/* ── BLOCK HEADER ── */}
      <div className="com-block-header">
        <div>
          <Link href="/forum" style={{ color: '#10b981', fontSize: 13, textDecoration: 'none' }}>
            ← חזרה לפורום
          </Link>
          <div className="com-block-title" style={{ fontSize: 22, marginTop: 8 }}>{post.title}</div>
        </div>
      </div>

      <div className="com-title-lines">
        <div className="com-title-line"></div>
        <div className="com-title-line"></div>
      </div>

      <div className="com-body">
        <div className="com-layout">

          {/* Main content */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

            {/* Post body */}
            <div className="com-card" style={{ padding: 24 }}>
              <div style={{ display: 'flex', gap: 16 }}>

                {/* Vote column */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, minWidth: 48 }}>
                  <button
                    onClick={() => handleVotePost(1)}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 20, color: '#10b981' }}
                    title="הצבע למעלה"
                  >▲</button>
                  <span style={{ fontWeight: 700, fontSize: 18, color: '#e5e7eb' }}>{post.votes}</span>
                  <button
                    onClick={() => handleVotePost(-1)}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 20, color: '#ef4444' }}
                    title="הצבע למטה"
                  >▼</button>
                </div>

                {/* Body */}
                <div style={{ flex: 1 }}>
                  <div style={{ color: '#e5e7eb', fontSize: 15, lineHeight: 1.8, whiteSpace: 'pre-wrap' }}>
                    {post.body}
                  </div>
                  <div style={{ marginTop: 16, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                    <span className="fr-status" style={{ color: s.color, background: s.bg, border: `1px solid ${s.border}` }}>
                      {s.text}
                    </span>
                    {tags.map(tag => (
                      <Link key={tag} href={`/forum?tag=${tag}`} className="com-tag">{tag}</Link>
                    ))}
                  </div>
                  <div style={{ marginTop: 12, fontSize: 12, color: '#888' }}>
                    נשאל ע״י <strong style={{ color: '#ccc' }}>{post.author_name}</strong> · {timeAgo(post.created_at)}
                    {' · '}{post.views} צפיות
                  </div>
                </div>
              </div>
            </div>

            {/* Replies header */}
            <div style={{ fontSize: 16, fontWeight: 700, color: '#e5e7eb', padding: '8px 0' }}>
              💬 {replies.length} תגובות
            </div>

            {/* Replies */}
            {replies.map(reply => (
              <div key={reply.id} className="com-card" style={{
                padding: 20,
                borderRight: reply.is_accepted ? '3px solid #10b981' : undefined,
              }}>
                <div style={{ display: 'flex', gap: 16 }}>

                  {/* Vote column */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, minWidth: 48 }}>
                    <button
                      onClick={() => handleVoteReply(reply.id, 1)}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 18, color: '#10b981' }}
                    >▲</button>
                    <span style={{ fontWeight: 700, fontSize: 16, color: '#e5e7eb' }}>{reply.votes}</span>
                    <button
                      onClick={() => handleVoteReply(reply.id, -1)}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 18, color: '#ef4444' }}
                    >▼</button>
                    {reply.is_accepted && (
                      <span style={{ color: '#10b981', fontSize: 20, marginTop: 4 }} title="תשובה מקובלת">✓</span>
                    )}
                  </div>

                  {/* Reply body */}
                  <div style={{ flex: 1 }}>
                    <div style={{ color: '#e5e7eb', fontSize: 14, lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
                      {reply.body}
                    </div>
                    <div style={{ marginTop: 10, display: 'flex', gap: 12, alignItems: 'center', fontSize: 12, color: '#888' }}>
                      <strong style={{ color: '#ccc' }}>{reply.author_name}</strong>
                      <span>{timeAgo(reply.created_at)}</span>
                      {isAuthor && !reply.is_accepted && post.status !== 'answered' && (
                        <button
                          onClick={() => handleAcceptReply(reply.id)}
                          style={{
                            background: 'none', border: '1px solid #10b981', borderRadius: 6,
                            color: '#10b981', padding: '2px 10px', cursor: 'pointer', fontSize: 11,
                          }}
                        >
                          ✓ קבל כתשובה
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {replies.length === 0 && (
              <div className="com-card" style={{ textAlign: 'center', padding: 32, color: '#888' }}>
                אין תגובות עדיין — היה הראשון להגיב!
              </div>
            )}

            {/* Reply form */}
            <div className="com-card" style={{ padding: 20 }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: '#e5e7eb', marginBottom: 10 }}>✏️ הוסף תגובה</div>
              <textarea
                value={replyBody}
                onChange={e => setReplyBody(e.target.value)}
                placeholder="כתוב את תגובתך כאן..."
                rows={4}
                style={{
                  width: '100%', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: 8, padding: 12, color: '#e5e7eb', fontSize: 14, resize: 'vertical',
                }}
              />
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 10 }}>
                <button
                  onClick={handleReply}
                  disabled={replyBody.length < 2}
                  className="com-cta-btn"
                  style={{ width: 'auto', padding: '8px 24px', opacity: replyBody.length < 2 ? 0.5 : 1 }}
                >
                  שלח תגובה →
                </button>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <aside className="com-sidebar">
            <div className="com-card" style={{ padding: 16 }}>
              <div className="com-sidebar-title">📊 סטטיסטיקות</div>
              <div style={{ fontSize: 13, color: '#aaa', display: 'flex', flexDirection: 'column', gap: 8 }}>
                <div>👁️ {post.views} צפיות</div>
                <div>💬 {replies.length} תגובות</div>
                <div>👍 {post.votes} הצבעות</div>
                <div>📅 {timeAgo(post.created_at)}</div>
              </div>
            </div>

            {tags.length > 0 && (
              <div className="com-card" style={{ padding: 16 }}>
                <div className="com-sidebar-title">🏷️ תגיות</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {tags.map(tag => (
                    <Link key={tag} href={`/forum?tag=${tag}`} className="com-tag">{tag}</Link>
                  ))}
                </div>
              </div>
            )}
          </aside>
        </div>
      </div>

      <div className="com-footer-bar">Doctor Scribe AI · Medical Hub · כל הזכויות שמורות</div>
    </div>
  )
}
