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

import asyncio
import html as html_lib
import json
import os
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect, Query
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


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, col_def: str) -> None:
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    existing = {c[1] for c in cols}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")


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
            _ensure_column(conn, "messages", "target", "TEXT NOT NULL DEFAULT 'all'")
            _ensure_column(conn, "messages", "acked_by", "TEXT NOT NULL DEFAULT ''")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bridge_state (
                    id      INTEGER PRIMARY KEY CHECK (id = 1),
                    enabled INTEGER NOT NULL DEFAULT 0
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_id ON messages(id)"
            )
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
.fr{display:flex;gap:9px;margin-top:9px;align-items:center;flex-wrap:wrap}.tsb{font-size:.76rem;color:#475569;margin-left:auto}
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
    <div class="ep" id="inbox_ep" style="margin-top:8px">...</div>
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
            <select id="target"><option value="cloud">to: cloud</option><option value="all">to: all</option><option value="local">to: local</option></select>
      <button class="btn btn-send" onclick="send()">&#x05E9;&#x05DC;&#x05D7;</button>
    </div>
  </div>
</div>
<script>
const BASE=window.location.origin+window.location.pathname.replace(/\/+$/,'');
const SELF='local';
let TOK=sessionStorage.getItem('dt_token');
(()=>{const p=new URLSearchParams(window.location.search);if(p.get('token')){TOK=p.get('token');sessionStorage.setItem('dt_token',TOK);history.replaceState({},'',window.location.pathname);}})();
const H=()=>({'X-Dev-Token':TOK,'Content-Type':'application/json'});
document.getElementById('ep').textContent=BASE+'/agent/messages';
document.getElementById('inbox_ep').textContent='Inbox: '+BASE+'/agent/messages?inbox_for='+SELF+'&only_unacked_for='+SELF;
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
        const d=await(await fetch(BASE+'/agent/messages?inbox_for='+SELF,{headers:H()})).json();
    const el=document.getElementById('msgs');
    if(!d.messages||!d.messages.length){el.innerHTML='<div class="empty">\u05D0\u05D9\u05DF \u05D4\u05D5\u05D3\u05E2\u05D5\u05EA</div>';return;}
        el.innerHTML=d.messages.map(m=>`<div class="msg msg-${m.role}"><span class="rb rb-${m.role}">${m.role}</span>${esc(m.content)}<div class="meta">#${m.id} | to:${m.target||'all'} | ${m.ts}${m.acked_by?(' | ack:'+m.acked_by):''}</div></div>`).join('');
  }catch(e){}
}
async function send(){
  const c=document.getElementById('inp').value.trim();
  if(!c)return;
  try{
        await fetch(BASE+'/agent/messages',{method:'POST',headers:H(),body:JSON.stringify({role:document.getElementById('role').value,target:document.getElementById('target').value,content:c})});
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
    target: str = Field("all", description="'local', 'cloud', or 'all'")
    content: str = Field(..., min_length=1, max_length=10000)


class AckIn(BaseModel):
    by: str = Field(..., description="'local' or 'cloud'")


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
    since_id: int = 0,
    inbox_for: Optional[str] = None,
    only_unacked_for: Optional[str] = None,
    x_dev_token: Optional[str] = Header(default=None, alias="X-Dev-Token"),
) -> dict[str, Any]:
    _check_token(x_dev_token)
    if inbox_for not in (None, "local", "cloud"):
        raise HTTPException(status_code=400, detail="inbox_for must be: local or cloud")
    if only_unacked_for not in (None, "local", "cloud"):
        raise HTTPException(status_code=400, detail="only_unacked_for must be: local or cloud")

    filters = ["id > ?"]
    params: list[Any] = [max(0, since_id)]
    if inbox_for:
        filters.append("target IN (?, 'all')")
        params.append(inbox_for)
        # Inbox should show messages from the other side (not self-authored)
        filters.append("role != ?")
        params.append(inbox_for)
    if only_unacked_for:
        filters.append("acked_by NOT LIKE ?")
        params.append(f"%,{only_unacked_for},%")

    where_sql = " AND ".join(filters)
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                f"SELECT id, role, target, content, ts, acked_by "
                f"FROM messages WHERE {where_sql} ORDER BY id DESC LIMIT ?",
                (*params, min(limit, 200)),
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
    if msg.target not in ("local", "cloud", "all"):
        raise HTTPException(status_code=400, detail="target must be: local, cloud, or all")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            cur = conn.execute(
                "INSERT INTO messages(role, target, content, ts, acked_by) VALUES(?,?,?,?,?)",
                (msg.role, msg.target, msg.content, ts, ""),
            )
            msg_id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()
    return {"id": msg_id, "ts": ts, "target": msg.target}


@app.post("/agent/messages/{message_id}/ack")
async def ack_message(
    message_id: int,
    body: AckIn,
    x_dev_token: Optional[str] = Header(default=None, alias="X-Dev-Token"),
) -> dict[str, Any]:
    _check_token(x_dev_token)
    if body.by not in ("local", "cloud"):
        raise HTTPException(status_code=400, detail="by must be: local or cloud")

    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT id, acked_by FROM messages WHERE id=?",
                (message_id,),
            ).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="message not found")

            current = row["acked_by"] or ""
            marker = f",{body.by},"
            normalized = current if current.startswith(",") else f",{current.strip(',')},"
            if normalized == ",,":
                normalized = ","
            if marker not in normalized:
                normalized = f"{normalized}{body.by},"
            conn.execute(
                "UPDATE messages SET acked_by=? WHERE id=?",
                (normalized, message_id),
            )
            conn.commit()
            return {"id": message_id, "acked_by": normalized}
        finally:
            conn.close()


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


