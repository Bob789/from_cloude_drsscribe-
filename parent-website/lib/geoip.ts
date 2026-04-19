import type { LangCode } from './translations'

export interface GeoResult {
  lang: LangCode
  flag: string
  countryCode: string
}

const COUNTRY_MAP: Record<string, { lang: LangCode; flag: string }> = {
  // Hebrew
  IL: { lang: 'he', flag: '🇮🇱' },

  // Arabic
  SA: { lang: 'ar', flag: '🇸🇦' },
  AE: { lang: 'ar', flag: '🇦🇪' },
  EG: { lang: 'ar', flag: '🇪🇬' },
  JO: { lang: 'ar', flag: '🇯🇴' },
  KW: { lang: 'ar', flag: '🇰🇼' },
  QA: { lang: 'ar', flag: '🇶🇦' },
  LB: { lang: 'ar', flag: '🇱🇧' },
  IQ: { lang: 'ar', flag: '🇮🇶' },
  SY: { lang: 'ar', flag: '🇸🇾' },
  MA: { lang: 'ar', flag: '🇲🇦' },
  TN: { lang: 'ar', flag: '🇹🇳' },
  LY: { lang: 'ar', flag: '🇱🇾' },
  DZ: { lang: 'ar', flag: '🇩🇿' },
  SD: { lang: 'ar', flag: '🇸🇩' },
  YE: { lang: 'ar', flag: '🇾🇪' },
  OM: { lang: 'ar', flag: '🇴🇲' },
  BH: { lang: 'ar', flag: '🇧🇭' },
  PS: { lang: 'ar', flag: '🇵🇸' },
  MR: { lang: 'ar', flag: '🇲🇷' },
  SO: { lang: 'ar', flag: '🇸🇴' },
  DJ: { lang: 'ar', flag: '🇩🇯' },

  // Russian
  RU: { lang: 'ru', flag: '🇷🇺' },
  BY: { lang: 'ru', flag: '🇧🇾' },
  KZ: { lang: 'ru', flag: '🇰🇿' },
  KG: { lang: 'ru', flag: '🇰🇬' },
  TJ: { lang: 'ru', flag: '🇹🇯' },
  TM: { lang: 'ru', flag: '🇹🇲' },
  UZ: { lang: 'ru', flag: '🇺🇿' },

  // Chinese Simplified
  CN: { lang: 'zh', flag: '🇨🇳' },

  // Chinese Traditional
  TW: { lang: 'zh-TW', flag: '🇹🇼' },
  HK: { lang: 'zh-TW', flag: '🇭🇰' },
  MO: { lang: 'zh-TW', flag: '🇲🇴' },

  // Vietnamese
  VN: { lang: 'vi', flag: '🇻🇳' },

  // Korean
  KR: { lang: 'ko', flag: '🇰🇷' },

  // Hindi
  IN: { lang: 'hi', flag: '🇮🇳' },

  // German
  DE: { lang: 'de', flag: '🇩🇪' },
  AT: { lang: 'de', flag: '🇦🇹' },

  // Spanish
  ES: { lang: 'es', flag: '🇪🇸' },
  MX: { lang: 'es', flag: '🇲🇽' },
  AR: { lang: 'es', flag: '🇦🇷' },
  CO: { lang: 'es', flag: '🇨🇴' },
  CL: { lang: 'es', flag: '🇨🇱' },
  PE: { lang: 'es', flag: '🇵🇪' },
  VE: { lang: 'es', flag: '🇻🇪' },
  EC: { lang: 'es', flag: '🇪🇨' },
  GT: { lang: 'es', flag: '🇬🇹' },
  CU: { lang: 'es', flag: '🇨🇺' },
  BO: { lang: 'es', flag: '🇧🇴' },
  DO: { lang: 'es', flag: '🇩🇴' },
  HN: { lang: 'es', flag: '🇭🇳' },
  PY: { lang: 'es', flag: '🇵🇾' },
  SV: { lang: 'es', flag: '🇸🇻' },
  NI: { lang: 'es', flag: '🇳🇮' },
  CR: { lang: 'es', flag: '🇨🇷' },
  PA: { lang: 'es', flag: '🇵🇦' },
  UY: { lang: 'es', flag: '🇺🇾' },

  // French
  FR: { lang: 'fr', flag: '🇫🇷' },
  BE: { lang: 'fr', flag: '🇧🇪' },
  CH: { lang: 'fr', flag: '🇨🇭' },
  LU: { lang: 'fr', flag: '🇱🇺' },
  CI: { lang: 'fr', flag: '🇨🇮' },
  SN: { lang: 'fr', flag: '🇸🇳' },
  CM: { lang: 'fr', flag: '🇨🇲' },

  // Portuguese
  PT: { lang: 'pt', flag: '🇵🇹' },
  BR: { lang: 'pt', flag: '🇧🇷' },
  AO: { lang: 'pt', flag: '🇦🇴' },
  MZ: { lang: 'pt', flag: '🇲🇿' },

  // Italian
  IT: { lang: 'it', flag: '🇮🇹' },

  // English-speaking (explicit, most fall to default)
  US: { lang: 'en', flag: '🇺🇸' },
  GB: { lang: 'en', flag: '🇬🇧' },
  AU: { lang: 'en', flag: '🇦🇺' },
  CA: { lang: 'en', flag: '🇨🇦' },
  NZ: { lang: 'en', flag: '🇳🇿' },
  SG: { lang: 'en', flag: '🇸🇬' },
  IE: { lang: 'en', flag: '🇮🇪' },
  ZA: { lang: 'en', flag: '🇿🇦' },
}

