import uuid
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, list[WebSocket]] = {}

    async def connect(self, visit_id: str, websocket: WebSocket):
        await websocket.accept()
        if visit_id not in self.connections:
            self.connections[visit_id] = []
        self.connections[visit_id].append(websocket)

    def disconnect(self, visit_id: str, websocket: WebSocket):
        if visit_id in self.connections:
            self.connections[visit_id].remove(websocket)
            if not self.connections[visit_id]:
                del self.connections[visit_id]

    async def send_status(self, visit_id: str, status: str, data: dict | None = None):
        message = json.dumps({"type": "status", "status": status, "data": data or {}})
        if visit_id in self.connections:
            for ws in self.connections[visit_id]:
                try:
                    await ws.send_text(message)
                except Exception:
                    pass


manager = ConnectionManager()


@router.websocket("/ws/visits/{visit_id}/status")
async def visit_status_ws(websocket: WebSocket, visit_id: str):
    await manager.connect(visit_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(visit_id, websocket)
