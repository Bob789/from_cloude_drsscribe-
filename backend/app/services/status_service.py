import json
from datetime import datetime, timezone
import redis.asyncio as aioredis
from app.config import settings

_redis = None


async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url_computed)
    return _redis


async def update_pipeline_status(visit_id: str, stage: str, progress_pct: int, error: str | None = None):
    r = await _get_redis()
    status = {
        "stage": stage,
        "progress_pct": progress_pct,
        "error": error,
        "started_at": "",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    existing = await r.get(f"pipeline:{visit_id}")
    if existing:
        prev = json.loads(existing)
        status["started_at"] = prev.get("started_at", "")
    else:
        status["started_at"] = datetime.now(timezone.utc).isoformat()

    await r.set(f"pipeline:{visit_id}", json.dumps(status), ex=86400)


async def get_pipeline_status(visit_id: str) -> dict:
    r = await _get_redis()
    data = await r.get(f"pipeline:{visit_id}")
    if data:
        return json.loads(data)
    return {"stage": "unknown", "progress_pct": 0, "error": None}
