import { NextResponse } from 'next/server'

const API = process.env.NEXT_PUBLIC_API_URL || 'https://app.drsscribe.com/api'
const SITE_URL = 'https://medicalhub.co.il'

function escapeXml(str: string): string {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

export async function GET() {
  try {
    const res = await fetch(`${API}/articles?sort=newest&per_page=30`, {
      next: { revalidate: 3600 }, // cache 1 hour
    })
    const data = res.ok ? await res.json() : { items: [] }
    const articles: any[] = data.items || []

    const items = articles.map((a: any) => {
      const pubDate = a.published_at
        ? new Date(a.published_at).toUTCString()
        : new Date().toUTCString()
      const tags = (a.tags || []).map((t: string) => `<category>${escapeXml(t)}</category>`).join('\n      ')
      return `
    <item>
      <title>${escapeXml(a.title)}</title>
      <link>${SITE_URL}/articles/${escapeXml(a.slug)}</link>
      <guid isPermaLink="true">${SITE_URL}/articles/${escapeXml(a.slug)}</guid>
      <description>${escapeXml(a.summary || '')}</description>
      <pubDate>${pubDate}</pubDate>
      <author>${escapeXml(a.author_name || 'Medical Hub')}</author>
      ${tags}
      ${a.hero_image_url ? `<enclosure url="${escapeXml(a.hero_image_url)}" type="image/jpeg" length="0"/>` : ''}
    </item>`
    }).join('\n')

    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
>
  <channel>
    <title>Medical Hub — מאמרים רפואיים</title>
    <link>${SITE_URL}/articles</link>
    <description>מאמרים רפואיים מקצועיים בעברית — קרדיולוגיה, נוירולוגיה, תזונה, בריאות הנפש ועוד</description>
    <language>he</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>
    <image>
      <url>${SITE_URL}/favicon.png</url>
      <title>Medical Hub</title>
      <link>${SITE_URL}</link>
    </image>
    ${items}
  </channel>
</rss>`

    return new NextResponse(xml, {
      status: 200,
      headers: {
        'Content-Type': 'application/rss+xml; charset=utf-8',
        'Cache-Control': 'public, max-age=3600, s-maxage=3600',
      },
    })
  } catch {
    return new NextResponse('RSS generation failed', { status: 500 })
  }
}
