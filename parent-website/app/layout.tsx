import type { Metadata } from 'next'
import './globals.css'
import './homepage.css'
import CookieBanner         from '@/components/CookieBanner'
import Header               from '@/components/Header'
import Footer               from '@/components/Footer'
import StarsCanvas          from '@/components/StarsCanvas'
import AccessibilityWidget  from '@/components/AccessibilityWidget'
import NavDebugger          from '@/components/NavDebugger'
import Link         from 'next/link'

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
    <html lang="he" dir="rtl">
      <head>
        <link rel="privacy-policy" href="https://drsscribe.com/privacy-policy" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
        <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
      </head>
      <body>
        {/* Stars floating in background — fixed, covers all pages */}
        <StarsCanvas />

        {/* Yellow top-bar — same on every page */}
        <div className="hp-topbar">
          <Link href="/product">חדש: תמלול רפואי אוטומטי לקליניקות — Doctor Scribe AI ←</Link>
        </div>

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
        <NavDebugger />
      </body>
    </html>
  )
}

