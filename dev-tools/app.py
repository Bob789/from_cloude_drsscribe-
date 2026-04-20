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

import html as html_lib
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
    finally:
        await context.close()
        await browser.close()
        await pw.stop()

    html_doc = _build_flat_html(snapshot)
    headers = {"Content-Disposition": 'inline; filename="flatten.html"'}
    if console_errors:
        headers["X-Console-Errors"] = " | ".join(console_errors[:5])[:1000]
    return Response(
        content=html_doc,
        media_type="text/html; charset=utf-8",
        headers=headers,
    )


def _esc(s: str) -> str:
    return html_lib.escape(s or "", quote=True)


def _build_flat_html(snapshot: dict[str, Any]) -> str:
    """Return static flattened HTML from page-evaluated snapshot payload."""
    html_doc = snapshot.get("html") if isinstance(snapshot, dict) else None
    if isinstance(html_doc, str) and html_doc.strip():
        return html_doc

    title = _esc(str(snapshot.get("title", "Flattened Page")))
    src_url = _esc(str(snapshot.get("url", "")))
    return (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        f"<title>{title}</title></head><body>"
        "<h1>Flatten failed</h1>"
        f"<p>Source: <a href=\"{src_url}\">{src_url}</a></p>"
        "</body></html>"
    )
