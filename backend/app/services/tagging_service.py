import uuid
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tag import Tag
from app.models.summary import Summary
from app.services.llm_service import extract_tags_with_llm


async def sync_diagnosis_tags(db: AsyncSession, summary: Summary):
    await db.execute(
        delete(Tag).where(
            and_(
                Tag.entity_type == "summary",
                Tag.entity_id == str(summary.id),
                Tag.tag_type == "diagnosis",
                Tag.source == "summary_auto",
            )
        )
    )

    created_tags = []
    if summary.diagnosis:
        for diag in summary.diagnosis:
            if isinstance(diag, dict):
                tag = Tag(
                    entity_type="summary",
                    entity_id=str(summary.id),
                    tag_type="diagnosis",
                    tag_code=diag.get("code", ""),
                    tag_label=diag.get("description", ""),
                    confidence=1.0,
                    source="summary_auto",
                )
                db.add(tag)
                created_tags.append(tag)

    await db.commit()
    return created_tags


async def extract_tags_from_summary(db: AsyncSession, summary: Summary):
    summary_text = " ".join(filter(None, [
        summary.chief_complaint,
        summary.findings,
        summary.treatment_plan,
        summary.recommendations,
    ]))

    if not summary_text.strip():
        return []

    try:
        tags_data = await extract_tags_with_llm(summary_text)
    except Exception:
        tags_data = []

    tags_data = [t for t in tags_data if t.get("tag_type") != "diagnosis"]

    created_tags = []
    for tag_data in tags_data:
        tag = Tag(
            entity_type="summary",
            entity_id=str(summary.id),
            tag_type=tag_data.get("tag_type", "other"),
            tag_code=tag_data.get("tag_code"),
            tag_label=tag_data.get("tag_label", ""),
            confidence=tag_data.get("confidence"),
            source="llm_extra",
        )
        db.add(tag)
        created_tags.append(tag)

    await db.commit()
    return created_tags
