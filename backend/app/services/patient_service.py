import uuid
import math
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.patient import Patient
from app.exceptions import DuplicateError
from app.utils.encryption import encrypt_field, decrypt_field, hash_field
from app.utils.logging import get_logger

logger = get_logger(__name__)


def encrypt_patient_pii(data: dict) -> dict:
    if "id_number" in data and data["id_number"]:
        data["id_number_hash"] = hash_field(data["id_number"])
        data["id_number"] = encrypt_field(data["id_number"])
    if "phone" in data and data["phone"]:
        data["phone"] = encrypt_field(data["phone"])
    if "name" in data and data["name"]:
        data["name"] = encrypt_field(data["name"])
    if "email" in data and data["email"]:
        data["email"] = encrypt_field(data["email"])
    return data


def decrypt_patient_pii(patient: Patient) -> Patient:
    for field in ("id_number", "phone", "name", "email"):
        try:
            val = getattr(patient, field, None)
            if val and len(val) > 50:  # encrypted values are long base64 strings
                setattr(patient, field, decrypt_field(val))
        except Exception as e:
            logger.error("decryption_failed", field=field, patient_id=str(patient.id), error=str(e))
            # For name, keep the value as-is (might be unencrypted legacy data)
            if field in ("name", "email"):
                pass  # keep original value
            else:
                setattr(patient, field, None)
    return patient


def prepare_patient(db, patient: Patient) -> Patient:
    db.expunge(patient)
    return decrypt_patient_pii(patient)


async def validate_patient_key(db: AsyncSession, data: dict, key_type: str, exclude_id: uuid.UUID | None = None):
    FIELD_LABELS = {"national_id": "תעודת זהות", "phone": "טלפון", "email": "אימייל"}
    label = FIELD_LABELS.get(key_type, key_type)

    field_name = "id_number" if key_type == "national_id" else key_type
    value = data.get(field_name)
    if not value:
        raise ValueError(f"השדה {label} הוא שדה חובה לפי הגדרות המזהה שלך")

    if key_type == "national_id":
        id_hash = hash_field(value)
        stmt = select(Patient).where(Patient.id_number_hash == id_hash)
        if exclude_id:
            stmt = stmt.where(Patient.id != exclude_id)
        existing = await db.execute(stmt)
        if existing.scalar_one_or_none():
            raise DuplicateError(label)
    elif key_type == "email":
        stmt = select(Patient).where(Patient.email == value)
        if exclude_id:
            stmt = stmt.where(Patient.id != exclude_id)
        existing = await db.execute(stmt)
        if existing.scalar_one_or_none():
            raise DuplicateError(label)
    elif key_type == "phone":
        phone_hash = hash_field(value)
        all_result = await db.execute(select(Patient))
        for p in all_result.scalars().all():
            if exclude_id and p.id == exclude_id:
                continue
            if p.phone:
                try:
                    decrypted = decrypt_field(p.phone)
                    if decrypted == value:
                        raise DuplicateError(label)
                except DuplicateError:
                    raise
                except Exception:
                    pass


async def create_patient(db: AsyncSession, data: dict, user_id: uuid.UUID, key_type: str = "national_id") -> Patient:
    await validate_patient_key(db, data, key_type)
    raw_id_number = data.get("id_number")
    data = encrypt_patient_pii(data)
    if raw_id_number and key_type != "national_id":
        existing = await db.execute(
            select(Patient).where(Patient.id_number_hash == data["id_number_hash"])
        )
        if existing.scalar_one_or_none():
            raise DuplicateError("תעודת זהות")
    patient = Patient(**data, created_by=user_id)
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return prepare_patient(db, patient)


async def get_patient(db: AsyncSession, patient_id: uuid.UUID) -> Patient | None:
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if patient:
        return prepare_patient(db, patient)
    return None


async def list_patients(db: AsyncSession, page: int = 1, per_page: int = 20, sort: str = "name", user_id: uuid.UUID | None = None) -> dict:
    sort_col = getattr(Patient, sort, Patient.name)
    base_filter = Patient.created_by == user_id if user_id else True
    total_result = await db.execute(select(func.count(Patient.id)).where(base_filter))
    total = total_result.scalar()
    offset = (page - 1) * per_page
    result = await db.execute(select(Patient).where(base_filter).order_by(sort_col).offset(offset).limit(per_page))
    patients = [prepare_patient(db, p) for p in result.scalars().all()]
    return {
        "items": patients,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": math.ceil(total / per_page) if total else 0,
    }


async def update_patient(db: AsyncSession, patient_id: uuid.UUID, data: dict) -> Patient | None:
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        return None
    raw_id_number = data.get("id_number")
    data = encrypt_patient_pii(data)
    if raw_id_number and data.get("id_number_hash"):
        existing = await db.execute(
            select(Patient).where(
                Patient.id_number_hash == data["id_number_hash"],
                Patient.id != patient_id,
            )
        )
        if existing.scalar_one_or_none():
            raise DuplicateError("תעודת זהות")
    for key, value in data.items():
        if value is not None:
            setattr(patient, key, value)
    await db.commit()
    await db.refresh(patient)
    return prepare_patient(db, patient)


async def search_patients(db: AsyncSession, query: str, user_id: uuid.UUID | None = None) -> list[Patient]:
    query = query.strip()
    if not query:
        return []

    digits = ''.join(c for c in query if c.isdigit())
    owner_filter = Patient.created_by == user_id if user_id else True

    # Name/email search via SQL ILIKE
    stmt = select(Patient).where(
        owner_filter,
        or_(
            Patient.name.ilike(f"%{query}%"),
            Patient.email.ilike(f"%{query}%"),
        )
    ).limit(50)
    result = await db.execute(stmt)
    prepared = [prepare_patient(db, p) for p in result.scalars().all()]
    matches = {p.id: p for p in prepared}

    # Phone search — encrypted field, must decrypt and filter in Python
    if len(digits) >= 3:
        all_result = await db.execute(select(Patient).where(owner_filter))
        all_prepared = [prepare_patient(db, p) for p in all_result.scalars().all()]
        for p in all_prepared:
            if p.id not in matches:
                if p.phone:
                    phone_digits = ''.join(c for c in p.phone if c.isdigit())
                    if digits in phone_digits:
                        matches[p.id] = p

    return list(matches.values())[:50]
