import csv
import io
import json
import uuid as uuid_mod
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, Request, Query, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, delete as sa_delete
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
from app.models.patient import Patient
from app.models.visit import Visit, VisitStatus
from app.models.summary import Summary, SummaryStatus
from app.models.recording import Recording
from app.models.transcription import Transcription
from app.models.tag import Tag
from app.models.patient_file import PatientFile
from app.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/patients", tags=["patients"])

# ─── CSV Field Mapping (friendly ↔ internal) ──────────────────────────────────
# Friendly names hide real DB column names from external users
CSV_EXPORT_HEADERS = [
    "Full Name", "National ID", "Date of Birth", "Phone Number", "Email Address",
    "Blood Type", "Allergies", "Occupation", "Home Address", "Insurance Details", "General Notes",
    "Visit Date", "Visit Status", "Visit Source",
    "Main Complaint", "Clinical Findings", "Diagnosis", "Treatment", "Follow-up",
    "Priority", "Clinical Notes",
]

_FRIENDLY_TO_INTERNAL = {
    "Full Name": "patient_name", "National ID": "id_number",
    "Date of Birth": "dob", "Phone Number": "phone", "Email Address": "email",
    "Blood Type": "blood_type", "Allergies": "allergies", "Occupation": "profession",
    "Home Address": "address", "Insurance Details": "insurance_info", "General Notes": "notes",
    "Visit Date": "visit_date", "Visit Status": "visit_status", "Visit Source": "visit_source",
    "Main Complaint": "chief_complaint", "Clinical Findings": "findings",
    "Diagnosis": "diagnosis", "Treatment": "treatment_plan", "Follow-up": "recommendations",
    "Priority": "urgency", "Clinical Notes": "summary_notes",
}

_INTERNAL_TO_FRIENDLY = {v: k for k, v in _FRIENDLY_TO_INTERNAL.items()}


def _map_row_to_internal(row: dict) -> dict:
    """Map CSV row with friendly headers to internal field names."""
    mapped = {}
    for key, value in row.items():
        internal = _FRIENDLY_TO_INTERNAL.get(key.strip(), key.strip())
        mapped[internal] = value
    return mapped


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


