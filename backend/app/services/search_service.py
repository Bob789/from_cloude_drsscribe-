import uuid as uuid_mod
import meilisearch
from sqlalchemy import select, or_, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.summary import Summary
from app.models.visit import Visit
from app.models.patient import Patient
from app.models.tag import Tag
from app.models.transcription import Transcription
from app.models.recording import Recording
from app.services.patient_service import decrypt_patient_pii
from app.utils.medical_encryption import decrypt_summary_fields, decrypt_transcription_fields

_client = None


def get_search_client():
    global _client
    if _client is None:
        _client = meilisearch.Client(settings.MEILISEARCH_URL, settings.MEILISEARCH_KEY)
    return _client


async def _get_patient_info(db: AsyncSession, visit_id):
    visit_r = await db.execute(select(Visit).where(Visit.id == visit_id))
    visit = visit_r.scalar_one_or_none()
    if not visit:
        return "", 0
    pat_r = await db.execute(select(Patient).where(Patient.id == visit.patient_id))
    pat = pat_r.scalar_one_or_none()
    if not pat:
        return "", 0
    db.expunge(pat)
    decrypt_patient_pii(pat)
    return pat.name, pat.display_id


async def _get_tags_for_summary(db: AsyncSession, summary_id: str) -> list[str]:
    r = await db.execute(select(Tag).where(and_(Tag.entity_type == "summary", Tag.entity_id == summary_id)))
    return [t.tag_label for t in r.scalars().all()]


async def search(query: str, index_name: str = "summaries", filters: str | None = None, offset: int = 0, limit: int = 20) -> dict:
    client = get_search_client()
    params = {"offset": offset, "limit": limit, "attributesToHighlight": ["*"]}
    if filters:
        params["filter"] = filters
    result = client.index(index_name).search(query, params)
    return {"hits": result["hits"], "total": result["estimatedTotalHits"], "offset": offset, "limit": limit}


async def combined_search(query: str, tags: list[str] | None = None, date_from: str | None = None, date_to: str | None = None, offset: int = 0, limit: int = 20, doctor_id: str | None = None) -> dict:
    filters = []
    if date_from:
        filters.append(f'created_at >= "{date_from}"')
    if date_to:
        filters.append(f'created_at <= "{date_to}"')
    if tags:
        tag_conditions = [f'tags = "{tag}"' for tag in tags]
        filters.append(f'({" OR ".join(tag_conditions)})')
    if doctor_id:
        filters.append(f'doctor_id = "{doctor_id}"')
    filter_str = " AND ".join(filters) if filters else None
    summaries = await search(query, "summaries", filter_str, offset, limit)
    transcriptions = await search(query, "transcriptions", filter_str, offset, limit)
    all_hits = summaries["hits"] + transcriptions["hits"]
    return {"hits": all_hits[:limit], "total": summaries["total"] + transcriptions["total"], "offset": offset, "limit": limit}


def _build_hit(s, patient_name: str, patient_display_id: int, tag_labels: list[str]) -> dict:
    # Decrypt summary fields if they are encrypted
    decrypt_summary_fields(s)

    diagnosis_str = ""
    if isinstance(s.diagnosis, list):
        diagnosis_str = ", ".join(str(d) for d in s.diagnosis)
    elif s.diagnosis:
        diagnosis_str = str(s.diagnosis)

    return {
        "id": str(s.id), "visit_id": str(s.visit_id),
        "patient_name": patient_name, "patient_display_id": patient_display_id,
        "chief_complaint": s.chief_complaint, "findings": s.findings,
        "diagnosis": diagnosis_str,
        "treatment_plan": s.treatment_plan, "recommendations": s.recommendations,
        "notes": s.notes,
        "urgency": s.urgency, "tags": tag_labels,
        "created_at": s.created_at.isoformat() if s.created_at else "",
    }


def _build_transcription_hit(t, patient_name: str, patient_display_id: int) -> dict:
    decrypt_transcription_fields(t)
    text = t.full_text or ""
    return {
        "id": str(t.id),
        "patient_name": patient_name, "patient_display_id": patient_display_id,
        "full_text": (text[:300] + "...") if len(text) > 300 else text,
        "created_at": t.created_at.isoformat() if t.created_at else "",
        "tags": [],
    }


def _is_uuid(s: str) -> bool:
    try:
        import uuid as uuid_mod
        uuid_mod.UUID(s)
        return True
    except ValueError:
        return False


def _apply_date_filters(stmt, date_from, date_to, date_col):
    if date_from:
        from datetime import datetime
        stmt = stmt.where(date_col >= datetime.fromisoformat(date_from))
    if date_to:
        from datetime import datetime
        stmt = stmt.where(date_col <= datetime.fromisoformat(date_to + "T23:59:59"))
    return stmt


