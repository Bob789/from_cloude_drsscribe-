from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.summary import Summary
from app.schemas.summary import SummaryResponse, SummaryUpdate
from app.tasks import process_summary
from app.services.audit_service import log_action
from app.services.activity_log_service import log_activity
from app.services.search_indexer import reindex_summary
from app.utils.id_resolver import get_summary_or_404, get_visit_or_404
from app.exceptions import NotFoundError, ForbiddenError
from app.models.user import UserRole
from app.utils.medical_encryption import decrypt_summary_fields, encrypt_summary_fields

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.post("/generate/{visit_id}", status_code=status.HTTP_202_ACCEPTED)
async def generate_summary(
    visit_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = await get_visit_or_404(db, visit_id)
    process_summary.delay(str(visit.id))
    await log_action(db, "generate_summary", "visit", str(visit.id), current_user.id)
    await log_activity(db, current_user.id, "CREATE", "summary", visit.id, "הפעיל יצירת סיכום אוטומטי", request=request)
    return {"message": "Summary generation started", "visit_id": str(visit.id)}


@router.get("/{summary_id}", response_model=SummaryResponse)
async def get_summary(
    summary_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    summary = await get_summary_or_404(db, summary_id)
    visit = await get_visit_or_404(db, str(summary.visit_id))
    if current_user.role != UserRole.admin and visit.doctor_id != current_user.id:
        raise ForbiddenError("אין הרשאה לצפות בסיכום זה")
    decrypt_summary_fields(summary)
    return summary


@router.get("/visit/{visit_id}", response_model=SummaryResponse)
async def get_summary_by_visit(
    visit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = await get_visit_or_404(db, visit_id)
    if current_user.role != UserRole.admin and visit.doctor_id != current_user.id:
        raise ForbiddenError("אין הרשאה לצפות בסיכום זה")
    result = await db.execute(select(Summary).where(Summary.visit_id == visit.id))
    summary = result.scalar_one_or_none()
    if not summary:
        raise NotFoundError("סיכום", visit_id)
    decrypt_summary_fields(summary)
    return summary


@router.put("/{summary_id}", response_model=SummaryResponse)
async def update_summary(
    summary_id: str,
    data: SummaryUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    summary = await get_summary_or_404(db, summary_id)
    visit = await get_visit_or_404(db, str(summary.visit_id))
    if current_user.role != UserRole.admin and visit.doctor_id != current_user.id:
        raise ForbiddenError("אין הרשאה לעדכן סיכום זה")
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(summary, key, value)
    encrypt_summary_fields(summary)
    await db.commit()
    await db.refresh(summary)
    await log_action(db, "update", "summary", str(summary.id), current_user.id)
    await log_activity(db, current_user.id, "UPDATE", "summary", summary.id, "עדכן סיכום", request=request)
    decrypt_summary_fields(summary)
    await reindex_summary(db, summary)
    return summary


@router.get("/{summary_id}/pdf")
async def export_summary_pdf(
    summary_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    summary = await get_summary_or_404(db, summary_id)
    visit = await get_visit_or_404(db, str(summary.visit_id))
    if current_user.role != UserRole.admin and visit.doctor_id != current_user.id:
        raise ForbiddenError("אין הרשאה לייצא סיכום זה")

    from app.services.pdf_service import generate_summary_pdf
    from fastapi.responses import Response

    # Decrypt medical data for PDF
    decrypt_summary_fields(summary)

    # Get patient info for the PDF
    from app.models.patient import Patient
    from app.utils.encryption import decrypt_field
    from app.services.patient_service import decrypt_patient_pii
    patient_result = await db.execute(select(Patient).where(Patient.id == visit.patient_id))
    patient = patient_result.scalar_one_or_none()

    # Decrypt id_number
    id_number = ""
    if patient and patient.id_number:
        try:
            id_number = decrypt_field(patient.id_number)
        except Exception:
            id_number = ""

    summary_data = {
        "chief_complaint": summary.chief_complaint,
        "findings": summary.findings,
        "diagnosis": summary.diagnosis,
        "treatment_plan": summary.treatment_plan,
        "recommendations": summary.recommendations,
    }
    # Decrypt patient PII
    patient_name = ""
    if patient:
        try:
            db.expunge(patient)
            decrypt_patient_pii(patient)
            patient_name = patient.name or ""
        except Exception:
            patient_name = patient.name or ""

    patient_data = {
        "name": patient_name,
        "id_number": id_number,
    } if patient else None
    visit_data = {
        "start_time": visit.start_time.isoformat() if visit.start_time else "",
        "doctor_name": current_user.name or "",
    }
    pdf_bytes = generate_summary_pdf(summary_data, patient=patient_data, visit=visit_data)
    await log_activity(db, current_user.id, "VIEW", "summary", summary.id, "ייצא סיכום ל-PDF", request=request)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=summary_{summary.display_id}.pdf"})
