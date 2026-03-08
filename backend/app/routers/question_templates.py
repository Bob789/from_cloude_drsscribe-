from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.question_template import QuestionTemplate
from app.schemas.question_template import QuestionTemplateCreate, QuestionTemplateUpdate, QuestionTemplateResponse
from app.services.activity_log_service import log_activity
from app.exceptions import NotFoundError, ForbiddenError

router = APIRouter(prefix="/question-templates", tags=["question-templates"])


async def _get_template_or_404(db: AsyncSession, template_id: int) -> QuestionTemplate:
    result = await db.execute(select(QuestionTemplate).where(QuestionTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise NotFoundError("כרטיסייה", template_id)
    return template


@router.post("", response_model=QuestionTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    data: QuestionTemplateCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    template = QuestionTemplate(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        icon=data.icon,
        color=data.color,
        questions=data.questions,
        is_shared=data.is_shared,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    await log_activity(db, current_user.id, "CREATE", "question_template", template.id, f"יצר כרטיסייה: {template.name}", request=request)
    return template


@router.get("", response_model=list[QuestionTemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(QuestionTemplate)
        .where(
            QuestionTemplate.is_active == True,
            or_(QuestionTemplate.user_id == current_user.id, QuestionTemplate.is_shared == True),
        )
        .order_by(QuestionTemplate.usage_count.desc(), QuestionTemplate.name)
    )
    return result.scalars().all()


@router.get("/{template_id}", response_model=QuestionTemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _get_template_or_404(db, template_id)


@router.put("/{template_id}", response_model=QuestionTemplateResponse)
async def update_template(
    template_id: int,
    data: QuestionTemplateUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    template = await _get_template_or_404(db, template_id)
    if template.user_id != current_user.id:
        raise ForbiddenError("אין הרשאה לעריכת כרטיסייה זו")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(template, key, value)
    await db.commit()
    await db.refresh(template)
    await log_activity(db, current_user.id, "UPDATE", "question_template", template.id, f"עדכן כרטיסייה: {template.name}", request=request)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    template = await _get_template_or_404(db, template_id)
    if template.user_id != current_user.id:
        raise ForbiddenError("אין הרשאה למחיקת כרטיסייה זו")

    template.is_active = False
    await db.commit()
    await log_activity(db, current_user.id, "DELETE", "question_template", template.id, f"מחק כרטיסייה: {template.name}", request=request)


@router.post("/{template_id}/duplicate", response_model=QuestionTemplateResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_template(
    template_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    original = await _get_template_or_404(db, template_id)
    copy = QuestionTemplate(
        user_id=current_user.id,
        name=f"{original.name} (עותק)",
        description=original.description,
        icon=original.icon,
        color=original.color,
        questions=original.questions,
        is_shared=False,
    )
    db.add(copy)
    await db.commit()
    await db.refresh(copy)
    await log_activity(db, current_user.id, "CREATE", "question_template", copy.id, f"שכפל כרטיסייה: {original.name}", request=request)
    return copy
