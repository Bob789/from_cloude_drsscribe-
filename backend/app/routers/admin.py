import uuid
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.permissions import require_admin
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog
from app.models.user_activity_log import UserActivityLog
from app.models.clinic import Clinic
from app.schemas.auth import UserResponse
from app.exceptions import NotFoundError

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
