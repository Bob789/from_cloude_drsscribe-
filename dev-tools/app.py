"""
DoctorScribe Dev-Tools service.

Internal-only utility to capture visual snapshots of pages (mainly Flutter Web)
and produce a single self-contained HTML file representing what the user sees.

Endpoints:
  POST /capture/screenshot  -> PNG of the full page
  POST /capture/flatten     -> Single self-contained HTML snapshot
  GET  /health              -> Liveness check

Auth: all capture endpoints require header `X-Dev-Token` matching DEV_TOOLS_TOKEN.
"""
from __future__ import annotations

import base64
import html as html_lib
import io
import json
import os
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

DEV_TOOLS_TOKEN = os.getenv("DEV_TOOLS_TOKEN", "dev-token-change-me")
DEFAULT_VIEWPORT_W = 1440
DEFAULT_VIEWPORT_H = 900
NAV_TIMEOUT_MS = 45_000

FLATTEN_JS = (Path(__file__).parent / "flatten.js").read_text(encoding="utf-8")

app = FastAPI(title="DoctorScribe Dev-Tools", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _check_token(token: Optional[str]) -> None:
    if not token or token != DEV_TOOLS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid dev-tools token")


class CaptureRequest(BaseModel):
    url: str = Field(..., description="Absolute URL to capture")
    viewport_width: int = Field(DEFAULT_VIEWPORT_W, ge=320, le=4000)
    viewport_height: int = Field(DEFAULT_VIEWPORT_H, ge=240, le=4000)
    wait_ms: int = Field(2500, ge=0, le=30_000, description="Extra wait after load")
    auth_token: Optional[str] = Field(
        None,
        description=(
            "Optional JWT to inject into localStorage as 'access_token' before navigation, "
            "so authenticated pages render correctly."
        ),
    )
    full_page: bool = Field(True)
    cookies: Optional[list[dict[str, Any]]] = Field(default=None)
    locale: str = Field("he-IL", description="Browser locale, e.g. 'he-IL', 'en-US'")


async def _render_page(req: CaptureRequest):
    """Open Chromium, set up auth, navigate, and return (page, browser, context)."""
    from playwright.async_api import async_playwright  # imported lazily

    pw = await async_playwright().start()
    browser = await pw.chromium.launch(args=["--no-sandbox"])
    context = await browser.new_context(
        viewport={"width": req.viewport_width, "height": req.viewport_height},
        device_scale_factor=1,
        locale=req.locale,
        extra_http_headers={"Accept-Language": f"{req.locale},{req.locale.split('-')[0]};q=0.9,en;q=0.5"},
    )

    if req.cookies:
        try:
            await context.add_cookies(req.cookies)  # type: ignore[arg-type]
        except Exception:
            pass

    page = await context.new_page()

    # Collect console errors for diagnostics
    console_errors: list[str] = []
    page.on("pageerror", lambda exc: console_errors.append(f"PAGEERROR: {exc}"))
    page.on("console", lambda msg: console_errors.append(f"{msg.type.upper()}: {msg.text}") if msg.type in ("error", "warning") else None)

    # Rewrite client-side requests to docker-internal hostnames.
    # Pages built with NEXT_PUBLIC_API_URL=http://localhost:8000/api will try to
    # hit localhost from inside this container — re-route them to the backend
    # service on the docker network.
    HOST_REWRITES = [
        ("http://localhost:8000", "http://backend:8000"),
        ("http://127.0.0.1:8000", "http://backend:8000"),
        ("http://localhost:3001", "http://parent-website:3000"),
        ("http://127.0.0.1:3001", "http://parent-website:3000"),
    ]

    async def _rewrite_route(route):
        try:
            url = route.request.url
            new_url = url
            for src, dst in HOST_REWRITES:
                if new_url.startswith(src):
                    new_url = dst + new_url[len(src):]
                    break
            if new_url == url:
                await route.continue_()
                return
            # Fetch from the rewritten URL ourselves and return the response
            # body to chromium as-if it came from the original URL. This avoids
            # CORS / cross-origin redirect issues.
            try:
                api_resp = await route.request.frame.page.context.request.fetch(
                    new_url,
                    method=route.request.method,
                    headers=route.request.headers,
                    data=route.request.post_data,
                )
                body = await api_resp.body()
                await route.fulfill(
                    status=api_resp.status,
                    headers=dict(api_resp.headers),
                    body=body,
                )
            except Exception as e:
                console_errors.append(f"FETCH_ERROR: {e} for {new_url}")
                await route.abort()
        except Exception as e:
            console_errors.append(f"ROUTE_ERROR: {e} on {route.request.url}")
            try:
                await route.continue_()
            except Exception:
                pass

    await context.route("**/*", _rewrite_route)

    if req.auth_token:
        # Inject token into localStorage *before* the SPA boots.
        origin = _origin_of(req.url)
        await context.add_init_script(
            f"window.localStorage.setItem('access_token', {json.dumps(req.auth_token)});"
        )
        # Also attempt to set it as Authorization for the first request
        await page.set_extra_http_headers({"Authorization": f"Bearer {req.auth_token}"})
        _ = origin  # placeholder for future per-origin logic

    await page.goto(req.url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)
    if req.wait_ms > 0:
        await page.wait_for_timeout(req.wait_ms)

    return pw, browser, context, page, console_errors


def _origin_of(url: str) -> str:
    try:
        from urllib.parse import urlparse

        u = urlparse(url)
        return f"{u.scheme}://{u.netloc}"
    except Exception:
        return ""


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "service": "dev-tools", "ts": int(time.time())}


