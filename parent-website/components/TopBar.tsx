'use client'

import Link from 'next/link'
import { FEATURES } from '@/lib/featureFlags'
import { useLanguage } from '@/components/LanguageProvider'

export default function TopBar() {
  const { t } = useLanguage()
  if (!FEATURES.product) return null
  return (
    <div className="hp-topbar">
      <Link href="/product">{t('topbar_new')}</Link>
    </div>
  )
}
