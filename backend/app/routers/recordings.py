import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, status
from fastapi.responses import Response
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User, UserRole
from app.models.recording import Recording
from app.models.recording_chunk import RecordingChunk
from app.models.visit import Visit
from app.schemas.recording import RecordingResponse, RecordingUploadResponse, ChunkUploadResponse, FinalizeResponse
from app.services.storage_service import upload_file, get_signed_url, get_s3_client
from app.services.audit_service import log_action
from app.services.activity_log_service import log_activity
from app.utils.id_resolver import get_visit_or_404
from app.utils.encryption import encrypt_audio, decrypt_audio
from app.tasks import process_transcription_chunked
from app.exceptions import ValidationError, NotFoundError, ForbiddenError
from app.config import settings

router = APIRouter(prefix="/recordings", tags=["recordings"])

ALLOWED_FORMATS = {"audio/webm", "audio/wav", "audio/flac", "audio/ogg", "audio/mpeg", "audio/x-wav"}
MAX_FILE_SIZE = 500 * 1024 * 1024
MAX_CHUNK_SIZE = 25 * 1024 * 1024


@router.post("/upload", response_model=RecordingUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_recording(
    visit_id: uuid.UUID,
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type and file.content_type not in ALLOWED_FORMATS:
        raise ValidationError(f"פורמט שמע לא נתמך: {file.content_type}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise ValidationError("הקובץ גדול מדי (מקסימום 500MB)")

    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "webm"
    key = f"recordings/{visit_id}/{uuid.uuid4()}.{ext}"

    encrypted_content, encrypted_dek = encrypt_audio(content)
    await upload_file(encrypted_content, key, file.content_type or "audio/webm")

    recording = Recording(
        visit_id=visit_id,
        audio_url=key,
        format=ext,
        file_size=len(content),
        encryption_key=encrypted_dek,
    )
    db.add(recording)
    await db.commit()
    await db.refresh(recording)
    await log_action(db, "upload", "recording", str(recording.id), current_user.id)
    await log_activity(db, current_user.id, "UPLOAD", "recording", recording.id, "העלה הקלטה", request=request)
    return RecordingUploadResponse(id=recording.id)


@router.post("/upload-chunk", response_model=ChunkUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_chunk(
    file: UploadFile = File(...),
    visit_id: str = Form(...),
    chunk_index: int = Form(...),
    is_final: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = await get_visit_or_404(db, visit_id)

    if file.content_type and file.content_type not in ALLOWED_FORMATS:
        raise ValidationError(f"פורמט שמע לא נתמך: {file.content_type}")

    content = await file.read()
    if len(content) > MAX_CHUNK_SIZE:
        raise ValidationError("הקטע גדול מדי (מקסימום 25MB)")

    key = f"recordings/{visit.id}/chunk_{chunk_index:04d}.webm"
    await upload_file(content, key, file.content_type or "audio/webm")

    chunk = RecordingChunk(
        visit_id=visit.id,
        chunk_index=chunk_index,
        audio_url=key,
        file_size=len(content),
    )
    db.add(chunk)
    await db.commit()
    await db.refresh(chunk)
    await log_action(db, "upload_chunk", "recording_chunk", str(chunk.id), current_user.id)

    if is_final:
        await _finalize_visit_recording(db, visit, current_user)

    return ChunkUploadResponse(chunk_id=chunk.id, chunk_index=chunk_index)


@router.post("/finalize/{visit_id}", response_model=FinalizeResponse)
async def finalize_recording(
    visit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = await get_visit_or_404(db, visit_id)

    recording = await _finalize_visit_recording(db, visit, current_user)

    chunks_q = await db.execute(
        select(sa_func.count(RecordingChunk.id)).where(RecordingChunk.visit_id == visit.id)
    )
    chunk_count = chunks_q.scalar() or 0

    return FinalizeResponse(
        recording_id=recording.id,
        chunk_count=chunk_count,
        total_size=recording.file_size or 0,
    )


async def _finalize_visit_recording(db: AsyncSession, visit: Visit, user: User) -> Recording:
    chunks_q = await db.execute(
        select(RecordingChunk)
        .where(RecordingChunk.visit_id == visit.id)
        .order_by(RecordingChunk.chunk_index)
    )
    chunks = chunks_q.scalars().all()
    if not chunks:
        raise ValidationError("לא נמצאו קטעי הקלטה לביקור זה")

    total_size = sum(c.file_size or 0 for c in chunks)
    total_duration = sum(c.duration_seconds or 0 for c in chunks)

    recording = Recording(
        visit_id=visit.id,
        audio_url=f"recordings/{visit.id}/chunked",
        format="webm",
        file_size=total_size,
        duration_seconds=total_duration if total_duration > 0 else None,
    )
    db.add(recording)
    await db.commit()
    await db.refresh(recording)
    await log_action(db, "finalize_recording", "recording", str(recording.id), user.id)

    process_transcription_chunked.delay(str(visit.id), str(recording.id))
    return recording


@router.get("/{recording_id}/audio")
async def download_audio(
    recording_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Recording).where(Recording.id == recording_id))
    recording = result.scalar_one_or_none()
    if not recording:
        raise NotFoundError("הקלטה", str(recording_id))

    visit_result = await db.execute(select(Visit).where(Visit.id == recording.visit_id))
    visit = visit_result.scalar_one_or_none()
    if current_user.role != UserRole.admin and visit and visit.doctor_id != current_user.id:
        raise ForbiddenError("אין הרשאה להאזין להקלטה זו")

    await log_action(db, "download", "recording", str(recording.id), current_user.id)

    if recording.encryption_key:
        # Proxy-decrypt: fetch encrypted bytes, decrypt, stream to client
        client = get_s3_client()
        s3_response = client.get_object(Bucket=settings.S3_BUCKET, Key=recording.audio_url)
        encrypted_data = s3_response["Body"].read()
        audio_data = decrypt_audio(encrypted_data, recording.encryption_key)
        mime = f"audio/{recording.format}" if recording.format else "audio/webm"
        return Response(content=audio_data, media_type=mime)

    # Legacy (unencrypted) recordings: return presigned URL
    signed_url = await get_signed_url(recording.audio_url)
    return {"url": signed_url, "expires_in": 3600}