@app.post("/capture/screenshot")
async def capture_screenshot(
    req: CaptureRequest,
    x_dev_token: Optional[str] = Header(default=None, alias="X-Dev-Token"),
) -> Response:
    _check_token(x_dev_token)

    pw, browser, context, page, console_errors = await _render_page(req)
    try:
        png_bytes = await page.screenshot(full_page=req.full_page, type="png")
    finally:
        await context.close()
        await browser.close()
        await pw.stop()

    headers = {"Content-Disposition": 'inline; filename="capture.png"'}
    if console_errors:
        # Expose first few errors in a header for debugging (truncated)
        headers["X-Console-Errors"] = " | ".join(console_errors[:5])[:1000]
    return Response(content=png_bytes, media_type="image/png", headers=headers)


@app.post("/capture/flatten")
async def capture_flatten(
    req: CaptureRequest,
    x_dev_token: Optional[str] = Header(default=None, alias="X-Dev-Token"),
) -> Response:
    _check_token(x_dev_token)

    pw, browser, context, page, console_errors = await _render_page(req)
    try:
        snapshot = await page.evaluate(FLATTEN_JS)
        # Also grab a screenshot to embed alongside, useful as a visual reference.
        png_bytes = await page.screenshot(full_page=True, type="png")
    finally:
        await context.close()
        await browser.close()
        await pw.stop()

    html_doc = _build_flat_html(snapshot, png_bytes)
    return Response(
        content=html_doc,
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": 'inline; filename="flatten.html"'},
    )


def _esc(s: str) -> str:
    return html_lib.escape(s or "", quote=True)


def _style_to_css(style: dict[str, str]) -> str:
    return ";".join(f"{k}:{v}" for k, v in style.items())


