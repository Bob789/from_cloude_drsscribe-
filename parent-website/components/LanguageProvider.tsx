'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { type LangCode, type Translations, translations, isRTL, t as tFn } from '@/lib/translations'
import { detectGeo, getCachedGeo, setLangOverride, type GeoResult } from '@/lib/geoip'

interface LanguageContextValue {
  lang: LangCode
  flag: string
  dir: 'rtl' | 'ltr'
  t: (key: keyof Translations, vars?: Record<string, string | number>) => string
  setLang: (lang: LangCode) => void
  ready: boolean
}

const DEFAULT_GEO: GeoResult = { lang: 'he', flag: '🇮🇱', countryCode: 'IL' }

const LanguageContext = createContext<LanguageContextValue>({
  lang: 'he',
  flag: '🇮🇱',
  dir: 'rtl',
  t: (key) => key as string,
  setLang: () => {},
  ready: false,
})

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  // Initialize immediately from cache so there's no flash to English
  const [geo, setGeo] = useState<GeoResult>(() => {
    if (typeof window !== 'undefined') {
      const cached = getCachedGeo()
      if (cached) return cached
    }
    return DEFAULT_GEO
  })
  const [ready, setReady] = useState(false)

  useEffect(() => {
    detectGeo().then((result) => {
      setGeo(result)
      setReady(true)
      document.documentElement.lang = result.lang
      document.documentElement.dir = isRTL(result.lang) ? 'rtl' : 'ltr'
    })
  }, [])

  const setLang = (lang: LangCode) => {
    setLangOverride(lang)
    const newFlag = geo.flag
    const newGeo: GeoResult = { lang, flag: newFlag, countryCode: geo.countryCode }
    setGeo(newGeo)
    document.documentElement.lang = lang
    document.documentElement.dir = isRTL(lang) ? 'rtl' : 'ltr'
  }

  const t = (key: keyof Translations, vars?: Record<string, string | number>) =>
    tFn(geo.lang, key, vars)

  const dir: 'rtl' | 'ltr' = isRTL(geo.lang) ? 'rtl' : 'ltr'

  return (
    <LanguageContext.Provider
      value={{
        lang: geo.lang,
        flag: geo.flag,
        dir,
        t,
        setLang,
        ready,
      }}
    >
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage(): LanguageContextValue {
  return useContext(LanguageContext)
}
