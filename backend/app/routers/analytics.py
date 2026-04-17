import hashlib
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.site_analytics import PageViewIn, SearchLogIn, EventIn
from app.models.site_analytics import SitePageView, SiteSearchLog, SiteEvent

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _hash_ip(ip: str) -> str:
    """Hash IP for privacy — we track patterns, not individuals."""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP", "")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


@router.post("/pageview", status_code=204)
async def track_pageview(data: PageViewIn, request: Request, db: AsyncSession = Depends(get_db)):
    ip = _get_client_ip(request)
    row = SitePageView(
        session_id=data.session_id,
        visitor_ip_hash=_hash_ip(ip),
        user_agent=request.headers.get("User-Agent"),
        referrer=data.referrer,
        page_path=data.page_path,
        article_slug=data.article_slug,
        duration_seconds=data.duration_seconds,
        device_type=data.device_type,
        utm_source=data.utm_source,
        utm_medium=data.utm_medium,
        utm_campaign=data.utm_campaign,
    )
    db.add(row)
    await db.commit()


@router.post("/search", status_code=204)
async def track_search(data: SearchLogIn, request: Request, db: AsyncSession = Depends(get_db)):
    row = SiteSearchLog(
        session_id=data.session_id,
        query=data.query,
        results_count=data.results_count,
        clicked_article_slug=data.clicked_article_slug,
    )
    db.add(row)
    await db.commit()


@router.post("/event", status_code=204)
async def track_event(data: EventIn, request: Request, db: AsyncSession = Depends(get_db)):
    row = SiteEvent(
        session_id=data.session_id,
        event_type=data.event_type,
        event_data=data.event_data,
        page_path=data.page_path,
    )
    db.add(row)
    await db.commit()
