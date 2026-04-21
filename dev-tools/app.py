"""
DoctorScribe Dev-Tools service.

Endpoints:
  POST /capture/screenshot  -> PNG of the full page
  POST /capture/flatten     -> Single self-contained HTML snapshot
  GET  /health              -> Liveness check
  GET  /cpanel              -> Real-time agent chat UI (WebSocket browser viewer)
  WS   /cpanel/ws           -> WebSocket for browser (viewer/local/cloud)
  TCP  :9090                -> Raw TCP socket for Copilot agents (local/cloud)

Auth: X-Dev-Token header or ?token= query param.
TCP:  First line JSON: {"token":"xxx","role":"local"}
"""
from __future__ import annotations

import asyncio
import html as html_lib
import json
import os
import sqlite3
import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

DEV_TOOLS_TOKEN = os.getenv("DEV_TOOLS_TOKEN", "dev-token-change-me")
TCP_PORT = int(os.getenv("CHAT_TCP_PORT", "9090"))
DEFAULT_VIEWPORT_W = 1440
DEFAULT_VIEWPORT_H = 900
NAV_TIMEOUT_MS = 45_000

FLATTEN_JS = (Path(__file__).parent / "flatten.js").read_text(encoding="utf-8")

# ── Persistent message store (SQLite) ────────────────────────────────────────
DB_PATH = Path(os.getenv("BRIDGE_DB_PATH", "/tmp/agent_bridge.db"))
_db_lock = threading.Lock()


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, col_def: str) -> None:
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    if column not in {c[1] for c in cols}:
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
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_id ON messages(id)")
            conn.execute("INSERT OR IGNORE INTO bridge_state(id, enabled) VALUES(1, 0)")
            conn.commit()
        finally:
            conn.close()


_init_db()


# ── Real-time Hub: WebSocket + TCP ───────────────────────────────────────────

class TcpConn:
    """One connected TCP agent."""
    __slots__ = ("role", "writer")

    def __init__(self, role: str, writer: asyncio.StreamWriter) -> None:
        self.role = role
        self.writer = writer

    async def send_json(self, payload: dict[str, Any]) -> bool:
        try:
            self.writer.write((json.dumps(payload) + "\n").encode())
            await self.writer.drain()
            return True
        except Exception:
            return False


class ChatHub:
    """Broadcast hub for both WebSocket (browser) and TCP (Copilot) clients."""

    def __init__(self) -> None:
        self._ws: list[tuple[str, WebSocket]] = []
        self._tcp: list[TcpConn] = []
        self._lock = asyncio.Lock()

    # ── registration ─────────────────────────────────────────────────────────
    async def add_ws(self, role: str, ws: WebSocket) -> None:
        async with self._lock:
            self._ws.append((role, ws))

    async def remove_ws(self, ws: WebSocket) -> None:
        async with self._lock:
            self._ws = [(r, w) for r, w in self._ws if w is not ws]

    async def add_tcp(self, tc: TcpConn) -> None:
        async with self._lock:
            self._tcp.append(tc)

    async def remove_tcp(self, tc: TcpConn) -> None:
        async with self._lock:
            self._tcp = [c for c in self._tcp if c is not tc]

    # ── broadcast ─────────────────────────────────────────────────────────────
    async def broadcast(self, payload: dict[str, Any]) -> None:
        dead_ws: list[WebSocket] = []
        dead_tcp: list[TcpConn] = []

        async with self._lock:
            ws_snap = list(self._ws)
            tcp_snap = list(self._tcp)

        for _, ws in ws_snap:
            try:
                await ws.send_json(payload)
            except Exception:
                dead_ws.append(ws)

        for tc in tcp_snap:
            if not await tc.send_json(payload):
                dead_tcp.append(tc)

        if dead_ws or dead_tcp:
            async with self._lock:
                if dead_ws:
                    self._ws = [(r, w) for r, w in self._ws if w not in dead_ws]
                if dead_tcp:
                    self._tcp = [c for c in self._tcp if c not in dead_tcp]

    async def roster(self) -> dict[str, int]:
        async with self._lock:
            counts: dict[str, int] = {}
            for role, _ in self._ws:
                counts[role] = counts.get(role, 0) + 1
            for tc in self._tcp:
                counts[tc.role] = counts.get(tc.role, 0) + 1
            return counts


hub = ChatHub()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _bridge_enabled() -> bool:
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            row = conn.execute("SELECT enabled FROM bridge_state WHERE id=1").fetchone()
            return bool(row[0]) if row else False
        finally:
            conn.close()


