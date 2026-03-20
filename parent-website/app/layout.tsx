import type { Metadata } from 'next'
import './globals.css'
import './homepage.css'
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
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
        <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
      </head>
      <body>
        {children}
        <CookieBanner />
      </body>
    </html>
  )
}
