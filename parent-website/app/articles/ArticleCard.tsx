import Link from 'next/link'
import { CATEGORY_META, CATEGORY_ICONS } from './constants'

interface Props {
  article:     any
  activeTag:   string
  onTagClick:  (tag: string) => void
  showDivider: boolean
}

export default function ArticleCard({ article, activeTag, onTagClick, showDivider }: Props) {
  const cat         = CATEGORY_META[article.category] || CATEGORY_META.general
  const icon        = CATEGORY_ICONS[article.category] || '📄'
  const publishDate = article.published_at
    ? new Date(article.published_at).toLocaleDateString('he-IL')
    : ''

  return (
    <>
      {showDivider && (
        <div className="pipe" style={{ margin: '16px 0' }}>
          <div className="arch arch-right"></div>
          <div className="pipe-lines">
            <div className="pipe-line"></div>
            <div className="pipe-line"></div>
          </div>
          <div className="arch arch-left"></div>
        </div>
      )}

      <Link href={`/articles/${article.slug}`} className="article-card" data-testid="article-card">
        <div className="card-inner">
          <div className="card-thumb">
            {article.hero_image_url
              ? <img src={article.hero_image_url} alt={article.hero_image_alt || article.title} className="card-thumb-img" />
              : <span className="card-thumb-icon">{icon}</span>
            }
          </div>
          <div className="card-body">
            <div className="card-title">{article.title}</div>
            <div className="card-desc">{article.summary}</div>

            <div className="card-meta-row">
              <span
                className="cat-badge"
                style={{ color: cat.color, background: cat.bg, border: `1px solid ${cat.color}44` }}
              >
                {cat.label}
              </span>
              {(article.tags || []).slice(0, 2).map((tag: string) => (
                <button
                  key={tag}
                  onClick={e => { e.preventDefault(); onTagClick(tag) }}
                  className={`tag-chip${activeTag === tag ? ' active' : ''}`}
                >
                  {tag}
                </button>
              ))}
              <span className="card-author">
                {article.author_name} · {article.read_time_minutes} דק׳ · {publishDate}
              </span>
            </div>

            <div className="card-stats">
              <span className="stat">👁️ {(article.views || 0).toLocaleString()}</span>
              <span className="stat">❤️ {article.likes || 0}</span>
              <span className="read-btn">קרא עוד →</span>
            </div>
          </div>
        </div>
      </Link>
    </>
  )
}
