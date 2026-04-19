import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

// Country -> language mapping (mirrors lib/geoip.ts COUNTRY_MAP keys)
const COUNTRY_TO_LANG: Record<string, string> = {
  IL: 'he',
  // Arabic
  SA: 'ar', AE: 'ar', EG: 'ar', JO: 'ar', KW: 'ar', QA: 'ar', LB: 'ar',
  IQ: 'ar', SY: 'ar', MA: 'ar', TN: 'ar', LY: 'ar', DZ: 'ar', SD: 'ar',
  YE: 'ar', OM: 'ar', BH: 'ar', PS: 'ar', MR: 'ar', SO: 'ar', DJ: 'ar',
  // Russian
  RU: 'ru', BY: 'ru', KZ: 'ru', KG: 'ru', TJ: 'ru', TM: 'ru', UZ: 'ru',
  // Chinese
  CN: 'zh', TW: 'zh-TW', HK: 'zh-TW', MO: 'zh-TW',
  // Other Asian
  VN: 'vi', KR: 'ko', IN: 'hi',
  // German
  DE: 'de', AT: 'de',
  // Spanish
  ES: 'es', MX: 'es', AR: 'es', CO: 'es', CL: 'es', PE: 'es', VE: 'es',
  EC: 'es', GT: 'es', CU: 'es', BO: 'es', DO: 'es', HN: 'es', PY: 'es',
  SV: 'es', NI: 'es', CR: 'es', PA: 'es', UY: 'es',
  // French
  FR: 'fr', BE: 'fr', CH: 'fr', LU: 'fr', CI: 'fr', SN: 'fr', CM: 'fr',
  // Portuguese
  PT: 'pt', BR: 'pt', AO: 'pt', MZ: 'pt',
  // Italian
  IT: 'it',
  // English
  US: 'en', GB: 'en', AU: 'en', CA: 'en', NZ: 'en', SG: 'en', IE: 'en', ZA: 'en',
}

const LANG_FLAG: Record<string, string> = {
  he: '🇮🇱', en: '🇺🇸', ar: '🇸🇦', ru: '🇷🇺', de: '🇩🇪',
  fr: '🇫🇷', es: '🇪🇸', pt: '🇧🇷', it: '🇮🇹', zh: '🇨🇳',
  'zh-TW': '🇹🇼', ko: '🇰🇷', hi: '🇮🇳', vi: '🇻🇳',
}

const COUNTRY_FLAG: Record<string, string> = {
  IL: '🇮🇱', SA: '🇸🇦', AE: '🇦🇪', EG: '🇪🇬', JO: '🇯🇴', KW: '🇰🇼',
  QA: '🇶🇦', LB: '🇱🇧', IQ: '🇮🇶', SY: '🇸🇾', MA: '🇲🇦', TN: '🇹🇳',
  LY: '🇱🇾', DZ: '🇩🇿', SD: '🇸🇩', YE: '🇾🇪', OM: '🇴🇲', BH: '🇧🇭',
  PS: '🇵🇸', MR: '🇲🇷', SO: '🇸🇴', DJ: '🇩🇯', RU: '🇷🇺', BY: '🇧🇾',
  KZ: '🇰🇿', KG: '🇰🇬', TJ: '🇹🇯', TM: '🇹🇲', UZ: '🇺🇿', CN: '🇨🇳',
  TW: '🇹🇼', HK: '🇭🇰', MO: '🇲🇴', VN: '🇻🇳', KR: '🇰🇷', IN: '🇮🇳',
  DE: '🇩🇪', AT: '🇦🇹', ES: '🇪🇸', MX: '🇲🇽', AR: '🇦🇷', CO: '🇨🇴',
  CL: '🇨🇱', PE: '🇵🇪', VE: '🇻🇪', EC: '🇪🇨', GT: '🇬🇹', CU: '🇨🇺',
  BO: '🇧🇴', DO: '🇩🇴', HN: '🇭🇳', PY: '🇵🇾', SV: '🇸🇻', NI: '🇳🇮',
  CR: '🇨🇷', PA: '🇵🇦', UY: '🇺🇾', FR: '🇫🇷', BE: '🇧🇪', CH: '🇨🇭',
  LU: '🇱🇺', CI: '🇨🇮', SN: '🇸🇳', CM: '🇨🇲', PT: '🇵🇹', BR: '🇧🇷',
  AO: '🇦🇴', MZ: '🇲🇿', IT: '🇮🇹', US: '🇺🇸', GB: '🇬🇧', AU: '🇦🇺',
  CA: '🇨🇦', NZ: '🇳🇿', SG: '🇸🇬', IE: '🇮🇪', ZA: '🇿🇦',
}

const SUPPORTED_LANGS = new Set(Object.values(COUNTRY_TO_LANG))

function normalizeIp(ip: string): string {
  // Strip IPv6-mapped IPv4 prefix: "::ffff:1.2.3.4" -> "1.2.3.4"
  return ip.replace(/^::ffff:/i, '').trim()
}

function getClientIp(req: NextRequest): string | null {
  // Prefer x-real-ip (set by our nginx) — it's the actual client IP
  const xri = req.headers.get('x-real-ip')
  if (xri) {
    const ip = normalizeIp(xri)
    if (ip && !isPrivateIp(ip)) return ip
  }
  // Walk x-forwarded-for chain, return first public IP
  const xff = req.headers.get('x-forwarded-for')
  if (xff) {
    for (const raw of xff.split(',')) {
      const ip = normalizeIp(raw)
      if (ip && !isPrivateIp(ip)) return ip
    }
  }
  // Last resort: return whatever x-real-ip had (even if private — caller will skip lookup)
  if (xri) return normalizeIp(xri)
  return null
}

