import { Suspense } from 'react'
import type { Metadata } from 'next'
import { Heebo, Rubik } from 'next/font/google'
import './globals.css'
import './homepage.css'
import CookieBanner         from '@/components/CookieBanner'

const heebo = Heebo({
  subsets: ['hebrew', 'latin'],
  weight: ['300', '400', '500', '700', '900'],
  display: 'swap',
  variable: '--font-heebo',
})

const rubik = Rubik({
  subsets: ['hebrew', 'latin'],
  weight: ['300', '400', '500', '600', '700', '800', '900'],
  display: 'swap',
  variable: '--font-rubik',
})
import Header               from '@/components/Header'
import Footer               from '@/components/Footer'
import StarsCanvas          from '@/components/StarsCanvas'
import AccessibilityWidget  from '@/components/AccessibilityWidget'
import SiteAnalytics        from '@/components/SiteAnalytics'
import Link         from 'next/link'
import { FEATURES } from '@/lib/featureFlags'

export const metadata: Metadata = {
  title: 'Medical Hub + Doctor Scribe AI',
  description: 'פלטפורמה מקיפה: מאמרים • פורום • מומחים • תמלול רפואי חכם',
  icons: {
    icon: '/favicon.png',
    apple: '/favicon.png',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: 'https://medicalhub.co.il',
  },
  openGraph: {
    title: 'Medical Hub + Doctor Scribe AI',
    description: 'פלטפורמה מקיפה: מאמרים • פורום • מומחים • תמלול רפואי חכם',
    url: 'https://medicalhub.co.il',
    siteName: 'Medical Hub',
    locale: 'he_IL',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Medical Hub + Doctor Scribe AI',
    description: 'פלטפורמה מקיפה: מאמרים • פורום • מומחים • תמלול רפואי חכם',
  },
  verification: {
    google: process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION || '',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="he" dir="rtl" className={`${heebo.variable} ${rubik.variable}`}>
      <head>
        <link rel="privacy-policy" href="https://medicalhub.co.il/privacy" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'WebSite',
              name: 'Medical Hub',
              url: 'https://medicalhub.co.il',
              description: 'פלטפורמה מקיפה: מאמרים רפואיים, פורום קהילתי, מומחים ותמלול רפואי חכם',
              inLanguage: 'he',
              potentialAction: {
                '@type': 'SearchAction',
                target: 'https://medicalhub.co.il/search?q={search_term_string}',
                'query-input': 'required name=search_term_string',
              },
            }),
          }}
        />
      </head>
      <body>
        {/* Stars floating in background — fixed, covers all pages */}
        <StarsCanvas />

        {/* Yellow top-bar — same on every page */}
        {FEATURES.product && (
        <div className="hp-topbar">
          <Link href="/product">חדש: תמלול רפואי אוטומטי לקליניקות, Doctor Scribe AI ←</Link>
        </div>
        )}

        {/* Shared header — blue + gold, auto-detects active page */}
        <Header />

        {/* Page content — yellow block written ONCE here, applies to all pages */}
        <main>
          <div className="site-block">
            {children}
          </div>
        </main>

        {/* Shared footer */}
        <Footer />

        <CookieBanner />
        <AccessibilityWidget />
        <Suspense fallback={null}><SiteAnalytics /></Suspense>
      </body>
    </html>
  )
}

