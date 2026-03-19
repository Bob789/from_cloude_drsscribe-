import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User, UserRole
from app.models.transcription import Transcription
from app.models.recording import Recording
from app.models.visit import Visit
from app.schemas.transcription import TranscriptionResponse, TranscriptionUpdate
from app.tasks import process_transcription
from app.services.audit_service import log_action

router = APIRouter(prefix="/transcriptions", tags=["transcriptions"])


async def _get_transcription_with_ownership(
    transcription_id: uuid.UUID,
    db: AsyncSession,
    current_user: User,
) -> Transcription:
    result = await db.execute(select(Transcription).where(Transcription.id == transcription_id))
    transcription = result.scalar_one_or_none()
    if not transcription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")

    if current_user.role != UserRole.admin:
        rec_result = await db.execute(select(Recording).where(Recording.id == transcription.recording_id))
        recording = rec_result.scalar_one_or_none()
        if recording:
            visit_result = await db.execute(select(Visit).where(Visit.id == recording.visit_id))
            visit = visit_result.scalar_one_or_none()
            if visit and visit.doctor_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return transcription


@router.post("/process/{recording_id}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_transcription(
    recording_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    process_transcription.delay(str(recording_id))
    await log_action(db, "trigger_transcription", "recording", str(recording_id), current_user.id)
    return {"message": "Transcription processing started", "recording_id": str(recording_id)}


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(
    transcription_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _get_transcription_with_ownership(transcription_id, db, current_user)


@router.put("/{transcription_id}", response_model=TranscriptionResponse)
async def update_transcription(
    transcription_id: uuid.UUID,
    data: TranscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transcription = await _get_transcription_with_ownership(transcription_id, db, current_user)
    if data.full_text is not None:
        transcription.full_text = data.full_text
    if data.speakers_json is not None:
        transcription.speakers_json = data.speakers_json
    await db.commit()
    await db.refresh(transcription)
    await log_action(db, "update", "transcription", str(transcription.id), current_user.id)
    return transcription