function isPrivateIp(ipRaw: string): boolean {
  if (!ipRaw) return true
  const ip = ipRaw.replace(/^::ffff:/i, '')
  if (ip === '127.0.0.1' || ip === '::1' || ip === '0.0.0.0') return true
  if (ip.startsWith('10.') || ip.startsWith('192.168.')) return true
  if (ip.startsWith('172.')) {
    const second = parseInt(ip.split('.')[1] || '0', 10)
    if (second >= 16 && second <= 31) return true
  }
  if (ip.startsWith('169.254.') || ip.startsWith('fc') || ip.startsWith('fd')) return true
  return false
}

function pickLangFromAcceptLanguage(header: string | null): string | null {
  if (!header) return null
  // e.g. "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7"
  const parts = header.split(',').map((p) => {
    const [tag, qStr] = p.trim().split(';q=')
    const q = qStr ? parseFloat(qStr) : 1
    return { tag: tag.toLowerCase(), q: isNaN(q) ? 1 : q }
  }).sort((a, b) => b.q - a.q)

  for (const { tag } of parts) {
    const primary = tag.split('-')[0]
    // Special case Traditional Chinese
    if (tag.startsWith('zh-tw') || tag.startsWith('zh-hk') || tag.startsWith('zh-mo')) {
      return 'zh-TW'
    }
    if (primary === 'zh') return 'zh'
    if (SUPPORTED_LANGS.has(primary)) return primary
  }
  return null
}

// Raw GET that bypasses Next.js fetch wrapper (avoids extra headers
// like next-action / OpenTelemetry that some providers flag as CORS/bot).
function rawGet(url: string, timeoutMs = 5000): Promise<{ status: number; body: string }> {
  // Lazy require so the route still bundles cleanly.
  const isHttps = url.startsWith('https://')
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const lib = isHttps ? require('https') : require('http')
  return new Promise((resolve, reject) => {
    const req = lib.get(
      url,
      {
        headers: {
          'User-Agent': 'curl/8.0.0',
          'Accept': '*/*',
        },
        timeout: timeoutMs,
      },
      (res: { statusCode?: number; on: (e: string, cb: (chunk?: Buffer) => void) => void }) => {
        const chunks: Buffer[] = []
        res.on('data', (c?: Buffer) => { if (c) chunks.push(c) })
        res.on('end', () => {
          resolve({ status: res.statusCode || 0, body: Buffer.concat(chunks).toString('utf8') })
        })
        res.on('error', reject)
      }
    )
    req.on('timeout', () => { req.destroy(new Error('timeout')) })
    req.on('error', reject)
  })
}

async function lookupCountry(ip: string): Promise<string | null> {
  // Try ipwho.is (free, HTTPS, no key required, 10k req/month)
  try {
    const { status, body } = await rawGet(`https://ipwho.is/${encodeURIComponent(ip)}?fields=country_code,success`)
    if (status === 200) {
      const data = JSON.parse(body)
      if (data?.success && typeof data.country_code === 'string') return data.country_code.toUpperCase()
      console.warn('[geo] ipwho.is bad payload', data)
    } else {
      console.warn('[geo] ipwho.is status', status)
    }
  } catch (e) {
    console.warn('[geo] ipwho.is error', (e as Error).message)
  }

  // Fallback: ipapi.co (free HTTPS, 1k req/day)
  try {
    const { status, body } = await rawGet(`https://ipapi.co/${encodeURIComponent(ip)}/country/`)
    if (status === 200) {
      const txt = body.trim().toUpperCase()
      if (/^[A-Z]{2}$/.test(txt)) return txt
      console.warn('[geo] ipapi.co bad payload', txt)
    } else {
      console.warn('[geo] ipapi.co status', status)
    }
  } catch (e) {
    console.warn('[geo] ipapi.co error', (e as Error).message)
  }

  // Third fallback: ip-api.com (free, JSON, no key, 45 req/min)
  try {
    const { status, body } = await rawGet(`http://ip-api.com/json/${encodeURIComponent(ip)}?fields=countryCode,status`)
    if (status === 200) {
      const data = JSON.parse(body)
      if (data?.status === 'success' && typeof data.countryCode === 'string') return data.countryCode.toUpperCase()
      console.warn('[geo] ip-api.com bad payload', data)
    } else {
      console.warn('[geo] ip-api.com status', status)
    }
  } catch (e) {
    console.warn('[geo] ip-api.com error', (e as Error).message)
  }

  return null
}

export async function GET(req: NextRequest) {
  const ip = getClientIp(req)
  const acceptLang = req.headers.get('accept-language')

  let countryCode: string = 'XX'
  let lang: string | null = null
  let flag = '🌐'

  // 1. Try IP-based lookup if we have a real public IP
  if (ip && !isPrivateIp(ip)) {
    const cc = await lookupCountry(ip)
    if (cc) {
      countryCode = cc
      lang = COUNTRY_TO_LANG[cc] ?? null
      flag = COUNTRY_FLAG[cc] ?? (lang ? LANG_FLAG[lang] : '🌐')
    }
  }

  // 2. Fallback to Accept-Language header (most browsers send the user's preferred language)
  if (!lang) {
    const headerLang = pickLangFromAcceptLanguage(acceptLang)
    if (headerLang) {
      lang = headerLang
      flag = LANG_FLAG[headerLang] ?? '🌐'
    }
  }

  // 3. Final fallback: English
  if (!lang) {
    lang = 'en'
    flag = '🇺🇸'
  }

  return NextResponse.json(
    { lang, flag, countryCode },
    {
      headers: {
        'Cache-Control': 'private, max-age=3600',
      },
    }
  )
}
