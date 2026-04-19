'use client'

import { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import '../article-theme.css'
import { useLanguage } from '@/components/LanguageProvider'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

interface GlossaryEntry { id: string; term: string; definition: string; category: string | null }

function injectGlossaryTooltips(html: string, terms: GlossaryEntry[]): string {
  if (typeof window === 'undefined' || terms.length === 0) return html
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const sorted = [...terms].sort((a, b) => b.term.length - a.term.length)

  function walkNode(node: Node) {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = node.textContent || ''
      for (const { term, definition } of sorted) {
        const idx = text.indexOf(term)
        if (idx >= 0) {
          const span = doc.createElement('span')
          span.className = 'glossary-term'
          span.setAttribute('data-def', definition)
          span.textContent = term
          const before = doc.createTextNode(text.slice(0, idx))
          const after = doc.createTextNode(text.slice(idx + term.length))
          const parent = node.parentNode!
          parent.insertBefore(before, node)
          parent.insertBefore(span, node)
          parent.insertBefore(after, node)
          parent.removeChild(node)
          walkNode(after)
          return
        }
      }
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      const el = node as Element
      if (['SCRIPT', 'STYLE', 'CODE', 'PRE', 'A'].includes(el.tagName)) return
      if (el.classList.contains('glossary-term')) return
      Array.from(node.childNodes).forEach(walkNode)
    }
  }

  walkNode(doc.body)
  return doc.body.innerHTML
}

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>()
  const searchParams = useSearchParams()
  const { t, lang } = useLanguage()
  const [article, setArticle] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [related, setRelated] = useState<any[]>([])
  const [processedHtml, setProcessedHtml] = useState<string>('')
  const [glossary, setGlossary] = useState<GlossaryEntry[]>([])

  // Comments state
  const [comments, setComments] = useState<any[]>([])
  const [commentBody, setCommentBody] = useState('')
  const [commentLoading, setCommentLoading] = useState(false)
  const [commentError, setCommentError] = useState('')
  const [currentUser, setCurrentUser] = useState<any>(null)

  useEffect(() => {
    try {
      const raw = localStorage.getItem('user')
      const token = localStorage.getItem('access_token')
      if (raw && token) setCurrentUser(JSON.parse(raw))
    } catch {}
    const onAuth = () => {
      try {
        const raw = localStorage.getItem('user')
        const token = localStorage.getItem('access_token')
        if (raw && token) setCurrentUser(JSON.parse(raw))
        else setCurrentUser(null)
      } catch {}
    }
    window.addEventListener('auth-changed', onAuth)
    return () => window.removeEventListener('auth-changed', onAuth)
  }, [])

  useEffect(() => {
    async function load() {
      try {
        const preview = searchParams.get('preview') ? '?preview=1' : ''
        const [res, glossRes, commentsRes] = await Promise.all([
          fetch(`${API}/articles/${slug}${preview}`),
          fetch(`${API}/glossary`),
          fetch(`${API}/articles/${slug}/comments`),
        ])
        const data = await res.json()
        const glossData: GlossaryEntry[] = glossRes.ok ? await glossRes.json() : []
        const commentsData = commentsRes.ok ? await commentsRes.json() : []
        setArticle(data)
        setGlossary(glossData)
        setComments(commentsData)

        // Fetch related articles
        if (data.category) {
          const relRes = await fetch(`${API}/articles?category=${data.category}&per_page=4`)
          const relData = await relRes.json()
          setRelated((relData.items || []).filter((a: any) => a.slug !== slug).slice(0, 3))
        }
      } catch { setError(true) }
      finally { setLoading(false) }
    }
    load()
  }, [slug, searchParams])

  // Inject glossary tooltips into article HTML once both are loaded
  useEffect(() => {
    if (article?.content_html && glossary.length > 0) {
      setProcessedHtml(injectGlossaryTooltips(article.content_html, glossary))
    } else if (article?.content_html) {
      setProcessedHtml(article.content_html)
    }
  }, [article, glossary])

  const handleLike = async () => {
    await fetch(`${API}/articles/${slug}/like`, { method: 'POST' })
    setArticle({ ...article, likes: (article.likes || 0) + 1 })
  }

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!commentBody.trim()) return
    setCommentLoading(true)
    setCommentError('')
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(`${API}/articles/${slug}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ body: commentBody.trim() }),
      })
      if (!res.ok) throw new Error()
      const newComment = await res.json()
      setComments(prev => [...prev, newComment])
      setCommentBody('')
    } catch { setCommentError(t('comment_error')) } finally {
      setCommentLoading(false)
    }
  }

  if (loading) return (
    <main style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center', direction: 'rtl' }}>
      <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: 16 }}>{t('article_loading')}</div>
    </main>
  )

  if (error || !article) return (
    <main style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16, direction: 'rtl' }}>
      <h1 style={{ fontSize: 28, color: 'white' }}>{t('article_not_found')}</h1>
      <Link href="/articles" style={{ color: '#fcf9c6' }}>{t('article_back_to_list')}</Link>
    </main>
  )

  const categoryLabels: Record<string, string> = {
    cardiology: t('cat_cardiology'), neurology: t('cat_neurology'), orthopedics: t('cat_orthopedics'),
    nutrition: t('cat_nutrition'), sleep: t('cat_sleep'), mental: t('cat_mental'), general: t('cat_general'),
    dermatology: t('cat_dermatology'), gastroenterology: t('cat_gastroenterology'), urology: t('cat_urology'),
  }

  const categoryLabel = categoryLabels[article.category] || article.category

  return (
    <>
      <head>
        <title>{article.seo_title || article.title} | Medical Hub</title>
        <meta name="description" content={article.seo_description || article.summary || ''} />
        {article.seo_keywords?.length > 0 && <meta name="keywords" content={article.seo_keywords.join(', ')} />}
        <meta property="og:title" content={article.title} />
        <meta property="og:description" content={article.summary || ''} />
        <meta property="og:type" content="article" />
        <meta property="og:url" content={`https://medicalhub.co.il/articles/${slug}`} />
        {article.hero_image_url && <meta property="og:image" content={article.hero_image_url} />}
        <meta name="robots" content="index, follow" />
        <link rel="canonical" href={`https://medicalhub.co.il/articles/${slug}`} />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
        <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Article',
              headline: article.title,
              description: article.seo_description || article.summary || '',
              image: article.hero_image_url || undefined,
              author: { '@type': 'Person', name: article.author_name },
              datePublished: article.published_at || article.created_at,
              dateModified: article.updated_at || article.created_at,
              publisher: { '@type': 'Organization', name: 'Medical Hub' },
              mainEntityOfPage: `https://medicalhub.co.il/articles/${slug}`,
              wordCount: article.content_html ? Math.round(article.content_html.replace(/<[^>]+>/g, '').split(/\s+/).length) : undefined,
              articleSection: categoryLabel,
            }),
          }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'BreadcrumbList',
              itemListElement: [
                { '@type': 'ListItem', position: 1, name: 'ראשי', item: 'https://medicalhub.co.il' },
                { '@type': 'ListItem', position: 2, name: 'מאמרים', item: 'https://medicalhub.co.il/articles' },
                { '@type': 'ListItem', position: 3, name: categoryLabel, item: `https://medicalhub.co.il/articles?category=${article.category}` },
                { '@type': 'ListItem', position: 4, name: article.title, item: `https://medicalhub.co.il/articles/${slug}` },
              ],
            }),
          }}
        />
      </head>

      <div className="article-block">

            <nav className="breadcrumb-bar" aria-label="breadcrumb">
              <Link href="/">ראשי</Link>
              <span className="bc-sep">›</span>
              <Link href="/articles">מאמרים</Link>
              <span className="bc-sep">›</span>
              <Link href={`/articles?category=${article.category}`}>{categoryLabel}</Link>
              <span className="bc-sep">›</span>
              <span className="bc-current">{article.title.length > 55 ? article.title.slice(0, 55) + '…' : article.title}</span>
            </nav>

            <div className="page-header-bar">
              <Link href="/articles" className="back-btn"><i className="fas fa-arrow-right"></i></Link>
              <div>
                <div className="page-title">Medical Hub · מאמר רפואי</div>
                <div className="page-subtitle">{categoryLabel}</div>
              </div>
            </div>
            <div className="title-lines">
              <div className="title-line"></div>
              <div className="title-line"></div>
            </div>

            <div className="article-hero">
              <span className="hero-badge">{categoryLabel}</span>
              <h1 className="hero-title">{article.title}</h1>
              <p className="hero-subtitle">{article.subtitle || article.summary}</p>
              <div className="hero-meta">
                <span>{article.author_name}{article.author_title ? ` · ${article.author_title}` : ''}</span>
                <span>•</span>
                <span>{t('article_read_time', { n: article.read_time_minutes })}</span>
                <span>•</span>
                <span>{article.views} {t('article_views')}</span>
                {article.published_at && (
                  <>
                  <span>•</span>
                  <span>{new Date(article.published_at).toLocaleDateString('he-IL')}</span>
                  </>
                )}
              </div>
            </div>

            <div className="divider-section">
              <div className="arch arch-right"></div>
              <div className="dark-lines-wrapper"><div className="dark-line"></div><div className="dark-line"></div></div>
              <div className="arch arch-left"></div>
            </div>

            <div className="article-body">
              {article.hero_image_url && (
                <div className="article-accent-img">
                  <img
                    src={article.hero_image_url}
                    alt={article.hero_image_alt || article.title}
                  />
                </div>
              )}
              <div dangerouslySetInnerHTML={{ __html: processedHtml || article.content_html || '' }} />
            </div>

            {article.tags?.length > 0 && (
              <div className="tags-section">
                {article.tags.map((tag: string) => (
                  <Link key={tag} href={`/articles/tag/${encodeURIComponent(tag)}`} className="tag-chip">#{tag}</Link>
                ))}
              </div>
            )}

            <div className="like-section">
              <button className="like-btn" onClick={handleLike}>
                {t('article_like_btn', { n: article.likes || 0 })}
              </button>
            </div>

            {/* COMMENTS SECTION */}
            <div style={{ padding: '0 24px 32px', direction: 'rtl' }}>
              <h3 style={{ color: '#003399', fontSize: 20, fontWeight: 700, marginBottom: 20, borderBottom: '1px solid rgba(0,51,153,0.15)', paddingBottom: 12 }}>
                {t('comments_title', { n: comments.length })}
              </h3>

              {comments.length === 0 && (
                <p style={{ color: '#383ce4', fontSize: 14, marginBottom: 20 }}>{t('comments_first')}</p>
              )}

              {comments.map((c: any) => (
                <div key={c.id} style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
                  <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(255,255,255,0.1)', flexShrink: 0, overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {c.author_avatar
                      ? <img src={c.author_avatar} alt={c.author_name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                      : <span style={{ color: 'white', fontSize: 16 }}>👤</span>
                    }
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', marginBottom: 4 }}>
                      <span style={{ color: 'white', fontWeight: 600, fontSize: 14 }}>{c.author_name}</span>
                      <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: 12 }}>
                        {new Date(c.created_at).toLocaleDateString('he-IL', { day: 'numeric', month: 'short', year: 'numeric' })}
                      </span>
                    </div>
                    <p style={{ color: 'rgba(255,255,255,0.85)', fontSize: 15, lineHeight: 1.6, margin: 0, whiteSpace: 'pre-wrap' }}>{c.body}</p>
                  </div>
                </div>
              ))}

              {/* Comment form */}
              {currentUser ? (
                <form onSubmit={handleAddComment} style={{ marginTop: 24 }}>
                  <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                    <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(255,255,255,0.1)', flexShrink: 0, overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      {currentUser.avatar_url
                        ? <img src={currentUser.avatar_url} alt={currentUser.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        : <span style={{ color: 'white', fontSize: 16 }}>👤</span>
                      }
                    </div>
                    <div style={{ flex: 1 }}>
                      <textarea
                        value={commentBody}
                        onChange={e => setCommentBody(e.target.value)}
                        placeholder={t('comment_placeholder')}
                        rows={3}
                        maxLength={2000}
                        style={{ width: '100%', background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: 10, padding: '10px 14px', color: 'white', fontSize: 14, resize: 'vertical', fontFamily: 'inherit', boxSizing: 'border-box' }}
                      />
                      {commentError && <p style={{ color: '#ff6b6b', fontSize: 13, margin: '4px 0 0' }}>{commentError}</p>}
                      <button
                        type="submit"
                        disabled={commentLoading || !commentBody.trim()}
                        style={{ marginTop: 8, background: '#2563eb', color: 'white', border: 'none', borderRadius: 8, padding: '8px 20px', fontSize: 14, fontWeight: 600, cursor: commentLoading || !commentBody.trim() ? 'not-allowed' : 'pointer', opacity: commentLoading || !commentBody.trim() ? 0.6 : 1 }}
                      >
                        {commentLoading ? t('comment_submitting') : t('comment_submit')}
                      </button>
                    </div>
                  </div>
                </form>
              ) : (
                <div style={{ marginTop: 20, padding: '16px 20px', background: 'rgba(255,255,255,0.05)', borderRadius: 10, border: '1px solid rgba(255,255,255,0.1)', textAlign: 'center' }}>
                  <span style={{ color: 'rgba(255,255,255,0.7)', fontSize: 14 }}>
                    <Link href={`${process.env.NEXT_PUBLIC_MEDSCRIBE_URL || 'https://app.drsscribe.com'}/login`} style={{ color: '#93c5fd', fontWeight: 600 }}>{t('comment_login_prompt')}</Link>
                    {' '}{t('comment_login_link')}
                  </span>
                </div>
              )}
            </div>

            {related.length > 0 && (
              <div className="related-section">
                <div className="related-title">{t('article_related')}</div>
                <div className="related-grid">
                  {related.map((r: any) => (
                    <Link key={r.slug} href={`/articles/${r.slug}`} className="related-card">
                      <h4>{r.title}</h4>
                      <p>{r.summary ? (r.summary.length > 80 ? r.summary.slice(0, 80) + '...' : r.summary) : 'קרא עוד...'}</p>
                    </Link>
                  ))}
                </div>
              </div>
            )}

             <div style={{ padding: '0 24px 24px 24px' }}>
                <div className="legal-notice">
                  <div className="legal-notice-title">{t('legal_title')}</div>
                  <p>{t('legal_text1')}</p>
                  <p>{t('legal_text2')}</p>
                </div>
            </div>

          </div>

          <div className="main-footer">
            Doctor Scribe AI · Medical Hub · כל הזכויות שמורות
          </div>

    </>
  )
}