async def search_by_tags(db: AsyncSession, tag_labels: list[str], date_from: str | None = None, date_to: str | None = None, offset: int = 0, limit: int = 20, urgency: str | None = None, doctor_id: uuid_mod.UUID | None = None) -> dict:
    tag_conditions = [Tag.tag_label.ilike(f"%{label}%") for label in tag_labels]
    tag_result = await db.execute(select(Tag.entity_id).where(and_(Tag.entity_type == "summary", or_(*tag_conditions))))
    entity_ids = [r[0] for r in tag_result.all()]
    if not entity_ids:
        return {"hits": [], "total": 0}

    summary_uuids = [uuid_mod.UUID(eid) for eid in entity_ids if _is_uuid(eid)]
    stmt = (
        select(Summary, Patient)
        .join(Visit, Summary.visit_id == Visit.id)
        .join(Patient, Visit.patient_id == Patient.id)
        .where(Summary.id.in_(summary_uuids))
    )
    if doctor_id:
        stmt = stmt.where(Visit.doctor_id == doctor_id)
    stmt = _apply_date_filters(stmt, date_from, date_to, Summary.created_at)
    if urgency:
        stmt = stmt.where(Summary.urgency == urgency)

    total_r = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_r.scalar()
    stmt = stmt.order_by(Summary.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)

    hits = []
    for s, pat in result.all():
        db.expunge(pat)
        decrypt_patient_pii(pat)
        stag_labels = await _get_tags_for_summary(db, str(s.id))
        hits.append(_build_hit(s, pat.name, pat.display_id, stag_labels))
    return {"hits": hits, "total": total}


async def search_db_text(db: AsyncSession, query: str, tag_labels: list[str] | None = None, date_from: str | None = None, date_to: str | None = None, offset: int = 0, limit: int = 20, urgency: str | None = None, doctor_id: uuid_mod.UUID | None = None) -> dict:
    tagged_ids = None
    if tag_labels:
        tag_conditions = [Tag.tag_label.ilike(f"%{label}%") for label in tag_labels]
        tag_result = await db.execute(select(Tag.entity_id).where(and_(Tag.entity_type == "summary", or_(*tag_conditions))))
        tagged_ids = [r[0] for r in tag_result.all()]
        if not tagged_ids:
            return {"hits": [], "total": 0}

    # Load summaries + patient data (no ILIKE — fields are encrypted)
    stmt = (
        select(Summary, Patient)
        .join(Visit, Summary.visit_id == Visit.id)
        .join(Patient, Visit.patient_id == Patient.id)
    )
    if doctor_id:
        stmt = stmt.where(Visit.doctor_id == doctor_id)
    if tagged_ids is not None:
        uuids = [uuid_mod.UUID(eid) for eid in tagged_ids if _is_uuid(eid)]
        stmt = stmt.where(Summary.id.in_(uuids))
    stmt = _apply_date_filters(stmt, date_from, date_to, Summary.created_at)
    if urgency:
        stmt = stmt.where(Summary.urgency == urgency)
    stmt = stmt.order_by(Summary.created_at.desc())
    result = await db.execute(stmt)

    # Decrypt in memory and match query text
    query_lower = query.lower()
    all_matches = []
    seen_visit_ids = set()
    for s, pat in result.all():
        db.expunge(s)
        db.expunge(pat)
        decrypt_summary_fields(s)
        decrypt_patient_pii(pat)

        fields = [s.chief_complaint, s.findings, s.treatment_plan, s.recommendations, s.notes, pat.name]
        if isinstance(s.diagnosis, list):
            fields.append(", ".join(str(d) for d in s.diagnosis))
        elif s.diagnosis:
            fields.append(str(s.diagnosis))

        if any(f and query_lower in str(f).lower() for f in fields):
            stag_labels = await _get_tags_for_summary(db, str(s.id))
            all_matches.append(_build_hit(s, pat.name, pat.display_id, stag_labels))
            seen_visit_ids.add(s.visit_id)

    total = len(all_matches)
    hits = all_matches[offset:offset + limit]

    # Also search transcription text (encrypted — decrypt in memory)
    if len(hits) < limit:
        trans_stmt = (
            select(Transcription, Patient)
            .join(Recording, Transcription.recording_id == Recording.id)
            .join(Visit, Recording.visit_id == Visit.id)
            .join(Patient, Visit.patient_id == Patient.id)
        )
        if doctor_id:
            trans_stmt = trans_stmt.where(Visit.doctor_id == doctor_id)
        if seen_visit_ids:
            trans_stmt = trans_stmt.where(Visit.id.notin_(seen_visit_ids))
        trans_stmt = trans_stmt.order_by(Transcription.created_at.desc())
        trans_result = await db.execute(trans_stmt)
        for t, pat in trans_result.all():
            db.expunge(t)
            db.expunge(pat)
            decrypt_transcription_fields(t)
            decrypt_patient_pii(pat)
            text = t.full_text or ""
            if query_lower in text.lower():
                hits.append(_build_transcription_hit(t, pat.name, pat.display_id))
                total += 1
                if len(hits) >= limit:
                    break

    return {"hits": hits, "total": total}
