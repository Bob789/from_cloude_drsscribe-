'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
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
  return `לפני ${Math.floor(days / 365)} שנים`
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('he-IL', { day: 'numeric', month: 'short', year: 'numeric' })
    + ' בשעה ' + d.toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' })
}

function renderFormatted(text: string): string {
  let h = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
  // Images: ![alt](https://url)
  h = h.replace(/!\[([^\]]{0,100})\]\((https?:\/\/[^)\s]{1,500})\)/g,
    '<img src="$2" alt="$1" class="so-fmt-img" loading="lazy" />')
  // Bold: **text**
  h = h.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  // Italic: *text*
  h = h.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')
  // Font size: {size:18}text{/size} — clamped 15–24
  h = h.replace(/\{size:(\d+)\}([\s\S]+?)\{\/size\}/g, (_m, px, txt) => {
    const s = Math.max(15, Math.min(24, parseInt(px)))
    return `<span style="font-size:${s}px">${txt}</span>`
  })
  // Preset colors: {red}text{/red}
  const colorMap: Record<string, string> = {
    red: '#d32f2f', blue: '#1565c0', green: '#2e7d32',
    orange: '#e65100', purple: '#7b1fa2', teal: '#00695c', brown: '#4e342e'
  }
  for (const [name, hex] of Object.entries(colorMap)) {
    h = h.replace(new RegExp(`\\{${name}\\}([\\s\\S]+?)\\{\\/${name}\\}`, 'g'),
      `<span style="color:${hex}">$1</span>`)
  }
  // Line-by-line: headings, lists, blockquotes
  const lines = h.split('\n')
  let out = '', i = 0
  while (i < lines.length) {
    const ln = lines[i]
    if (ln.startsWith('### ')) { out += `<h3 class="so-fmt-h3">${ln.slice(4)}</h3>`; i++; continue }
    if (ln.startsWith('&gt; ')) { out += `<blockquote class="so-fmt-bq">${ln.slice(5)}</blockquote>`; i++; continue }
    if (/^\d+\.\s/.test(ln)) {
      out += '<ol class="so-fmt-ol">'
      while (i < lines.length && /^\d+\.\s/.test(lines[i]))
        out += `<li>${lines[i++].replace(/^\d+\.\s/, '')}</li>`
      out += '</ol>'; continue
    }
    if (/^[-•]\s/.test(ln)) {
      out += '<ul class="so-fmt-ul">'
      while (i < lines.length && /^[-•]\s/.test(lines[i]))
        out += `<li>${lines[i++].replace(/^[-•]\s/, '')}</li>`
      out += '</ul>'; continue
    }
    out += ln + '\n'; i++
  }
  return out
}

function isHTML(text: string): boolean {
  return /<[a-z][\s\S]*>/i.test(text)
}

