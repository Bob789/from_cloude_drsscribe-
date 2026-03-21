import { Category, Sort, TABS, SORT_LABELS } from './constants'

interface Props {
  search:       string
  category:     Category
  sort:         Sort
  articleCount: number
  onSearch:     (v: string) => void
  onCategory:   (c: Category) => void
  onSort:       (s: Sort) => void
}

export default function ArticleFilters({ search, category, sort, articleCount, onSearch, onCategory, onSort }: Props) {
  return (
    <>
      <div className="search-bar">
        <div className="search-wrap">
          <i className="fas fa-search"></i>
          <input
            type="text"
            className="search-input"
            placeholder="חפש מאמר, תגית או כותב..."
            value={search}
            onChange={e => onSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="filters">
        <div className="cat-pills">
          {TABS.map(t => (
            <button
              key={t.id}
              onClick={() => onCategory(t.id)}
              className={`cat-pill${category === t.id ? ' active' : ''}`}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className="sort-row">
          {(['hot', 'new', 'popular'] as Sort[]).map(s => (
            <button
              key={s}
              onClick={() => onSort(s)}
              className={`sort-btn${sort === s ? ' active' : ''}`}
            >
              {SORT_LABELS[s]}
            </button>
          ))}
          <span className="sort-count">{articleCount} מאמרים</span>
        </div>
      </div>
    </>
  )
}
