from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.visit import Visit, VisitStatus
from app.models.summary import Summary, SummaryStatus
from app.models.tag import Tag
from app.models.question_template import QuestionTemplate
from app.schemas.visit import ManualVisitCreate
from app.services.audit_service import log_action
from app.services.activity_log_service import log_activity

router = APIRouter(prefix="/visits", tags=["visits"])


@router.post("/manual", status_code=status.HTTP_201_CREATED)
async def create_manual_visit(
    data: ManualVisitCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = Visit(
        patient_id=data.patient_id,
        doctor_id=current_user.id,
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        status=VisitStatus.completed,
        source="manual",
    )
    db.add(visit)
    await db.commit()
    await db.refresh(visit)

    summary = Summary(
        visit_id=visit.id,
        chief_complaint=data.chief_complaint,
        findings=data.findings,
        diagnosis=data.diagnosis,
        treatment_plan=data.treatment_plan,
        recommendations=data.recommendations,
        urgency=data.urgency,
        notes=data.notes,
        questionnaire_data=data.questionnaire_data,
        custom_fields=data.custom_fields,
        source="manual",
        status=SummaryStatus.done,
    )
    db.add(summary)
    await db.commit()
    await db.refresh(summary)

    if data.questionnaire_data:
        template_ids = set()
        for qd in data.questionnaire_data:
            tid = qd.get("template_id")
            if tid:
                template_ids.add(tid)
        if template_ids:
            result = await db.execute(
                select(QuestionTemplate).where(QuestionTemplate.id.in_(template_ids))
            )
            for tmpl in result.scalars().all():
                tmpl.usage_count = (tmpl.usage_count or 0) + 1
            await db.commit()

    if data.tags:
        for tag_data in data.tags:
            tag = Tag(
                entity_type="summary",
                entity_id=str(summary.id),
                tag_type=tag_data.get("tag_type", "diagnosis"),
                tag_code=tag_data.get("tag_code"),
                tag_label=tag_data.get("tag_label", ""),
                source="manual",
            )
            db.add(tag)
        await db.commit()

    await log_action(db, "create_manual", "visit", str(visit.id), current_user.id)
    await log_activity(db, current_user.id, "CREATE", "visit", str(visit.id), "יצר סיכום ידני", request=request)

    return {
        "visit_id": str(visit.id),
        "visit_display_id": visit.display_id,
        "summary_id": str(summary.id),
        "summary_display_id": summary.display_id,
        "message": "Manual visit created",
    }
