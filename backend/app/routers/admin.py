import uuid
from fastapi import APIRouter, Depends, status, Query, Body
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.permissions import require_admin
from app.middleware.auth import get_current_user
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog
from app.models.user_activity_log import UserActivityLog
from app.models.clinic import Clinic
from app.models.admin_message import AdminMessage
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.recording import Recording
from app.models.transcription import Transcription
from app.models.summary import Summary
from app.schemas.auth import UserResponse
from app.exceptions import NotFoundError
from app.services.auth_service import generate_tokens

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.put("/users/{user_id}/role")
async def change_role(
    user_id: uuid.UUID,
    role: UserRole,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("משתמש", user_id)
    user.role = role
    await db.commit()
    return {"message": f"Role updated to {role.value}"}


@router.put("/users/{user_id}/active")
async def toggle_active(
    user_id: uuid.UUID,
    active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("משתמש", user_id)
    user.is_active = active
    await db.commit()
    return {"message": f"User {'activated' if active else 'deactivated'}"}


@router.get("/audit")
async def get_audit_logs(
    user_id: uuid.UUID | None = Query(None),
    action: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    stmt = select(AuditLog)
    if user_id:
        stmt = stmt.where(AuditLog.user_id == user_id)
    if action:
        stmt = stmt.where(AuditLog.action.ilike(f"%{action}%"))

    total_q = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_q.scalar() or 0

    stmt = stmt.order_by(AuditLog.timestamp.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    return {
        "items": [
            {
                "id": str(log.id),
                "user_id": str(log.user_id) if log.user_id else None,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/clinics")
async def list_clinics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(Clinic).order_by(Clinic.name))
    clinics = result.scalars().all()
    return [{"id": str(c.id), "name": c.name, "address": c.address, "timezone": c.timezone} for c in clinics]


@router.post("/clinics", status_code=status.HTTP_201_CREATED)
async def create_clinic(
    name: str,
    address: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    clinic = Clinic(name=name, address=address)
    db.add(clinic)
    await db.commit()
    await db.refresh(clinic)
    return {"id": str(clinic.id), "name": clinic.name}


@router.get("/activity-logs")
async def get_activity_logs(
    user_id: uuid.UUID | None = Query(None),
    action: str | None = Query(None),
    entity_type: str | None = Query(None),
    error_only: bool = Query(False),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    stmt = select(UserActivityLog)
    if user_id:
        stmt = stmt.where(UserActivityLog.user_id == user_id)
    if action:
        stmt = stmt.where(UserActivityLog.action == action)
    if entity_type:
        stmt = stmt.where(UserActivityLog.entity_type == entity_type)
    if error_only:
        stmt = stmt.where(UserActivityLog.action == "ERROR")
    if date_from:
        stmt = stmt.where(UserActivityLog.created_at >= date_from)
    if date_to:
        stmt = stmt.where(UserActivityLog.created_at <= date_to)

    total_q = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_q.scalar() or 0

    stmt = stmt.order_by(UserActivityLog.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    user_ids = {log.user_id for log in logs}
    users_result = await db.execute(select(User).where(User.id.in_(user_ids))) if user_ids else None
    users_map = {u.id: u.name for u in (users_result.scalars().all() if users_result else [])}

    return {
        "items": [
            {
                "id": log.id,
                "user_id": str(log.user_id),
                "user_name": users_map.get(log.user_id, ""),
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "description": log.description,
                "metadata": log.metadata_json,
                "error_id": log.error_id,
                "error_message": log.error_message,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


# ─── Stats ───────────────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    users_total = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    users_active = (await db.execute(select(func.count()).select_from(User).where(User.is_active == True))).scalar() or 0  # noqa
    patients_total = (await db.execute(select(func.count()).select_from(Patient))).scalar() or 0
    visits_total = (await db.execute(select(func.count()).select_from(Visit))).scalar() or 0
    recordings_total = (await db.execute(select(func.count()).select_from(Recording))).scalar() or 0
    transcriptions_total = (await db.execute(select(func.count()).select_from(Transcription))).scalar() or 0
    summaries_total = (await db.execute(select(func.count()).select_from(Summary))).scalar() or 0
    messages_unread = (await db.execute(select(func.count()).select_from(AdminMessage).where(AdminMessage.is_read == False))).scalar() or 0  # noqa
    errors_total = (await db.execute(select(func.count()).select_from(UserActivityLog).where(UserActivityLog.action == "ERROR"))).scalar() or 0

    return {
        "users": {"total": users_total, "active": users_active, "blocked": users_total - users_active},
        "patients": patients_total,
        "visits": visits_total,
        "recordings": recordings_total,
        "transcriptions": transcriptions_total,
        "summaries": summaries_total,
        "messages_unread": messages_unread,
        "errors_total": errors_total,
    }


# ─── Messages ─────────────────────────────────────────────────────────────────


def _msg_dict(m):
    return {
        "id": str(m.id),
        "user_id": str(m.user_id) if m.user_id else None,
        "user_email": m.user_email,
        "user_name": m.user_name,
        "subject": m.subject,
        "body": m.body,
        "category": m.category,
        "direction": m.direction,
        "is_read": m.is_read,
        "thread_id": str(m.thread_id) if m.thread_id else None,
        "attachments": m.attachments or [],
        "created_at": m.created_at.isoformat(),
    }


@router.get("/messages/threads")
async def get_threads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all conversation threads (grouped by thread_id), newest first."""
    # Get all messages ordered by date
    all_msgs = (await db.execute(
        select(AdminMessage).order_by(AdminMessage.created_at.asc())
    )).scalars().all()

    # Group into threads
    threads: dict[str, list] = {}
    standalone = []
    for m in all_msgs:
        tid = str(m.thread_id) if m.thread_id else str(m.id)
        threads.setdefault(tid, []).append(m)

    # Build thread summaries, sorted by latest message
    result = []
    for tid, msgs in threads.items():
        first = msgs[0]
        last = msgs[-1]
        unread = sum(1 for m in msgs if not m.is_read and m.direction == "inbound")
        result.append({
            "thread_id": tid,
            "subject": first.subject,
            "user_id": str(first.user_id) if first.user_id else None,
            "user_email": first.user_email,
            "user_name": first.user_name,
            "category": first.category,
            "message_count": len(msgs),
            "unread_count": unread,
            "last_message": _msg_dict(last),
            "last_activity": last.created_at.isoformat(),
        })
    result.sort(key=lambda t: t["last_activity"], reverse=True)
    return result


@router.get("/messages/thread/{thread_id}")
async def get_thread_messages(
    thread_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all messages in a thread, ordered chronologically."""
    msgs = (await db.execute(
        select(AdminMessage).where(
            (AdminMessage.thread_id == thread_id) | (AdminMessage.id == thread_id)
        ).order_by(AdminMessage.created_at.asc())
    )).scalars().all()
    # Mark inbound as read
    for m in msgs:
        if not m.is_read and m.direction == "inbound":
            m.is_read = True
    await db.commit()
    return [_msg_dict(m) for m in msgs]


@router.put("/messages/{message_id}/read")
async def mark_message_read(
    message_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    msg = (await db.execute(select(AdminMessage).where(AdminMessage.id == message_id))).scalar_one_or_none()
    if not msg:
        raise NotFoundError("הודעה", message_id)
    msg.is_read = True
    await db.commit()
    return {"ok": True}


# ─── Send message (any authenticated user) ────────────────────────────────────

@router.post("/messages", status_code=status.HTTP_201_CREATED)
async def send_message(
    subject: str = Body(...),
    body: str = Body(...),
    category: str = Body("general"),
    thread_id: str | None = Body(None),
    attachments: list[dict] | None = Body(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    msg = AdminMessage(
        user_id=current_user.id,
        user_email=current_user.email,
        user_name=current_user.name,
        subject=subject,
        body=body,
        category=category,
        direction="inbound",
        thread_id=uuid.UUID(thread_id) if thread_id else None,
        attachments=attachments or [],
    )
    db.add(msg)
    await db.flush()
    # If no thread_id, this is a new thread — set thread_id = own id
    if not msg.thread_id:
        msg.thread_id = msg.id
    await db.commit()
    return {"ok": True, "id": str(msg.id), "thread_id": str(msg.thread_id)}


# ─── Admin compose / reply ────────────────────────────────────────────────────

@router.post("/messages/compose", status_code=status.HTTP_201_CREATED)
async def compose_message(
    subject: str = Body(...),
    body: str = Body(...),
    recipient_ids: list[str] = Body(...),
    thread_id: str | None = Body(None),
    attachments: list[dict] | None = Body(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Send message to specific users or all users.
    recipient_ids: list of user UUIDs, or ['all'] for broadcast.
    """
    if recipient_ids == ["all"]:
        targets = (await db.execute(
            select(User).where(User.is_active == True)  # noqa
        )).scalars().all()
    else:
        uids = [uuid.UUID(uid) for uid in recipient_ids]
        targets = (await db.execute(
            select(User).where(User.id.in_(uids))
        )).scalars().all()

    if not targets:
        raise NotFoundError("משתמשים", "none")

    tid = uuid.UUID(thread_id) if thread_id else None
    count = 0
    for u in targets:
        msg = AdminMessage(
            user_id=u.id,
            user_email=u.email,
            user_name=u.name,
            subject=subject,
            body=body,
            category="support",
            direction="outbound",
            attachments=attachments or [],
            thread_id=tid,
        )
        db.add(msg)
        await db.flush()
        if not msg.thread_id:
            msg.thread_id = msg.id
        count += 1
    await db.commit()
    return {"ok": True, "sent_to": count}


# ─── Impersonate (view-as) ────────────────────────────────────────────────────

@router.post("/impersonate/{user_id}")
async def impersonate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    target = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not target:
        raise NotFoundError("משתמש", user_id)
    tokens = generate_tokens(str(target.id))
    return {
        "access_token": tokens["access_token"],
        "user": {"id": str(target.id), "email": target.email, "name": target.name},
        "note": "impersonation token — valid for 30 minutes",
    }
