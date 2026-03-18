from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User, UserRole
from app.models.visit import Visit, VisitStatus
from app.models.summary import Summary
from app.models.transcription import Transcription
from app.models.recording import Recording
from app.models.tag import Tag
from app.schemas.visit import VisitCreate, VisitResponse, VisitUpdateWithSummary
from app.services.audit_service import log_action
from app.services.activity_log_service import log_activity
from app.services.llm_service import normalize_diagnosis
from app.services.tagging_service import sync_diagnosis_tags
from app.utils.id_resolver import get_visit_or_404, get_patient_or_404
from app.exceptions import ForbiddenError
from app.utils.medical_encryption import decrypt_summary_fields, decrypt_transcription_fields

router = APIRouter(prefix="/visits", tags=["visits"])


@router.post("", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
async def create_visit(data: VisitCreate, request: Request, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    visit = Visit(
        patient_id=data.patient_id, doctor_id=current_user.id,
        start_time=data.start_time or datetime.now(timezone.utc), status=VisitStatus.in_progress, source="recording",
    )
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
    await log_action(db, "create", "visit", str(visit.id), current_user.id)
    await log_activity(db, current_user.id, "CREATE", "visit", visit.id, "יצר ביקור חדש", request=request)
    return visit


@router.get("/{visit_id}", response_model=VisitResponse)
async def get_visit(visit_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    visit = await get_visit_or_404(db, visit_id)
    if current_user.role != UserRole.admin and visit.doctor_id != current_user.id:
        raise ForbiddenError("אין הרשאה לצפות בביקור זה")
    return visit


@router.get("/{visit_id}/status")
async def get_visit_status(visit_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    visit = await get_visit_or_404(db, visit_id)
    if current_user.role != UserRole.admin and visit.doctor_id != current_user.id:
        raise ForbiddenError("אין הרשאה")
    rec_q = await db.execute(select(Recording).where(Recording.visit_id == visit.id))
    recording = rec_q.scalars().first()
    t_status = s_status = None
    if recording:
        t_q = await db.execute(select(Transcription).where(Transcription.recording_id == recording.id))
        trans = t_q.scalars().first()
        if trans:
            t_status = trans.status.value
    s_q = await db.execute(select(Summary).where(Summary.visit_id == visit.id))
    summ = s_q.scalars().first()
    if summ:
        s_status = summ.status.value
    return {"transcription_status": t_status, "summary_status": s_status}


@router.get("/patient/{patient_id}")
async def get_patient_visits(patient_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    patient = await get_patient_or_404(db, patient_id)

    # Doctor isolation: only the doctor who created this patient (or admin) can view
    if current_user.role != UserRole.admin and patient.created_by != current_user.id:
        raise ForbiddenError("אין הרשאה לצפות במטופל זה")

    result = await db.execute(select(Visit).where(Visit.patient_id == patient.id).order_by(Visit.start_time.desc()))
    visits = result.scalars().all()

    visits_data = []
    for visit in visits:
        summary_result = await db.execute(select(Summary).where(Summary.visit_id == visit.id).order_by(Summary.created_at.desc()))
        summary = summary_result.scalars().first()
        rec_result = await db.execute(select(Recording).where(Recording.visit_id == visit.id))
        recording = rec_result.scalars().first()
        transcription = None
        if recording:
            trans_result = await db.execute(select(Transcription).where(Transcription.recording_id == recording.id))
            transcription = trans_result.scalars().first()
        tags_result = await db.execute(
            select(Tag).where(Tag.entity_type == "summary", Tag.entity_id == str(summary.id))
        ) if summary else None
        tags = [{"id": str(t.id), "tag_type": t.tag_type, "tag_code": t.tag_code, "tag_label": t.tag_label}
                for t in (tags_result.scalars().all() if tags_result else [])]

        # Decrypt encrypted medical data before returning
        if summary:
            decrypt_summary_fields(summary)
        if transcription:
            decrypt_transcription_fields(transcription)

        visits_data.append({
            "id": str(visit.id), "display_id": visit.display_id, "doctor_id": str(visit.doctor_id),
            "start_time": visit.start_time.isoformat() if visit.start_time else None,
            "end_time": visit.end_time.isoformat() if visit.end_time else None,
            "status": visit.status.value, "source": visit.source,
            "summary": {
                "id": str(summary.id), "display_id": summary.display_id,
                "summary_text": summary.summary_text,
                "chief_complaint": summary.chief_complaint, "findings": summary.findings,
                "diagnosis": summary.diagnosis, "treatment_plan": summary.treatment_plan,
                "recommendations": summary.recommendations, "urgency": summary.urgency,
                "source": summary.source, "notes": summary.notes,
                "custom_fields": summary.custom_fields, "tags": tags,
            } if summary else None,
            "transcription": {
                "id": str(transcription.id), "full_text": transcription.full_text,
                "status": transcription.status.value, "confidence_score": transcription.confidence_score,
            } if transcription else None,
        })
    return visits_data


@router.put("/{visit_id}", response_model=VisitResponse)
async def update_visit(visit_id: str, data: VisitUpdateWithSummary, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    visit = await get_visit_or_404(db, visit_id)
    if current_user.role != UserRole.admin and visit.doctor_id != current_user.id:
        await log_action(db, "unauthorized_edit_attempt", "visit", str(visit.id), current_user.id)
        raise ForbiddenError("אין הרשאה לעריכת ביקור זה")

    visit_fields = {"start_time", "end_time", "status"}
    summary_fields = {"chief_complaint", "findings", "diagnosis", "treatment_plan", "recommendations", "urgency"}
    update_data = data.model_dump(exclude_none=True)
    visit_updates = {k: v for k, v in update_data.items() if k in visit_fields}
    summary_updates = {k: v for k, v in update_data.items() if k in summary_fields}

    for key, value in visit_updates.items():
        setattr(visit, key, value)
    if summary_updates:
        summary_result = await db.execute(select(Summary).where(Summary.visit_id == visit.id).order_by(Summary.created_at.desc()))
        summary = summary_result.scalars().first()
        if summary:
            if "diagnosis" in summary_updates:
                summary_updates["diagnosis"] = normalize_diagnosis(summary_updates["diagnosis"])
            for key, value in summary_updates.items():
                setattr(summary, key, value)
            await db.commit()
            if "diagnosis" in summary_updates:
                await sync_diagnosis_tags(db, summary)

    await db.commit()
    await db.refresh(visit)
    await log_action(db, "update", "visit", str(visit.id), current_user.id)
    return visit


@router.put("/{visit_id}/complete", response_model=VisitResponse)
async def complete_visit(visit_id: str, request: Request, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    visit = await get_visit_or_404(db, visit_id)
    if current_user.role != UserRole.admin and visit.doctor_id != current_user.id:
        await log_action(db, "unauthorized_edit_attempt", "visit", str(visit.id), current_user.id)
        raise ForbiddenError("אין הרשאה לעריכת ביקור זה")

    visit.status = VisitStatus.completed
    visit.end_time = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(visit)
    await log_action(db, "complete", "visit", str(visit.id), current_user.id)
    await log_activity(db, current_user.id, "UPDATE", "visit", visit.id, "השלים ביקור", request=request)
    return visit