def _save_message(role: str, target: str, content: str, ts: str) -> int:
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            cur = conn.execute(
                "INSERT INTO messages(role,target,content,ts,acked_by) VALUES(?,?,?,?,'')",
                (role, target, content, ts),
            )
            conn.commit()
            return int(cur.lastrowid or 0)
        finally:
            conn.close()


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


# ── TCP server ────────────────────────────────────────────────────────────────

async def _tcp_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    tc: Optional[TcpConn] = None
    try:
        raw = await asyncio.wait_for(reader.readline(), timeout=15.0)
        if not raw:
            return
        try:
            auth = json.loads(raw.decode().strip())
        except Exception:
            writer.write(b'{"type":"error","content":"Expected JSON auth line"}\n')
            await writer.drain()
            return

        if auth.get("token") != DEV_TOOLS_TOKEN:
            writer.write(b'{"type":"error","content":"Unauthorized"}\n')
            await writer.drain()
            return

        role = str(auth.get("role", "local"))
        if role not in ("local", "cloud", "viewer"):
            role = "local"

        if not _bridge_enabled():
            writer.write(b'{"type":"error","content":"Bridge is OFF - enable it in /cpanel"}\n')
            await writer.drain()
            return

        tc = TcpConn(role, writer)
        await hub.add_tcp(tc)
        await tc.send_json({"type": "welcome", "role": role, "ts": _now_utc(),
                            "hint": "Send JSON lines: {\"content\":\"hello\",\"target\":\"all\"}"})
        await hub.broadcast({"type": "system", "content": f"{role} connected (TCP:{TCP_PORT})", "ts": _now_utc()})
        await hub.broadcast({"type": "roster", "counts": await hub.roster()})

        async for raw_line in reader:
            line = raw_line.decode().strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                content = str(data.get("content", "")).strip()
                target = str(data.get("target", "all"))
            except (json.JSONDecodeError, ValueError):
                content = line[:5000]
                target = "all"

            if not content:
                continue
            if target not in ("local", "cloud", "all"):
                target = "all"

            ts = _now_utc()
            msg_id = _save_message(role, target, content, ts)
            await hub.broadcast({"type": "msg", "id": msg_id, "role": role,
                                 "target": target, "content": content, "ts": ts})

    except (asyncio.TimeoutError, asyncio.IncompleteReadError, ConnectionResetError, BrokenPipeError):
        pass
    except Exception:
        pass
    finally:
        if tc:
            await hub.remove_tcp(tc)
            await hub.broadcast({"type": "system", "content": f"{tc.role} disconnected", "ts": _now_utc()})
            await hub.broadcast({"type": "roster", "counts": await hub.roster()})
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


async def _run_tcp_server() -> None:
    server = await asyncio.start_server(_tcp_handler, "0.0.0.0", TCP_PORT)
    addrs = [s.getsockname() for s in server.sockets]
    print(f"[chat] TCP server ready on {addrs}", flush=True)
    async with server:
        await server.serve_forever()


# ── CPanel HTML ───────────────────────────────────────────────────────────────

