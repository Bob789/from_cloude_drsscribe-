import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User, UserRole
from app.models.patient_file import PatientFile, FileCategory
from app.exceptions import ForbiddenError
from app.schemas.patient_file import FileUploadResponse, FileListResponse, FileUpdateRequest
from app.services.storage_service import upload_file, get_signed_url, delete_file
from app.services.audit_service import log_action
from app.utils.id_resolver import get_patient_or_404, resolve_visit

router = APIRouter(prefix="/patients/{patient_id}/files", tags=["patient-files"])

ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/gif", "image/webp", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/dicom"}
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".doc", ".docx", ".dcm"}
MAX_FILE_SIZE = 50 * 1024 * 1024


def _to_response(pf: PatientFile) -> dict:
    return {"id": pf.id, "patient_id": str(pf.patient_id), "file_name": pf.file_name, "file_size": pf.file_size, "mime_type": pf.mime_type, "category": pf.category, "description": pf.description, "created_at": pf.created_at}


def _validate_file(filename: str, content_type: str | None, size: int):
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if filename and "." in filename else ""
    if ext and ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type not allowed: {ext}")
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"MIME type not allowed: {content_type}")
    if size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")


async def _get_patient(db: AsyncSession, patient_id: str, current_user: User | None = None):
    patient = await get_patient_or_404(db, patient_id)
    if current_user and current_user.role != UserRole.admin and patient.created_by != current_user.id:
        raise ForbiddenError("אין הרשאה לגשת לקבצי מטופל זה")
    return patient


async def _get_file(db: AsyncSession, patient_id, file_id: int, current_user: User | None = None):
    patient = await _get_patient(db, patient_id, current_user)
    result = await db.execute(select(PatientFile).where(PatientFile.id == file_id, PatientFile.patient_id == patient.id))
    pf = result.scalar_one_or_none()
    if not pf:
        raise HTTPException(status_code=404, detail="File not found")
    return patient, pf


async def _do_upload(db, patient, file: UploadFile, category: str, current_user, visit_uuid=None, description=None):
    content = await file.read()
    _validate_file(file.filename or "", file.content_type, len(content))
    ext = ("." + file.filename.rsplit(".", 1)[-1].lower()) if file.filename and "." in file.filename else ""
    key = f"patients/{patient.id}/files/{uuid.uuid4()}{ext}"
    await upload_file(content, key, file.content_type or "application/octet-stream")
    pf = PatientFile(
        patient_id=patient.id, visit_id=visit_uuid, uploaded_by=current_user.id,
        file_name=file.filename or "unknown", file_key=key, file_size=len(content),
        mime_type=file.content_type, category=category if category in [c.value for c in FileCategory] else "other",
        description=description,
    )
    db.add(pf)
    await db.commit()
    await db.refresh(pf)
    await log_action(db, "upload_file", "patient_file", str(pf.id), current_user.id)
    return pf


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_patient_file(patient_id: str, file: UploadFile = File(...), category: str = Form("other"), description: str = Form(None), visit_id: str = Form(None), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    patient = await _get_patient(db, patient_id, current_user)
    visit_uuid = None
    if visit_id:
        visit = await resolve_visit(db, visit_id)
        if visit:
            visit_uuid = visit.id
    pf = await _do_upload(db, patient, file, category, current_user, visit_uuid, description)
    return _to_response(pf)


@router.post("/upload-multiple", status_code=status.HTTP_201_CREATED)
async def upload_multiple_files(patient_id: str, files: list[UploadFile] = File(...), category: str = Form("other"), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    patient = await _get_patient(db, patient_id, current_user)
    return [_to_response(await _do_upload(db, patient, f, category, current_user)) for f in files]


@router.get("/")
async def list_files(patient_id: str, category: str | None = None, visit_id: str | None = None, page: int = 1, per_page: int = 20, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    patient = await _get_patient(db, patient_id, current_user)
    query = select(PatientFile).where(PatientFile.patient_id == patient.id)
    if category:
        query = query.where(PatientFile.category == category)
    if visit_id:
        visit = await resolve_visit(db, visit_id)
        if visit:
            query = query.where(PatientFile.visit_id == visit.id)
    total = (await db.execute(select(sa_func.count()).select_from(query.subquery()))).scalar() or 0
    query = query.order_by(PatientFile.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    files = (await db.execute(query)).scalars().all()
    return {"files": [_to_response(f) for f in files], "total": total}


@router.get("/{file_id}")
async def get_file(patient_id: str, file_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, pf = await _get_file(db, patient_id, file_id, current_user)
    return _to_response(pf)


@router.get("/{file_id}/download")
async def download_file(patient_id: str, file_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, pf = await _get_file(db, patient_id, file_id, current_user)
    signed_url = await get_signed_url(pf.file_key, expires=3600)
    await log_action(db, "download_file", "patient_file", str(pf.id), current_user.id)
    return {"download_url": signed_url, "file_name": pf.file_name, "expires_in": 3600}


@router.get("/{file_id}/preview")
async def preview_file(patient_id: str, file_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, pf = await _get_file(db, patient_id, file_id, current_user)
    signed_url = await get_signed_url(pf.file_key, expires=3600)
    is_previewable = pf.mime_type in {"image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"}
    return {"preview_url": signed_url, "file_name": pf.file_name, "mime_type": pf.mime_type, "is_previewable": is_previewable, "expires_in": 3600}


@router.put("/{file_id}")
async def update_file(patient_id: str, file_id: int, data: FileUpdateRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, pf = await _get_file(db, patient_id, file_id, current_user)
    if data.category is not None:
        pf.category = data.category if data.category in [c.value for c in FileCategory] else pf.category
    if data.description is not None:
        pf.description = data.description
    if data.visit_id is not None:
        visit = await resolve_visit(db, data.visit_id)
        if visit:
            pf.visit_id = visit.id
    await db.commit()
    await db.refresh(pf)
    return _to_response(pf)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient_file(patient_id: str, file_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, pf = await _get_file(db, patient_id, file_id, current_user)
    try:
        await delete_file(pf.file_key)
    except Exception:
        pass
    await log_action(db, "delete_file", "patient_file", str(pf.id), current_user.id)
    await db.delete(pf)
    await db.commit()
