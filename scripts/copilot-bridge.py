#!/usr/bin/env python3
"""
DrScribe Copilot Bridge — TCP real-time chat between agents.

Usage (local PC agent):
    DEV_TOOLS_TOKEN=your_token BRIDGE_ROLE=local python copilot-bridge.py

Usage (cloud agent):
    DEV_TOOLS_TOKEN=your_token BRIDGE_ROLE=cloud python copilot-bridge.py

Optional env vars:
    BRIDGE_HOST  — server host (default: drsscribe.com)
    CHAT_PORT    — TCP port   (default: 9090)

Protocol (after auth):
    Send:    {"content": "your message", "target": "all"}
    Receive: {"type": "msg", "role": "cloud", "content": "...", "ts": "..."}
    Receive: {"type": "system", "content": "cloud connected", "ts": "..."}
    Receive: {"type": "roster", "counts": {"local": 1, "cloud": 1}}
"""
import asyncio
import json
import os
import sys

BRIDGE_HOST = os.getenv("BRIDGE_HOST", "drsscribe.com")
CHAT_PORT   = int(os.getenv("CHAT_PORT", "9090"))
TOKEN       = os.getenv("DEV_TOOLS_TOKEN", "")
ROLE        = os.getenv("BRIDGE_ROLE", "local")   # "local" or "cloud"


def _fmt(m: dict) -> str:
    mtype = m.get("type", "msg")
    if mtype == "roster":
        c = m.get("counts", {})
        return f"[roster] local:{c.get('local', 0)}  cloud:{c.get('cloud', 0)}  viewer:{c.get('viewer', 0)}"
    role    = m.get("role") or mtype
    content = m.get("content", "")
    ts      = m.get("ts", "")
    mid     = f" #{m['id']}" if m.get("id") else ""
    tgt     = f" → {m['target']}" if m.get("target") and m.get("target") != "all" else ""
    return f"[{role}{tgt}{mid}  {ts}]\n{content}"


async def _recv_loop(reader: asyncio.StreamReader) -> None:
    async for raw in reader:
        line = raw.decode().strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            print("\n" + _fmt(msg), flush=True)
            print(">>> ", end="", flush=True)
        except Exception:
            print(f"\n{line}", flush=True)
            print(">>> ", end="", flush=True)


async def _send_loop(writer: asyncio.StreamWriter) -> None:
    loop = asyncio.get_event_loop()
    print(">>> ", end="", flush=True)
    while True:
        try:
            line = await loop.run_in_executor(None, sys.stdin.readline)
        except EOFError:
            break
        line = line.strip()
        if not line:
            continue
        payload = json.dumps({"content": line, "target": "all"}) + "\n"
        try:
            writer.write(payload.encode())
            await writer.drain()
        except Exception as e:
            print(f"[bridge] send error: {e}", flush=True)
            break


async def run() -> None:
    if not TOKEN:
        print("ERROR: set DEV_TOOLS_TOKEN environment variable", flush=True)
        sys.exit(1)

    print(f"[bridge] Connecting to {BRIDGE_HOST}:{CHAT_PORT} as role={ROLE}", flush=True)

    while True:
        try:
            reader, writer = await asyncio.open_connection(BRIDGE_HOST, CHAT_PORT)
            print(f"[bridge] Connected ✓", flush=True)

            # Auth
            auth = json.dumps({"token": TOKEN, "role": ROLE}) + "\n"
            writer.write(auth.encode())
            await writer.drain()

            # First response (welcome or error)
            welcome_raw = await asyncio.wait_for(reader.readline(), timeout=10.0)
            welcome = json.loads(welcome_raw.decode().strip())
            if welcome.get("type") == "error":
                print(f"[bridge] Server error: {welcome.get('content')}", flush=True)
                writer.close()
                await writer.wait_closed()
                return

            print(f"[bridge] {welcome.get('content', 'ok')} — bridge ready. Type messages below.", flush=True)
            print("[bridge] Press Ctrl+C to exit.\n", flush=True)

            recv_task = asyncio.create_task(_recv_loop(reader))
            send_task = asyncio.create_task(_send_loop(writer))
            done, pending = await asyncio.wait(
                [recv_task, send_task], return_when=asyncio.FIRST_COMPLETED
            )
            for t in pending:
                t.cancel()

            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

        except (ConnectionRefusedError, OSError) as e:
            print(f"[bridge] Cannot connect: {e}. Retrying in 5s...", flush=True)
            await asyncio.sleep(5)
        except asyncio.TimeoutError:
            print("[bridge] Auth timeout. Retrying in 5s...", flush=True)
            await asyncio.sleep(5)
        except KeyboardInterrupt:
            print("\n[bridge] Bye.", flush=True)
            return
        except Exception as e:
            print(f"[bridge] Error: {e}. Retrying in 5s...", flush=True)
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n[bridge] Bye.")