const DEFAULT_RESULT: GeoResult = { lang: 'en', flag: '🌐', countryCode: 'XX' }

const LS_LANG_KEY        = 'mh_lang_v2'
const LS_FLAG_KEY        = 'mh_flag_v2'
const LS_CC_KEY          = 'mh_cc_v2'
const LS_USER_OVERRIDE   = 'mh_user_override_v2'

// Representative flag for each language (used when user manually picks)
const LANG_DEFAULT_FLAG: Record<string, string> = {
  he: '🇮🇱', en: '🇺🇸', ar: '🇸🇦', ru: '🇷🇺',
  de: '🇩🇪', fr: '🇫🇷', es: '🇪🇸', pt: '🇧🇷',
  it: '🇮🇹', zh: '🇨🇳', 'zh-TW': '🇹🇼', ko: '🇰🇷',
  hi: '🇮🇳', vi: '🇻🇳',
}

export function getCachedGeo(): GeoResult | null {
  try {
    const lang = localStorage.getItem(LS_LANG_KEY) as LangCode | null
    const flag = localStorage.getItem(LS_FLAG_KEY)
    const countryCode = localStorage.getItem(LS_CC_KEY)
    if (lang && flag && countryCode) return { lang, flag, countryCode }
  } catch {}
  return null
}

export function setCachedGeo(result: GeoResult): void {
  try {
    localStorage.setItem(LS_LANG_KEY, result.lang)
    localStorage.setItem(LS_FLAG_KEY, result.flag)
    localStorage.setItem(LS_CC_KEY, result.countryCode)
  } catch {}
}

export function setLangOverride(lang: LangCode): void {
  try {
    const current = getCachedGeo()
    const flag = LANG_DEFAULT_FLAG[lang] ?? '🌐'
    const cc = current?.countryCode ?? 'XX'
    localStorage.setItem(LS_LANG_KEY, lang)
    localStorage.setItem(LS_FLAG_KEY, flag)
    localStorage.setItem(LS_CC_KEY, cc)
    localStorage.setItem(LS_USER_OVERRIDE, '1')  // mark as manually selected
  } catch {}
}

export async function detectGeo(): Promise<GeoResult> {
  // If user manually selected a language, never override it
  try {
    if (localStorage.getItem(LS_USER_OVERRIDE) === '1') {
      const cached = getCachedGeo()
      if (cached) return cached
    }
  } catch {}

  // Call same-origin server endpoint — no mixed-content / CORS issues.
  // Server reads X-Real-IP from Nginx and resolves country via HTTPS provider,
  // with Accept-Language as fallback.
  try {
    const res = await fetch('/api/geo', {
      signal: AbortSignal.timeout(4000),
      cache: 'no-store',
    })
    if (!res.ok) throw new Error('geo fetch failed')
    const data = await res.json()
    const lang: LangCode = (data.lang ?? 'en') as LangCode
    const flag: string = data.flag ?? '🌐'
    const countryCode: string = (data.countryCode ?? 'XX').toUpperCase()
    const result: GeoResult = { lang, flag, countryCode }
    setCachedGeo(result)
    return result
  } catch {
    // Last-resort fallback: use cached value if any, otherwise English
    const cached = getCachedGeo()
    if (cached) return cached
    return DEFAULT_RESULT
  }
}
