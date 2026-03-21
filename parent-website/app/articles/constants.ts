export type Category =
  | 'all' | 'cardiology' | 'neurology' | 'orthopedics' | 'nutrition'
  | 'sleep' | 'mental' | 'general' | 'dermatology' | 'gastroenterology' | 'urology'

export type Sort = 'hot' | 'new' | 'popular'

export interface Author { name: string; title: string; count: number }

export const CATEGORY_META: Record<string, { label: string; color: string; bg: string }> = {
  cardiology:       { label: 'לב וכלי דם', color: '#f87171', bg: 'rgba(248,113,113,0.1)' },
  neurology:        { label: 'נוירולוגיה', color: '#a78bfa', bg: 'rgba(167,139,250,0.1)' },
  orthopedics:      { label: 'אורתופדיה',  color: '#60a5fa', bg: 'rgba(96,165,250,0.1)'  },
  nutrition:        { label: 'תזונה',       color: '#16a34a', bg: 'rgba(22,163,74,0.1)'   },
  sleep:            { label: 'שינה',        color: '#fbbf24', bg: 'rgba(251,191,36,0.1)'  },
  mental:           { label: 'בריאות נפש', color: '#f472b6', bg: 'rgba(244,114,182,0.1)' },
  general:          { label: 'כללי',        color: '#64748b', bg: 'rgba(100,116,139,0.1)' },
  dermatology:      { label: 'עור',         color: '#fb923c', bg: 'rgba(251,146,60,0.1)'  },
  gastroenterology: { label: 'גסטרו',      color: '#22c55e', bg: 'rgba(34,197,94,0.1)'   },
  urology:          { label: 'אורולוגיה',  color: '#38bdf8', bg: 'rgba(56,189,248,0.1)'  },
}

export const CATEGORY_ICONS: Record<string, string> = {
  cardiology: '❤️', neurology: '🧠', orthopedics: '🦴', nutrition: '🥗',
  sleep: '😴', mental: '🧘', general: '📋', dermatology: '🧴',
  gastroenterology: '🫁', urology: '💊',
}

export const TABS: { id: Category; label: string }[] = [
  { id: 'all',         label: '📋 הכל'   },
  { id: 'cardiology',  label: '❤️ לב'    },
  { id: 'neurology',   label: '🧠 נוירו' },
  { id: 'orthopedics', label: '🦴 אורתו' },
  { id: 'nutrition',   label: '🥗 תזונה' },
  { id: 'sleep',       label: '😴 שינה'  },
  { id: 'mental',      label: '🧘 נפש'   },
]

export const SORT_LABELS: Record<Sort, string> = {
  hot: '🔥 חם', new: '🆕 חדש', popular: '👁️ פופולרי',
}
