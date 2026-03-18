import csv
import io
import json
import uuid as uuid_mod
from datetime import datetime, timezone
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

    writer.writerow([
        'patient_name', 'id_number', 'dob', 'phone', 'email',
        'blood_type', 'allergies', 'profession', 'address', 'insurance_info', 'notes',
        'visit_date', 'visit_status', 'visit_source',
        'chief_complaint', 'findings', 'diagnosis', 'treatment_plan',
        'recommendations', 'urgency', 'summary_notes',
    ])

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
    required = {'patient_name'}
    if not required.issubset(set(reader.fieldnames or [])):
        raise ValidationError("חסרה עמודת patient_name בקובץ CSV")

    created_patients = 0
    created_visits = 0
    errors = []
    # Cache patients by name to avoid duplicates within same import
    patient_cache: dict[str, Patient] = {}

    for row_num, row in enumerate(reader, start=2):
        try:
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
