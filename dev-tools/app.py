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
import sqlite3
import threading
import time
from datetime import datetime, timezone
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

# ── Agent Bridge (SQLite message queue) ──────────────────────────────────────
DB_PATH = Path(os.getenv("BRIDGE_DB_PATH", "/tmp/agent_bridge.db"))
_db_lock = threading.Lock()


def _init_db() -> None:
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    role    TEXT NOT NULL,
                    content TEXT NOT NULL,
                    ts      TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bridge_state (
                    id      INTEGER PRIMARY KEY CHECK (id = 1),
                    enabled INTEGER NOT NULL DEFAULT 0
                )
            """)
            conn.execute("INSERT OR IGNORE INTO bridge_state(id, enabled) VALUES(1, 0)")
            conn.commit()
        finally:
            conn.close()


_init_db()
# ─────────────────────────────────────────────────────────────────────────────


def _build_ui_html() -> str:
    return """<!DOCTYPE html>
<html dir="ltr" lang="he"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dev Tools — DoctorScribe</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}body{background:#0f172a;color:#e2e8f0;font-family:system-ui,sans-serif;min-height:100vh}
.hdr{background:#1e293b;padding:14px 24px;border-bottom:1px solid #334155;display:flex;align-items:center;gap:12px}
.hdr h1{font-size:1.1rem;font-weight:700}.badge{font-size:.68rem;background:#7c3aed;color:#fff;padding:2px 8px;border-radius:999px;letter-spacing:.05em}
.wrap{max-width:860px;margin:0 auto;padding:20px 16px;display:grid;gap:18px}
.card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:18px}
.ct{font-size:.78rem;text-transform:uppercase;letter-spacing:.09em;color:#94a3b8;margin-bottom:14px}
.row{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.dot{width:11px;height:11px;border-radius:50%}.dot-on{background:#22c55e;box-shadow:0 0 7px #22c55e99}.dot-off{background:#ef4444}
.lbl{font-weight:600;font-size:.95rem}
.btn{border:none;border-radius:8px;padding:8px 20px;font-size:.88rem;font-weight:600;cursor:pointer;transition:opacity .15s}.btn:hover{opacity:.82}
.btn-on{background:#22c55e;color:#fff}.btn-off{background:#ef4444;color:#fff}.btn-send{background:#7c3aed;color:#fff}
.btn-clr{background:transparent;color:#ef4444;border:1px solid #ef444455;padding:6px 14px;font-size:.8rem;border-radius:8px;cursor:pointer;margin-left:auto}
.ep{background:#0f172a;border:1px solid #334155;border-radius:7px;padding:9px 13px;font-family:monospace;font-size:.78rem;color:#7dd3fc;word-break:break-all;margin-top:10px}
.msgs{display:flex;flex-direction:column;gap:7px;max-height:400px;overflow-y:auto}
.msg{padding:9px 13px;border-radius:8px;font-size:.86rem;line-height:1.55;border-left:3px solid}
.msg-local{background:#172554;border-color:#3b82f6}.msg-cloud{background:#14532d;border-color:#22c55e}.msg-system{background:#2d1f09;border-color:#f59e0b}
.rb{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-right:6px}
.rb-local{color:#60a5fa}.rb-cloud{color:#4ade80}.rb-system{color:#fbbf24}
.meta{font-size:.7rem;color:#475569;margin-top:3px}.empty{color:#475569;text-align:center;padding:28px;font-size:.86rem}
textarea{width:100%;background:#0f172a;border:1px solid #334155;color:#e2e8f0;border-radius:8px;padding:9px;font-size:.86rem;resize:vertical;min-height:75px}
textarea:focus{outline:none;border-color:#7c3aed}
select{background:#0f172a;border:1px solid #334155;color:#e2e8f0;border-radius:8px;padding:7px 12px;font-size:.86rem}
.fr{display:flex;gap:9px;margin-top:9px;align-items:center}.tsb{font-size:.76rem;color:#475569;margin-left:auto}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}.pls{width:7px;height:7px;border-radius:50%;background:#22c55e;animation:pulse 2s infinite;display:inline-block;margin-right:5px}
</style></head><body>
<div class="hdr">
  <span>&#x1F527;</span>
  <h1>DoctorScribe Dev Tools</h1>
  <span class="badge">INTERNAL</span>
  <span class="tsb"><span class="pls"></span><span id="ts">&#x05D8;&#x05D5;&#x05E2;&#x05DF;...</span></span>
</div>
<div class="wrap">
  <div class="card">
    <div class="ct">Agent Bridge</div>
    <div class="row">
      <div id="dot" class="dot dot-off"></div>
      <span id="lbl" class="lbl">&#x05DB;&#x05D1;&#x05D5;&#x05D9;</span>
      <button id="tbtn" class="btn btn-on" onclick="toggleBridge()">&#x05D4;&#x05D3;&#x05DC;&#x05E7; &#x05D2;&#x05E9;&#x05E8;</button>
    </div>
    <p style="margin-top:10px;font-size:.8rem;color:#64748b">
      &#x05DB;&#x05D0;&#x05E9;&#x05E8; &#x05D4;&#x05D2;&#x05E9;&#x05E8; &#x05E4;&#x05E2;&#x05D9;&#x05DC;, &#x05D4;&#x05E1;&#x05D5;&#x05DB;&#x05DF; &#x05D1;&#x05E2;&#x05E0;&#x05DF; &#x05E9;&#x05D5;&#x05DC;&#x05D7; &#x05E9;&#x05D2;&#x05D9;&#x05D0;&#x05D5;&#x05EA; &#x05D5;&#x05D0;&#x05D9;&#x05E8;&#x05D5;&#x05E2;&#x05D9;&#x05DD; &#x05DC;&#x05DB;&#x05D0;&#x05DF;.<br>
      Copilot &#x05E7;&#x05D5;&#x05E8;&#x05D0; &#x05D4;&#x05D5;&#x05D3;&#x05E2;&#x05D5;&#x05EA; &#x05D0;&#x05DC;&#x05D5; &#x05D1;&#x05EA;&#x05D7;&#x05D9;&#x05DC;&#x05EA; &#x05DB;&#x05DC; &#x05E9;&#x05D9;&#x05D7;&#x05D4;.
    </p>
    <div class="ct" style="margin-top:14px;margin-bottom:6px">Cloud Endpoint (POST with X-Dev-Token header):</div>
    <div class="ep" id="ep">...</div>
  </div>
  <div class="card">
    <div class="ct" style="display:flex;align-items:center">
      &#x05D4;&#x05D5;&#x05D3;&#x05E2;&#x05D5;&#x05EA;
      <button class="btn-clr" onclick="clearMsgs()">&#x05E0;&#x05E7;&#x05D4; &#x05D4;&#x05DB;&#x05DC;</button>
    </div>
    <div id="msgs" class="msgs"><div class="empty">&#x05D0;&#x05D9;&#x05DF; &#x05D4;&#x05D5;&#x05D3;&#x05E2;&#x05D5;&#x05EA;</div></div>
  </div>
  <div class="card">
    <div class="ct">&#x05E9;&#x05DC;&#x05D7; &#x05D4;&#x05D5;&#x05D3;&#x05E2;&#x05D4; &#x05D7;&#x05D3;&#x05E9;&#x05D4;</div>
    <textarea id="inp" placeholder="&#x05DB;&#x05EA;&#x05D5;&#x05D1; &#x05D4;&#x05D5;&#x05D3;&#x05E2;&#x05D4;..."></textarea>
    <div class="fr">
      <select id="role"><option value="local">local (Copilot)</option><option value="system">system</option></select>
      <button class="btn btn-send" onclick="send()">&#x05E9;&#x05DC;&#x05D7;</button>
    </div>
  </div>
</div>
<script>
const BASE=window.location.origin+window.location.pathname.replace(/\/+$/,'');
let TOK=sessionStorage.getItem('dt_token');
(()=>{const p=new URLSearchParams(window.location.search);if(p.get('token')){TOK=p.get('token');sessionStorage.setItem('dt_token',TOK);history.replaceState({},'',window.location.pathname);}})();
const H=()=>({'X-Dev-Token':TOK,'Content-Type':'application/json'});
document.getElementById('ep').textContent=BASE+'/agent/messages';
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
async function loadStatus(){
  try{
    const d=await(await fetch(BASE+'/agent/status',{headers:H()})).json();
    const on=d.enabled;
    document.getElementById('dot').className='dot '+(on?'dot-on':'dot-off');
    document.getElementById('lbl').textContent=on?'\u05E4\u05E2\u05D9\u05DC':'\u05DB\u05D1\u05D5\u05D9';
    const b=document.getElementById('tbtn');
    b.textContent=on?'\u05DB\u05D1\u05D4 \u05D2\u05E9\u05E8':'\u05D4\u05D3\u05DC\u05E7 \u05D2\u05E9\u05E8';
    b.className='btn '+(on?'btn-off':'btn-on');
  }catch(e){}
}
async function toggleBridge(){
  try{
    const d=await(await fetch(BASE+'/agent/status',{headers:H()})).json();
    await fetch(BASE+'/agent/status',{method:'POST',headers:H(),body:JSON.stringify({enabled:!d.enabled})});
    await loadStatus();
  }catch(e){alert('\u05E9\u05D2\u05D9\u05D0\u05D4: '+e);}
}
async function loadMsgs(){
  try{
    const d=await(await fetch(BASE+'/agent/messages',{headers:H()})).json();
    const el=document.getElementById('msgs');
    if(!d.messages||!d.messages.length){el.innerHTML='<div class="empty">\u05D0\u05D9\u05DF \u05D4\u05D5\u05D3\u05E2\u05D5\u05EA</div>';return;}
    el.innerHTML=d.messages.map(m=>`<div class="msg msg-${m.role}"><span class="rb rb-${m.role}">${m.role}</span>${esc(m.content)}<div class="meta">${m.ts}</div></div>`).join('');
  }catch(e){}
}
async function send(){
  const c=document.getElementById('inp').value.trim();
  if(!c)return;
  try{
    await fetch(BASE+'/agent/messages',{method:'POST',headers:H(),body:JSON.stringify({role:document.getElementById('role').value,content:c})});
    document.getElementById('inp').value='';
    await loadMsgs();
  }catch(e){alert('\u05E9\u05D2\u05D9\u05D0\u05D4: '+e);}
}
async function clearMsgs(){
  if(!confirm('\u05DC\u05DE\u05D7\u05D5\u05E7 \u05D0\u05EA \u05DB\u05DC \u05D4\u05D4\u05D5\u05D3\u05E2\u05D5\u05EA?'))return;
  try{await fetch(BASE+'/agent/messages',{method:'DELETE',headers:H()});await loadMsgs();}catch(e){}
}
async function refresh(){
  await Promise.all([loadStatus(),loadMsgs()]);
  document.getElementById('ts').textContent='\u05E2\u05D5\u05D3\u05DB\u05DF: '+new Date().toLocaleTimeString('he-IL');
}
refresh();
setInterval(refresh,30000);
<\/script>
</body></html>"""


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


class MessageIn(BaseModel):
    role: str = Field("local", description="'local', 'cloud', or 'system'")
    content: str = Field(..., min_length=1, max_length=10000)


class BridgeStatusIn(BaseModel):
    enabled: bool


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


@app.get("/", include_in_schema=False)
async def ui(token: Optional[str] = None) -> Response:
    if not token or token != DEV_TOOLS_TOKEN:
        return Response(
            content='<!doctype html><html><body style="background:#0f172a;color:#ef4444;font-family:system-ui;padding:2rem"><h1>401 Unauthorized</h1><p>Add ?token=YOUR_TOKEN to the URL</p></body></html>',
            media_type="text/html; charset=utf-8",
            status_code=401,
        )
    return Response(content=_build_ui_html(), media_type="text/html; charset=utf-8")


@app.get("/agent/status")
async def get_bridge_status(
    x_dev_token: Optional[str] = Header(default=None, alias="X-Dev-Token"),
) -> dict[str, Any]:
    _check_token(x_dev_token)
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            row = conn.execute("SELECT enabled FROM bridge_state WHERE id=1").fetchone()
            return {"enabled": bool(row[0]) if row else False}
        finally:
            conn.close()


@app.post("/agent/status")
async def set_bridge_status(
    body: BridgeStatusIn,
    x_dev_token: Optional[str] = Header(default=None, alias="X-Dev-Token"),
) -> dict[str, Any]:
    _check_token(x_dev_token)
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            conn.execute("UPDATE bridge_state SET enabled=? WHERE id=1", (int(body.enabled),))
            conn.commit()
        finally:
            conn.close()
    return {"enabled": body.enabled}


@app.get("/agent/messages")
async def get_messages(
    limit: int = 50,
    x_dev_token: Optional[str] = Header(default=None, alias="X-Dev-Token"),
) -> dict[str, Any]:
    _check_token(x_dev_token)
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT id, role, content, ts FROM messages ORDER BY id DESC LIMIT ?",
                (min(limit, 200),),
            ).fetchall()
            return {"messages": [dict(r) for r in rows]}
        finally:
            conn.close()


@app.post("/agent/messages")
async def post_message(
    msg: MessageIn,
    x_dev_token: Optional[str] = Header(default=None, alias="X-Dev-Token"),
) -> dict[str, Any]:
    _check_token(x_dev_token)
    if msg.role not in ("local", "cloud", "system"):
        raise HTTPException(status_code=400, detail="role must be: local, cloud, or system")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            cur = conn.execute(
                "INSERT INTO messages(role, content, ts) VALUES(?,?,?)",
                (msg.role, msg.content, ts),
            )
            msg_id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()
    return {"id": msg_id, "ts": ts}


@app.delete("/agent/messages")
async def clear_messages(
    x_dev_token: Optional[str] = Header(default=None, alias="X-Dev-Token"),
) -> dict[str, Any]:
    _check_token(x_dev_token)
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            conn.execute("DELETE FROM messages")
            conn.commit()
        finally:
            conn.close()
    return {"cleared": True}


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
