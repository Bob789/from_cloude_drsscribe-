from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientListResponse
from app.services.patient_service import create_patient, list_patients, update_patient, search_patients, prepare_patient
from app.services.audit_service import log_action
from app.services.activity_log_service import log_activity
from app.utils.id_resolver import get_patient_or_404
from app.models.user import UserRole
from app.exceptions import NotFoundError, ForbiddenError

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientResponse, status_code=201)
async def create(
    data: PatientCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = await create_patient(db, data.model_dump(exclude_none=True), current_user.id, key_type=current_user.patient_key_type.value)
    await log_action(db, "create", "patient", str(patient.id), current_user.id)
    await log_activity(db, current_user.id, "CREATE", "patient", patient.id, f"יצר מטופל {patient.name}", request=request)
    return patient


@router.get("", response_model=PatientListResponse)
async def list_all(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort: str = Query("name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_patients(db, page, per_page, sort, current_user.id)


@router.get("/search", response_model=list[PatientResponse])
async def search(
    request: Request,
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = await search_patients(db, q, current_user.id)
    await log_activity(db, current_user.id, "SEARCH", "patient", description=f'חיפוש: "{q}"', metadata={"query": q, "results_count": len(results)}, request=request)
    return results


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_by_id(
    patient_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = await get_patient_or_404(db, patient_id)
    if current_user.role != UserRole.admin and patient.created_by != current_user.id:
        raise ForbiddenError("אין הרשאה לצפות במטופל זה")
    prepared = prepare_patient(db, patient)
    await log_activity(db, current_user.id, "VIEW", "patient", patient_id, f"צפה בכרטיס מטופל {prepared.name}", request=request)
    return prepared


@router.put("/{patient_id}", response_model=PatientResponse)
async def update(
    patient_id: str,
    data: PatientUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = await get_patient_or_404(db, patient_id)
    if current_user.role != UserRole.admin and patient.created_by != current_user.id:
        raise ForbiddenError("אין הרשאה לעדכן מטופל זה")
    patient = await update_patient(db, patient.id, data.model_dump(exclude_none=True))
    if not patient:
        raise NotFoundError("מטופל", patient_id)
    await log_action(db, "update", "patient", str(patient.id), current_user.id)
    await log_activity(db, current_user.id, "UPDATE", "patient", patient.id, f"עדכן מטופל {patient.name}", request=request)
    return patient
