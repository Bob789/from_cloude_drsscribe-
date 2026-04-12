'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

async function getValidToken(): Promise<string | null> {
  const token = localStorage.getItem('access_token')
  if (!token) return null

  // Quick check: try /auth/me
  const res = await fetch(`${API}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (res.ok) return token

  // Token expired — try refresh
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) return null

  const refreshRes = await fetch(`${API}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh }),
  })
  if (!refreshRes.ok) return null

  const data = await refreshRes.json()
  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('refresh_token', data.refresh_token)
  localStorage.setItem('user', JSON.stringify(data.user))
  window.dispatchEvent(new Event('auth-changed'))
  return data.access_token
}

const AVATAR_OPTIONS = [
  '/avatars/avatar1.svg',
  '/avatars/avatar2.svg',
  '/avatars/avatar3.svg',
  '/avatars/avatar4.svg',
  '/avatars/avatar5.svg',
  '/avatars/avatar6.svg',
]

export default function ProfilePage() {
  const router = useRouter()
  const [nickname, setNickname] = useState('')
  const [avatarUrl, setAvatarUrl] = useState('')
  const [customUrl, setCustomUrl] = useState('')
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [user, setUser] = useState<any>(null)
  const [allUsers, setAllUsers] = useState<any[]>([])
  const [impersonating, setImpersonating] = useState(false)

  useEffect(() => {
    const init = async () => {
      const token = await getValidToken()
      if (!token) {
        router.push('/login')
        return
      }
      try {
        const raw = localStorage.getItem('user')
        if (raw) {
          const u = JSON.parse(raw)
          setUser(u)
          setNickname(u.nickname || '')
          setAvatarUrl(u.avatar_url || '')
        }
      } catch {}

      // Also fetch latest from API
      try {
        const res = await fetch(`${API}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.ok) {
          const data = await res.json()
          setUser(data)
          setNickname(data.nickname || '')
          setAvatarUrl(data.avatar_url || '')
          // If admin, load user list
          if (data.role === 'admin') {
            const usersRes = await fetch(`${API}/auth/users`, {
              headers: { Authorization: `Bearer ${token}` },
            })
            if (usersRes.ok) setAllUsers(await usersRes.json())
          }
        }
      } catch {}
    }
    init()
  }, [router])

  const handleSave = async () => {
    setSaving(true)
    setError('')
    setSuccess(false)
    const token = await getValidToken()
    if (!token) { router.push('/login'); return }

    try {
      const res = await fetch(`${API}/auth/me/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          nickname: nickname.trim() || null,
          avatar_url: avatarUrl.trim() || null,
        }),
      })
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || 'שגיאה בשמירה')
      }
      const updated = await res.json()
      // Update localStorage so Header and forum reflect changes immediately
      const stored = JSON.parse(localStorage.getItem('user') || '{}')
      stored.nickname = updated.nickname
      stored.avatar_url = updated.avatar_url
      localStorage.setItem('user', JSON.stringify(stored))
      window.dispatchEvent(new Event('auth-changed'))
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (e: any) {
      setError(e.message || 'שגיאה בשמירה')
    } finally {
      setSaving(false)
    }
  }

  if (!user) return null

  return (
    <div style={{ maxWidth: 520, margin: '40px auto', padding: '0 20px' }}>
      <h1 style={{ fontSize: 28, marginBottom: 8, color: '#1a2744' }}>פרופיל</h1>
      <p style={{ color: '#666', marginBottom: 32, fontSize: 14 }}>
        שנה את הכינוי והאווטאר שלך. הכינוי יופיע בפורום במקום השם האמיתי.
      </p>

      {/* Current info */}
      <div style={{ background: '#f5f7fb', borderRadius: 12, padding: 20, marginBottom: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
        {avatarUrl ? (
          <img src={avatarUrl} alt="" style={{ width: 56, height: 56, borderRadius: '50%', objectFit: 'cover', border: '2px solid #ddd' }} />
        ) : (
          <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'linear-gradient(135deg, #001f6b, #3366cc)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 900, fontSize: 20 }}>
            {(nickname || user.name || '?')[0]}
          </div>
        )}
        <div>
          <div style={{ fontWeight: 700, fontSize: 16 }}>{nickname || user.name}</div>
          <div style={{ color: '#999', fontSize: 13 }}>{user.email}</div>
        </div>
      </div>

      {/* Nickname */}
      <label style={{ display: 'block', marginBottom: 6, fontWeight: 600, fontSize: 14 }}>כינוי (Nickname)</label>
      <input
        type="text"
        value={nickname}
        onChange={e => setNickname(e.target.value)}
        placeholder={user.name || 'הכינוי שלך...'}
        maxLength={50}
        style={{
          width: '100%', padding: '10px 14px', borderRadius: 10,
          border: '1px solid #ddd', fontSize: 15, marginBottom: 20,
          fontFamily: 'inherit',
        }}
      />

      {/* Avatar selection */}
      <label style={{ display: 'block', marginBottom: 6, fontWeight: 600, fontSize: 14 }}>אווטאר</label>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
        {AVATAR_OPTIONS.map(url => (
          <button
            key={url}
            onClick={() => setAvatarUrl(url)}
            style={{
              width: 52, height: 52, borderRadius: '50%', border: avatarUrl === url ? '3px solid #3366cc' : '2px solid #ddd',
              padding: 0, cursor: 'pointer', background: '#f0f0f0', overflow: 'hidden',
              transition: 'border-color 0.2s',
            }}
          >
            <img src={url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </button>
        ))}
        {/* Clear avatar */}
        <button
          onClick={() => setAvatarUrl('')}
          style={{
            width: 52, height: 52, borderRadius: '50%', border: !avatarUrl ? '3px solid #3366cc' : '2px solid #ddd',
            padding: 0, cursor: 'pointer', background: 'linear-gradient(135deg, #001f6b, #3366cc)',
            color: 'white', fontWeight: 700, fontSize: 11, display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'border-color 0.2s',
          }}
        >
          ברירת מחדל
        </button>
      </div>

      {/* Custom URL */}
      <div style={{ marginBottom: 24 }}>
        <label style={{ fontSize: 12, color: '#999' }}>או הזן URL לתמונה מותאמת אישית:</label>
        <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
          <input
            type="url"
            value={customUrl}
            onChange={e => setCustomUrl(e.target.value)}
            placeholder="https://..."
            style={{
              flex: 1, padding: '8px 12px', borderRadius: 8,
              border: '1px solid #ddd', fontSize: 13, fontFamily: 'inherit',
            }}
          />
          <button
            onClick={() => { if (customUrl.trim()) setAvatarUrl(customUrl.trim()) }}
            style={{
              padding: '8px 14px', borderRadius: 8, background: '#3366cc', color: 'white',
              border: 'none', fontSize: 13, cursor: 'pointer', fontWeight: 600,
            }}
          >
            השתמש
          </button>
        </div>
      </div>

      {/* Save button */}
      <button
        onClick={handleSave}
        disabled={saving}
        style={{
          width: '100%', padding: '12px', borderRadius: 12,
          background: saving ? '#999' : 'linear-gradient(135deg, #001f6b, #3366cc)',
          color: 'white', border: 'none', fontSize: 16, fontWeight: 700,
          cursor: saving ? 'not-allowed' : 'pointer',
          transition: 'all 0.2s', fontFamily: 'inherit',
        }}
      >
        {saving ? 'שומר...' : 'שמור שינויים'}
      </button>

      {success && (
        <div style={{ marginTop: 12, color: '#22c55e', fontWeight: 600, textAlign: 'center' }}>
          ✓ הפרופיל עודכן בהצלחה!
        </div>
      )}
      {error && (
        <div style={{ marginTop: 12, color: '#ef4444', fontWeight: 600, textAlign: 'center' }}>
          {error}
        </div>
      )}

      {/* Admin: Impersonation */}
      {user?.role === 'admin' && allUsers.length > 0 && (
        <div style={{ marginTop: 48, borderTop: '2px solid #e5e7eb', paddingTop: 24 }}>
          <h2 style={{ fontSize: 20, color: '#1a2744', marginBottom: 4 }}>🔑 התחברות כמשתמש אחר</h2>
          <p style={{ color: '#888', fontSize: 13, marginBottom: 16 }}>אדמין בלבד — לחץ על משתמש כדי להתחבר בתור שלו.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {allUsers.filter(u => u.id !== user.id).map(u => (
              <button
                key={u.id}
                disabled={impersonating}
                onClick={async () => {
                  setImpersonating(true)
                  try {
                    const token = await getValidToken()
                    if (!token) { router.push('/login'); return }
                    const res = await fetch(`${API}/auth/impersonate/${u.id}`, {
                      method: 'POST',
                      headers: { Authorization: `Bearer ${token}` },
                    })
                    if (!res.ok) throw new Error('Failed')
                    const data = await res.json()
                    localStorage.setItem('access_token', data.access_token)
                    localStorage.setItem('refresh_token', data.refresh_token)
                    localStorage.setItem('user', JSON.stringify(data.user))
                    window.dispatchEvent(new Event('auth-changed'))
                    router.push('/forum')
                  } catch {
                    setError('שגיאה בהתחברות כמשתמש')
                  } finally {
                    setImpersonating(false)
                  }
                }}
                style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: '10px 16px', borderRadius: 10,
                  border: '1px solid #e5e7eb', background: '#fafbfc',
                  cursor: impersonating ? 'not-allowed' : 'pointer',
                  transition: 'all 0.15s', textAlign: 'right',
                  fontFamily: 'inherit',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = '#f0f4ff')}
                onMouseLeave={e => (e.currentTarget.style.background = '#fafbfc')}
              >
                {u.avatar_url ? (
                  <img src={u.avatar_url} alt="" style={{ width: 36, height: 36, borderRadius: '50%', objectFit: 'cover' }} />
                ) : (
                  <div style={{
                    width: 36, height: 36, borderRadius: '50%',
                    background: 'linear-gradient(135deg, #001f6b, #3366cc)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: 'white', fontWeight: 800, fontSize: 14,
                  }}>
                    {(u.nickname || u.name || '?')[0]}
                  </div>
                )}
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14, color: '#333' }}>{u.nickname || u.name}</div>
                  <div style={{ fontSize: 12, color: '#999' }}>{u.email}</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
