import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy import select, func, desc, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.site_analytics import PageViewIn, SearchLogIn, EventIn
from app.models.site_analytics import SitePageView, SiteSearchLog, SiteEvent
from app.middleware.permissions import require_admin
from app.models.user import User

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
        visitor_id=data.visitor_id,
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
        visitor_id=data.visitor_id,
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
        visitor_id=data.visitor_id,
        event_type=data.event_type,
        event_data=data.event_data,
        page_path=data.page_path,
    )
    db.add(row)
    await db.commit()


# ── ADMIN DASHBOARD ──────────────────────────────────────────────────────────

@router.get("/dashboard")
async def analytics_dashboard(
    hours: int = Query(24, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    since_realtime = datetime.now(timezone.utc) - timedelta(minutes=30)

    # Total pageviews in period
    total_pv = (await db.execute(
        select(func.count()).where(SitePageView.created_at >= since)
    )).scalar() or 0

    # Unique sessions in period
    unique_sessions = (await db.execute(
        select(func.count(distinct(SitePageView.session_id))).where(SitePageView.created_at >= since)
    )).scalar() or 0

    # Active now (last 30 min)
    active_now = (await db.execute(
        select(func.count(distinct(SitePageView.session_id))).where(SitePageView.created_at >= since_realtime)
    )).scalar() or 0

    # Avg time on page (only rows with duration)
    avg_duration = (await db.execute(
        select(func.avg(SitePageView.duration_seconds)).where(
            SitePageView.created_at >= since,
            SitePageView.duration_seconds.isnot(None),
            SitePageView.duration_seconds > 0,
        )
    )).scalar()

    # Top pages
    top_pages_rows = (await db.execute(
        select(SitePageView.page_path, func.count().label("views"))
        .where(SitePageView.created_at >= since)
        .group_by(SitePageView.page_path)
        .order_by(desc("views"))
        .limit(15)
    )).all()

    # Top referrers
    top_referrers_rows = (await db.execute(
        select(SitePageView.referrer, func.count().label("count"))
        .where(SitePageView.created_at >= since, SitePageView.referrer.isnot(None), SitePageView.referrer != "")
        .group_by(SitePageView.referrer)
        .order_by(desc("count"))
        .limit(10)
    )).all()

    # Device breakdown
    device_rows = (await db.execute(
        select(SitePageView.device_type, func.count().label("count"))
        .where(SitePageView.created_at >= since, SitePageView.device_type.isnot(None))
        .group_by(SitePageView.device_type)
        .order_by(desc("count"))
    )).all()

    # UTM sources
    utm_rows = (await db.execute(
        select(SitePageView.utm_source, func.count().label("count"))
        .where(SitePageView.created_at >= since, SitePageView.utm_source.isnot(None))
        .group_by(SitePageView.utm_source)
        .order_by(desc("count"))
        .limit(10)
    )).all()

    # Top searches
    top_searches_rows = (await db.execute(
        select(SiteSearchLog.query, func.count().label("count"), func.avg(SiteSearchLog.results_count).label("avg_results"))
        .where(SiteSearchLog.created_at >= since)
        .group_by(SiteSearchLog.query)
        .order_by(desc("count"))
        .limit(20)
    )).all()

    # Recent searches (last 50)
    recent_searches_rows = (await db.execute(
        select(SiteSearchLog.query, SiteSearchLog.results_count, SiteSearchLog.clicked_article_slug, SiteSearchLog.created_at)
        .where(SiteSearchLog.created_at >= since)
        .order_by(desc(SiteSearchLog.created_at))
        .limit(50)
    )).all()

    # Hourly traffic (last 24h buckets)
    hourly_rows = (await db.execute(
        select(
            func.date_trunc("hour", SitePageView.created_at).label("hour"),
            func.count().label("views"),
            func.count(distinct(SitePageView.session_id)).label("sessions"),
        )
        .where(SitePageView.created_at >= datetime.now(timezone.utc) - timedelta(hours=24))
        .group_by("hour")
        .order_by("hour")
    )).all()

    # Active sessions detail (last 30 min — latest page per session)
    active_sessions_rows = (await db.execute(
        select(
            SitePageView.session_id,
            func.max(SitePageView.created_at).label("last_seen"),
            func.max(SitePageView.page_path).label("current_page"),
            func.max(SitePageView.device_type).label("device"),
            func.count().label("page_count"),
        )
        .where(SitePageView.created_at >= since_realtime)
        .group_by(SitePageView.session_id)
        .order_by(desc("last_seen"))
        .limit(50)
    )).all()

    return {
        "summary": {
            "total_pageviews": total_pv,
            "unique_sessions": unique_sessions,
            "active_now": active_now,
            "avg_duration_seconds": round(avg_duration) if avg_duration else None,
            "period_hours": hours,
        },
        "top_pages": [{"path": r.page_path, "views": r.views} for r in top_pages_rows],
        "top_referrers": [{"referrer": r.referrer, "count": r.count} for r in top_referrers_rows],
        "devices": [{"type": r.device_type, "count": r.count} for r in device_rows],
        "utm_sources": [{"source": r.utm_source, "count": r.count} for r in utm_rows],
        "top_searches": [{"query": r.query, "count": r.count, "avg_results": round(r.avg_results or 0)} for r in top_searches_rows],
        "recent_searches": [{"query": r.query, "results": r.results_count, "clicked": r.clicked_article_slug, "time": r.created_at.isoformat()} for r in recent_searches_rows],
        "hourly_traffic": [{"hour": r.hour.isoformat(), "views": r.views, "sessions": r.sessions} for r in hourly_rows],
        "active_sessions": [{"session": r.session_id[:8], "last_seen": r.last_seen.isoformat(), "page": r.current_page, "device": r.device, "pages": r.page_count} for r in active_sessions_rows],
    }


@router.get("/visitor/{visitor_id}")
async def visitor_history(
    visitor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Full browsing history of a specific visitor (by localStorage visitor_id)."""
    pages = (await db.execute(
        select(SitePageView)
        .where(SitePageView.visitor_id == visitor_id)
        .order_by(desc(SitePageView.created_at))
        .limit(200)
    )).scalars().all()

    searches = (await db.execute(
        select(SiteSearchLog)
        .where(SiteSearchLog.visitor_id == visitor_id)
        .order_by(desc(SiteSearchLog.created_at))
        .limit(100)
    )).scalars().all()

    # Group pages by session
    sessions: dict = {}
    for p in pages:
        sid = p.session_id
        if sid not in sessions:
            sessions[sid] = {"session_id": sid, "first_seen": p.created_at, "last_seen": p.created_at, "pages": []}
        sessions[sid]["pages"].append({
            "path": p.page_path,
            "article": p.article_slug,
            "duration": p.duration_seconds,
            "time": p.created_at.isoformat(),
            "referrer": p.referrer,
        })
        if p.created_at < sessions[sid]["first_seen"]:
            sessions[sid]["first_seen"] = p.created_at
        if p.created_at > sessions[sid]["last_seen"]:
            sessions[sid]["last_seen"] = p.created_at

    return {
        "visitor_id": visitor_id,
        "total_sessions": len(sessions),
        "total_pageviews": len(pages),
        "sessions": [
            {**v, "first_seen": v["first_seen"].isoformat(), "last_seen": v["last_seen"].isoformat()}
            for v in sorted(sessions.values(), key=lambda x: x["last_seen"], reverse=True)
        ],
        "searches": [{"query": s.query, "results": s.results_count, "clicked": s.clicked_article_slug, "time": s.created_at.isoformat()} for s in searches],
    }
