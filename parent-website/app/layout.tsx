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
import Link         from 'next/link'
import { FEATURES } from '@/lib/featureFlags'

export const metadata: Metadata = {
  title: 'Medical Hub + Doctor Scribe AI',
  description: 'פלטפורמה מקיפה: מאמרים • פורום • מומחים • תמלול רפואי חכם',
  icons: {
    icon: '/favicon.png',
    apple: '/favicon.png',
  },
  openGraph: {
    title: 'Medical Hub + Doctor Scribe AI',
    description: 'פלטפורמה מקיפה: מאמרים • פורום • מומחים • תמלול רפואי חכם',
    url: 'https://medicalhub.co.il',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="he" dir="rtl" className={`${heebo.variable} ${rubik.variable}`}>
      <head>
        <link rel="privacy-policy" href="https://medicalhub.co.il/privacy" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
      </head>
      <body>
        {/* Stars floating in background — fixed, covers all pages */}
        <StarsCanvas />

        {/* Yellow top-bar — same on every page */}
        {FEATURES.product && (
        <div className="hp-topbar">
          <Link href="/product">חדש: תמלול רפואי אוטומטי לקליניקות — Doctor Scribe AI ←</Link>
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
      </body>
    </html>
  )
}

