import uuid
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.config import settings
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.services.hebrew_holidays import get_holidays, get_holidays_range
from app.services import redis_service

CALENDAR_REDIRECT_URI = settings.GOOGLE_CALENDAR_REDIRECT_URI

router = APIRouter(prefix="/appointments", tags=["appointments"])


def _appointment_to_response(appt: Appointment) -> dict:
    return {
        "id": appt.id,
        "patient_id": str(appt.patient_id) if appt.patient_id else None,
        "patient_name": appt.patient.name if appt.patient else None,
        "title": appt.title,
        "description": appt.description,
        "start_time": appt.start_time.isoformat(),
        "end_time": appt.end_time.isoformat(),
        "duration_minutes": appt.duration_minutes,
        "status": appt.status,
        "reminder_minutes": appt.reminder_minutes,
        "synced_to_google": appt.synced_to_google,
        "google_event_id": appt.google_event_id,
        "created_at": appt.created_at.isoformat(),
    }


# ── Calendar connection ──

@router.get("/calendar/auth-url")
async def get_calendar_auth_url(
    current_user: User = Depends(get_current_user),
):
    from app.services.calendar_service import get_calendar_auth_url
    state = secrets.token_urlsafe(32)
    r = await redis_service.get_redis()
    await r.setex(f"oauth_state:{state}", 300, str(current_user.id))  # one-time, 5 min TTL
    auth_url = get_calendar_auth_url(CALENDAR_REDIRECT_URI, state=state)
    return {"auth_url": auth_url}


@router.get("/calendar/callback")
async def calendar_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    r = await redis_service.get_redis()
    user_id_str = await r.getdel(f"oauth_state:{state}")  # atomic read+delete → one-time-use
    if not user_id_str:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id_str)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from app.services.calendar_service import exchange_code_for_tokens
    tokens = exchange_code_for_tokens(code, CALENDAR_REDIRECT_URI)
    user.calendar_refresh_token = tokens.get("refresh_token")
    user.calendar_connected = True
    user.calendar_connected_at = datetime.now(timezone.utc)
    await db.commit()

    return HTMLResponse("""
    <html dir="rtl"><body style="font-family:sans-serif;text-align:center;padding:60px;background:#0f172a;color:#e2e8f0">
    <h2>Google Calendar מחובר בהצלחה!</h2>
    <p>אפשר לסגור חלון זה ולחזור לאפליקציה.</p>
    <script>setTimeout(()=>window.close(),3000)</script>
    </body></html>
    """)


@router.get("/calendar/status")
async def calendar_status(current_user: User = Depends(get_current_user)):
    return {
        "connected": current_user.calendar_connected,
        "connected_at": current_user.calendar_connected_at.isoformat() if current_user.calendar_connected_at else None,
    }


# ── Holidays ──

@router.get("/holidays")
async def holidays(
    year: int | None = None,
    date_from: str | None = Query(None, alias="from"),
    date_to: str | None = Query(None, alias="to"),
):
    if date_from and date_to:
        return get_holidays_range(date_from, date_to)
    return get_holidays(year or datetime.now().year)


# ── CRUD ──