# ── CPanel: real-time agent chat over WebSocket (TCP-over-TLS) ───────────────
class ChatHub:
    """In-memory broadcast hub for connected agents/viewers."""

    def __init__(self) -> None:
        self.connections: list[tuple[str, WebSocket]] = []
        self.lock = asyncio.Lock()

    async def add(self, role: str, ws: WebSocket) -> None:
        async with self.lock:
            self.connections.append((role, ws))

    async def remove(self, ws: WebSocket) -> None:
        async with self.lock:
            self.connections = [(r, w) for (r, w) in self.connections if w is not ws]

    async def broadcast(self, payload: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        async with self.lock:
            conns = list(self.connections)
        for _role, ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        if dead:
            async with self.lock:
                self.connections = [(r, w) for (r, w) in self.connections if w not in dead]

    async def roster(self) -> dict[str, int]:
        async with self.lock:
            counts: dict[str, int] = {}
            for role, _ws in self.connections:
                counts[role] = counts.get(role, 0) + 1
            return counts


hub = ChatHub()


def _bridge_enabled() -> bool:
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            row = conn.execute("SELECT enabled FROM bridge_state WHERE id=1").fetchone()
            return bool(row[0]) if row else False
        finally:
            conn.close()


def _save_chat_message(role: str, target: str, content: str, ts: str) -> int:
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            cur = conn.execute(
                "INSERT INTO messages(role, target, content, ts, acked_by) VALUES(?,?,?,?,?)",
                (role, target, content, ts, ""),
            )
            conn.commit()
            return int(cur.lastrowid or 0)
        finally:
            conn.close()


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _build_cpanel_html() -> str:
    return """<!DOCTYPE html>
<html lang="he" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DrScribe CPanel \u2014 Agent Chat</title>
<style>
  :root{color-scheme:dark}
  *{box-sizing:border-box}
  body{margin:0;background:#0b1020;color:#e2e8f0;font-family:system-ui,'Segoe UI',Arial;display:flex;flex-direction:column;height:100vh}
  header{background:#111827;padding:.75rem 1rem;border-bottom:1px solid #1f2937;display:flex;align-items:center;gap:1rem;flex-wrap:wrap}
  header h1{font-size:1rem;margin:0;color:#93c5fd}
  .pill{padding:.2rem .55rem;border-radius:999px;font-size:.75rem;background:#1e293b;color:#cbd5e1}
  .pill.on{background:#064e3b;color:#6ee7b7}
  .pill.off{background:#7f1d1d;color:#fca5a5}
  button{cursor:pointer;border:0;padding:.45rem .9rem;border-radius:6px;font-weight:600;font-size:.85rem}
  button.toggle{background:#2563eb;color:white}
  button.toggle.off{background:#dc2626}
  button.send{background:#16a34a;color:white}
  #log{flex:1;overflow-y:auto;padding:1rem;display:flex;flex-direction:column;gap:.5rem}
  .msg{padding:.55rem .8rem;border-radius:8px;max-width:75%;line-height:1.4;word-wrap:break-word;white-space:pre-wrap}
  .msg.local{background:#1e3a8a;align-self:flex-end}
  .msg.cloud{background:#065f46;align-self:flex-start}
  .msg.system{background:#374151;align-self:center;font-size:.8rem;opacity:.8}
  .meta{font-size:.7rem;opacity:.7;margin-top:.2rem}
  footer{background:#111827;padding:.75rem;border-top:1px solid #1f2937;display:flex;gap:.5rem}
  #input{flex:1;background:#1e293b;color:#e2e8f0;border:1px solid #334155;border-radius:6px;padding:.55rem;font-family:inherit;font-size:.9rem;resize:none;min-height:2.5rem;max-height:8rem}
  #status{font-size:.75rem;color:#94a3b8}
  select{background:#1e293b;color:#e2e8f0;border:1px solid #334155;border-radius:6px;padding:.4rem}
</style></head><body>
<header>
  <h1>\U0001F91D DrScribe CPanel \u2014 Agent Chat</h1>
  <span id="bridgePill" class="pill">\u05d8\u05d5\u05e2\u05df...</span>
  <span id="connPill" class="pill off">WS \u05de\u05e0\u05d5\u05ea\u05e7</span>
  <span id="rosterPill" class="pill">\u05d0\u05d9\u05df \u05de\u05e9\u05ea\u05ea\u05e4\u05d9\u05dd</span>
  <button id="toggleBtn" class="toggle">\u2699\ufe0f \u05d4\u05d3\u05dc\u05e7\u05ea \u05e9\u05d9\u05e8\u05d5\u05ea</button>
  <select id="role"><option value="viewer">Viewer</option><option value="local">Local</option><option value="cloud">Cloud</option></select>
  <button id="connectBtn" class="toggle">\U0001F50C \u05d4\u05ea\u05d7\u05d1\u05e8\u05d5\u05ea</button>
  <span id="status"></span>
</header>
<div id="log"></div>
<footer>
  <textarea id="input" placeholder="\u05db\u05ea\u05d5\u05d1 \u05d4\u05d5\u05d3\u05e2\u05d4 (Enter \u05dc\u05e9\u05dc\u05d9\u05d7\u05d4, Shift+Enter \u05dc\u05e9\u05d5\u05e8\u05d4 \u05d7\u05d3\u05e9\u05d4)"></textarea>
  <button class="send" id="sendBtn">\u05e9\u05dc\u05d7</button>
</footer>
<script>
const params = new URLSearchParams(location.search);
const TOKEN = params.get('token') || '';
if (!TOKEN) { document.body.innerHTML = '<h1 style=\"padding:2rem;color:#ef4444\">401 \u2014 \u05d4\u05d5\u05e1\u05e3 ?token=YOUR_TOKEN \u05dc-URL</h1>'; throw new Error('no token'); }

const log = document.getElementById('log');
const input = document.getElementById('input');
const sendBtn = document.getElementById('sendBtn');
const toggleBtn = document.getElementById('toggleBtn');
const connectBtn = document.getElementById('connectBtn');
const roleSel = document.getElementById('role');
const bridgePill = document.getElementById('bridgePill');
const connPill = document.getElementById('connPill');
const rosterPill = document.getElementById('rosterPill');
const statusEl = document.getElementById('status');

let ws = null;
let bridgeOn = false;
const API_BASE = location.pathname.includes('/dev-tools/') ? '/dev-tools' : '';

function append(m){
  const d = document.createElement('div');
  const cls = m.role || (m.type === 'system' ? 'system' : 'local');
  d.className = 'msg ' + cls;
  const target = m.target && m.target !== 'all' ? ' \u2192 ' + m.target : '';
  d.innerHTML = '<div>'+escapeHtml(m.content||'')+'</div><div class=\"meta\">'+(m.role||m.type||'')+target+' \u00b7 '+(m.ts||'')+'</div>';
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
}
function escapeHtml(s){return s.replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c]))}

async function loadStatus(){
  const r = await fetch(API_BASE+'/agent/status', {headers:{'X-Dev-Token':TOKEN}});
  const j = await r.json();
  bridgeOn = !!j.enabled;
  bridgePill.textContent = bridgeOn ? '\u05d2\u05e9\u05e8 \u05e4\u05e2\u05d9\u05dc' : '\u05d2\u05e9\u05e8 \u05db\u05d1\u05d5\u05d9';
  bridgePill.className = 'pill ' + (bridgeOn ? 'on' : 'off');
  toggleBtn.textContent = bridgeOn ? '\u23fb \u05db\u05d9\u05d1\u05d5\u05d9 \u05e9\u05d9\u05e8\u05d5\u05ea' : '\u2699\ufe0f \u05d4\u05d3\u05dc\u05e7\u05ea \u05e9\u05d9\u05e8\u05d5\u05ea';
  toggleBtn.className = 'toggle' + (bridgeOn ? ' off' : '');
}
async function toggleBridge(){
  const r = await fetch(API_BASE+'/agent/status', {method:'POST',headers:{'X-Dev-Token':TOKEN,'Content-Type':'application/json'},body:JSON.stringify({enabled:!bridgeOn})});
  await r.json();
  await loadStatus();
}
async function loadHistory(){
  const r = await fetch(API_BASE+'/agent/messages?limit=50', {headers:{'X-Dev-Token':TOKEN}});
  const j = await r.json();
  log.innerHTML = '';
  (j.messages||[]).forEach(append);
}

function connect(){
  if (ws) { try{ws.close()}catch(e){} ws=null; }
  const role = roleSel.value;
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const url = proto + '//' + location.host + location.pathname.replace(/\\/$/,'') + '/ws?role=' + encodeURIComponent(role) + '&token=' + encodeURIComponent(TOKEN);
  ws = new WebSocket(url);
  ws.onopen = () => { connPill.textContent='WS \u05de\u05d7\u05d5\u05d1\u05e8 ('+role+')'; connPill.className='pill on'; };
  ws.onclose = (e) => { connPill.textContent='WS \u05de\u05e0\u05d5\u05ea\u05e7 ('+e.code+')'; connPill.className='pill off'; };
  ws.onerror = () => { connPill.textContent='WS \u05e9\u05d2\u05d9\u05d0\u05d4'; connPill.className='pill off'; };
  ws.onmessage = (e) => {
    try{
      const m = JSON.parse(e.data);
      if (m.type === 'roster') { rosterPill.textContent = 'local:'+(m.counts.local||0)+' cloud:'+(m.counts.cloud||0)+' viewer:'+(m.counts.viewer||0); return; }
      append(m);
    }catch(err){console.warn(err)}
  };
}

function send(){
  const text = input.value.trim();
  if (!text || !ws || ws.readyState !== 1) return;
  ws.send(JSON.stringify({content:text,target:'all'}));
  input.value = '';
}

input.addEventListener('keydown',e=>{ if(e.key==='Enter' && !e.shiftKey){e.preventDefault();send();}});
sendBtn.onclick = send;
toggleBtn.onclick = toggleBridge;
connectBtn.onclick = connect;

(async()=>{ await loadStatus(); await loadHistory(); })();
setInterval(loadStatus, 15000);
</script>
</body></html>"""


@app.get("/agent-chat", include_in_schema=False)
@app.get("/agent-chat/", include_in_schema=False)
async def cpanel_ui(token: Optional[str] = None) -> Response:
    if not token or token != DEV_TOOLS_TOKEN:
        return Response(
            content='<!doctype html><html><body style="background:#0f172a;color:#ef4444;font-family:system-ui;padding:2rem"><h1>401 Unauthorized</h1><p>Add ?token=YOUR_TOKEN to the URL</p></body></html>',
            media_type="text/html; charset=utf-8",
            status_code=401,
        )
    return Response(content=_build_cpanel_html(), media_type="text/html; charset=utf-8")


@app.websocket("/agent-chat/ws")
async def cpanel_ws(
    websocket: WebSocket,
    role: str = Query("viewer"),
    token: str = Query(""),
) -> None:
    if token != DEV_TOOLS_TOKEN:
        await websocket.close(code=4401)
        return
    if role not in ("local", "cloud", "viewer"):
        await websocket.close(code=4400)
        return
    if not _bridge_enabled():
        await websocket.accept()
        await websocket.send_json({
            "type": "system",
            "content": "Bridge is OFF. Toggle it ON in /agent-chat before chatting.",
            "ts": _now_utc(),
        })
        await websocket.close(code=4403)
        return

    await websocket.accept()
    await hub.add(role, websocket)
    join_msg = {"type": "system", "content": f"{role} connected", "ts": _now_utc()}
    await hub.broadcast(join_msg)
    await hub.broadcast({"type": "roster", "counts": await hub.roster()})

    try:
        while True:
            data = await websocket.receive_json()
            content = str(data.get("content", "")).strip()
            if not content:
                continue
            target = str(data.get("target", "all"))
            if target not in ("local", "cloud", "all"):
                target = "all"
            ts = _now_utc()
            msg_id = _save_chat_message(role, target, content, ts)
            await hub.broadcast({
                "type": "msg",
                "id": msg_id,
                "role": role,
                "target": target,
                "content": content,
                "ts": ts,
            })
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_json({"type": "system", "content": f"error: {exc}", "ts": _now_utc()})
        except Exception:
            pass
    finally:
        await hub.remove(websocket)
        await hub.broadcast({"type": "system", "content": f"{role} disconnected", "ts": _now_utc()})
        await hub.broadcast({"type": "roster", "counts": await hub.roster()})
