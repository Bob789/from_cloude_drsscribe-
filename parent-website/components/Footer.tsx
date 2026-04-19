'use client'

import Link from 'next/link'
import { FEATURES } from '@/lib/featureFlags'
import { useLanguage } from '@/components/LanguageProvider'

export default function Footer() {
  const { t } = useLanguage()
  return (
    <footer>
      <div className="footer-logo">MedicalHub</div>
      <div className="footer-links">
        <Link href="/articles">{t('nav_articles')}</Link>
        {FEATURES.forum && <Link href="/forum">{t('nav_forum')}</Link>}
        {FEATURES.experts && <Link href="/experts">{t('nav_experts')}</Link>}
        {FEATURES.product && <Link href="/product">Doctor Scribe AI</Link>}
      </div>
      <div className="footer-legal">
        <Link href="/terms">{t('footer_terms')}</Link>
        <span>|</span>
        <Link href="/privacy">{t('footer_privacy')}</Link>
        <span>|</span>
        <Link href="/medical-disclaimer">{t('footer_disclaimer')}</Link>
      </div>
      <div className="footer-copy">© 2026 Medical Hub</div>
    </footer>
  )
}
