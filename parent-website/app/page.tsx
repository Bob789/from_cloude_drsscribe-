'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { FEATURES } from '@/lib/featureFlags'
import ArticleCard from './articles/ArticleCard'
import { useLanguage } from '@/components/LanguageProvider'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'

export default function HomePage() {
  // Stars rising animation handled globally in StarsCanvas (layout.tsx)

  const router = useRouter()
  const { t } = useLanguage()
  const [width, setWidth] = useState(0)
  const [articles, setArticles] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [stats, setStats] = useState({ articles: 0, forum_posts: 0, experts: 0 })

  useEffect(() => {
    async function loadArticles() {
      try {
        const res = await fetch(`${API}/articles?per_page=5&sort=newest`)
        if (res.ok) {
          const data = await res.json()
          setArticles(data.items || [])
        }
      } catch {}
    }
    async function loadStats() {
      try {
        const res = await fetch(`${API}/site/stats`)
        if (res.ok) setStats(await res.json())
      } catch {}
    }
    loadArticles()
    loadStats()
  }, [])

  useEffect(() => {
    setWidth(window.innerWidth)
    const onResize = () => setWidth(window.innerWidth)
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  // Scroll reveal
  useEffect(() => {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target as HTMLElement
          el.style.opacity = '1'
          el.style.transform = 'translateY(0)'
          el.style.transition = 'opacity 0.5s, transform 0.5s'
          observer.unobserve(el)
        }
      })
    }, { threshold: 0.1 })

    const elements = document.querySelectorAll('.hp .article-card, .hp .side-card, .hp .scribe-widget, .hp .editorial-box')
    elements.forEach(el => {
      const htmlEl = el as HTMLElement
      htmlEl.style.opacity = '0'
      htmlEl.style.transform = 'translateY(24px)'
      observer.observe(el)
    })

    return () => observer.disconnect()
  }, [])

  return (
    <div className="hp">

            {/* HERO */}
            <div className="hero">

              <h1 className="hero-title">
                {t('hero_title')}
              </h1>
              <p className="hero-sub">{t('hero_subtitle')}</p>
              <div className="hero-search">
                <input
                  type="text"
                  placeholder={t('filter_search')}
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && searchQuery.trim().length >= 2) {
                      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`)
                    }
                  }}
                />
                <button
                  className="search-btn"
                  onClick={() => {
                    if (searchQuery.trim().length >= 2) {
                      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`)
                    }
                  }}
                ><i className="fas fa-search"></i> {t('filter_search')}</button>
              </div>
              <div className="hero-stats">
                <div className="stat-item">
                  <div className="stat-num">{stats.articles.toLocaleString()}</div>
                  <div className="stat-lbl">{t('stat_articles')}</div>
                </div>
                {FEATURES.forum && (
                <div className="stat-item">
                  <div className="stat-num">{stats.forum_posts.toLocaleString()}</div>
                  <div className="stat-lbl">{t('stat_forum')}</div>
                </div>
                )}
                {FEATURES.experts && (
                <div className="stat-item">
                  <div className="stat-num">{stats.experts}</div>
                  <div className="stat-lbl">{t('stat_experts')}</div>
                </div>
                )}
              </div>
            </div>

            <div className="title-lines">
              <div className="title-line"></div>
              <div className="title-line"></div>
            </div>

            {/* MAIN GRID */}
            <div className="main-grid">

              {/* ARTICLES COLUMN */}
              <div className="articles-col">
                <div className="section-label">
                  <div className="section-title">
                    <i className="fas fa-newspaper"></i> {t('section_latest')}
                  </div>
                  <span className="section-badge">Medical Hub</span>
                </div>

                {/* Dynamic Articles */}
                <div id="article-page-root">
                  {articles.map((article, index) => (
                    <ArticleCard
                      key={article.id}
                      article={article}
                      activeTag=""
                      onTagClick={(tag) => router.push(`/articles?tag=${encodeURIComponent(tag)}`)}
                      showDivider={index > 0}
                    />
                  ))}
                </div>

                {/* Editorial box */}
                <div className="editorial-box">
                  <span className="ed-tag">{t('editorial_tag')}</span>
                  <div className="ed-title">{t('editorial_title')}</div>
                  <div className="ed-text">{t('editorial_text')}</div>
                  <Link href="http://localhost:3001/login" className="ed-btn">{t('editorial_btn')}</Link>
                </div>
              </div>

              {/* SIDEBAR */}
              <aside className="sidebar">

                {/* Doctor Scribe AI */}
                {FEATURES.product && (
                <div className="scribe-widget">
                  <span className="sponsored-tag">SPONSORED</span>
                  <div className="scribe-title">🎤 Doctor Scribe AI</div>
                  <div className="scribe-desc">המערכת החכמה לתמלול וסיכום ביקורים רפואיים בעברית. חוסכים 50% מזמן התיעוד</div>
                  <ul className="scribe-features">
                    <li>תמלול מדויק בעברית רפואית</li>
                    <li>סיכום אוטומטי לתיק הרפואי</li>
                    <li>הפקת הפניות ומכתבי שחרור</li>
                    <li>אבטחת מידע בתקן מחמיר</li>
                  </ul>
                  <Link href="/product" className="scribe-btn">נסו חינם ל-14 יום</Link>
                  <div className="scribe-sub">אין צורך בכרטיס אשראי</div>
                </div>
                )}

                {/* Experts */}
                {FEATURES.experts && (
                <div className="side-card">
                  <div className="side-title">🩺 מומחים מובילים</div>
                  <div className="expert-list">
                    <div className="expert-row">
                      <div className="expert-avatar">D</div>
                      <div>
                        <div className="expert-name">ד&quot;ר דניאל כהן</div>
                        <div className="expert-spec">אורתופדיה • תל אביב</div>
                      </div>
                    </div>
                    <div className="expert-row">
                      <div className="expert-avatar">M</div>
                      <div>
                        <div className="expert-name">פרופ׳ מרים לוי</div>
                        <div className="expert-spec">נוירולוגיה • ירושלים</div>
                      </div>
                    </div>
                    <div className="expert-row">
                      <div className="expert-avatar">S</div>
                      <div>
                        <div className="expert-name">ד&quot;ר שרה אברמוביץ</div>
                        <div className="expert-spec">קרדיולוגיה • חיפה</div>
                      </div>
                    </div>
                    <div className="expert-row">
                      <div className="expert-avatar">Y</div>
                      <div>
                        <div className="expert-name">ד&quot;ר יוסי מזרחי</div>
                        <div className="expert-spec">אנדוקרינולוגיה • ת&quot;א</div>
                      </div>
                    </div>
                  </div>
                  <Link href="/experts" className="side-link">לכל המומחים →</Link>
                </div>
                )}

                {/* Forum hot topics */}
                {FEATURES.forum && (
                <div className="side-card">
                  <div className="side-title">💬 חם בפורום</div>
                  <div className="forum-list">
                    <div className="forum-row">
                      <div className="forum-q">כאב גב תחתון אחרי אימון</div>
                      <div className="forum-meta">
                        <span className="forum-replies">12 תגובות</span>
                        <span className="dr-badge">רופא השיב</span>
                      </div>
                    </div>
                    <div className="forum-row">
                      <div className="forum-q">האם צריך MRI לכאבי ראש?</div>
                      <div className="forum-meta">
                        <span className="forum-replies">7 תגובות</span>
                      </div>
                    </div>
                    <div className="forum-row">
                      <div className="forum-q">תופעות לוואי של מטפורמין</div>
                      <div className="forum-meta">
                        <span className="forum-replies">15 תגובות</span>
                        <span className="dr-badge">רופא השיב</span>
                      </div>
                    </div>
                    <div className="forum-row">
                      <div className="forum-q">נדודי שינה כרוניים - עזרה</div>
                      <div className="forum-meta">
                        <span className="forum-replies">31 תגובות</span>
                      </div>
                    </div>
                    <div className="forum-row">
                      <div className="forum-q">שיטות להפחתת לחץ דם</div>
                      <div className="forum-meta">
                        <span className="forum-replies">18 תגובות</span>
                        <span className="dr-badge">רופא השיב</span>
                      </div>
                    </div>
                  </div>
                  <Link href="/forum" className="side-link">לפורום המלא →</Link>
                </div>
                )}

              </aside>
            </div>

            {/* BOTTOM CTA */}
            {FEATURES.product && (
            <div className="bottom-cta">
              <div className="cta-eyebrow">DOCTOR SCRIBE AI</div>
              <h2 className="cta-title">אתם מטפלים,<br /><span>ה-AI כותב</span></h2>
              <p className="cta-sub">תמלול וסיכום אוטומטי של ביקורים רפואיים בעברית. לקליניקות פרטיות ורופאים עצמאיים</p>
              <div className="cta-btns">
                <Link href="/product" className="cta-primary">התחילו ניסיון חינם</Link>
                <Link href="/product" className="cta-ghost">דמו אונליין</Link>
              </div>
            </div>
            )}

      </div>
  )
}