function renderBody(text: string): string {
  return isHTML(text) ? text : renderFormatted(text)
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
  const [replySort, setReplySort] = useState<'votes' | 'oldest' | 'newest'>('votes')
  const editorRef = useRef<HTMLDivElement>(null)
  const [showColors, setShowColors] = useState(false)
  const [showFontSize, setShowFontSize] = useState(false)

  const execCmd = (cmd: string, value?: string) => {
    editorRef.current?.focus()
    document.execCommand(cmd, false, value)
  }

  const insertImageWYSIWYG = () => {
    const url = prompt('הכנס כתובת תמונה (URL):')
    if (!url) return
    try { new URL(url) } catch { alert('כתובת לא תקינה'); return }
    if (!/^https?:\/\//i.test(url)) { alert('הכתובת חייבת להתחיל ב-https://'); return }
    editorRef.current?.focus()
    document.execCommand('insertImage', false, url)
  }

  const getEditorHTML = (): string => {
    return editorRef.current?.innerHTML?.trim() || ''
  }

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

  const sortedReplies = [...replies].sort((a, b) => {
    // Accepted always on top
    if (a.is_accepted && !b.is_accepted) return -1
    if (!a.is_accepted && b.is_accepted) return 1
    if (replySort === 'votes') return b.votes - a.votes
    if (replySort === 'newest') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  })

  const handleReply = async () => {
    const html = getEditorHTML()
    if (html.length < 2 || html === '<br>') return
    try {
      const res = await authFetch(`${API}/forum/posts/${id}/replies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ body: html }),
      })
      if (res.ok) {
        if (editorRef.current) editorRef.current.innerHTML = ''
        loadReplies()
        loadPost()
      } else {
        const err = await res.json().catch(() => null)
        alert(err?.detail || 'שגיאה בשליחת התגובה')
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : ''
      if (msg === 'no_token' || msg === 'token_expired') {
        alert('יש להתחבר מחדש כדי להגיב')
        window.location.href = '/login'
      } else { alert('שגיאת רשת — נסה שוב') }
    }
  }

  const handleVotePost = async (value: number) => {
    try {
      const res = await authFetch(`${API}/forum/posts/${id}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value }),
      })
      if (res.ok) loadPost()
    } catch {}
  }

  const handleVoteReply = async (replyId: string, value: number) => {
    try {
      const res = await authFetch(`${API}/forum/replies/${replyId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value }),
      })
      if (res.ok) loadReplies()
    } catch {}
  }

  const [acceptToast, setAcceptToast] = useState<string | null>(null)

  const handleAcceptReply = async (replyId: string) => {
    try {
      const res = await authFetch(`${API}/forum/replies/${replyId}/accept`, {
        method: 'POST',
        headers: {},
      })
      if (res.ok) {
        setAcceptToast('+15 נקודות למשיב!')
        setTimeout(() => setAcceptToast(null), 3000)
        loadReplies(); loadPost()
      }
    } catch {}
  }

  if (loading) return (
    <div id="forum-page-root">
      <div className="com-body" style={{ textAlign: 'center', padding: 80, color: '#848d97' }}>טוען...</div>
    </div>
  )

  if (error || !post) return (
    <div id="forum-page-root">
      <div className="com-body" style={{ textAlign: 'center', padding: 80, color: '#848d97' }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>😕</div>
        <div>השאלה לא נמצאה</div>
        <Link href="/forum" style={{ color: '#0074cc', marginTop: 16, display: 'inline-block' }}>
          ← חזרה לפורום
        </Link>
      </div>
    </div>
  )

  const tags = post.tags ? post.tags.split(',').map(t => t.trim()).filter(Boolean) : []
  const currentUserId = getCurrentUserId()
  const isAuthor = currentUserId === post.author_id

  return (
    <div id="forum-page-root">

      {/* ── Question Header (SO style) ── */}
      <div className="so-post-header">
        <div className="so-post-header-top">
          <Link href="/forum" className="so-back-link">← חזרה לפורום</Link>
        </div>
        <h1 className="so-post-title">{post.title}</h1>
        <div className="so-post-header-meta">
          <span>נשאל <time>{formatDate(post.created_at)}</time></span>
          {post.updated_at && <span>עודכן <time>{timeAgo(post.updated_at)}</time></span>}
          <span>נצפה {post.views} פעמים</span>
        </div>
      </div>

      <div className="so-post-divider"></div>

      <div className="so-post-body-wrap">
        <div className="so-post-layout">

          {/* ═══ Main column ═══ */}
          <div className="so-post-main">

            {/* ── Question ── */}
            <div className="so-post-cell">
              {/* Vote column */}
              <div className="so-vote-cell">
                <button onClick={() => handleVotePost(1)} className="so-vote-btn so-vote-up" title="הצבע למעלה">
                  <svg width="36" height="36" viewBox="0 0 36 36"><path d="M2 25h32L18 9 2 25Z" fill="currentColor"/></svg>
                </button>
                <div className="so-vote-count">{post.votes}</div>
                <button onClick={() => handleVotePost(-1)} className="so-vote-btn so-vote-down" title="הצבע למטה">
                  <svg width="36" height="36" viewBox="0 0 36 36"><path d="M2 11h32L18 27 2 11Z" fill="currentColor"/></svg>
                </button>
                {post.status === 'answered' && (
                  <div className="so-accepted-big" title="לשאלה זו יש תשובה מקובלת">
                    <svg width="24" height="24" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/></svg>
                  </div>
                )}
              </div>

              {/* Post content */}
              <div className="so-post-content">
                <div className="so-post-text so-fmt-content" dangerouslySetInnerHTML={{ __html: renderBody(post.body) }} />

                <div className="so-post-tags">
                  {tags.map(tag => (
                    <Link key={tag} href={`/forum?tag=${tag}`} className="so-tag">{tag}</Link>
                  ))}
                </div>

                <div className="so-post-actions-row">
                  <div className="so-post-actions">
                    <button className="so-action-link">שתף</button>
                    <button className="so-action-link">עקוב</button>
                  </div>
                  <div className="so-user-box so-user-box-asker">
                    <div className="so-user-box-time">נשאל {timeAgo(post.created_at)}</div>
                    <div className="so-user-box-info">
                      <div className="so-user-avatar-md">{post.author_name.charAt(0)}</div>
                      <div>
                        <div className="so-user-box-name">{post.author_name}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* ── Answers header ── */}
            <div className="so-answers-header">
              <h2 className="so-answers-count">{replies.length} {replies.length === 1 ? 'תשובה' : 'תשובות'}</h2>
              <div className="so-answers-sort">
                מיון לפי:
                {(['votes', 'oldest', 'newest'] as const).map(s => (
                  <button
                    key={s}
                    onClick={() => setReplySort(s)}
                    className={`so-sort-btn${replySort === s ? ' so-sort-active' : ''}`}
                  >
                    {{ votes: 'הצבעות', oldest: 'ישן ביותר', newest: 'חדש ביותר' }[s]}
                  </button>
                ))}
              </div>
            </div>

            {/* ── Answer list ── */}
            {sortedReplies.map(reply => (
              <div key={reply.id} className={`so-post-cell so-answer-cell${reply.is_accepted ? ' so-answer-accepted' : ''}`} id={`answer-${reply.id}`}>
                <div className="so-vote-cell">
                  <button onClick={() => handleVoteReply(reply.id, 1)} className="so-vote-btn so-vote-up" title="הצבע למעלה">
                    <svg width="36" height="36" viewBox="0 0 36 36"><path d="M2 25h32L18 9 2 25Z" fill="currentColor"/></svg>
                  </button>
                  <div className="so-vote-count">{reply.votes}</div>
                  <button onClick={() => handleVoteReply(reply.id, -1)} className="so-vote-btn so-vote-down" title="הצבע למטה">
                    <svg width="36" height="36" viewBox="0 0 36 36"><path d="M2 11h32L18 27 2 11Z" fill="currentColor"/></svg>
                  </button>
                  {reply.is_accepted ? (
                    <div className="so-accepted-block">
                      <div className="so-accepted-big" title="תשובה מאושרת">
                        <svg width="24" height="24" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/></svg>
                      </div>
                      <span className="so-accepted-label">תשובה מאושרת</span>
                    </div>
                  ) : isAuthor && post.status !== 'answered' ? (
                    <button onClick={() => handleAcceptReply(reply.id)} className="so-accept-btn" title="אשר כתשובה הטובה ביותר">
                      <svg width="24" height="24" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/></svg>
                      <span className="so-accept-btn-text">אשר תשובה</span>
                    </button>
                  ) : null}
                </div>

                <div className="so-post-content">
                  <div className="so-post-text so-fmt-content" dangerouslySetInnerHTML={{ __html: renderBody(reply.body) }} />

                  <div className="so-post-actions-row">
                    <div className="so-post-actions">
                      <button className="so-action-link">שתף</button>
                    </div>
                    <div className="so-user-box">
                      <div className="so-user-box-time">ענה {timeAgo(reply.created_at)}</div>
                      <div className="so-user-box-info">
                        <div className="so-user-avatar-md">{reply.author_name.charAt(0)}</div>
                        <div>
                          <div className="so-user-box-name">{reply.author_name}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {replies.length === 0 && (
              <div className="so-no-answers">
                עדיין אין תשובות. היה הראשון לענות!
              </div>
            )}

            {/* ── Your Answer form ── */}
            <div className="so-answer-form">
              <h2 className="so-answer-form-title">התשובה שלך</h2>
              <div className="so-editor-toolbar">
                <button type="button" className="so-tb-btn" title="מודגש" onClick={() => execCmd('bold')}><b>B</b></button>
                <button type="button" className="so-tb-btn so-tb-italic" title="נטוי" onClick={() => execCmd('italic')}><i>I</i></button>
                <span className="so-tb-sep" />
                <button type="button" className="so-tb-btn" title="כותרת" onClick={() => execCmd('formatBlock', 'h3')}>H</button>
                <button type="button" className="so-tb-btn" title="רשימה ממוספרת" onClick={() => execCmd('insertOrderedList')}>1.</button>
                <button type="button" className="so-tb-btn" title="רשימה" onClick={() => execCmd('insertUnorderedList')}>•</button>
                <button type="button" className="so-tb-btn" title="ציטוט" onClick={() => execCmd('formatBlock', 'blockquote')}>❝</button>
                <span className="so-tb-sep" />
                <button type="button" className="so-tb-btn" title="תמונה" onClick={insertImageWYSIWYG}>🖼</button>
                <div className="so-tb-color-wrap">
                  <button type="button" className="so-tb-btn" title="צבע טקסט" onClick={() => { setShowColors(!showColors); setShowFontSize(false) }}>🎨</button>
                  {showColors && (
                    <div className="so-tb-color-dropdown">
                      {Object.entries({ red: '#d32f2f', blue: '#1565c0', green: '#2e7d32', orange: '#e65100', purple: '#7b1fa2', teal: '#00695c', brown: '#4e342e' }).map(([name, hex]) => (
                        <button key={name} className="so-tb-color-dot" style={{ background: hex }} title={name}
                          onClick={() => { execCmd('foreColor', hex); setShowColors(false) }} />
                      ))}
                    </div>
                  )}
                </div>
                <div className="so-tb-color-wrap">
                  <button type="button" className="so-tb-btn" title="גודל פונט" onClick={() => { setShowFontSize(!showFontSize); setShowColors(false) }}>A<span className="so-tb-fontsize-icon">±</span></button>
                  {showFontSize && (
                    <div className="so-tb-fontsize-dropdown">
                      {[{label: 'רגיל', px: '3'}, {label: 'בינוני', px: '4'}, {label: 'גדול', px: '5'}, {label: 'גדול מאוד', px: '6'}].map(opt => (
                        <button key={opt.px} className="so-tb-fontsize-opt"
                          onClick={() => { execCmd('fontSize', opt.px); setShowFontSize(false) }}>
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <div
                ref={editorRef}
                className="so-wysiwyg-editor"
                contentEditable
                data-placeholder="כתוב את תשובתך כאן..."
                onFocus={() => { setShowColors(false); setShowFontSize(false) }}
              />
              <button
                onClick={handleReply}
                className="so-submit-answer-btn"
              >
                פרסם תשובה
              </button>
            </div>
          </div>

          {/* ═══ Sidebar ═══ */}
          <aside className="com-sidebar">
            {/* Stats widget */}
            <div className="so-sidebar-widget">
              <div className="so-sidebar-widget-header">סטטיסטיקות</div>
              <div className="so-sidebar-widget-body">
                <div className="so-sidebar-stat-row"><span>👁️</span> {post.views} צפיות</div>
                <div className="so-sidebar-stat-row"><span>💬</span> {replies.length} {replies.length === 1 ? 'תשובה' : 'תשובות'}</div>
                <div className="so-sidebar-stat-row"><span>👍</span> {post.votes} הצבעות</div>
                <div className="so-sidebar-stat-row"><span>📅</span> נשאל {timeAgo(post.created_at)}</div>
              </div>
            </div>

            {/* Tags widget */}
            {tags.length > 0 && (
              <div className="so-sidebar-widget">
                <div className="so-sidebar-widget-header">תגיות קשורות</div>
                <div className="so-sidebar-widget-body" style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {tags.map(tag => (
                    <Link key={tag} href={`/forum?tag=${tag}`} className="so-tag">{tag}</Link>
                  ))}
                </div>
              </div>
            )}
          </aside>
        </div>
      </div>

      {/* Medical disclaimer */}
      <div className="so-medical-disclaimer">⚕️ המידע באתר זה הוא כללי בלבד ואינו מהווה ייעוץ רפואי. בכל מצב רפואי — פנה לרופא.</div>

      {acceptToast && <div className="so-accept-toast">{acceptToast}</div>}
      <div className="com-footer-bar">Doctor Scribe AI · Medical Hub · כל הזכויות שמורות</div>
    </div>
  )
}
