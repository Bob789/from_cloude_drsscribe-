from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.summary import Summary
from app.models.transcription import Transcription
from app.models.visit import Visit
from app.models.patient import Patient
from app.models.recording import Recording
from app.services.search_service import get_search_client, _get_patient_info, _get_tags_for_summary


async def init_indexes():
    client = get_search_client()
    client.create_index("transcriptions", {"primaryKey": "id"})
    client.create_index("summaries", {"primaryKey": "id"})

    client.index("transcriptions").update_settings({
        "searchableAttributes": ["full_text", "patient_name", "language"],
        "filterableAttributes": ["recording_id", "language", "status", "created_at", "tags", "visit_id"],
        "sortableAttributes": ["created_at"],
    })
    client.index("summaries").update_settings({
        "searchableAttributes": ["chief_complaint", "findings", "treatment_plan", "recommendations", "patient_name"],
        "filterableAttributes": ["visit_id", "urgency", "status", "created_at", "tags"],
        "sortableAttributes": ["created_at"],
    })


async def reindex_all(db: AsyncSession):
    client = get_search_client()
    await init_indexes()
    client.index("summaries").delete_all_documents()
    client.index("transcriptions").delete_all_documents()

    result = await db.execute(select(Summary))
    summaries = result.scalars().all()
    summary_docs = []
    for s in summaries:
        patient_name, patient_display_id = await _get_patient_info(db, s.visit_id)
        tags_list = await _get_tags_for_summary(db, str(s.id))
        summary_docs.append({
            "id": str(s.id), "visit_id": str(s.visit_id),
            "patient_name": patient_name, "patient_display_id": patient_display_id,
            "chief_complaint": s.chief_complaint or "", "findings": s.findings or "",
            "treatment_plan": s.treatment_plan or "", "recommendations": s.recommendations or "",
            "urgency": s.urgency, "status": s.status.value if s.status else "done",
            "tags": tags_list, "created_at": s.created_at.isoformat() if s.created_at else "",
        })
    if summary_docs:
        client.index("summaries").add_documents(summary_docs)

    result = await db.execute(select(Transcription))
    transcriptions = result.scalars().all()
    trans_docs = []
    for t in transcriptions:
        rec_r = await db.execute(select(Recording).where(Recording.id == t.recording_id))
        rec = rec_r.scalar_one_or_none()
        patient_name, patient_display_id, visit_id = "", 0, ""
        if rec:
            visit_r = await db.execute(select(Visit).where(Visit.id == rec.visit_id))
            visit = visit_r.scalar_one_or_none()
            if visit:
                visit_id = str(visit.id)
                pat_r = await db.execute(select(Patient).where(Patient.id == visit.patient_id))
                pat = pat_r.scalar_one_or_none()
                if pat:
                    patient_name = pat.name
                    patient_display_id = pat.display_id
        trans_docs.append({
            "id": str(t.id), "recording_id": str(t.recording_id),
            "visit_id": visit_id, "patient_name": patient_name, "patient_display_id": patient_display_id,
            "full_text": t.full_text or "", "language": t.language or "he",
            "status": t.status.value if t.status else "done", "tags": [],
            "created_at": t.created_at.isoformat() if t.created_at else "",
        })
    if trans_docs:
        client.index("transcriptions").add_documents(trans_docs)

    return {"summaries_indexed": len(summary_docs), "transcriptions_indexed": len(trans_docs)}


async def reindex_summary(db: AsyncSession, summary: Summary):
    patient_name, patient_display_id = await _get_patient_info(db, summary.visit_id)
    tags_list = await _get_tags_for_summary(db, str(summary.id))
    await index_summary(str(summary.id), {
        "visit_id": str(summary.visit_id),
        "patient_name": patient_name, "patient_display_id": patient_display_id,
        "chief_complaint": summary.chief_complaint or "", "findings": summary.findings or "",
        "treatment_plan": summary.treatment_plan or "", "recommendations": summary.recommendations or "",
        "urgency": summary.urgency, "status": summary.status.value if summary.status else "done",
        "tags": tags_list, "created_at": summary.created_at.isoformat() if summary.created_at else "",
    })


async def index_transcription(transcription_id: str, data: dict):
    client = get_search_client()
    client.index("transcriptions").add_documents([{"id": transcription_id, **data}])


async def index_summary(summary_id: str, data: dict):
    client = get_search_client()
    client.index("summaries").add_documents([{"id": summary_id, **data}])
