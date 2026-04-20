import { NextRequest, NextResponse } from 'next/server'

const DEV_TOOLS_URL = process.env.DEV_TOOLS_URL || 'http://medscribe-dev-tools:8090'
const DEV_TOOLS_TOKEN = process.env.DEV_TOOLS_TOKEN || 'dev-token-change-me'

export async function POST(req: NextRequest) {
  const url = new URL(req.url)
  const kind = url.searchParams.get('kind') === 'flatten' ? 'flatten' : 'screenshot'

  let body: any
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 })
  }

  // NOTE: We intentionally do NOT rewrite the URL here. The dev-tools
  // service has its own HOST_REWRITES and Playwright route interception
  // that handles localhost mapping while preserving the original origin
  // (so client-side fetch calls keep working). Rewriting here would
  // change the page origin and break some apps.

  try {
    const upstream = await fetch(`${DEV_TOOLS_URL}/capture/${kind}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Dev-Token': DEV_TOOLS_TOKEN,
      },
      body: JSON.stringify(body),
    })

    const buf = await upstream.arrayBuffer()
    const passHeaders: Record<string, string> = {
      'Content-Type': upstream.headers.get('Content-Type') || 'application/octet-stream',
    }
    const consoleErrors = upstream.headers.get('X-Console-Errors')
    if (consoleErrors) passHeaders['X-Console-Errors'] = consoleErrors
    if (!upstream.ok) {
      return new NextResponse(buf, { status: upstream.status, headers: passHeaders })
    }
    return new NextResponse(buf, { status: 200, headers: passHeaders })
  } catch (e: any) {
    return NextResponse.json(
      { error: 'Upstream unreachable', detail: e.message || String(e), url: body?.url },
      { status: 502 },
    )
  }
}

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'
