'use client'

import { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import '../article-theme.css'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>()
  const searchParams = useSearchParams()
  const [article, setArticle] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [related, setRelated] = useState<any[]>([])

  useEffect(() => {
    async function load() {
      try {
        const preview = searchParams.get('preview') ? '?preview=1' : ''
        const res = await fetch(`${API}/articles/${slug}${preview}`)
        const data = await res.json()
        setArticle(data)

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

  const handleLike = async () => {
    await fetch(`${API}/articles/${slug}/like`, { method: 'POST' })
    setArticle({ ...article, likes: (article.likes || 0) + 1 })
  }

  if (loading) return (
    <main style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center', direction: 'rtl' }}>
      <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: 16 }}>טוען מאמר...</div>
    </main>
  )

  if (error || !article) return (
    <main style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16, direction: 'rtl' }}>
      <h1 style={{ fontSize: 28, color: 'white' }}>המאמר לא נמצא</h1>
      <Link href="/articles" style={{ color: '#fcf9c6' }}>חזרה למאמרים</Link>
    </main>
  )

  const categoryLabels: Record<string, string> = {
    cardiology: 'קרדיולוגיה', neurology: 'נוירולוגיה', orthopedics: 'אורתופדיה',
    nutrition: 'תזונה', sleep: 'שינה', mental: 'בריאות הנפש', general: 'כללי',
    dermatology: 'דרמטולוגיה', gastroenterology: 'גסטרו', urology: 'אורולוגיה',
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
        {article.hero_image_url && <meta property="og:image" content={article.hero_image_url} />}
        <link rel="canonical" href={`https://drsscribe.com/articles/${slug}`} />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
        <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
      </head>

      <div className="article-block">

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
                <span>{article.read_time_minutes} דקות קריאה</span>
                <span>•</span>
                <span>{article.views} צפיות</span>
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

            <div
              className="article-body"
              dangerouslySetInnerHTML={{ __html: article.content_html || '' }}
            />

            {article.tags?.length > 0 && (
              <div className="tags-section">
                {article.tags.map((tag: string) => (
                  <span key={tag} className="tag-chip">#{tag}</span>
                ))}
              </div>
            )}

            <div className="like-section">
              <button className="like-btn" onClick={handleLike}>
                ❤️ אהבתי ({article.likes || 0})
              </button>
            </div>

            {related.length > 0 && (
              <div className="related-section">
                <div className="related-title">מאמרים נוספים שיעניינו אותך</div>
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
                <strong>הבהרה משפטית:</strong> מאמר זה נועד למטרות מידע כללי בלבד ואינו מהווה תחליף לייעוץ רפואי מקצועי.
                </div>
            </div>

          </div>

          <div className="main-footer">
            Doctor Scribe AI · Medical Hub · כל הזכויות שמורות
          </div>

    </>
  )
}
