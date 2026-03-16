from fastapi import APIRouter, Request
from sqlalchemy import text
from app.config import settings
from app.database import engine
import httpx
import structlog

router = APIRouter(tags=["health"])
logger = structlog.get_logger()

# Country → app locale mapping
_COUNTRY_LOCALE = {
    "IL": "he", "US": "en", "GB": "en", "AU": "en", "CA": "en", "NZ": "en", "IE": "en", "IN": "en",
    "DE": "de", "AT": "de", "CH": "de",
    "FR": "fr", "BE": "fr", "LU": "fr", "MC": "fr",
    "ES": "es", "MX": "es", "AR": "es", "CL": "es", "CO": "es", "PE": "es",
    "PT": "pt", "BR": "pt",
    "KR": "ko",
    "IT": "it",
}


@router.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}


@router.get("/ready")
async def readiness():
    checks = {}
    overall = "healthy"

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)[:100]}"
        overall = "degraded"

    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.redis_url_computed)
        await r.ping()
        await r.close()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)[:100]}"
        overall = "degraded"

    try:
        import boto3
        s3 = boto3.client("s3", endpoint_url=settings.S3_ENDPOINT,
                          aws_access_key_id=settings.S3_ACCESS_KEY,
                          aws_secret_access_key=settings.S3_SECRET_KEY)
        s3.list_buckets()
        checks["s3"] = "ok"
    except Exception as e:
        checks["s3"] = f"error: {str(e)[:100]}"
        overall = "degraded"

    try:
        import meilisearch
        client = meilisearch.Client(settings.MEILISEARCH_URL, settings.MEILISEARCH_KEY)
        client.health()
        checks["meilisearch"] = "ok"
    except Exception as e:
        checks["meilisearch"] = f"error: {str(e)[:100]}"
        overall = "degraded"

    status_code = 200 if overall == "healthy" else 503
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=status_code, content={"status": overall, "checks": checks})


@router.get("/geo-locale")
async def get_geo_locale(request: Request):
    """Detect locale based on client IP country. No auth required."""
    # Get real client IP from proxy headers
    ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or request.headers.get("X-Real-IP", "") or request.client.host if request.client else ""

    country = ""
    locale = "he"  # default

    if ip and ip not in ("127.0.0.1", "::1", "localhost"):
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"http://ip-api.com/json/{ip}?fields=countryCode")
                if res.status_code == 200:
                    country = res.json().get("countryCode", "")
                    locale = _COUNTRY_LOCALE.get(country, "en")
        except Exception as e:
            logger.debug("geo_locale_lookup_failed", ip=ip, error=str(e))

    return {"locale": locale, "country": country}