def _build_flat_html(snapshot: dict[str, Any], png_bytes: bytes) -> str:
    """Turn the raw snapshot into one self-contained absolute-positioned HTML page."""
    doc_w = int(snapshot.get("docW", DEFAULT_VIEWPORT_W))
    doc_h = int(snapshot.get("docH", DEFAULT_VIEWPORT_H))
    elements: list[dict[str, Any]] = snapshot.get("elements", [])
    title = snapshot.get("title", "Captured Page")
    src_url = snapshot.get("url", "")

    png_b64 = base64.b64encode(png_bytes).decode("ascii")

    parts: list[str] = []
    parts.append("<!doctype html>")
    parts.append('<html><head><meta charset="utf-8">')
    parts.append(f"<title>{_esc(title)} — Flattened</title>")
    parts.append(
        "<style>"
        "body{margin:0;font-family:system-ui,sans-serif;background:#0b0d10;color:#eaeaea}"
        ".meta{padding:12px 16px;background:#11151a;border-bottom:1px solid #222;"
        "position:sticky;top:0;z-index:9999;font-size:13px}"
        ".meta a{color:#8ab4ff}"
        ".tabs{display:flex;gap:8px;margin-top:8px}"
        ".tabs button{background:#1a1f26;color:#eaeaea;border:1px solid #2a2f36;"
        "padding:6px 12px;border-radius:4px;cursor:pointer;font-size:12px}"
        ".tabs button.active{background:#2a4060;border-color:#3a5a80}"
        ".pane{display:none;position:relative}"
        ".pane.active{display:block}"
        f"#stage{{position:relative;width:{doc_w}px;height:{doc_h}px;background:#fff;color:#000;"
        f"margin:16px auto;box-shadow:0 0 30px rgba(0,0,0,.5);overflow:hidden}}"
        ".el{position:absolute;box-sizing:border-box;white-space:nowrap;overflow:hidden;"
        "display:flex;align-items:center;justify-content:flex-start;pointer-events:none;"
        "text-overflow:ellipsis}"
        ".el[data-tag=img]{justify-content:center}"
        f"#screenshot img{{display:block;max-width:100%;width:{doc_w}px;margin:16px auto;"
        f"box-shadow:0 0 30px rgba(0,0,0,.5)}}"
        "</style>"
    )
    parts.append("</head><body>")

    parts.append('<div class="meta">')
    parts.append(
        f"<div><strong>Flattened capture</strong> &middot; "
        f'source: <a href="{_esc(src_url)}" target="_blank">{_esc(src_url)}</a> '
        f"&middot; size: {doc_w}×{doc_h} &middot; elements: {len(elements)}</div>"
    )
    parts.append(
        '<div class="tabs">'
        '<button class="active" data-pane="flat">Flat HTML</button>'
        '<button data-pane="screenshot">Screenshot</button>'
        "</div>"
    )
    parts.append("</div>")

    # --- Flat pane ---
    parts.append('<div class="pane active" id="flat"><div id="stage">')
    for idx, el in enumerate(elements):
        x, y, w, h = int(el.get("x", 0)), int(el.get("y", 0)), int(el.get("w", 0)), int(el.get("h", 0))
        if x + w < 0 or y + h < 0 or x > doc_w or y > doc_h:
            continue
        css = _style_to_css(el.get("style", {}))
        text = el.get("text", "")
        aria = el.get("ariaLabel", "")
        role = el.get("role", "")
        img_src = el.get("imgSrc")
        tag = el.get("tag", "div")

        # Force monotonic z-index based on DOM source order so later elements
        # (typically text/icons inside containers) render on top of earlier
        # ones (containers/backgrounds).
        attrs = (
            f'style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;z-index:{idx};{_esc(css)}" '
            f'data-tag="{_esc(tag)}"'
        )
        if role:
            attrs += f' role="{_esc(role)}"'
        if aria:
            attrs += f' aria-label="{_esc(aria)}"'

        if img_src and img_src.startswith(("http://", "https://", "data:")):
            parts.append(f'<div class="el" {attrs}><img src="{_esc(img_src)}" '
                         f'style="width:100%;height:100%;object-fit:contain" alt=""></div>')
        else:
            display_text = text or aria or ""
            parts.append(f'<div class="el" {attrs}>{_esc(display_text)}</div>')
    parts.append("</div></div>")

    # --- Screenshot pane ---
    parts.append('<div class="pane" id="screenshot">')
    parts.append(f'<img src="data:image/png;base64,{png_b64}" alt="Full page screenshot">')
    parts.append("</div>")

    parts.append(
        "<script>"
        "document.querySelectorAll('.tabs button').forEach(b=>{"
        "b.addEventListener('click',()=>{"
        "document.querySelectorAll('.tabs button').forEach(x=>x.classList.remove('active'));"
        "document.querySelectorAll('.pane').forEach(x=>x.classList.remove('active'));"
        "b.classList.add('active');"
        "document.getElementById(b.dataset.pane).classList.add('active');"
        "});});"
        "</script>"
    )
    parts.append("</body></html>")
    return "".join(parts)
