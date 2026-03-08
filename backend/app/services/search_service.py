import meilisearch
from sqlalchemy import select, or_, func, and_, cast, Text as SAText
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.summary import Summary
from app.models.visit import Visit
from app.models.patient import Patient
from app.models.tag import Tag
from app.models.transcription import Transcription
from app.models.recording import Recording

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


async def combined_search(query: str, tags: list[str] | None = None, date_from: str | None = None, date_to: str | None = None, offset: int = 0, limit: int = 20) -> dict:
    filters = []
    if date_from:
        filters.append(f'created_at >= "{date_from}"')
    if date_to:
        filters.append(f'created_at <= "{date_to}"')
    if tags:
        tag_conditions = [f'tags = "{tag}"' for tag in tags]
        filters.append(f'({" OR ".join(tag_conditions)})')
    filter_str = " AND ".join(filters) if filters else None
    summaries = await search(query, "summaries", filter_str, offset, limit)
    transcriptions = await search(query, "transcriptions", filter_str, offset, limit)
    all_hits = summaries["hits"] + transcriptions["hits"]
    return {"hits": all_hits[:limit], "total": summaries["total"] + transcriptions["total"], "offset": offset, "limit": limit}


def _build_hit(s, patient_name: str, patient_display_id: int, tag_labels: list[str]) -> dict:
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


async def search_by_tags(db: AsyncSession, tag_labels: list[str], date_from: str | None = None, date_to: str | None = None, offset: int = 0, limit: int = 20, urgency: str | None = None) -> dict:
    tag_conditions = [Tag.tag_label.ilike(f"%{label}%") for label in tag_labels]
    tag_result = await db.execute(select(Tag.entity_id).where(and_(Tag.entity_type == "summary", or_(*tag_conditions))))
    entity_ids = [r[0] for r in tag_result.all()]
    if not entity_ids:
        return {"hits": [], "total": 0}

    import uuid as uuid_mod
    summary_uuids = [uuid_mod.UUID(eid) for eid in entity_ids if _is_uuid(eid)]
    stmt = (
        select(Summary, Patient.name, Patient.display_id)
        .join(Visit, Summary.visit_id == Visit.id)
        .join(Patient, Visit.patient_id == Patient.id)
        .where(Summary.id.in_(summary_uuids))
    )
    stmt = _apply_date_filters(stmt, date_from, date_to, Summary.created_at)
    if urgency:
        stmt = stmt.where(Summary.urgency == urgency)

    total_r = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_r.scalar()
    stmt = stmt.order_by(Summary.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)

    hits = []
    for s, patient_name, patient_display_id in result.all():
        stag_labels = await _get_tags_for_summary(db, str(s.id))
        hits.append(_build_hit(s, patient_name, patient_display_id, stag_labels))
    return {"hits": hits, "total": total}


async def search_db_text(db: AsyncSession, query: str, tag_labels: list[str] | None = None, date_from: str | None = None, date_to: str | None = None, offset: int = 0, limit: int = 20, urgency: str | None = None) -> dict:
    pattern = f"%{query}%"

    tagged_ids = None
    if tag_labels:
        tag_conditions = [Tag.tag_label.ilike(f"%{label}%") for label in tag_labels]
        tag_result = await db.execute(select(Tag.entity_id).where(and_(Tag.entity_type == "summary", or_(*tag_conditions))))
        tagged_ids = [r[0] for r in tag_result.all()]
        if not tagged_ids:
            return {"hits": [], "total": 0}

    stmt = (
        select(Summary, Patient.name, Patient.display_id)
        .join(Visit, Summary.visit_id == Visit.id)
        .join(Patient, Visit.patient_id == Patient.id)
        .where(or_(
            Summary.chief_complaint.ilike(pattern),
            Summary.findings.ilike(pattern),
            Summary.treatment_plan.ilike(pattern),
            Summary.recommendations.ilike(pattern),
            Summary.notes.ilike(pattern),
            cast(Summary.diagnosis, SAText).ilike(pattern),
            Patient.name.ilike(pattern),
        ))
    )

    if tagged_ids is not None:
        import uuid as uuid_mod
        uuids = [uuid_mod.UUID(eid) for eid in tagged_ids if _is_uuid(eid)]
        stmt = stmt.where(Summary.id.in_(uuids))
    stmt = _apply_date_filters(stmt, date_from, date_to, Summary.created_at)
    if urgency:
        stmt = stmt.where(Summary.urgency == urgency)

    total_r = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_r.scalar()
    stmt = stmt.order_by(Summary.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)

    hits = []
    seen_visit_ids = set()
    for s, patient_name, patient_display_id in result.all():
        stag_labels = await _get_tags_for_summary(db, str(s.id))
        hits.append(_build_hit(s, patient_name, patient_display_id, stag_labels))
        seen_visit_ids.add(s.visit_id)

    # Also search transcription text
    if len(hits) < limit:
        remaining = limit - len(hits)
        trans_stmt = (
            select(Transcription, Patient.name, Patient.display_id)
            .join(Recording, Transcription.recording_id == Recording.id)
            .join(Visit, Recording.visit_id == Visit.id)
            .join(Patient, Visit.patient_id == Patient.id)
            .where(Transcription.full_text.ilike(pattern))
        )
        if seen_visit_ids:
            trans_stmt = trans_stmt.where(Visit.id.notin_(seen_visit_ids))
        trans_stmt = trans_stmt.order_by(Transcription.created_at.desc()).limit(remaining)
        trans_result = await db.execute(trans_stmt)
        for t, patient_name, patient_display_id in trans_result.all():
            hits.append(_build_transcription_hit(t, patient_name, patient_display_id))
            total += 1

    return {"hits": hits, "total": total}