@router.delete("/{patient_id}", status_code=status.HTTP_200_OK)
async def delete_patient(
    patient_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a patient and ALL related data permanently."""
    patient = await get_patient_or_404(db, patient_id)
    if current_user.role != UserRole.admin and patient.created_by != current_user.id:
        raise ForbiddenError("אין הרשאה למחוק מטופל זה")

    patient_name = patient.name
    patient_uuid = patient.id

    # Get all visits for this patient
    visits = (await db.execute(select(Visit).where(Visit.patient_id == patient_uuid))).scalars().all()
    visit_ids = [v.id for v in visits]

    if visit_ids:
        # Get all summaries for these visits
        summaries = (await db.execute(select(Summary).where(Summary.visit_id.in_(visit_ids)))).scalars().all()
        summary_ids = [s.id for s in summaries]

        # Delete tags linked to summaries
        if summary_ids:
            await db.execute(sa_delete(Tag).where(Tag.entity_type == "summary", Tag.entity_id.in_([str(sid) for sid in summary_ids])))

        # Get all recordings for these visits
        recordings = (await db.execute(select(Recording).where(Recording.visit_id.in_(visit_ids)))).scalars().all()
        recording_ids = [r.id for r in recordings]

        # Delete transcriptions linked to recordings
        if recording_ids:
            await db.execute(sa_delete(Transcription).where(Transcription.recording_id.in_(recording_ids)))

        # Delete recordings
        if recording_ids:
            await db.execute(sa_delete(Recording).where(Recording.id.in_(recording_ids)))

        # Delete summaries
        if summary_ids:
            await db.execute(sa_delete(Summary).where(Summary.id.in_(summary_ids)))

        # Delete visits
        await db.execute(sa_delete(Visit).where(Visit.id.in_(visit_ids)))

    # Delete patient files
    await db.execute(sa_delete(PatientFile).where(PatientFile.patient_id == patient_uuid))

    # Delete the patient
    await db.delete(patient)
    await db.commit()

    await log_action(db, "delete", "patient", str(patient_uuid), current_user.id)
    await log_activity(db, current_user.id, "DELETE", "patient", patient_uuid, f"מחק מטופל {patient_name} וכל ההיסטוריה שלו", request=request)

    return {"ok": True, "message": f"המטופל {patient_name} וכל ההיסטוריה שלו נמחקו לצמיתות"}


# ─── CSV Export ────────────────────────────────────────────────────────────────

@router.get("/export/csv")
async def export_patients_csv(
    ids: str = Query(None, description="Comma-separated patient display_ids, or empty for all"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export selected patients + visit history as CSV. Pass ids=1,2,3 or omit for all."""
    from app.services.patient_service import decrypt_patient_pii
    from app.utils.medical_encryption import decrypt_summary_fields

    stmt = select(Patient).where(Patient.created_by == current_user.id).order_by(Patient.name)
    if ids:
        id_list = [int(x.strip()) for x in ids.split(",") if x.strip().isdigit()]
        if id_list:
            stmt = stmt.where(Patient.display_id.in_(id_list))

    patients = (await db.execute(stmt)).scalars().all()

    output = io.StringIO()
    output.write('\ufeff')  # BOM for Excel Hebrew
    writer = csv.writer(output)

    writer.writerow(CSV_EXPORT_HEADERS)

    for patient in patients:
        # Decrypt PII before export
        db.expunge(patient)
        decrypt_patient_pii(patient)

        visits = (await db.execute(
            select(Visit).where(Visit.patient_id == patient.id).order_by(Visit.start_time)
        )).scalars().all()

        patient_base = [
            patient.name or '',
            patient.id_number or '',
            str(patient.dob) if patient.dob else '',
            patient.phone or '',
            patient.email or '',
            patient.blood_type or '',
            json.dumps(patient.allergies, ensure_ascii=False) if patient.allergies else '',
            patient.profession or '',
            patient.address or '',
            patient.insurance_info or '',
            patient.notes or '',
        ]

        if not visits:
            writer.writerow(patient_base + [''] * 10)
        else:
            for visit in visits:
                summary = (await db.execute(
                    select(Summary).where(Summary.visit_id == visit.id).order_by(Summary.created_at.desc())
                )).scalars().first()

                # Decrypt summary fields
                if summary:
                    decrypt_summary_fields(summary)

                row = patient_base + [
                    visit.start_time.isoformat() if visit.start_time else '',
                    visit.status.value if visit.status else '',
                    visit.source or '',
                    summary.chief_complaint or '' if summary else '',
                    summary.findings or '' if summary else '',
                    json.dumps(summary.diagnosis, ensure_ascii=False) if summary and summary.diagnosis else '',
                    summary.treatment_plan or '' if summary else '',
                    summary.recommendations or '' if summary else '',
                    summary.urgency or '' if summary else '',
                    summary.notes or '' if summary else '',
                ]
                writer.writerow(row)

    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="patients_export_{timestamp}.csv"'},
    )


# ─── CSV Import ────────────────────────────────────────────────────────────────

