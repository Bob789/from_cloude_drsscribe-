import redis.asyncio as redis
from app.config import settings

_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(
            settings.redis_url_computed,
            encoding="utf-8",
            decode_responses=True,
        )
    return _client


async def close_redis() -> None:
    global _client
    if _client:
        await _client.aclose()
        _client = None


async def blacklist_access_token(jti: str, ttl_seconds: int) -> None:
    r = await get_redis()
    await r.setex(f"bl:{jti}", max(ttl_seconds, 1), "1")


async def is_access_token_blacklisted(jti: str) -> bool:
    r = await get_redis()
    return bool(await r.exists(f"bl:{jti}"))


async def mark_refresh_token_used(jti: str, ttl_seconds: int) -> None:
    r = await get_redis()
    await r.setex(f"rt:{jti}", max(ttl_seconds, 1), "1")


async def is_refresh_token_used(jti: str) -> bool:
    r = await get_redis()
    return bool(await r.exists(f"rt:{jti}"))
