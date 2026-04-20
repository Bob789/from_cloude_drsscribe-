// NOTE: This is the system admin panel. URL is not published anywhere.
// Access is restricted to the system administrator only.
'use client'

import { useState, useEffect, useCallback } from 'react'
import Script from 'next/script'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'
const GOOGLE_CLIENT_ID = '459295230393-a7tahndgdhses9shhg0oue74ealf009r.apps.googleusercontent.com'
const ADMIN_EMAIL = 'yossil1306@gmail.com'

type Tab = 'stats' | 'users' | 'messages' | 'errors' | 'content' | 'analytics' | 'devtools'

function useAdminData(token: string | null) {
  const [stats, setStats] = useState<any>(null)
  const [users, setUsers] = useState<any[]>([])
  const [threads, setThreads] = useState<any[]>([])
  const [errors, setErrors] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const fetchAll = useCallback(async () => {
    if (!token) return
    const h = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
    setLoading(true)
    try {
      const [s, u, t, e] = await Promise.all([
        fetch(`${API}/admin/stats`, { headers: h }).then(r => r.json()),
        fetch(`${API}/admin/users`, { headers: h }).then(r => r.json()),
        fetch(`${API}/admin/messages/threads`, { headers: h }).then(r => r.json()),
        fetch(`${API}/admin/activity-logs?error_only=true&per_page=50`, { headers: h }).then(r => r.json()),
      ])
      setStats(s)
      setUsers(Array.isArray(u) ? u : [])
      setThreads(Array.isArray(t) ? t : [])
      setErrors(e?.items || [])
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }, [token])

  useEffect(() => { fetchAll() }, [fetchAll])
  return { stats, users, threads, errors, loading, refetch: fetchAll }
}

export default function CpanelPage() {
  const [token, setToken] = useState<string | null>(null)
  const [loginError, setLoginError] = useState('')
  const [loginLoading, setLoginLoading] = useState(false)
  const [tab, setTab] = useState<Tab>('stats')
  const [searchUser, setSearchUser] = useState('')
  const [impersonateUrl, setImpersonateUrl] = useState<string | null>(null)
  const { stats, users, threads, errors, loading, refetch } = useAdminData(token)

  // Messages state
  const [selectedThread, setSelectedThread] = useState<any>(null)
  const [threadMessages, setThreadMessages] = useState<any[]>([])
  const [threadLoading, setThreadLoading] = useState(false)
  const [replyBody, setReplyBody] = useState('')
  const [replySending, setReplySending] = useState(false)
  const [replyAttachments, setReplyAttachments] = useState<any[]>([])
  const [showCompose, setShowCompose] = useState(false)
  const [composeSubject, setComposeSubject] = useState('')
  const [composeBody, setComposeBody] = useState('')
  const [composeRecipients, setComposeRecipients] = useState<string[]>([])
  const [composeSending, setComposeSending] = useState(false)
  const [composeResult, setComposeResult] = useState('')
  const [recipientSearch, setRecipientSearch] = useState('')
  const [composeAttachments, setComposeAttachments] = useState<any[]>([])
  const [uploading, setUploading] = useState(false)
  const [expandedUsers, setExpandedUsers] = useState<Set<string>>(new Set())

  // Content state
  const [articles, setArticles] = useState<any[]>([])
  const [articleJobs, setArticleJobs] = useState<any[]>([])
  const [articleStats, setArticleStats] = useState<any>(null)
  const [genTopic, setGenTopic] = useState('')
  const [genConfig, setGenConfig] = useState<any>({ tone: 'professional', audience: 'general', length: 'medium', persona: 'general' })
  const [generating, setGenerating] = useState(false)
  const [genResult, setGenResult] = useState<any>(null)
  const [_editArticle, _setEditArticle] = useState<any>(null) // reserved for future editor

  // Glossary state
  const [glossaryTerms, setGlossaryTerms] = useState<any[]>([])
  const [newTerm, setNewTerm] = useState('')
  const [newDefinition, setNewDefinition] = useState('')
  const [glossarySaving, setGlossarySaving] = useState(false)

  // Analytics state
  const [analyticsData, setAnalyticsData] = useState<any>(null)
  const [analyticsHours, setAnalyticsHours] = useState(24)
  const [analyticsLoading, setAnalyticsLoading] = useState(false)

  const fetchAnalytics = useCallback(async (h = analyticsHours) => {
    if (!token) return
    setAnalyticsLoading(true)
    try {
      const res = await fetch(`${API}/analytics/dashboard?hours=${h}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setAnalyticsData(await res.json())
    } catch {}
    finally { setAnalyticsLoading(false) }
  }, [token, analyticsHours])

  // Dev Tools state
  const [devToolsState, setDevToolsState] = useState<any>(null)
  const [devToolsBusy, setDevToolsBusy] = useState(false)
  const [devToolsError, setDevToolsError] = useState<string | null>(null)

  // Capture form state
  const [captureUrl, setCaptureUrl] = useState('http://localhost/he')
  const [captureFullPage, setCaptureFullPage] = useState(true)
  const [captureWaitMs, setCaptureWaitMs] = useState(2500)
  const [captureViewportW, setCaptureViewportW] = useState(1440)
  const [captureViewportH, setCaptureViewportH] = useState(900)
  const [captureUseAuth, setCaptureUseAuth] = useState(false)
  const [captureLocale, setCaptureLocale] = useState('he-IL')
  const [devToolsToken, setDevToolsToken] = useState('dev-token-change-me')
  const [captureBusy, setCaptureBusy] = useState(false)
  const [captureError, setCaptureError] = useState<string | null>(null)
  const [captureResult, setCaptureResult] = useState<{ kind: 'png' | 'html'; url: string; filename: string } | null>(null)

  const ensureGoogleOAuth = async (): Promise<any | null> => {
    const w = window as any
    if (w.google?.accounts?.oauth2) return w.google

    const waitForGoogle = (timeoutMs: number) => new Promise<any | null>((resolve) => {
      const started = Date.now()
      const timer = setInterval(() => {
        if (w.google?.accounts?.oauth2) {
          clearInterval(timer)
          resolve(w.google)
          return
        }
        if (Date.now() - started > timeoutMs) {
          clearInterval(timer)
          resolve(null)
        }
      }, 120)
    })

    const preloaded = await waitForGoogle(1800)
    if (preloaded) return preloaded

    let script = document.querySelector('script[data-google-gsi="1"]') as HTMLScriptElement | null
    if (!script) {
      script = document.createElement('script')
      script.src = 'https://accounts.google.com/gsi/client'
      script.async = true
      script.defer = true
      script.setAttribute('data-google-gsi', '1')
      document.head.appendChild(script)
    }

    await new Promise<void>((resolve) => {
      let resolved = false
      const finish = () => {
        if (resolved) return
        resolved = true
        resolve()
      }
      script!.addEventListener('load', finish, { once: true })
      script!.addEventListener('error', finish, { once: true })
      setTimeout(finish, 3500)
    })

    return await waitForGoogle(2000)
  }

  const runCapture = async (kind: 'screenshot' | 'flatten') => {
    setCaptureBusy(true); setCaptureError(null); setCaptureResult(null)
    try {
      const body: any = {
        url: captureUrl,
        full_page: captureFullPage,
        wait_ms: captureWaitMs,
        locale: captureLocale,
        viewport_width: captureViewportW,
        viewport_height: captureViewportH,
      }
      if (captureUseAuth && token) body.auth_token = token
      const res = await fetch(`/cpanel/api/capture?kind=${kind}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`)
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const ts = new Date().toISOString().replace(/[:.]/g, '-')
      const filename = kind === 'screenshot' ? `capture-${ts}.png` : `flatten-${ts}.html`
      setCaptureResult({
        kind: kind === 'screenshot' ? 'png' : 'html',
        url,
        filename,
      })
      // Auto-trigger download so the user always gets the file, even if the
      // preview iframe/img fails to render (e.g. CSP, X-Frame-Options).
      try {
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        a.remove()
      } catch { /* preview link still works as fallback */ }
    } catch (e: any) {
      setCaptureError(e.message || String(e))
    } finally {
      setCaptureBusy(false)
    }
  }

  const fetchDevTools = useCallback(async () => {
    if (!token) return
    setDevToolsBusy(true); setDevToolsError(null)
    try {
      const res = await fetch(`${API}/admin/dev-tools/status`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`)
      setDevToolsState(await res.json())
    } catch (e: any) {
      setDevToolsError(e.message || String(e))
    } finally { setDevToolsBusy(false) }
  }, [token])

  const devToolsAction = async (action: 'start' | 'stop') => {
    if (!token) return
    setDevToolsBusy(true); setDevToolsError(null)
    try {
      const res = await fetch(`${API}/admin/dev-tools/${action}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`)
      const data = await res.json()
      setDevToolsState(data.state || null)
    } catch (e: any) {
      setDevToolsError(e.message || String(e))
    } finally { setDevToolsBusy(false) }
  }

  useEffect(() => { if (tab === 'devtools') fetchDevTools() }, [tab, fetchDevTools])

  useEffect(() => { if (tab === 'analytics') fetchAnalytics() }, [tab])

  const fetchContent = useCallback(async () => {
    if (!token) return
    const h = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
    try {
      const [arts, jobs, st] = await Promise.all([
        fetch(`${API}/admin/articles?per_page=100`, { headers: h }).then(r => r.json()),
        fetch(`${API}/admin/articles/jobs`, { headers: h }).then(r => r.json()),
        fetch(`${API}/admin/articles/stats`, { headers: h }).then(r => r.json()),
      ])
      setArticles(arts?.items || [])
      setArticleJobs(Array.isArray(jobs) ? jobs : [])
      setArticleStats(st)
    } catch {}
  }, [token])

  useEffect(() => {
    if (tab === 'content') {
      fetchContent()
      fetch(`${API}/glossary`).then(r => r.ok ? r.json() : []).then(setGlossaryTerms).catch(() => {})
    }
  }, [tab, fetchContent])

  const addGlossaryTerm = async () => {
    if (!token || !newTerm.trim() || !newDefinition.trim()) return
    setGlossarySaving(true)
    try {
      const res = await fetch(`${API}/admin/glossary`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ term: newTerm.trim(), definition: newDefinition.trim() }),
      })
      if (res.ok) {
        setNewTerm('')
        setNewDefinition('')
        const updated = await fetch(`${API}/glossary`).then(r => r.json())
        setGlossaryTerms(updated)
      }
    } catch {}
    finally { setGlossarySaving(false) }
  }

  const deleteGlossaryTerm = async (id: string) => {
    if (!token) return
    await fetch(`${API}/admin/glossary/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
    const updated = await fetch(`${API}/glossary`).then(r => r.json())
    setGlossaryTerms(updated)
  }

  const generateArticle = async () => {
    if (!token || !genTopic.trim()) return
    setGenerating(true)
    setGenResult(null)
    try {
      const res = await fetch(`${API}/admin/articles/generate`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: genTopic.trim(), config: genConfig }),
      })
      const data = await res.json()
      setGenResult(data)
      if (data.ok) { setGenTopic(''); fetchContent() }
    } catch (e) { setGenResult({ ok: false, error: 'שגיאת חיבור' }) }
    finally { setGenerating(false) }
  }

  const changeArticleStatus = async (articleId: string, newStatus: string) => {
    if (!token) return
    await fetch(`${API}/admin/articles/${articleId}/status`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_status: newStatus }),
    })
    fetchContent()
  }

  const deleteArticle = async (articleId: string) => {
    if (!token) return
    await fetch(`${API}/admin/articles/${articleId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
    fetchContent()
  }

  const handleGoogleLogin = async () => {
    setLoginError('')
    setLoginLoading(true)
    try {
      const google = await ensureGoogleOAuth()
      if (!google?.accounts?.oauth2) {
        setLoginError('שגיאה בטעינת שירות Google — בדוק חיבור אינטרנט או חסימת סקריפטים ונסה שוב')
        setLoginLoading(false)
        return
      }
      const client = google.accounts.oauth2.initTokenClient({
        client_id: GOOGLE_CLIENT_ID,
        scope: 'email profile openid',
        callback: async (tokenResponse: any) => {
          if (tokenResponse.error) { setLoginError('הכניסה עם Google נכשלה — נסה שוב'); setLoginLoading(false); return }
          try {
            const res = await fetch(`${API}/auth/google`, {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ token: tokenResponse.access_token, token_type: 'access_token' }),
            })
            if (!res.ok) { setLoginError('הכניסה נכשלה — נסה שוב'); setLoginLoading(false); return }
            const data = await res.json()
            if (data.user?.email !== ADMIN_EMAIL && data.user?.role !== 'admin') { setLoginError('אין לך הרשאה לגשת ללוח הבקרה'); setLoginLoading(false); return }
            setToken(data.access_token)
          } catch { setLoginError('שגיאת חיבור לשרת — נסה שוב') }
          finally { setLoginLoading(false) }
        },
      })
      client.requestAccessToken()
    } catch { setLoginError('שגיאה בכניסה — נסה שוב'); setLoginLoading(false) }
  }

  const toggleBlock = async (userId: string, active: boolean) => {
    if (!token) return
    await fetch(`${API}/admin/users/${userId}/active?active=${!active}`, { method: 'PUT', headers: { Authorization: `Bearer ${token}` } })
    refetch()
  }

  const impersonate = async (userId: string) => {
    if (!token) return
    const res = await fetch(`${API}/admin/impersonate/${userId}`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } })
    const data = await res.json()
    setImpersonateUrl(`https://app.drsscribe.com/dashboard?impersonate=${data.access_token}`)
  }

  // ── Messages functions ──────────────────────────────────────────────────────

  const openThread = async (thread: any) => {
    if (!token) return
    setSelectedThread(thread)
    setThreadLoading(true)
    setReplyBody('')
    try {
      const res = await fetch(`${API}/admin/messages/thread/${thread.thread_id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      const msgs = await res.json()
      setThreadMessages(Array.isArray(msgs) ? msgs : [])
    } catch { setThreadMessages([]) }
    finally { setThreadLoading(false) }
  }

  const sendReply = async () => {
    if (!token || !selectedThread || !replyBody.trim()) return
    setReplySending(true)
    try {
      await fetch(`${API}/admin/messages/compose`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: `תגובה: ${selectedThread.subject}`,
          body: replyBody.trim(),
          recipient_ids: [selectedThread.user_id],
          thread_id: selectedThread.thread_id,
          attachments: replyAttachments,
        }),
      })
      setReplyBody('')
      setReplyAttachments([])
      openThread(selectedThread)
      refetch()
    } catch (err) { console.error(err) }
    finally { setReplySending(false) }
  }

  const handleReplyFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !token) return
    if (file.size > 10 * 1024 * 1024) { alert('קובץ גדול מדי — מקסימום 10MB'); return }
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch(`${API}/messages/upload-attachment`, {
        method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: formData,
      })
      if (!res.ok) { const err = await res.json(); alert(err.message || 'שגיאה'); setUploading(false); return }
      const data = await res.json()
      setReplyAttachments(prev => [...prev, { key: data.key, name: data.name, url: data.url, size: data.size }])
    } catch { alert('שגיאה בהעלאת הקובץ') }
    finally { setUploading(false); e.target.value = '' }
  }

  // Avatar colors by user
  const AVATAR_COLORS = ['#34d399', '#38bdf8', '#a78bfa', '#f472b6', '#fb923c', '#facc15', '#4ade80', '#f87171', '#22d3ee', '#e879f9']
  const getUserColor = (name: string) => {
    let hash = 0
    for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
    return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length]
  }
  const getInitial = (name: string) => (name || '?')[0].toUpperCase()

  const toggleUserExpand = (userId: string) => {
    setExpandedUsers(prev => {
      const next = new Set(prev)
      next.has(userId) ? next.delete(userId) : next.add(userId)
      return next
    })
  }

  // Group threads by user
  const threadsByUser = threads.reduce((acc: Record<string, any[]>, t: any) => {
    const uid = t.user_id || t.user_email || 'unknown'
    if (!acc[uid]) acc[uid] = []
    acc[uid].push(t)
    return acc
  }, {} as Record<string, any[]>)

  const formatDateTime = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleString('he-IL', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  const sendCompose = async () => {
    if (!token || !composeSubject.trim() || !composeBody.trim() || composeRecipients.length === 0) return
    setComposeSending(true)
    try {
      const res = await fetch(`${API}/admin/messages/compose`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: composeSubject.trim(),
          body: composeBody.trim(),
          recipient_ids: composeRecipients,
          attachments: composeAttachments,
        }),
      })
      const data = await res.json()
      setComposeResult(`ההודעה נשלחה ל-${data.sent_to} משתמשים`)
      setComposeSubject('')
      setComposeBody('')
      setComposeRecipients([])
      setComposeAttachments([])
      setTimeout(() => { setComposeResult(''); setShowCompose(false) }, 2000)
      refetch()
    } catch (err) { console.error(err) }
    finally { setComposeSending(false) }
  }

  const toggleRecipient = (userId: string) => {
    if (userId === 'all') {
      setComposeRecipients(prev => prev.includes('all') ? [] : ['all'])
      return
    }
    setComposeRecipients(prev => {
      const filtered = prev.filter(id => id !== 'all')
      return filtered.includes(userId) ? filtered.filter(id => id !== userId) : [...filtered, userId]
    })
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !token) return
    if (file.size > 10 * 1024 * 1024) { alert('קובץ גדול מדי — מקסימום 10MB'); return }
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch(`${API}/messages/upload-attachment`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      })
      if (!res.ok) { const err = await res.json(); alert(err.message || 'שגיאה בהעלאת הקובץ'); setUploading(false); return }
      const data = await res.json()
      setComposeAttachments(prev => [...prev, { key: data.key, name: data.name, url: data.url, size: data.size }])
    } catch { alert('שגיאה בהעלאת הקובץ') }
    finally { setUploading(false); e.target.value = '' }
  }

  const activeUsers = users.filter(u => u.is_active)
  const filteredUsers = users.filter(u => u.name?.includes(searchUser) || u.email?.includes(searchUser))
  const filteredRecipients = activeUsers.filter(u =>
    !recipientSearch || u.name?.toLowerCase().includes(recipientSearch.toLowerCase()) || u.email?.toLowerCase().includes(recipientSearch.toLowerCase())
  )

  // ── Login screen ────────────────────────────────────────────────────────────
  if (!token) {
    return (
      <>
        <Script src="https://accounts.google.com/gsi/client" strategy="afterInteractive" data-google-gsi="1" />
        <main style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(180deg, #0b1020, #060a15)', padding: 24 }}>
          <div style={{ width: '100%', maxWidth: 400, background: 'rgba(18,26,51,0.85)', border: '1px solid var(--border)', borderRadius: 24, padding: 48 }}>
            <div style={{ textAlign: 'center', marginBottom: 32 }}>
              <img src="/favicon.png" alt="" width={64} height={64} style={{ borderRadius: 16, marginBottom: 16 }} />
              <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e0f2fe' }}>כניסה למערכת</h1>
            </div>
            {loginError && (
              <div role="alert" style={{ padding: '12px 16px', borderRadius: 12, border: '1px solid rgba(239,68,68,0.4)', background: 'rgba(239,68,68,0.1)', color: '#fca5a5', fontSize: 14, textAlign: 'center', marginBottom: 20 }}>
                {loginError}
              </div>
            )}
            <button onClick={handleGoogleLogin} disabled={loginLoading} style={{ width: '100%', padding: '15px 20px', fontSize: 16, fontWeight: 700, textAlign: 'center', background: '#1a73e8', color: '#fff', border: 'none', borderRadius: 12, cursor: loginLoading ? 'not-allowed' : 'pointer', opacity: loginLoading ? 0.7 : 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, transition: 'box-shadow 0.2s, background 0.2s' }}
              onMouseEnter={e => { e.currentTarget.style.background = '#1557b0'; e.currentTarget.style.boxShadow = '0 2px 12px rgba(26,115,232,0.4)' }}
              onMouseLeave={e => { e.currentTarget.style.background = '#1a73e8'; e.currentTarget.style.boxShadow = 'none' }}
            >
              {!loginLoading && (
                <svg width="20" height="20" viewBox="0 0 48 48" style={{ background: '#fff', borderRadius: 4, padding: 2 }}>
                  <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
                  <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
                  <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
                  <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
                </svg>
              )}
              {loginLoading ? '⏳ מתחבר...' : 'התחבר באמצעות Google'}
            </button>
          </div>
        </main>
      </>
    )
  }

  // ── Dashboard ───────────────────────────────────────────────────────────────
  const unreadCount = threads.reduce((sum: number, t: any) => sum + (t.unread_count || 0), 0)

  return (
    <main style={{ background: 'var(--bg)', minHeight: '100vh', padding: '24px 20px' }}>
      <div style={{ maxWidth: 1400, margin: '0 auto' }}>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28, flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h1 style={{ fontSize: 26, fontWeight: 700, color: '#e0f2fe' }}>⚙️ לוח בקרה</h1>
            <p style={{ color: 'var(--muted)', fontSize: 14 }}>Doctor Scribe AI</p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={refetch} className="btn btn-secondary" style={{ padding: '10px 20px' }}>🔄 רענן</button>
            <button onClick={() => setToken(null)} className="btn btn-secondary" style={{ padding: '10px 20px' }}>יציאה</button>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
          {([
            { key: 'stats', label: '📊 סטטיסטיקות' },
            { key: 'users', label: `👥 משתמשים (${users.length})` },
            { key: 'messages', label: `✉️ הודעות${unreadCount > 0 ? ` (${unreadCount})` : ''}` },
            { key: 'errors', label: `🚨 שגיאות (${errors.length})` },
            { key: 'content', label: '📰 תוכן' },
            { key: 'analytics', label: '📊 אנליטיקס' },
            { key: 'devtools', label: '🛠️ Dev Tools' },
          ] as { key: Tab; label: string }[]).map(t => (
            <button key={t.key} onClick={() => setTab(t.key)}
              className={`btn ${tab === t.key ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '10px 20px', fontWeight: tab === t.key ? 700 : 400 }}>
              {t.label}
            </button>
          ))}
        </div>

        {loading && <div style={{ textAlign: 'center', color: 'var(--muted)', padding: 40 }}>טוען...</div>}

        {/* ══ STATS ══ */}
        {!loading && tab === 'stats' && stats && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
            {[
              { label: 'משתמשים פעילים', value: stats.users?.active, icon: '👤', color: '#34d399' },
              { label: 'משתמשים חסומים', value: stats.users?.blocked, icon: '🚫', color: '#f87171' },
              { label: 'מטופלים', value: stats.patients, icon: '🏥', color: '#38bdf8' },
              { label: 'ביקורים', value: stats.visits, icon: '🩺', color: '#a78bfa' },
              { label: 'הקלטות', value: stats.recordings, icon: '🎤', color: '#fb923c' },
              { label: 'תמלולים', value: stats.transcriptions, icon: '📝', color: '#facc15' },
              { label: 'סיכומים', value: stats.summaries, icon: '🧠', color: '#4ade80' },
              { label: 'הודעות חדשות', value: stats.messages_unread, icon: '✉️', color: '#f472b6' },
              { label: 'שגיאות', value: stats.errors_total, icon: '🚨', color: '#ef4444' },
            ].map(s => (
              <div key={s.label} className="card" style={{ padding: '20px 24px', display: 'flex', alignItems: 'center', gap: 16 }}>
                <span style={{ fontSize: 36 }}>{s.icon}</span>
                <div>
                  <div style={{ fontSize: 32, fontWeight: 800, color: s.color }}>{s.value ?? '—'}</div>
                  <div style={{ fontSize: 13, color: 'var(--muted)' }}>{s.label}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ══ USERS ══ */}
        {!loading && tab === 'users' && (
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
              <input type="search" placeholder="חיפוש לפי שם / אימייל..." value={searchUser} onChange={e => setSearchUser(e.target.value)} className="search-input" style={{ width: '100%', padding: '10px 14px', fontSize: 14 }} />
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
                <thead>
                  <tr style={{ background: 'rgba(56,189,248,0.05)', borderBottom: '1px solid var(--border)' }}>
                    {['שם', 'אימייל', 'תפקיד', 'סטטוס', 'נרשם', 'פעולות'].map(h => (
                      <th key={h} style={{ padding: '12px 16px', textAlign: 'right', fontWeight: 600, color: 'var(--muted)', whiteSpace: 'nowrap' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.map(u => (
                    <tr key={u.id} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '12px 16px', fontWeight: 600 }}>{u.name}</td>
                      <td style={{ padding: '12px 16px', color: 'var(--muted)' }}>{u.email}</td>
                      <td style={{ padding: '12px 16px' }}>
                        <span style={{ padding: '3px 10px', borderRadius: 20, background: u.role === 'admin' ? 'rgba(167,139,250,0.15)' : 'rgba(56,189,248,0.1)', color: u.role === 'admin' ? '#a78bfa' : '#38bdf8', fontSize: 12 }}>{u.role}</span>
                      </td>
                      <td style={{ padding: '12px 16px' }}>
                        <span style={{ padding: '3px 10px', borderRadius: 20, background: u.is_active ? 'rgba(52,211,153,0.1)' : 'rgba(239,68,68,0.1)', color: u.is_active ? '#34d399' : '#f87171', fontSize: 12 }}>{u.is_active ? 'פעיל' : 'חסום'}</span>
                      </td>
                      <td style={{ padding: '12px 16px', color: 'var(--muted)', whiteSpace: 'nowrap' }}>{u.created_at ? new Date(u.created_at).toLocaleDateString('he-IL') : '—'}</td>
                      <td style={{ padding: '12px 16px' }}>
                        <div style={{ display: 'flex', gap: 8 }}>
                          <button onClick={() => toggleBlock(u.id, u.is_active)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: 12 }}>{u.is_active ? '🚫 חסום' : '✅ שחרר'}</button>
                          <button onClick={() => impersonate(u.id)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: 12 }}>👁 צפה</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ══ MESSAGES — Outlook-style ══ */}
        {!loading && tab === 'messages' && (
          <div style={{ display: 'flex', gap: 0, height: 'calc(100vh - 200px)', minHeight: 500, border: '1px solid var(--border)', borderRadius: 16, overflow: 'hidden' }}>

            {/* Right panel — thread list grouped by user */}
            <div style={{ width: 380, borderLeft: '1px solid var(--border)', background: 'var(--card)', display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
              {/* Toolbar */}
              <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', display: 'flex', gap: 8 }}>
                <button onClick={() => { setShowCompose(true); setSelectedThread(null); setComposeRecipients([]); setComposeSubject(''); setComposeBody(''); setComposeAttachments([]) }} className="btn btn-primary" style={{ padding: '8px 16px', fontSize: 13, fontWeight: 700, flex: 1 }}>
                  ✏️ הודעה חדשה
                </button>
              </div>

              {/* Thread list grouped by user with collapse */}
              <div style={{ flex: 1, overflowY: 'auto' }}>
                {Object.keys(threadsByUser).length === 0 && <div style={{ textAlign: 'center', color: 'var(--muted)', padding: 40, fontSize: 14 }}>אין הודעות</div>}
                {Object.entries(threadsByUser).map(([uid, userThreads]: [string, any[]]) => {
                  const firstThread = userThreads[0]
                  const userName = firstThread.user_name || firstThread.user_email || '?'
                  const userEmail = firstThread.user_email || ''
                  const isExpanded = expandedUsers.has(uid)
                  const totalUnread = userThreads.reduce((s: number, t: any) => s + (t.unread_count || 0), 0)
                  const color = getUserColor(userName)

                  return (
                    <div key={uid}>
                      {/* User header row */}
                      <div
                        onClick={() => toggleUserExpand(uid)}
                        style={{ padding: '10px 14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10, borderBottom: '1px solid var(--border)', background: 'rgba(255,255,255,0.02)', transition: 'background 0.15s' }}
                        onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.05)' }}
                        onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.02)' }}
                      >
                        {/* Expand/collapse +/- */}
                        <span style={{ width: 20, height: 20, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 4, background: 'rgba(255,255,255,0.06)', color: 'var(--muted)', fontSize: 14, fontWeight: 700, flexShrink: 0 }}>
                          {isExpanded ? '−' : '+'}
                        </span>
                        {/* Avatar circle */}
                        <span style={{ width: 36, height: 36, borderRadius: '50%', background: color, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 16, fontWeight: 700, flexShrink: 0, border: `2px solid ${color}44` }}>
                          {getInitial(userName)}
                        </span>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontWeight: 600, fontSize: 14, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{userName}</div>
                          <div style={{ fontSize: 11, color: 'var(--muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{userEmail}</div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
                          {totalUnread > 0 && (
                            <span style={{ minWidth: 20, height: 20, borderRadius: 10, background: '#ef4444', color: '#fff', fontSize: 11, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 6px' }}>
                              {totalUnread}
                            </span>
                          )}
                          <span style={{ fontSize: 11, color: 'var(--muted)' }}>{userThreads.length}</span>
                        </div>
                      </div>

                      {/* Expanded threads for this user */}
                      {isExpanded && userThreads.map((t: any) => (
                        <div
                          key={t.thread_id}
                          onClick={() => { openThread(t); setShowCompose(false) }}
                          style={{
                            padding: '10px 14px 10px 52px',
                            borderBottom: '1px solid rgba(255,255,255,0.03)',
                            cursor: 'pointer',
                            background: selectedThread?.thread_id === t.thread_id ? 'rgba(56,189,248,0.08)' : 'transparent',
                            transition: 'background 0.15s',
                          }}
                          onMouseEnter={e => { if (selectedThread?.thread_id !== t.thread_id) e.currentTarget.style.background = 'rgba(255,255,255,0.03)' }}
                          onMouseLeave={e => { if (selectedThread?.thread_id !== t.thread_id) e.currentTarget.style.background = 'transparent' }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
                            {t.unread_count > 0 && <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#38bdf8', flexShrink: 0 }} />}
                            <span style={{ fontWeight: t.unread_count > 0 ? 700 : 400, fontSize: 13, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {t.subject}
                            </span>
                            <span style={{ fontSize: 10, color: 'var(--muted)', flexShrink: 0 }}>{formatDateTime(t.last_activity)}</span>
                          </div>
                          <div style={{ fontSize: 12, color: 'var(--muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {t.last_message?.body?.substring(0, 60)}
                          </div>
                          <div style={{ display: 'flex', gap: 6, marginTop: 3, alignItems: 'center' }}>
                            <span style={{ padding: '1px 6px', borderRadius: 10, background: 'rgba(167,139,250,0.12)', color: '#a78bfa', fontSize: 10 }}>{t.category}</span>
                            {t.message_count > 1 && <span style={{ fontSize: 10, color: 'var(--muted)' }}>{t.message_count} הודעות</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Left panel — conversation or compose */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'var(--bg)' }}>

              {/* Compose new message */}
              {showCompose && (
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 24, overflowY: 'auto' }}>
                  <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16, color: '#e0f2fe' }}>✏️ הודעה חדשה</h3>

                  {/* Recipient picker */}
                  <div style={{ marginBottom: 14 }}>
                    <label style={{ fontSize: 13, color: 'var(--muted)', marginBottom: 6, display: 'block' }}>אל:</label>
                    {/* Selected recipients chips */}
                    {composeRecipients.length > 0 && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
                        {composeRecipients.includes('all') ? (
                          <span style={{ padding: '4px 12px', borderRadius: 20, background: 'rgba(56,189,248,0.15)', color: '#38bdf8', fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                            כל המשתמשים
                            <button onClick={() => setComposeRecipients([])} style={{ background: 'none', border: 'none', color: '#38bdf8', cursor: 'pointer', padding: 0, fontSize: 14 }}>✕</button>
                          </span>
                        ) : (
                          composeRecipients.map(id => {
                            const u = users.find((u: any) => u.id === id)
                            return u ? (
                              <span key={id} style={{ padding: '4px 12px', borderRadius: 20, background: 'rgba(56,189,248,0.15)', color: '#38bdf8', fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                                {u.name || u.email}
                                <button onClick={() => toggleRecipient(id)} style={{ background: 'none', border: 'none', color: '#38bdf8', cursor: 'pointer', padding: 0, fontSize: 14 }}>✕</button>
                              </span>
                            ) : null
                          })
                        )}
                      </div>
                    )}
                    {/* Recipient search and scrollable list */}
                    <input type="search" placeholder="חפש משתמש..." value={recipientSearch} onChange={e => setRecipientSearch(e.target.value)} className="search-input" style={{ width: '100%', padding: '7px 12px', fontSize: 13, marginBottom: 6 }} />
                    <div style={{ maxHeight: 140, overflowY: 'auto', border: '1px solid var(--border)', borderRadius: 10, background: 'var(--card)' }}>
                      <div onClick={() => toggleRecipient('all')} style={{ padding: '7px 14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10, borderBottom: '1px solid var(--border)', background: composeRecipients.includes('all') ? 'rgba(56,189,248,0.08)' : 'transparent' }}>
                        <input type="checkbox" checked={composeRecipients.includes('all')} readOnly style={{ accentColor: '#38bdf8' }} />
                        <span style={{ fontWeight: 700, fontSize: 13, color: '#38bdf8' }}>כל המשתמשים ({activeUsers.length})</span>
                      </div>
                      {filteredRecipients.map((u: any) => (
                        <div key={u.id} onClick={() => toggleRecipient(u.id)} style={{ padding: '6px 14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10, borderBottom: '1px solid rgba(255,255,255,0.03)', background: composeRecipients.includes(u.id) ? 'rgba(56,189,248,0.06)' : 'transparent' }}>
                          <input type="checkbox" checked={composeRecipients.includes(u.id) || composeRecipients.includes('all')} readOnly style={{ accentColor: '#38bdf8' }} />
                          <span style={{ width: 28, height: 28, borderRadius: '50%', background: getUserColor(u.name), display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 13, fontWeight: 700, flexShrink: 0 }}>{getInitial(u.name)}</span>
                          <span style={{ fontSize: 13 }}>{u.name}</span>
                          <span style={{ fontSize: 11, color: 'var(--muted)' }}>{u.email}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <input type="text" placeholder="נושא..." value={composeSubject} onChange={e => setComposeSubject(e.target.value)} className="search-input" style={{ width: '100%', padding: '7px 14px', fontSize: 14, marginBottom: 12 }} />

                  <textarea placeholder="תוכן ההודעה..." value={composeBody} onChange={e => setComposeBody(e.target.value)} rows={5} className="search-input" style={{ width: '100%', padding: '10px 14px', fontSize: 14, resize: 'vertical', flex: 1, marginBottom: 12 }} />

                  {/* Attachments */}
                  {composeAttachments.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 10 }}>
                      {composeAttachments.map((a: any, i: number) => (
                        <span key={i} style={{ padding: '4px 10px', borderRadius: 8, background: 'rgba(56,189,248,0.1)', border: '1px solid rgba(56,189,248,0.2)', color: '#38bdf8', fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                          📎 {a.name}
                          <button onClick={() => setComposeAttachments(prev => prev.filter((_, j) => j !== i))} style={{ background: 'none', border: 'none', color: '#38bdf8', cursor: 'pointer', padding: 0, fontSize: 14 }}>✕</button>
                        </span>
                      ))}
                    </div>
                  )}

                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <label style={{ cursor: uploading ? 'not-allowed' : 'pointer', padding: '8px 14px', fontSize: 13, borderRadius: 10, border: '1px solid var(--border)', color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: 6, opacity: uploading ? 0.5 : 1 }}>
                      {uploading ? '⏳ מעלה...' : '📎 צרף קובץ'}
                      <input type="file" onChange={handleFileUpload} style={{ display: 'none' }} accept=".jpg,.jpeg,.png,.gif,.webp,.pdf,.doc,.docx,.xls,.xlsx,.csv,.txt,.rtf" disabled={uploading} />
                    </label>
                    <button onClick={sendCompose} disabled={composeSending || !composeSubject.trim() || !composeBody.trim() || composeRecipients.length === 0} className="btn btn-primary" style={{ padding: '8px 28px', fontSize: 14, fontWeight: 700, opacity: composeSending ? 0.6 : 1 }}>
                      {composeSending ? '⏳ שולח...' : '📤 שלח'}
                    </button>
                    <button onClick={() => { setShowCompose(false); setComposeAttachments([]) }} className="btn btn-secondary" style={{ padding: '8px 20px', fontSize: 14 }}>ביטול</button>
                    {composeResult && <span style={{ color: '#34d399', fontSize: 13 }}>{composeResult}</span>}
                  </div>
                </div>
              )}

              {/* Thread conversation view */}
              {!showCompose && selectedThread && (
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                  {/* Thread header with avatar */}
                  <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--border)', background: 'var(--card)', display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ width: 40, height: 40, borderRadius: '50%', background: getUserColor(selectedThread.user_name), display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 18, fontWeight: 700, flexShrink: 0 }}>
                      {getInitial(selectedThread.user_name)}
                    </span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 2 }}>{selectedThread.subject}</div>
                      <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                        {selectedThread.user_name} · {selectedThread.user_email} · {selectedThread.message_count} הודעות
                      </div>
                    </div>
                  </div>

                  {/* Messages */}
                  <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px' }}>
                    {threadLoading && <div style={{ textAlign: 'center', color: 'var(--muted)', padding: 40 }}>טוען...</div>}
                    {!threadLoading && threadMessages.map((m: any) => (
                      <div key={m.id} style={{ marginBottom: 12, display: 'flex', justifyContent: m.direction === 'outbound' ? 'flex-start' : 'flex-end' }}>
                        <div style={{
                          maxWidth: '75%', padding: '12px 16px', borderRadius: 16,
                          background: m.direction === 'outbound'
                            ? 'linear-gradient(135deg, rgba(56,189,248,0.12), rgba(56,189,248,0.06))'
                            : 'rgba(255,255,255,0.05)',
                          border: `1px solid ${m.direction === 'outbound' ? 'rgba(56,189,248,0.2)' : 'rgba(255,255,255,0.08)'}`,
                        }}>
                          <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                            <span style={{ fontWeight: 600, color: m.direction === 'outbound' ? '#38bdf8' : '#a78bfa' }}>
                              {m.direction === 'outbound' ? '📤 צוות תמיכה' : `📥 ${m.user_name}`}
                            </span>
                            · {formatDateTime(m.created_at)}
                          </div>
                          <div style={{ fontSize: 14, lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>{m.body}</div>
                          {m.attachments?.length > 0 && (
                            <div style={{ marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                              {m.attachments.map((a: any, i: number) => (
                                <a key={i} href={a.url} target="_blank" rel="noreferrer" style={{ padding: '4px 10px', borderRadius: 8, background: 'rgba(255,255,255,0.06)', color: '#38bdf8', fontSize: 12, textDecoration: 'none' }}>
                                  📎 {a.name}
                                </a>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Reply box with attachment support */}
                  <div style={{ padding: '12px 20px', borderTop: '1px solid var(--border)', background: 'var(--card)' }}>
                    {replyAttachments.length > 0 && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
                        {replyAttachments.map((a: any, i: number) => (
                          <span key={i} style={{ padding: '3px 8px', borderRadius: 8, background: 'rgba(56,189,248,0.1)', border: '1px solid rgba(56,189,248,0.2)', color: '#38bdf8', fontSize: 11, display: 'flex', alignItems: 'center', gap: 4 }}>
                            📎 {a.name}
                            <button onClick={() => setReplyAttachments(prev => prev.filter((_, j) => j !== i))} style={{ background: 'none', border: 'none', color: '#38bdf8', cursor: 'pointer', padding: 0, fontSize: 12 }}>✕</button>
                          </span>
                        ))}
                      </div>
                    )}
                    <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
                      <label style={{ cursor: 'pointer', padding: '8px', borderRadius: 8, color: 'var(--muted)', display: 'flex', alignItems: 'center', flexShrink: 0 }}>
                        📎
                        <input type="file" onChange={handleReplyFileUpload} style={{ display: 'none' }} accept=".jpg,.jpeg,.png,.gif,.webp,.pdf,.doc,.docx,.xls,.xlsx,.csv,.txt,.rtf" />
                      </label>
                      <textarea
                        placeholder="כתוב תגובה..."
                        value={replyBody}
                        onChange={e => setReplyBody(e.target.value)}
                        rows={2}
                        className="search-input"
                        style={{ flex: 1, padding: '8px 14px', fontSize: 14, resize: 'none' }}
                        onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendReply() } }}
                      />
                      <button onClick={sendReply} disabled={replySending || !replyBody.trim()} className="btn btn-primary" style={{ padding: '8px 20px', fontSize: 14, fontWeight: 700 }}>
                        {replySending ? '⏳' : '📤 שלח'}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Empty state */}
              {!showCompose && !selectedThread && (
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: 'var(--muted)' }}>
                  <span style={{ fontSize: 48, marginBottom: 16 }}>✉️</span>
                  <p style={{ fontSize: 16 }}>בחר שיחה או צור הודעה חדשה</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ══ ERRORS ══ */}
        {!loading && tab === 'errors' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {errors.length === 0 && <div style={{ textAlign: 'center', color: 'var(--muted)', padding: 40 }}>אין שגיאות 🎉</div>}
            {errors.map((e: any) => (
              <div key={e.id} className="card" style={{ padding: '16px 20px', borderColor: 'rgba(239,68,68,0.3)', background: 'rgba(239,68,68,0.03)' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8, marginBottom: 4 }}>
                  <span style={{ fontWeight: 700, color: '#f87171', fontSize: 13 }}>🚨 {e.action}</span>
                  {e.error_id && <span style={{ fontSize: 11, color: 'var(--muted)' }}>#{e.error_id}</span>}
                </div>
                <p style={{ fontSize: 13, color: 'var(--text)', marginBottom: 4 }}>{e.error_message || e.description}</p>
                <div style={{ fontSize: 11, color: 'var(--muted)' }}>
                  👤 {e.user_name} · {e.entity_type}/{e.entity_id} · {new Date(e.created_at).toLocaleString('he-IL')}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ══ CONTENT ══ */}
        {!loading && tab === 'content' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Stats strip */}
            {articleStats && (
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                {[
                  { label: 'מפורסמים', value: articleStats.published, color: '#34d399' },
                  { label: 'טיוטות', value: articleStats.drafts, color: '#facc15' },
                  { label: 'בבדיקה', value: articleStats.review, color: '#38bdf8' },
                  { label: 'צפיות', value: articleStats.total_views, color: '#e879f9' },
                  { label: 'לייקים', value: articleStats.total_likes, color: '#f472b6' },
                ].map(s => (
                  <div key={s.label} className="card" style={{ padding: '12px 18px', display: 'flex', alignItems: 'center', gap: 10, flex: '1 1 120px' }}>
                    <span style={{ fontSize: 24, fontWeight: 800, color: s.color }}>{s.value ?? 0}</span>
                    <span style={{ fontSize: 12, color: 'var(--muted)' }}>{s.label}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Generate new article */}
            <div className="card" style={{ padding: '20px 24px' }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 14, color: '#e0f2fe' }}>✨ יצירת מאמר חדש עם AI</h3>
              <div style={{ display: 'flex', gap: 10, marginBottom: 12, flexWrap: 'wrap' }}>
                <input type="text" placeholder="נושא המאמר (עברית)..." value={genTopic} onChange={e => setGenTopic(e.target.value)} className="search-input" style={{ flex: 2, padding: '10px 14px', fontSize: 14, minWidth: 200 }} />
                <select value={genConfig.tone} onChange={e => setGenConfig({...genConfig, tone: e.target.value})} className="search-input" style={{ padding: '8px 12px', fontSize: 13 }}>
                  <option value="professional">מקצועי</option>
                  <option value="accessible">נגיש</option>
                  <option value="clinical">קליני</option>
                </select>
                <select value={genConfig.audience} onChange={e => setGenConfig({...genConfig, audience: e.target.value})} className="search-input" style={{ padding: '8px 12px', fontSize: 13 }}>
                  <option value="general">קהל רחב</option>
                  <option value="patients">מטופלים</option>
                  <option value="professionals">מקצוענים</option>
                </select>
                <select value={genConfig.length} onChange={e => setGenConfig({...genConfig, length: e.target.value})} className="search-input" style={{ padding: '8px 12px', fontSize: 13 }}>
                  <option value="short">קצר</option>
                  <option value="medium">בינוני</option>
                  <option value="long">ארוך</option>
                </select>
                <select value={genConfig.persona} onChange={e => setGenConfig({...genConfig, persona: e.target.value})} className="search-input" style={{ padding: '8px 12px', fontSize: 13 }}>
                  <option value="general">צוות Medical Hub</option>
                  <option value="doctor">ד"ר דניאל כהן</option>
                  <option value="nutritionist">דנה לוי - תזונאית</option>
                  <option value="physiotherapist">ד"ר מיכל ברק - פיזיו</option>
                  <option value="psychologist">ד"ר אורן שפירא - פסיכולוג</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                <button onClick={generateArticle} disabled={generating || !genTopic.trim()} className="btn btn-primary" style={{ padding: '10px 24px', fontSize: 14, fontWeight: 700, opacity: generating ? 0.6 : 1 }}>
                  {generating ? '⏳ מייצר מאמר...' : '✨ ייצר מאמר'}
                </button>
                {genResult && (
                  <div style={{ marginTop: 12 }}>
                    {genResult.ok ? (
                      <div style={{ background: 'rgba(52,211,153,0.08)', border: '1px solid rgba(52,211,153,0.25)', borderRadius: 10, padding: '12px 16px', fontSize: 13 }}>
                        <div style={{ fontWeight: 700, color: '#34d399', marginBottom: 6 }}>✓ {genResult.title}</div>
                        {/* Mistral key expired alert */}
                        {genResult.mistral_expired && (
                          <div style={{ background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, padding: '8px 12px', marginBottom: 8, color: '#f87171', fontWeight: 700 }}>
                            🔑 MISTRAL_API_KEY פג תוקף — יש לעדכן ב-.env
                          </div>
                        )}
                        {/* Quality score */}
                        {genResult.quality_score != null && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6, flexWrap: 'wrap' }}>
                            <span style={{ fontWeight: 700, color: genResult.quality_score >= 90 ? '#34d399' : genResult.quality_score >= 70 ? '#facc15' : '#f87171', fontSize: 15 }}>
                              ציון Mistral: {genResult.quality_score}/100
                            </span>
                            {genResult.auto_published
                              ? <span style={{ background: 'rgba(52,211,153,0.15)', color: '#34d399', padding: '2px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700 }}>✅ פורסם אוטומטית</span>
                              : <span style={{ background: 'rgba(250,204,21,0.15)', color: '#facc15', padding: '2px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700 }}>⏳ שמור כטיוטה (מתחת לסף {90})</span>
                            }
                            {genResult.retry_attempted && (
                              <span style={{ background: 'rgba(56,189,248,0.1)', color: '#38bdf8', padding: '2px 10px', borderRadius: 20, fontSize: 11 }}>
                                🔄 תוקן ע&quot;י GPT → ציון חדש: {genResult.retry_score ?? '—'}/100
                              </span>
                            )}
                          </div>
                        )}
                        {/* Issues from Mistral */}
                        {genResult.issues?.length > 0 && genResult.quality_score < 90 && (
                          <div style={{ background: 'rgba(239,68,68,0.07)', borderRadius: 8, padding: '8px 12px' }}>
                            <div style={{ fontWeight: 700, color: '#f87171', marginBottom: 4, fontSize: 12 }}>⚠️ בעיות שנמצאו ע&quot;י Mistral:</div>
                            {genResult.issues.map((iss: string, i: number) => (
                              <div key={i} style={{ color: 'rgba(255,255,255,0.7)', fontSize: 12, paddingRight: 8 }}>• {iss}</div>
                            ))}
                          </div>
                        )}
                      </div>
                    ) : (
                      <div style={{ color: '#f87171', fontSize: 13, background: 'rgba(239,68,68,0.08)', padding: '8px 12px', borderRadius: 8 }}>
                        ✕ {genResult.error}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Recent jobs */}
            {articleJobs.length > 0 && (
              <div className="card" style={{ padding: '16px 20px' }}>
                <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10, color: 'var(--muted)' }}>משימות יצירה אחרונות</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {articleJobs.slice(0, 5).map((j: any) => (
                    <div key={j.id} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13 }}>
                      <span style={{ padding: '2px 8px', borderRadius: 10, fontSize: 11, background: j.status === 'done' ? 'rgba(52,211,153,0.1)' : j.status === 'error' ? 'rgba(239,68,68,0.1)' : 'rgba(56,189,248,0.1)', color: j.status === 'done' ? '#34d399' : j.status === 'error' ? '#f87171' : '#38bdf8' }}>
                        {j.status}
                      </span>
                      <span style={{ flex: 1 }}>{j.topic}</span>
                      {j.error_message && <span style={{ color: '#f87171', fontSize: 11 }}>{j.error_message.substring(0, 50)}</span>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Articles table */}
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--border)', fontWeight: 700, fontSize: 15 }}>
                📰 מאמרים ({articles.length})
              </div>
              {articles.length === 0 ? (
                <div style={{ textAlign: 'center', color: 'var(--muted)', padding: 40 }}>אין מאמרים עדיין — ייצר את הראשון!</div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                    <thead>
                      <tr style={{ background: 'rgba(56,189,248,0.05)', borderBottom: '1px solid var(--border)' }}>
                        {['כותרת', 'קטגוריה', 'סטטוס', 'ציון', 'בדיקת עובדות', 'צפיות', 'תאריך', 'פעולות'].map(h => (
                          <th key={h} style={{ padding: '10px 14px', textAlign: 'right', fontWeight: 600, color: 'var(--muted)', whiteSpace: 'nowrap' }}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {articles.map((a: any) => {
                        const statusColors: Record<string, { bg: string; color: string }> = {
                          draft: { bg: 'rgba(250,204,21,0.1)', color: '#facc15' },
                          review: { bg: 'rgba(56,189,248,0.1)', color: '#38bdf8' },
                          published: { bg: 'rgba(52,211,153,0.1)', color: '#34d399' },
                          archived: { bg: 'rgba(107,107,127,0.1)', color: '#6b6b7f' },
                        }
                        const statusLabels: Record<string, string> = { draft: 'טיוטה', review: 'בבדיקה', published: 'מפורסם', archived: 'בארכיון' }
                        const fcColors: Record<string, string> = { unchecked: '#6b6b7f', flagged: '#f87171', verified: '#34d399' }
                        const fcLabels: Record<string, string> = { unchecked: '⬜', flagged: '🚩', verified: '✅' }
                        const sc = statusColors[a.status] || statusColors.draft

                        return (
                          <tr key={a.id} style={{ borderBottom: '1px solid var(--border)' }}>
                            <td style={{ padding: '10px 14px', fontWeight: 600, maxWidth: 250, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.title}</td>
                            <td style={{ padding: '10px 14px', color: 'var(--muted)' }}>{a.category}</td>
                            <td style={{ padding: '10px 14px' }}>
                              <span style={{ padding: '2px 10px', borderRadius: 20, background: sc.bg, color: sc.color, fontSize: 11 }}>{statusLabels[a.status] || a.status}</span>
                            </td>
                            <td style={{ padding: '10px 14px', textAlign: 'center' }}>
                              {a.quality_score != null ? (
                                <span
                                  title={a.quality_notes || ''}
                                  style={{
                                    fontWeight: 700, fontSize: 12, cursor: a.quality_notes ? 'help' : 'default',
                                    color: a.quality_score >= 90 ? '#34d399' : a.quality_score >= 70 ? '#facc15' : '#f87171',
                                  }}
                                >
                                  {a.quality_score}
                                  {a.quality_notes?.includes('פג תוקף') && ' 🔑'}
                                  {a.quality_notes?.includes('תוקן') && ' 🔄'}
                                </span>
                              ) : <span style={{ color: 'var(--muted)', fontSize: 11 }}>—</span>}
                            </td>
                            <td style={{ padding: '10px 14px', textAlign: 'center' }}>{fcLabels[a.fact_check_status] || '⬜'}</td>
                            <td style={{ padding: '10px 14px', color: 'var(--muted)' }}>{a.views}</td>
                            <td style={{ padding: '10px 14px', color: 'var(--muted)', whiteSpace: 'nowrap' }}>{a.created_at?.substring(0, 10)}</td>
                            <td style={{ padding: '10px 14px' }}>
                              <div style={{ display: 'flex', gap: 6 }}>
                                {a.status === 'draft' && <button onClick={() => changeArticleStatus(a.id, 'published')} className="btn btn-primary" style={{ padding: '4px 10px', fontSize: 11 }}>פרסם</button>}
                                {a.status === 'published' && <button onClick={() => changeArticleStatus(a.id, 'draft')} className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11 }}>הסתר</button>}
                                {a.slug && <a href={`/articles/${a.slug}?preview=1`} target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11, textDecoration: 'none' }}>👁</a>}
                                <button onClick={() => deleteArticle(a.id)} className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11, color: '#f87171' }}>🗑</button>
                              </div>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* ── Glossary Management ── */}
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--border)', fontWeight: 700, fontSize: 15 }}>
                📖 מילון מושגים ({glossaryTerms.length})
              </div>
              <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 12 }}>
                {/* Add new term */}
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'flex-start' }}>
                  <input
                    type="text"
                    placeholder="מושג (עברית)..."
                    value={newTerm}
                    onChange={e => setNewTerm(e.target.value)}
                    className="search-input"
                    style={{ padding: '8px 12px', fontSize: 13, flex: '1 1 140px', minWidth: 100 }}
                  />
                  <input
                    type="text"
                    placeholder="הגדרה..."
                    value={newDefinition}
                    onChange={e => setNewDefinition(e.target.value)}
                    className="search-input"
                    style={{ padding: '8px 12px', fontSize: 13, flex: '3 1 240px', minWidth: 180 }}
                    onKeyDown={e => { if (e.key === 'Enter') addGlossaryTerm() }}
                  />
                  <button
                    onClick={addGlossaryTerm}
                    disabled={glossarySaving || !newTerm.trim() || !newDefinition.trim()}
                    className="btn btn-primary"
                    style={{ padding: '8px 18px', fontSize: 13, opacity: glossarySaving ? 0.6 : 1, whiteSpace: 'nowrap' }}
                  >
                    {glossarySaving ? '...' : '+ הוסף'}
                  </button>
                </div>
                {/* Terms list */}
                {glossaryTerms.length === 0 ? (
                  <div style={{ color: 'var(--muted)', fontSize: 13, textAlign: 'center', padding: '12px 0' }}>אין מושגים עדיין</div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 320, overflowY: 'auto' }}>
                    {glossaryTerms.map((t: any) => (
                      <div key={t.id} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', padding: '8px 12px', borderRadius: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)' }}>
                        <span style={{ fontWeight: 700, fontSize: 13, color: '#38bdf8', whiteSpace: 'nowrap', minWidth: 80 }}>{t.term}</span>
                        <span style={{ fontSize: 12, color: 'var(--muted)', flex: 1, lineHeight: 1.5 }}>{t.definition}</span>
                        <button onClick={() => deleteGlossaryTerm(t.id)} style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer', fontSize: 14, padding: '0 4px', flexShrink: 0 }}>🗑</button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ══ ANALYTICS ══ */}
        {tab === 'analytics' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

            {/* Period selector + refresh */}
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
              {[1, 6, 24, 72, 168, 720].map(h => (
                <button key={h} onClick={() => { setAnalyticsHours(h); fetchAnalytics(h) }}
                  className={`btn ${analyticsHours === h ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ padding: '6px 14px', fontSize: 12 }}>
                  {h === 1 ? 'שעה אחרונה' : h === 6 ? '6 שעות' : h === 24 ? '24 שעות' : h === 72 ? '3 ימים' : h === 168 ? 'שבוע' : '30 יום'}
                </button>
              ))}
              <button onClick={() => fetchAnalytics(analyticsHours)} className="btn btn-secondary" style={{ padding: '6px 14px', fontSize: 12 }}>🔄 רענן</button>
            </div>

            {analyticsLoading && <div style={{ textAlign: 'center', color: 'var(--muted)', padding: 40 }}>טוען נתוני אנליטיקס...</div>}

            {!analyticsLoading && analyticsData && (
              <>
                {/* Summary cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
                  {[
                    { label: 'מבקרים עכשיו', value: analyticsData.summary.active_now, icon: '🟢', color: '#34d399' },
                    { label: 'סשנים ייחודיים', value: analyticsData.summary.unique_sessions, icon: '👤', color: '#38bdf8' },
                    { label: 'צפיות בדפים', value: analyticsData.summary.total_pageviews, icon: '📄', color: '#a78bfa' },
                    { label: 'זמן ממוצע בדף', value: analyticsData.summary.avg_duration_seconds ? `${Math.floor(analyticsData.summary.avg_duration_seconds / 60)}:${String(analyticsData.summary.avg_duration_seconds % 60).padStart(2,'0')} דק׳` : 'אין נתון', icon: '⏱', color: '#fb923c' },
                  ].map(s => (
                    <div key={s.label} className="card" style={{ padding: '16px 20px', textAlign: 'center' }}>
                      <div style={{ fontSize: 24, marginBottom: 6 }}>{s.icon}</div>
                      <div style={{ fontSize: 22, fontWeight: 800, color: s.color }}>{s.value ?? '—'}</div>
                      <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>{s.label}</div>
                    </div>
                  ))}
                </div>

                {/* Active sessions now */}
                {analyticsData.active_sessions?.length > 0 && (
                  <div className="card" style={{ padding: 20 }}>
                    <div style={{ fontWeight: 700, marginBottom: 12, fontSize: 14 }}>🟢 מבקרים פעילים (30 דקות אחרונות)</div>
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                        <thead>
                          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
                            {['סשן', 'עמוד נוכחי', 'מכשיר', 'דפים שנצפו', 'פעיל לפני'].map(h => (
                              <th key={h} style={{ textAlign: 'right', padding: '6px 12px', color: 'var(--muted)', fontWeight: 600 }}>{h}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {analyticsData.active_sessions.map((s: any, i: number) => {
                            const ago = Math.round((Date.now() - new Date(s.last_seen).getTime()) / 60000)
                            return (
                              <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                                <td style={{ padding: '8px 12px', fontFamily: 'monospace', color: '#34d399' }}>#{s.session}</td>
                                <td style={{ padding: '8px 12px', color: 'var(--text)' }}>{s.page}</td>
                                <td style={{ padding: '8px 12px', color: 'var(--muted)' }}>{s.device || 'לא ידוע'}</td>
                                <td style={{ padding: '8px 12px', color: 'var(--muted)', textAlign: 'center' }}>{s.pages}</td>
                                <td style={{ padding: '8px 12px', color: ago < 5 ? '#34d399' : 'var(--muted)' }}>{ago === 0 ? 'עכשיו' : `לפני ${ago} דק׳`}</td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Two column: top pages + searches */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>

                  {/* Top pages */}
                  <div className="card" style={{ padding: 20 }}>
                    <div style={{ fontWeight: 700, marginBottom: 12, fontSize: 14 }}>📄 עמודים פופולריים</div>
                    {analyticsData.top_pages.length === 0
                      ? <div style={{ color: 'var(--muted)', fontSize: 13 }}>אין נתונים עדיין</div>
                      : analyticsData.top_pages.map((p: any, i: number) => {
                          const maxV = analyticsData.top_pages[0].views
                          return (
                            <div key={i} style={{ marginBottom: 8 }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 3 }}>
                                <span style={{ color: 'var(--text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '75%' }}>{p.path}</span>
                                <span style={{ color: '#a78bfa', fontWeight: 700 }}>{p.views}</span>
                              </div>
                              <div style={{ height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.06)' }}>
                                <div style={{ height: '100%', borderRadius: 2, background: '#a78bfa', width: `${(p.views / maxV) * 100}%` }} />
                              </div>
                            </div>
                          )
                        })
                    }
                  </div>

                  {/* Top searches */}
                  <div className="card" style={{ padding: 20 }}>
                    <div style={{ fontWeight: 700, marginBottom: 12, fontSize: 14 }}>🔍 חיפושים נפוצים</div>
                    {analyticsData.top_searches.length === 0
                      ? <div style={{ color: 'var(--muted)', fontSize: 13 }}>אין חיפושים עדיין</div>
                      : analyticsData.top_searches.map((s: any, i: number) => {
                          const maxC = analyticsData.top_searches[0].count
                          return (
                            <div key={i} style={{ marginBottom: 8 }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 3 }}>
                                <span style={{ color: 'var(--text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '75%' }}>{s.query}</span>
                                <span style={{ color: '#38bdf8', fontWeight: 700 }}>{s.count}x</span>
                              </div>
                              <div style={{ height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.06)' }}>
                                <div style={{ height: '100%', borderRadius: 2, background: '#38bdf8', width: `${(s.count / maxC) * 100}%` }} />
                              </div>
                            </div>
                          )
                        })
                    }
                  </div>
                </div>

                {/* Two column: referrers + devices */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div className="card" style={{ padding: 20 }}>
                    <div style={{ fontWeight: 700, marginBottom: 12, fontSize: 14 }}>🔗 מקורות תנועה</div>
                    {analyticsData.top_referrers.length === 0
                      ? <div style={{ color: 'var(--muted)', fontSize: 13 }}>תנועה ישירה בלבד</div>
                      : analyticsData.top_referrers.map((r: any, i: number) => (
                          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: 12 }}>
                            <span style={{ color: 'var(--text)', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '78%' }}>{r.referrer}</span>
                            <span style={{ color: '#fb923c', fontWeight: 700 }}>{r.count}</span>
                          </div>
                        ))
                    }
                  </div>

                  <div className="card" style={{ padding: 20 }}>
                    <div style={{ fontWeight: 700, marginBottom: 12, fontSize: 14 }}>📱 מכשירים</div>
                    {analyticsData.devices.length === 0
                      ? <div style={{ color: 'var(--muted)', fontSize: 13 }}>אין נתונים עדיין</div>
                      : analyticsData.devices.map((d: any, i: number) => {
                          const icon = d.type === 'mobile' ? '📱' : d.type === 'tablet' ? '📟' : '🖥'
                          const label = d.type === 'mobile' ? 'נייד' : d.type === 'tablet' ? 'טאבלט' : 'מחשב'
                          return (
                            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: 12 }}>
                              <span style={{ color: 'var(--text)' }}>{icon} {label}</span>
                              <span style={{ color: '#34d399', fontWeight: 700 }}>{d.count}</span>
                            </div>
                          )
                        })
                    }
                  </div>
                </div>

                {/* Recent searches */}
                {analyticsData.recent_searches?.length > 0 && (
                  <div className="card" style={{ padding: 20 }}>
                    <div style={{ fontWeight: 700, marginBottom: 12, fontSize: 14 }}>🕐 חיפושים אחרונים</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 300, overflowY: 'auto' }}>
                      {analyticsData.recent_searches.map((s: any, i: number) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '5px 8px', background: 'rgba(255,255,255,0.02)', borderRadius: 6, fontSize: 12 }}>
                          <span style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                            <span style={{ color: '#38bdf8' }}>🔍</span>
                            <span style={{ color: 'var(--text)' }}>{s.query}</span>
                            {s.clicked && <span style={{ color: '#34d399', fontSize: 11 }}>→ {s.clicked}</span>}
                          </span>
                          <span style={{ color: 'var(--muted)', fontSize: 11 }}>
                            {s.results} תוצאות · {new Date(s.time).toLocaleTimeString('he-IL')}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Hourly traffic chart (ASCII bars) */}
                {analyticsData.hourly_traffic?.length > 0 && (
                  <div className="card" style={{ padding: 20 }}>
                    <div style={{ fontWeight: 700, marginBottom: 12, fontSize: 14 }}>📈 תנועה שעתית (24 שעות)</div>
                    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 3, height: 80, overflowX: 'auto' }}>
                      {(() => {
                        const maxV = Math.max(...analyticsData.hourly_traffic.map((h: any) => h.views), 1)
                        return analyticsData.hourly_traffic.map((h: any, i: number) => {
                          const height = Math.max(4, (h.views / maxV) * 72)
                          const hour = new Date(h.hour).getHours()
                          return (
                            <div key={i} title={`${hour}:00 — ${h.views} צפיות`} style={{ flex: '1 0 auto', minWidth: 18 }}>
                              <div style={{ height, background: 'linear-gradient(to top, #a78bfa, #38bdf8)', borderRadius: '3px 3px 0 0', opacity: 0.85 }} />
                              <div style={{ fontSize: 9, color: 'var(--muted)', textAlign: 'center', marginTop: 2 }}>{hour}</div>
                            </div>
                          )
                        })
                      })()}
                    </div>
                  </div>
                )}
              </>
            )}

            {!analyticsLoading && !analyticsData && (
              <div style={{ textAlign: 'center', color: 'var(--muted)', padding: 60 }}>
                אין נתוני אנליטיקס עדיין. המידע יצטבר כשמבקרים ייכנסו לאתר.
              </div>
            )}
          </div>
        )}

        {/* ══ DEV TOOLS ══ */}
        {tab === 'devtools' && (
          <div className="card" style={{ padding: 24 }}>
            <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>🛠️ Dev Tools — שליטה בקונטיינר</h2>
            <p style={{ color: 'var(--muted)', fontSize: 13, marginBottom: 20 }}>
              שירות פנימי לצילום מסך ויצירת HTML שטוח של דפי האפליקציה.
              רץ על פורט 8090.
            </p>

            <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 16, flexWrap: 'wrap' }}>
              <button onClick={fetchDevTools} disabled={devToolsBusy}
                className="btn btn-secondary" style={{ padding: '8px 16px' }}>
                בדוק חיבור
              </button>
            </div>

            {devToolsError && (
              <div style={{ padding: 12, marginBottom: 16, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.4)', borderRadius: 8, color: '#fca5a5', fontSize: 13 }}>
                ❌ {devToolsError}
              </div>
            )}

            {devToolsState && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 24 }}>
                <div style={{ padding: 16, background: 'rgba(255,255,255,0.03)', borderRadius: 8 }}>
                  <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>מצב</div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: devToolsState.running ? '#34d399' : '#9ca3af' }}>
                    {devToolsState.running ? '● פועל' : '○ מושבת'}
                  </div>
                </div>
                <div style={{ padding: 16, background: 'rgba(255,255,255,0.03)', borderRadius: 8 }}>
                  <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>סטטוס</div>
                  <div style={{ fontSize: 14, fontWeight: 600 }}>{devToolsState.status || '—'}</div>
                </div>
                <div style={{ padding: 16, background: 'rgba(255,255,255,0.03)', borderRadius: 8 }}>
                  <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>פורט</div>
                  <div style={{ fontSize: 14, fontWeight: 600 }}>{devToolsState.host_port || 8090}</div>
                </div>
                {devToolsState.id && (
                  <div style={{ padding: 16, background: 'rgba(255,255,255,0.03)', borderRadius: 8 }}>
                    <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>Container ID</div>
                    <div style={{ fontSize: 13, fontFamily: 'monospace' }}>{devToolsState.id}</div>
                  </div>
                )}
              </div>
            )}

            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <button
                onClick={() => devToolsAction('start')}
                disabled={devToolsBusy || devToolsState?.running}
                className="btn"
                style={{
                  padding: '12px 24px',
                  background: devToolsState?.running ? 'rgba(255,255,255,0.05)' : '#10b981',
                  color: devToolsState?.running ? 'var(--muted)' : 'white',
                  border: 'none',
                  borderRadius: 8,
                  fontWeight: 700,
                  cursor: (devToolsBusy || devToolsState?.running) ? 'not-allowed' : 'pointer',
                  opacity: (devToolsBusy || devToolsState?.running) ? 0.5 : 1,
                }}
              >
                ▶ {devToolsState?.exists ? 'הפעל' : 'צור והפעל'}
              </button>
              <button
                onClick={() => devToolsAction('stop')}
                disabled={devToolsBusy || !devToolsState?.running}
                className="btn"
                style={{
                  padding: '12px 24px',
                  background: !devToolsState?.running ? 'rgba(255,255,255,0.05)' : '#ef4444',
                  color: !devToolsState?.running ? 'var(--muted)' : 'white',
                  border: 'none',
                  borderRadius: 8,
                  fontWeight: 700,
                  cursor: (devToolsBusy || !devToolsState?.running) ? 'not-allowed' : 'pointer',
                  opacity: (devToolsBusy || !devToolsState?.running) ? 0.5 : 1,
                }}
              >
                ■ כבה
              </button>
              <button
                onClick={fetchDevTools}
                disabled={devToolsBusy}
                className="btn btn-secondary"
                style={{ padding: '12px 24px' }}
              >
                🔄 רענן
              </button>
            </div>

            {devToolsBusy && (
              <div style={{ marginTop: 16, color: 'var(--muted)', fontSize: 13 }}>טוען...</div>
            )}

            <div style={{ marginTop: 32, padding: 20, background: 'rgba(56,189,248,0.06)', border: '1px solid rgba(56,189,248,0.25)', borderRadius: 10 }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>📸 צילום דף / שטוח HTML</h3>
              <p style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 16 }}>
                הזיני URL מלא של הדף שתרצי לצלם (Frontend, Parent-website, או כל אתר חיצוני). הקונטיינר ייפתח Chromium, יטען את הדף, ויחזיר PNG או קובץ HTML עצמאי.
              </p>

              <div style={{ display: 'grid', gap: 12 }}>
                <label style={{ display: 'block' }}>
                  <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>URL מלא של הדף</div>
                  <input
                    type="text"
                    value={captureUrl}
                    onChange={e => setCaptureUrl(e.target.value)}
                    placeholder="http://localhost/he או https://drsscribe.com/he"
                    style={{ width: '100%', padding: '10px 12px', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 6, color: '#eaeaea', fontSize: 14, fontFamily: 'monospace' }}
                  />
                  <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>
                    💡 דוגמאות: <code>http://localhost/he</code> (Flutter) · <code>http://parent-website:3000/cpanel</code> (Next.js פנימי) · <code>https://drsscribe.com/he/dashboard</code> (חיצוני)
                  </div>
                </label>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10 }}>
                  <label>
                    <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>Preset מכשיר</div>
                    <select
                      onChange={e => {
                        const v = e.target.value
                        if (v === 'mobile') { setCaptureViewportW(390); setCaptureViewportH(844) }
                        else if (v === 'tablet') { setCaptureViewportW(820); setCaptureViewportH(1180) }
                        else if (v === 'laptop') { setCaptureViewportW(1366); setCaptureViewportH(768) }
                        else if (v === 'desktop') { setCaptureViewportW(1920); setCaptureViewportH(1080) }
                        else if (v === 'wide') { setCaptureViewportW(2560); setCaptureViewportH(1440) }
                      }}
                      defaultValue=""
                      style={{ width: '100%', padding: '8px 10px', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 6, color: '#eaeaea', fontSize: 13 }}
                    >
                      <option value="">בחר/י...</option>
                      <option value="mobile">📱 Mobile (390×844)</option>
                      <option value="tablet">📱 Tablet (820×1180)</option>
                      <option value="laptop">💻 Laptop (1366×768)</option>
                      <option value="desktop">🖥 Desktop (1920×1080)</option>
                      <option value="wide">🖥 Wide (2560×1440)</option>
                    </select>
                  </label>
                  <label>
                    <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>רוחב Viewport</div>
                    <input type="number" value={captureViewportW} onChange={e => setCaptureViewportW(Number(e.target.value))} style={{ width: '100%', padding: '8px 10px', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 6, color: '#eaeaea', fontSize: 13 }} />
                  </label>
                  <label>
                    <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>גובה Viewport (לא משפיע על דף מלא)</div>
                    <input type="number" value={captureViewportH} onChange={e => setCaptureViewportH(Number(e.target.value))} style={{ width: '100%', padding: '8px 10px', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 6, color: '#eaeaea', fontSize: 13 }} />
                  </label>
                  <label>
                    <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>המתן (ms) אחרי טעינה</div>
                    <input type="number" value={captureWaitMs} onChange={e => setCaptureWaitMs(Number(e.target.value))} style={{ width: '100%', padding: '8px 10px', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 6, color: '#eaeaea', fontSize: 13 }} />
                  </label>
                  <label>
                    <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>DEV_TOOLS_TOKEN</div>
                    <input type="text" value={devToolsToken} onChange={e => setDevToolsToken(e.target.value)} style={{ width: '100%', padding: '8px 10px', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 6, color: '#eaeaea', fontSize: 13, fontFamily: 'monospace' }} />
                  </label>
                </div>

                <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', fontSize: 13 }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                    <input type="checkbox" checked={captureFullPage} onChange={e => setCaptureFullPage(e.target.checked)} />
                    <span>צלם דף מלא (עם גלילה). ללא — רק viewport גלוי.</span>
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                    <input type="checkbox" checked={captureUseAuth} onChange={e => setCaptureUseAuth(e.target.checked)} />
                    <span>הזרק את ה-JWT שלי (לדפים מאובטחים)</span>
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span style={{ fontSize: 12, color: 'var(--muted)' }}>שפה:</span>
                    <select value={captureLocale} onChange={e => setCaptureLocale(e.target.value)} style={{ padding: '4px 8px', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 4, color: '#eaeaea', fontSize: 12 }}>
                      <option value="he-IL">🇮🇱 עברית</option>
                      <option value="en-US">🇺🇸 English</option>
                      <option value="de-DE">🇩🇪 Deutsch</option>
                      <option value="fr-FR">🇫🇷 Français</option>
                      <option value="es-ES">🇪🇸 Español</option>
                      <option value="pt-PT">🇵🇹 Português</option>
                      <option value="it-IT">🇮🇹 Italiano</option>
                      <option value="ko-KR">🇰🇷 한국어</option>
                    </select>
                  </label>
                </div>

                <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 4 }}>
                  <button
                    onClick={() => runCapture('screenshot')}
                    disabled={captureBusy || !devToolsState?.running || !captureUrl}
                    style={{ padding: '10px 22px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: 8, fontWeight: 700, cursor: (captureBusy || !devToolsState?.running) ? 'not-allowed' : 'pointer', opacity: (captureBusy || !devToolsState?.running) ? 0.5 : 1 }}
                  >
                    📸 צלם PNG
                  </button>
                  <button
                    onClick={() => runCapture('flatten')}
                    disabled={captureBusy || !devToolsState?.running || !captureUrl}
                    style={{ padding: '10px 22px', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: 8, fontWeight: 700, cursor: (captureBusy || !devToolsState?.running) ? 'not-allowed' : 'pointer', opacity: (captureBusy || !devToolsState?.running) ? 0.5 : 1 }}
                  >
                    📄 שטוח ל-HTML
                  </button>
                  {!devToolsState?.running && (
                    <span style={{ fontSize: 12, color: '#fbbf24', alignSelf: 'center' }}>⚠️ הפעילי קודם את הקונטיינר (כפתור ▶ למעלה)</span>
                  )}
                </div>

                {captureBusy && <div style={{ color: 'var(--muted)', fontSize: 13 }}>⏳ מצלם... (יכול לקחת 5-15 שניות)</div>}

                {captureError && (
                  <div style={{ padding: 12, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.4)', borderRadius: 8, color: '#fca5a5', fontSize: 13 }}>
                    ❌ {captureError}
                  </div>
                )}

                {captureResult && (
                  <div style={{ padding: 16, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 8 }}>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 12, flexWrap: 'wrap' }}>
                      <span style={{ color: '#34d399', fontWeight: 700 }}>✅ הצילום מוכן</span>
                      <a href={captureResult.url} download={captureResult.filename} style={{ padding: '6px 14px', background: '#10b981', color: 'white', borderRadius: 6, textDecoration: 'none', fontSize: 13, fontWeight: 600 }}>
                        ⬇ הורד {captureResult.filename}
                      </a>
                      <a href={captureResult.url} target="_blank" rel="noreferrer" style={{ padding: '6px 14px', background: 'rgba(255,255,255,0.1)', color: '#eaeaea', borderRadius: 6, textDecoration: 'none', fontSize: 13 }}>
                        🔗 פתח בטאב חדש
                      </a>
                    </div>
                    {captureResult.kind === 'png' ? (
                      <img src={captureResult.url} alt="capture" style={{ maxWidth: '100%', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 6 }} />
                    ) : (
                      <iframe src={captureResult.url} style={{ width: '100%', height: 600, border: '1px solid rgba(255,255,255,0.15)', borderRadius: 6, background: 'white' }} />
                    )}
                  </div>
                )}
              </div>
            </div>

            <details style={{ marginTop: 16 }}>
              <summary style={{ cursor: 'pointer', fontSize: 13, color: 'var(--muted)' }}>📖 שימוש מ-curl (מתקדם)</summary>
              <pre style={{ marginTop: 8, padding: 12, background: 'rgba(0,0,0,0.3)', borderRadius: 6, overflowX: 'auto', fontSize: 12, color: '#e5e7eb' }}>
{`curl -X POST http://localhost:8090/capture/screenshot \\
  -H "X-Dev-Token: ${devToolsToken}" \\
  -H "Content-Type: application/json" \\
  -d '{"url":"${captureUrl}","full_page":${captureFullPage}}' \\
  -o page.png

# מדריך מלא: docs/DEV_TOOLS_GUIDE.md`}
              </pre>
            </details>
          </div>
        )}

        {impersonateUrl && (
          <div style={{ marginTop: 24, padding: '16px 20px', background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.4)', borderRadius: 12 }}>
            <p style={{ fontWeight: 700, marginBottom: 8 }}>🔑 קישור כניסה כמשתמש (תקף 30 דקות):</p>
            <a href={impersonateUrl} target="_blank" rel="noreferrer" style={{ color: '#fbbf24', wordBreak: 'break-all', fontSize: 13 }}>{impersonateUrl}</a>
            <button onClick={() => setImpersonateUrl(null)} style={{ marginRight: 12, background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer' }}>✕</button>
          </div>
        )}

      </div>
    </main>
  )
}