@router.post("/import/csv")
async def import_patients_csv(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Import patients + visit history from CSV."""
    content = await file.read()
    # Try UTF-8-BOM, then UTF-8, then latin-1
    for enc in ('utf-8-sig', 'utf-8', 'latin-1'):
        try:
            text = content.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValidationError("לא ניתן לקרוא את הקובץ — ודא שהוא בפורמט UTF-8")

    reader = csv.DictReader(io.StringIO(text))
    required_friendly = {'Full Name'}
    required_legacy = {'patient_name'}
    fieldnames = set(reader.fieldnames or [])
    if not required_friendly.issubset(fieldnames) and not required_legacy.issubset(fieldnames):
        raise ValidationError("חסרה עמודת 'Full Name' בקובץ CSV")

    # Detect whether the CSV uses friendly or legacy headers
    uses_friendly = 'Full Name' in fieldnames

    created_patients = 0
    created_visits = 0
    errors = []
    # Cache patients by name to avoid duplicates within same import
    patient_cache: dict[str, Patient] = {}

    for row_num, row in enumerate(reader, start=2):
        try:
            # Map friendly headers to internal names if needed
            if uses_friendly:
                row = _map_row_to_internal(row)

            name = (row.get('patient_name') or '').strip()
            if not name:
                continue

            # Get or create patient
            if name in patient_cache:
                patient = patient_cache[name]
            else:
                # Check if patient already exists for this doctor
                existing = (await db.execute(
                    select(Patient).where(Patient.name == name, Patient.created_by == current_user.id)
                )).scalars().first()

                if existing:
                    patient = existing
                else:
                    allergies_raw = row.get('allergies', '')
                    try:
                        allergies = json.loads(allergies_raw) if allergies_raw else None
                    except (json.JSONDecodeError, TypeError):
                        allergies = [allergies_raw] if allergies_raw else None

                    dob = None
                    dob_raw = (row.get('dob') or '').strip()
                    if dob_raw:
                        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
                            try:
                                dob = datetime.strptime(dob_raw, fmt).date()
                                break
                            except ValueError:
                                continue

                    patient = Patient(
                        name=name,
                        id_number=row.get('id_number', '').strip() or None,
                        dob=dob,
                        phone=row.get('phone', '').strip() or None,
                        email=row.get('email', '').strip() or None,
                        blood_type=row.get('blood_type', '').strip() or None,
                        allergies=allergies,
                        profession=row.get('profession', '').strip() or None,
                        address=row.get('address', '').strip() or None,
                        insurance_info=row.get('insurance_info', '').strip() or None,
                        notes=row.get('notes', '').strip() or None,
                        created_by=current_user.id,
                    )
                    db.add(patient)
                    await db.flush()
                    created_patients += 1

                patient_cache[name] = patient

            # Create visit if visit_date exists
            visit_date_raw = (row.get('visit_date') or '').strip()
            if visit_date_raw:
                try:
                    visit_time = datetime.fromisoformat(visit_date_raw)
                except ValueError:
                    visit_time = datetime.now(timezone.utc)

                visit_status_raw = (row.get('visit_status') or 'completed').strip()
                try:
                    visit_status = VisitStatus(visit_status_raw)
                except ValueError:
                    visit_status = VisitStatus.completed

                visit = Visit(
                    patient_id=patient.id,
                    doctor_id=current_user.id,
                    start_time=visit_time,
                    end_time=visit_time,
                    status=visit_status,
                    source=row.get('visit_source', 'import').strip() or 'import',
                )
                db.add(visit)
                await db.flush()
                created_visits += 1

                # Create summary if any summary field exists
                chief = (row.get('chief_complaint') or '').strip()
                findings = (row.get('findings') or '').strip()
                treatment = (row.get('treatment_plan') or '').strip()
                recommendations = (row.get('recommendations') or '').strip()

                if chief or findings or treatment or recommendations:
                    diag_raw = (row.get('diagnosis') or '').strip()
                    try:
                        diagnosis = json.loads(diag_raw) if diag_raw else None
                    except (json.JSONDecodeError, TypeError):
                        diagnosis = None

                    summary = Summary(
                        visit_id=visit.id,
                        chief_complaint=chief or None,
                        findings=findings or None,
                        diagnosis=diagnosis,
                        treatment_plan=treatment or None,
                        recommendations=recommendations or None,
                        urgency=(row.get('urgency') or 'low').strip(),
                        source='import',
                        notes=(row.get('summary_notes') or '').strip() or None,
                        status=SummaryStatus.done,
                    )
                    db.add(summary)

        except Exception as e:
            errors.append(f"שורה {row_num}: {str(e)[:80]}")
            if len(errors) > 20:
                break

    await db.commit()

    await log_activity(db, current_user.id, "IMPORT", "patient", description=f"ייבא {created_patients} מטופלים ו-{created_visits} ביקורים מ-CSV", request=request)

    return {
        "ok": True,
        "created_patients": created_patients,
        "created_visits": created_visits,
        "errors": errors,
    }


# ─── Sample CSV Download ──────────────────────────────────────────────────────

@router.get("/import/sample-csv")
async def download_sample_csv(
    current_user: User = Depends(get_current_user),
):
    """Download a sample CSV file with one example row showing the expected format."""
    output = io.StringIO()
    output.write('\ufeff')  # BOM for Excel Hebrew
    writer = csv.writer(output)

    writer.writerow(CSV_EXPORT_HEADERS)

    writer.writerow([
        "Israel Israeli", "123456789", "1985-03-15", "+972-50-1234567", "israel@example.com",
        "A+", '["Penicillin"]', "Engineer", "123 Herzl St, Tel Aviv", "Maccabi", "Regular checkup patient",
        "2025-01-15T10:00:00", "completed", "clinic",
        "Headache for 3 days", "BP 120/80, Temp 37.2", '[{"code":"R51","description":"Headache"}]',
        "Paracetamol 500mg x3/day", "Follow-up in 2 weeks", "low", "",
    ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="import_template.csv"'},
    )


# ─── Handwritten Image Import (OpenAI Vision) ─────────────────────────────────

@router.post("/import/handwritten")
async def import_from_handwritten_images(
    request: Request,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Import a patient from handwritten document images using OpenAI Vision."""
    from app.services.handwritten_import_service import extract_patient_from_images

    if not files:
        raise ValidationError("יש להעלות לפחות תמונה אחת")
    if len(files) > 10:
        raise ValidationError("ניתן להעלות עד 10 תמונות בכל פעם")

    ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    MAX_SIZE = 20 * 1024 * 1024  # 20MB per image

    image_data_list = []
    for f in files:
        # Infer content type from extension if not set or generic
        content_type = f.content_type
        if not content_type or content_type == "application/octet-stream":
            import mimetypes
            ext = "." + (f.filename or "").rsplit(".", 1)[-1].lower() if f.filename and "." in f.filename else ""
            content_type = mimetypes.guess_type(f.filename or "")[0] or ""

        if content_type not in ALLOWED_TYPES:
            # Fallback: check extension
            ext = "." + (f.filename or "").rsplit(".", 1)[-1].lower() if f.filename and "." in f.filename else ""
            if ext not in ALLOWED_EXTENSIONS:
                raise ValidationError(f"סוג קובץ {f.content_type} אינו נתמך. השתמש ב-JPEG, PNG, WebP או GIF")
            content_type = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp", "gif": "image/gif"}.get(ext.lstrip("."), "image/jpeg")

        data = await f.read()
        if len(data) > MAX_SIZE:
            raise ValidationError(f"הקובץ {f.filename} גדול מדי (מקסימום 20MB)")
        image_data_list.append({"data": data, "content_type": content_type, "filename": f.filename})

    try:
        extracted = await extract_patient_from_images(image_data_list)
    except Exception as e:
        logger.error("handwritten_import_failed", error=str(e))
        raise ValidationError(f"שגיאה בעיבוד התמונות: {str(e)[:100]}")

    # Create patient from extracted data
    patient_data = {
        "name": extracted.get("name", "").strip(),
        "id_number": extracted.get("id_number", "").strip() or None,
        "phone": extracted.get("phone", "").strip() or None,
        "email": extracted.get("email", "").strip() or None,
        "blood_type": extracted.get("blood_type", "").strip() or None,
        "profession": extracted.get("profession", "").strip() or None,
        "address": extracted.get("address", "").strip() or None,
        "insurance_info": extracted.get("insurance_info", "").strip() or None,
        "notes": extracted.get("notes", "").strip() or None,
    }

    dob_raw = extracted.get("dob", "").strip()
    if dob_raw:
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d.%m.%Y', '%d-%m-%Y'):
            try:
                patient_data["dob"] = datetime.strptime(dob_raw, fmt).date()
                break
            except ValueError:
                continue

    allergies_raw = extracted.get("allergies")
    if allergies_raw:
        if isinstance(allergies_raw, list):
            patient_data["allergies"] = allergies_raw
        elif isinstance(allergies_raw, str):
            patient_data["allergies"] = [a.strip() for a in allergies_raw.split(",") if a.strip()]

    if not patient_data["name"]:
        raise ValidationError("לא ניתן היה לזהות שם מטופל מהתמונות")

    from app.services.patient_service import encrypt_patient_pii
    patient_data = {k: v for k, v in patient_data.items() if v is not None}
    patient_data = encrypt_patient_pii(patient_data)
    patient = Patient(**patient_data, created_by=current_user.id)
    db.add(patient)
    await db.flush()

    created_visits = 0
    # Create a visit + summary if medical content was found
    medical = extracted.get("medical_summary", {})
    if medical and any(medical.get(f) for f in ("chief_complaint", "findings", "treatment_plan", "recommendations", "diagnosis_text")):
        visit = Visit(
            patient_id=patient.id,
            doctor_id=current_user.id,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            status=VisitStatus.completed,
            source="handwritten_import",
        )
        db.add(visit)
        await db.flush()
        created_visits = 1

        diag_text = medical.get("diagnosis_text", "").strip()
        diagnosis = [{"code": "", "description": diag_text}] if diag_text else None

        summary = Summary(
            visit_id=visit.id,
            chief_complaint=medical.get("chief_complaint", "").strip() or None,
            findings=medical.get("findings", "").strip() or None,
            diagnosis=diagnosis,
            treatment_plan=medical.get("treatment_plan", "").strip() or None,
            recommendations=medical.get("recommendations", "").strip() or None,
            urgency=medical.get("urgency", "low").strip() or "low",
            source="handwritten_import",
            status=SummaryStatus.done,
        )
        db.add(summary)

    await db.commit()

    # Prepare response with decrypted data
    from app.services.patient_service import decrypt_patient_pii
    db.expunge(patient)
    decrypt_patient_pii(patient)

    await log_action(db, "create", "patient", str(patient.id), current_user.id)
    await log_activity(db, current_user.id, "IMPORT", "patient", patient.id, f"ייבא מטופל {patient.name} מתמונות כתב יד", request=request)

    return {
        "ok": True,
        "patient": {
            "id": str(patient.id),
            "name": patient.name,
            "display_id": patient.display_id,
        },
        "created_visits": created_visits,
        "extracted_data": extracted,
    }