def _build_cpanel_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DrScribe CPanel — Agent Chat</title>
<style>
:root{color-scheme:dark}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#070d1a;color:#e2e8f0;font-family:'Segoe UI',system-ui,sans-serif;height:100vh;display:flex;flex-direction:column;overflow:hidden}
header{background:#111827;padding:10px 18px;border-bottom:1px solid #1e293b;display:flex;align-items:center;gap:8px;flex-wrap:wrap;flex-shrink:0}
h1{font-size:.95rem;font-weight:700;color:#93c5fd;margin-left:4px}
.pill{padding:2px 10px;border-radius:999px;font-size:.72rem;font-weight:600;white-space:nowrap}
.on{background:#064e3b;color:#6ee7b7}.off{background:#4c0519;color:#fda4af}.ok{background:#1e3a8a;color:#93c5fd}
.btn{cursor:pointer;border:0;border-radius:6px;padding:6px 14px;font-size:.82rem;font-weight:600;white-space:nowrap}
.bg{background:#16a34a;color:#fff}.br{background:#dc2626;color:#fff}.bb{background:#2563eb;color:#fff}.bv{background:#7c3aed;color:#fff}
select{background:#1e293b;color:#e2e8f0;border:1px solid #334155;border-radius:6px;padding:5px 9px;font-size:.82rem}
#log{flex:1;overflow-y:auto;padding:12px 16px;display:flex;flex-direction:column;gap:5px}
.msg{padding:7px 11px;border-radius:8px;max-width:78%;font-size:.86rem;line-height:1.5;word-break:break-word;white-space:pre-wrap}
.msg.local{background:#1e3a8a;align-self:flex-end;border-bottom-right-radius:2px}
.msg.cloud{background:#14532d;align-self:flex-start;border-bottom-left-radius:2px}
.msg.system{background:#1e293b;align-self:center;font-size:.74rem;opacity:.7;max-width:100%;text-align:center;border-radius:4px}
.msg.viewer{background:#292524;align-self:center}
.lbl{font-size:.67rem;font-weight:700;text-transform:uppercase;opacity:.65;display:block;margin-bottom:2px}
.ts{font-size:.65rem;opacity:.45;display:block;margin-top:3px}
footer{background:#111827;padding:9px 14px;border-top:1px solid #1e293b;display:flex;gap:7px;align-items:flex-end;flex-shrink:0}
textarea{flex:1;background:#1e293b;color:#e2e8f0;border:1px solid #334155;border-radius:7px;padding:8px 10px;font-size:.86rem;resize:none;min-height:38px;max-height:110px;font-family:inherit;line-height:1.4}
textarea:focus{outline:none;border-color:#7c3aed}
.empty{text-align:center;color:#334155;padding:48px 0;font-size:.85rem;flex:1;display:flex;align-items:center;justify-content:center}
</style>
</head>
<body>
<header>
  <h1>&#x1F91D; DrScribe &mdash; Agent Chat</h1>
  <span id="bPill" class="pill off">Bridge &#x05DB;&#x05D1;&#x05D5;&#x05D9;</span>
  <span id="wPill" class="pill off">WS &#x05DE;&#x05E0;&#x05D5;&#x05EA;&#x05E7;</span>
  <span id="rPill" class="pill" style="background:#1e293b;color:#64748b">&#x05D0;&#x05D9;&#x05DF; &#x05E1;&#x05D5;&#x05DB;&#x05E0;&#x05D9;&#x05DD;</span>
  <button id="tBtn" class="btn bg" onclick="toggleBridge()">&#x26A1; &#x05D4;&#x05D3;&#x05DC;&#x05E7; Bridge</button>
  <select id="roleSel"><option value="viewer">Viewer</option><option value="local">Local</option><option value="cloud">Cloud</option></select>
  <button class="btn bb" onclick="connect()">&#x1F50C; &#x05D4;&#x05EA;&#x05D7;&#x05D1;&#x05E8;</button>
  <button class="btn" style="background:#334155;color:#94a3b8;font-size:.75rem" onclick="clearLog()">&#x05E0;&#x05E7;&#x05D4;</button>
</header>
<div id="log"><div class="empty">&#x05D0;&#x05D9;&#x05DF; &#x05D4;&#x05D5;&#x05D3;&#x05E2;&#x05D5;&#x05EA; &mdash; &#x05D4;&#x05D3;&#x05DC;&#x05E7; Bridge &#x05D5;&#x05DC;&#x05D7;&#x05E5; &#x05D4;&#x05EA;&#x05D7;&#x05D1;&#x05E8;</div></div>
<footer>
  <textarea id="inp" placeholder="&#x05DB;&#x05EA;&#x05D5;&#x05D1; &#x05D4;&#x05D5;&#x05D3;&#x05E2;&#x05D4; (Enter &#x05DC;&#x05E9;&#x05DC;&#x05D9;&#x05D7;&#x05D4;, Shift+Enter &#x05DC;&#x05E9;&#x05D5;&#x05E8;&#x05D4; &#x05D7;&#x05D3;&#x05E9;&#x05D4;)" onkeydown="onKey(event)"></textarea>
  <button class="btn bv" onclick="send()">&#x05E9;&#x05DC;&#x05D7;</button>
</footer>
<script>
const P=new URLSearchParams(location.search);
const TOK=P.get('token')||'';
if(!TOK){document.body.innerHTML='<h1 style="padding:2rem;color:#ef4444">401 \u2014 \u05d4\u05d5\u05e1\u05e3 ?token=TOKEN</h1>';throw 0;}
const BASE=location.origin;
const WS_BASE=(location.protocol==='https:'?'wss':'ws')+'://'+location.host;
let ws=null,bridgeOn=false;

function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}

function append(m){
  const log=document.getElementById('log');
  const emp=log.querySelector('.empty');if(emp)emp.remove();
  const d=document.createElement('div');
  const cls=(m.role&&['local','cloud','system','viewer'].includes(m.role))?m.role:(m.type==='system'?'system':'local');
  d.className='msg '+cls;
  const tgt=m.target&&m.target!=='all'?' \u2192 '+m.target:'';
  if(cls!=='system')d.innerHTML='<span class="lbl">'+esc(cls)+tgt+'</span>';
  d.innerHTML+='<span>'+esc(m.content||'')+'</span><span class="ts">'+(m.ts||'')+(m.id?' #'+m.id:'')+'</span>';
  log.appendChild(d);log.scrollTop=log.scrollHeight;
}

async function loadStatus(){
  try{
    const j=await(await fetch(BASE+'/dev-tools/agent/status',{headers:{'X-Dev-Token':TOK}})).json();
    bridgeOn=!!j.enabled;
    const bp=document.getElementById('bPill');
    bp.textContent=bridgeOn?'Bridge \u05e4\u05e2\u05d9\u05dc':'Bridge \u05db\u05d1\u05d5\u05d9';
    bp.className='pill '+(bridgeOn?'on':'off');
    const tb=document.getElementById('tBtn');
    tb.textContent=bridgeOn?'\u23f9 \u05db\u05d1\u05d4 Bridge':'\u26a1 \u05d4\u05d3\u05dc\u05e7 Bridge';
    tb.className='btn '+(bridgeOn?'br':'bg');
  }catch(e){}
}

async function toggleBridge(){
  try{
    await fetch(BASE+'/dev-tools/agent/status',{method:'POST',headers:{'X-Dev-Token':TOK,'Content-Type':'application/json'},body:JSON.stringify({enabled:!bridgeOn})});
    await loadStatus();
  }catch(e){alert('\u05e9\u05d2\u05d9\u05d0\u05d4: '+e);}
}

function connect(){
  if(ws){try{ws.close()}catch(e){}ws=null;}
  const role=document.getElementById('roleSel').value;
  const url=WS_BASE+'/dev-tools/chat/ws?role='+encodeURIComponent(role)+'&token='+encodeURIComponent(TOK);
  const wp=document.getElementById('wPill');
  wp.textContent='WS \u05de\u05ea\u05d7\u05d1\u05e8...';wp.className='pill';
  ws=new WebSocket(url);
  ws.onopen=()=>{wp.textContent='WS \u05de\u05d7\u05d5\u05d1\u05e8 ('+role+')';wp.className='pill ok';};
  ws.onclose=e=>{wp.textContent='WS \u05de\u05e0\u05d5\u05ea\u05e7 ('+e.code+')';wp.className='pill off';};
  ws.onerror=()=>{wp.textContent='WS \u05e9\u05d2\u05d9\u05d0\u05d4';wp.className='pill off';};
  ws.onmessage=e=>{
    try{
      const m=JSON.parse(e.data);
      if(m.type==='roster'){
        const c=m.counts||{};
        document.getElementById('rPill').textContent='local:'+(c.local||0)+' cloud:'+(c.cloud||0)+' viewer:'+(c.viewer||0);
        return;
      }
      append(m);
    }catch(err){}
  };
}

function send(){
  const inp=document.getElementById('inp');
  const text=inp.value.trim();
  if(!text||!ws||ws.readyState!==1)return;
  ws.send(JSON.stringify({content:text,target:'all'}));
  inp.value='';
}
function onKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}}
function clearLog(){document.getElementById('log').innerHTML='<div class="empty">\u05e0\u05e7\u05d4</div>';}

loadStatus();
setInterval(loadStatus,15000);
// Auto-connect as viewer on load
setTimeout(()=>connect(),300);
</script>
</body>
</html>"""


# ── FastAPI app ───────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app_: FastAPI):
    asyncio.create_task(_run_tcp_server())
    yield


app = FastAPI(title="DoctorScribe Dev-Tools", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


def _check_token(token: Optional[str]) -> None:
    if not token or token != DEV_TOOLS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid dev-tools token")


# ── Pydantic models ───────────────────────────────────────────────────────────

class BridgeStatusIn(BaseModel):
    enabled: bool


class CaptureRequest(BaseModel):
    url: str = Field(..., description="Absolute URL to capture")
    viewport_width: int = Field(DEFAULT_VIEWPORT_W, ge=320, le=4000)
    viewport_height: int = Field(DEFAULT_VIEWPORT_H, ge=240, le=4000)
    wait_ms: int = Field(2500, ge=0, le=30_000)
    auth_token: Optional[str] = Field(None)
    full_page: bool = Field(True)
    cookies: Optional[list[dict[str, Any]]] = Field(default=None)
    locale: str = Field("he-IL")


# ── Capture helpers ───────────────────────────────────────────────────────────

async def _render_page(req: CaptureRequest):
    from playwright.async_api import async_playwright

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
    console_errors: list[str] = []
    page.on("pageerror", lambda exc: console_errors.append(f"PAGEERROR: {exc}"))
    page.on("console", lambda msg: console_errors.append(f"{msg.type.upper()}: {msg.text}") if msg.type in ("error", "warning") else None)

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
            try:
                api_resp = await route.request.frame.page.context.request.fetch(
                    new_url, method=route.request.method,
                    headers=route.request.headers, data=route.request.post_data,
                )
                body = await api_resp.body()
                await route.fulfill(status=api_resp.status, headers=dict(api_resp.headers), body=body)
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
        await context.add_init_script(
            f"window.localStorage.setItem('access_token', {json.dumps(req.auth_token)});"
        )
        await page.set_extra_http_headers({"Authorization": f"Bearer {req.auth_token}"})

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


def _esc(s: str) -> str:
    return html_lib.escape(s or "", quote=True)


def _build_flat_html(snapshot: dict[str, Any]) -> str:
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


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "service": "dev-tools", "tcp_port": TCP_PORT, "ts": int(time.time())}


# ── Bridge state ──────────────────────────────────────────────────────────────

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


# ── Chat history (read-only, for UI reload) ───────────────────────────────────

@app.get("/agent/messages")
async def get_messages(
    limit: int = 100,
    since_id: int = 0,
    x_dev_token: Optional[str] = Header(default=None, alias="X-Dev-Token"),
) -> dict[str, Any]:
    _check_token(x_dev_token)
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT id,role,target,content,ts FROM messages WHERE id>? ORDER BY id DESC LIMIT ?",
                (max(0, since_id), min(limit, 500)),
            ).fetchall()
            return {"messages": [dict(r) for r in rows]}
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


# ── CPanel UI ─────────────────────────────────────────────────────────────────

@app.get("/chat", include_in_schema=False)
@app.get("/chat/", include_in_schema=False)
async def chat_ui(token: Optional[str] = None) -> Response:
    if not token or token != DEV_TOOLS_TOKEN:
        return Response(
            content='<!doctype html><html><body style="background:#070d1a;color:#ef4444;font-family:system-ui;padding:2rem"><h1>401</h1><p>Add ?token=YOUR_TOKEN</p></body></html>',
            media_type="text/html; charset=utf-8",
            status_code=401,
        )
    return Response(content=_build_cpanel_html(), media_type="text/html; charset=utf-8")


# ── Chat WebSocket (browser viewer) ──────────────────────────────────────────

@app.websocket("/chat/ws")
async def cpanel_ws(
    websocket: WebSocket,
    role: str = Query("viewer"),
    token: str = Query(""),
) -> None:
    if token != DEV_TOOLS_TOKEN:
        await websocket.close(code=4401)
        return
    if role not in ("local", "cloud", "viewer"):
        role = "viewer"

    if not _bridge_enabled():
        await websocket.accept()
        await websocket.send_json({
            "type": "system",
            "content": "Bridge is OFF — click the toggle to enable it.",
            "ts": _now_utc(),
        })
        await websocket.close(code=4403)
        return

    await websocket.accept()
    await hub.add_ws(role, websocket)
    await hub.broadcast({"type": "system", "content": f"{role} connected (WS)", "ts": _now_utc()})
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
            msg_id = _save_message(role, target, content, ts)
            await hub.broadcast({
                "type": "msg", "id": msg_id, "role": role,
                "target": target, "content": content, "ts": ts,
            })
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await hub.remove_ws(websocket)
        await hub.broadcast({"type": "system", "content": f"{role} disconnected", "ts": _now_utc()})
        await hub.broadcast({"type": "roster", "counts": await hub.roster()})


# ── Capture endpoints ─────────────────────────────────────────────────────────

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
    headers: dict[str, str] = {"Content-Disposition": 'inline; filename="capture.png"'}
    if console_errors:
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
    headers: dict[str, str] = {"Content-Disposition": 'inline; filename="flatten.html"'}
    if console_errors:
        headers["X-Console-Errors"] = " | ".join(console_errors[:5])[:1000]
    return Response(content=html_doc, media_type="text/html; charset=utf-8", headers=headers)