@router.post("")
async def create_appointment(
    data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    end_time = data.start_time + timedelta(minutes=data.duration_minutes)
    appt = Appointment(
        user_id=current_user.id,
        patient_id=uuid.UUID(data.patient_id) if data.patient_id else None,
        title=data.title,
        description=data.description,
        start_time=data.start_time,
        end_time=end_time,
        duration_minutes=data.duration_minutes,
        reminder_minutes=data.reminder_minutes,
    )
    db.add(appt)
    await db.flush()

    if data.sync_to_google and current_user.calendar_connected and current_user.calendar_refresh_token:
        try:
            from app.services.calendar_service import create_event
            result = await create_event(current_user.calendar_refresh_token, {
                "title": data.title,
                "description": data.description or "",
                "start_time": data.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "reminder_minutes": data.reminder_minutes,
            })
            appt.google_event_id = result["google_event_id"]
            appt.synced_to_google = True
        except Exception:
            pass

    await db.commit()
    await db.refresh(appt)
    return _appointment_to_response(appt)


@router.get("")
async def list_appointments(
    date_from: str | None = None,
    date_to: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Appointment).where(Appointment.user_id == current_user.id)
    if date_from:
        q = q.where(Appointment.start_time >= datetime.fromisoformat(date_from))
    if date_to:
        q = q.where(Appointment.start_time <= datetime.fromisoformat(date_to + "T23:59:59"))
    if status:
        q = q.where(Appointment.status == status)
    q = q.order_by(Appointment.start_time)
    result = await db.execute(q)
    return [_appointment_to_response(a) for a in result.scalars().all()]


@router.get("/today")
async def today_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    result = await db.execute(
        select(Appointment)
        .where(Appointment.user_id == current_user.id, Appointment.start_time >= start, Appointment.start_time < end)
        .order_by(Appointment.start_time)
    )
    return [_appointment_to_response(a) for a in result.scalars().all()]


@router.get("/google/today")
async def google_today_events(current_user: User = Depends(get_current_user)):
    if not current_user.calendar_connected or not current_user.calendar_refresh_token:
        return []
    try:
        from app.services.calendar_service import get_today_events
        return await get_today_events(current_user.calendar_refresh_token)
    except Exception:
        return []


@router.post("/google/sync")
async def sync_google_events(
    date_from: str | None = None,
    date_to: str | None = None,
    current_user: User = Depends(get_current_user),
):
    if not current_user.calendar_connected or not current_user.calendar_refresh_token:
        raise HTTPException(status_code=400, detail="Google Calendar לא מחובר")
    try:
        from app.services.calendar_service import get_events_range
        today = datetime.now().strftime("%Y-%m-%d")
        events = await get_events_range(
            current_user.calendar_refresh_token,
            date_from or today,
            date_to or today,
        )
        return {"events": events, "count": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patient/{patient_id}")
async def patient_appointments(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.utils.id_resolver import resolve_patient
    patient = await resolve_patient(db, patient_id)
    if not patient:
        return []
    q = select(Appointment).where(
        Appointment.user_id == current_user.id,
        Appointment.patient_id == patient.id,
    ).order_by(Appointment.start_time.desc())
    result = await db.execute(q)
    return [_appointment_to_response(a) for a in result.scalars().all()]


@router.get("/{appointment_id}")
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id, Appointment.user_id == current_user.id)
    )
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="פגישה לא נמצאה")
    return _appointment_to_response(appt)


@router.put("/{appointment_id}")
async def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id, Appointment.user_id == current_user.id)
    )
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="פגישה לא נמצאה")

    if data.title is not None:
        appt.title = data.title
    if data.description is not None:
        appt.description = data.description
    if data.start_time is not None:
        appt.start_time = data.start_time
        appt.end_time = data.start_time + timedelta(minutes=data.duration_minutes or appt.duration_minutes)
    if data.duration_minutes is not None:
        appt.duration_minutes = data.duration_minutes
        appt.end_time = appt.start_time + timedelta(minutes=data.duration_minutes)
    if data.status is not None:
        appt.status = data.status
    if data.reminder_minutes is not None:
        appt.reminder_minutes = data.reminder_minutes

    if appt.synced_to_google and appt.google_event_id and current_user.calendar_refresh_token:
        try:
            from app.services.calendar_service import update_event
            await update_event(current_user.calendar_refresh_token, appt.google_event_id, {
                "title": appt.title,
                "start_time": appt.start_time.isoformat(),
                "end_time": appt.end_time.isoformat(),
                "description": appt.description or "",
            })
        except Exception:
            pass

    await db.commit()
    await db.refresh(appt)
    return _appointment_to_response(appt)


@router.delete("/{appointment_id}")
async def delete_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id, Appointment.user_id == current_user.id)
    )
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="פגישה לא נמצאה")

    if appt.synced_to_google and appt.google_event_id and current_user.calendar_refresh_token:
        try:
            from app.services.calendar_service import delete_event
            await delete_event(current_user.calendar_refresh_token, appt.google_event_id)
        except Exception:
            pass

    await db.delete(appt)
    await db.commit()
    return {"status": "deleted"}
