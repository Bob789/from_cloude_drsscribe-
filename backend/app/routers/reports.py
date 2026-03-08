from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.permissions import require_admin
from app.models.user import User
from app.models.visit import Visit
from app.models.transcription import Transcription
from app.models.summary import Summary

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/usage")
async def usage_report(
    period: str = Query("month", regex="^(week|month|year)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    now = datetime.now(timezone.utc)
    if period == "week":
        start = now - timedelta(days=7)
    elif period == "month":
        start = now - timedelta(days=30)
    else:
        start = now - timedelta(days=365)

    visits_q = await db.execute(select(func.count(Visit.id)).where(Visit.created_at >= start))
    transcriptions_q = await db.execute(select(func.count(Transcription.id)).where(Transcription.created_at >= start))
    summaries_q = await db.execute(select(func.count(Summary.id)).where(Summary.created_at >= start))

    return {
        "period": period,
        "start_date": start.isoformat(),
        "visits": visits_q.scalar() or 0,
        "transcriptions": transcriptions_q.scalar() or 0,
        "summaries": summaries_q.scalar() or 0,
    }


@router.get("/doctors")
async def doctor_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(
        select(User.id, User.name, User.email, func.count(Visit.id).label("visit_count"))
        .outerjoin(Visit, Visit.doctor_id == User.id)
        .group_by(User.id, User.name, User.email)
        .order_by(func.count(Visit.id).desc())
    )
    return [
        {"id": str(row[0]), "name": row[1], "email": row[2], "visit_count": row[3]}
        for row in result.all()
    ]
