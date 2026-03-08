import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.tag import Tag

router = APIRouter(prefix="/tags", tags=["tags"])


class TagCreate(BaseModel):
    entity_type: str
    entity_id: str
    tag_type: str
    tag_code: str | None = None
    tag_label: str


class TagUpdate(BaseModel):
    tag_type: str | None = None
    tag_code: str | None = None
    tag_label: str | None = None


@router.get("")
async def list_tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Tag.tag_type, Tag.tag_label, Tag.tag_code, func.count(Tag.id).label("count"))
        .group_by(Tag.tag_type, Tag.tag_label, Tag.tag_code)
        .order_by(func.count(Tag.id).desc())
    )
    tags = [{"tag_type": r[0], "tag_label": r[1], "tag_code": r[2], "count": r[3]} for r in result.all()]
    return {"tags": tags, "total": len(tags)}


@router.post("")
async def create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = Tag(
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        tag_type=data.tag_type,
        tag_code=data.tag_code,
        tag_label=data.tag_label,
        source="manual",
    )
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return {"id": str(tag.id), "tag_label": tag.tag_label, "tag_type": tag.tag_type}


@router.put("/{tag_id}")
async def update_tag(
    tag_id: str,
    data: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Tag).where(Tag.id == uuid.UUID(tag_id)))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(tag, key, value)
    await db.commit()
    await db.refresh(tag)
    return {"id": str(tag.id), "tag_label": tag.tag_label, "tag_type": tag.tag_type, "tag_code": tag.tag_code}


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Tag).where(Tag.id == uuid.UUID(tag_id)))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    await db.delete(tag)
    await db.commit()


@router.get("/{tag_code}/visits")
async def visits_by_tag(
    tag_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Tag).where(Tag.tag_code == tag_code).order_by(Tag.created_at.desc())
    )
    tags = result.scalars().all()
    visit_ids = [t.entity_id for t in tags if t.entity_type == "summary"]
    return {"tag_code": tag_code, "visit_ids": visit_ids, "total": len(visit_ids)}
