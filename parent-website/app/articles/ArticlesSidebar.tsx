import Link from 'next/link'
import { Category, Author, CATEGORY_META } from './constants'

interface Props {
  category:    Category
  catCounts:   Record<string, number>
  allTags:     string[]
  topAuthors:  Author[]
  activeTag:   string
  onCategory:  (c: Category) => void
  onTag:       (tag: string) => void
}

export default function ArticlesSidebar({
  category, catCounts, allTags, topAuthors, activeTag, onCategory, onTag,
}: Props) {
  return (
    <aside className="sidebar">

      {/* Categories */}
      <div className="side-card">
        <div className="side-card-title">📂 קטגוריות</div>
        <div className="cat-list">
          {Object.entries(CATEGORY_META).map(([id, meta]) => (
            <button
              key={id}
              onClick={() => onCategory(id as Category)}
              className={`cat-row${category === id ? ' active' : ''}`}
            >
              <span>{meta.label}</span>
              <span className="cat-count" style={{ color: meta.color, background: meta.bg }}>
                {catCounts[id] || 0}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Hot tags */}
      {allTags.length > 0 && (
        <div className="side-card">
          <div className="side-card-title">🔥 תגיות חמות</div>
          <div className="tags-wrap">
            {allTags.slice(0, 12).map(tag => (
              <button
                key={tag}
                onClick={() => onTag(tag)}
                className={`tag-chip${activeTag === tag ? ' active' : ''}`}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Top authors */}
      {topAuthors.length > 0 && (
        <div className="side-card">
          <div className="side-card-title">✍️ כותבים מובילים</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {topAuthors.map(a => (
              <div key={a.name} className="author-row">
                <div>
                  <div className="author-name">{a.name}</div>
                  {a.title && <div className="author-sub">{a.title}</div>}
                </div>
                <span className="author-count">{a.count} מאמרים</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* CTA */}
      <div className="cta-side">
        <div className="cta-title">🎤 Doctor Scribe AI</div>
        <div className="cta-text">תמלול וסיכום אוטומטי של ביקורים רפואיים לקליניקות פרטיות.</div>
        <Link href="/product" className="cta-btn">למד עוד →</Link>
      </div>

    </aside>
  )
}
