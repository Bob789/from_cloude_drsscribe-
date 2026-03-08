import json
from datetime import datetime, timezone
import redis.asyncio as aioredis
from app.config import settings

MAX_CONCURRENT_SESSIONS = 3
SESSION_TIMEOUT_HOURS = 8

_redis = None


async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url_computed)
    return _redis


async def register_session(user_id: str, token_jti: str) -> bool:
    r = await _get_redis()
    key = f"sessions:{user_id}"

    sessions = await r.lrange(key, 0, -1)
    active_sessions = []
    for s in sessions:
        session_data = json.loads(s)
        created = datetime.fromisoformat(session_data["created_at"])
        if (datetime.now(timezone.utc) - created).total_seconds() < SESSION_TIMEOUT_HOURS * 3600:
            active_sessions.append(session_data)

    await r.delete(key)

    if len(active_sessions) >= MAX_CONCURRENT_SESSIONS:
        active_sessions = active_sessions[1:]

    active_sessions.append({"jti": token_jti, "created_at": datetime.now(timezone.utc).isoformat()})

    for session in active_sessions:
        await r.rpush(key, json.dumps(session))
    await r.expire(key, SESSION_TIMEOUT_HOURS * 3600)

    return True


async def is_session_valid(user_id: str, token_jti: str) -> bool:
    r = await _get_redis()
    key = f"sessions:{user_id}"
    sessions = await r.lrange(key, 0, -1)
    for s in sessions:
        session_data = json.loads(s)
        if session_data.get("jti") == token_jti:
            return True
    return False


async def revoke_all_sessions(user_id: str):
    r = await _get_redis()
    await r.delete(f"sessions:{user_id}")
