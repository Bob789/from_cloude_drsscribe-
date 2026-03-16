import type { Metadata } from 'next'
import './globals.css'
import CookieBanner from '@/components/CookieBanner'

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
      </head>
      <body>
        {children}
        <footer className="site-footer">
          <p>© 2026 Medical Hub • <a href="https://drsscribe.com/privacy-policy">Doctor Scribe AI Privacy Policy</a> • <a href="https://drsscribe.com/privacy-policy">מדיניות פרטיות</a> • <a href="https://drsscribe.com/terms">תנאי שימוש</a></p>
        </footer>
        <CookieBanner />
      </body>
    </html>
  )
}
