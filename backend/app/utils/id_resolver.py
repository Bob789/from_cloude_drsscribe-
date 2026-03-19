import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.summary import Summary
from app.exceptions import NotFoundError


async def _resolve_entity(db: AsyncSession, id_str: str, model_class):
    try:
        display_id = int(id_str)
        result = await db.execute(select(model_class).where(model_class.display_id == display_id))
        entity = result.scalar_one_or_none()
        if entity:
            return entity
    except (ValueError, TypeError):
        pass
    try:
        uid = uuid.UUID(id_str)
        result = await db.execute(select(model_class).where(model_class.id == uid))
        return result.scalar_one_or_none()
    except (ValueError, TypeError):
        return None


async def resolve_patient(db: AsyncSession, id_str: str) -> Patient | None:
    return await _resolve_entity(db, id_str, Patient)


async def resolve_visit(db: AsyncSession, id_str: str) -> Visit | None:
    return await _resolve_entity(db, id_str, Visit)


async def resolve_summary(db: AsyncSession, id_str: str) -> Summary | None:
    return await _resolve_entity(db, id_str, Summary)


async def get_patient_or_404(db: AsyncSession, id_str: str) -> Patient:
    patient = await _resolve_entity(db, id_str, Patient)
    if not patient:
        raise NotFoundError("מטופל", id_str)
    return patient


async def get_visit_or_404(db: AsyncSession, id_str: str) -> Visit:
    visit = await _resolve_entity(db, id_str, Visit)
    if not visit:
        raise NotFoundError("ביקור", id_str)
    return visit


async def get_summary_or_404(db: AsyncSession, id_str: str) -> Summary:
    summary = await _resolve_entity(db, id_str, Summary)
    if not summary:
        raise NotFoundError("סיכום", id_str)
    return summary
