from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.visit import Visit
from app.models.patient import Patient
from app.models.transcription import Transcription, TranscriptionStatus
from app.utils.encryption import decrypt_field
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

HEBREW_DAYS = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today_start - timedelta(days=7)

    doctor_filter = Visit.doctor_id == current_user.id

    today_visits_q = await db.execute(
        select(func.count(Visit.id)).where(Visit.start_time >= today_start, doctor_filter)
    )
    today_visits = today_visits_q.scalar() or 0

    pending_q = await db.execute(
        select(func.count(Transcription.id)).where(Transcription.status.in_([TranscriptionStatus.pending, TranscriptionStatus.processing]))
    )
    pending_transcriptions = pending_q.scalar() or 0

    total_patients_q = await db.execute(
        select(func.count(Patient.id)).where(Patient.created_by == current_user.id)
    )
    total_patients = total_patients_q.scalar() or 0

    week_visits_q = await db.execute(
        select(func.count(Visit.id)).where(Visit.start_time >= week_ago, doctor_filter)
    )
    visits_this_week = week_visits_q.scalar() or 0

    first_of_month = today_start.replace(day=1)
    monthly_tx_q = await db.execute(
        select(func.count(Transcription.id)).where(
            Transcription.status == TranscriptionStatus.done,
            Transcription.created_at >= first_of_month,
        )
    )
    monthly_transcriptions = monthly_tx_q.scalar() or 0

    # Find most recent Sunday (start of Israeli week)
    # Python weekday: Monday=0 ... Sunday=6
    days_since_sunday = (today_start.weekday() + 1) % 7
    week_start = today_start - timedelta(days=days_since_sunday)

    visits_by_day = []
    for i in range(7):  # Sunday(0) through Saturday(6)
        day_start = week_start + timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        day_q = await db.execute(
            select(func.count(Visit.id)).where(Visit.start_time >= day_start, Visit.start_time < day_end, doctor_filter)
        )
        count = day_q.scalar() or 0

        patients = []
        if count > 0:
            visits_q = await db.execute(
                select(Visit, Patient)
                .join(Patient, Visit.patient_id == Patient.id)
                .where(Visit.start_time >= day_start, Visit.start_time < day_end, doctor_filter)
                .order_by(Visit.start_time.desc())
            )
            for visit, patient in visits_q.all():
                # Decrypt patient name (stored encrypted with AES-256-GCM)
                patient_name = patient.name
                try:
                    if patient_name and len(patient_name) > 50:
                        patient_name = decrypt_field(patient_name)
                except Exception as e:
                    logger.error("dashboard_decrypt_failed", patient_id=str(patient.id), error=str(e))
                patients.append({
                    "name": patient_name,
                    "patient_display_id": patient.display_id,
                    "time": visit.start_time.strftime("%H:%M") if visit.start_time else "",
                })

        visits_by_day.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "day_name": HEBREW_DAYS[i],
            "count": count,
            "patients": patients,
        })

    return {
        "today_visits": today_visits,
        "pending_transcriptions": pending_transcriptions,
        "total_patients": total_patients,
        "visits_this_week": visits_this_week,
        "monthly_transcriptions": monthly_transcriptions,
        "visits_by_day": visits_by_day,
    }
