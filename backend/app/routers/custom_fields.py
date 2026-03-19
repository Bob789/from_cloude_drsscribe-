from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.custom_field import CustomField

router = APIRouter(prefix="/custom-fields", tags=["custom-fields"])


class CustomFieldCreate(BaseModel):
    field_name: str
    field_order: int = 0


class CustomFieldUpdate(BaseModel):
    field_name: str | None = None
    field_order: int | None = None


@router.get("")
async def list_custom_fields(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CustomField)
        .where(CustomField.user_id == current_user.id)
        .order_by(CustomField.field_order, CustomField.id)
    )
    fields = result.scalars().all()
    return [
        {"id": f.id, "field_name": f.field_name, "field_order": f.field_order}
        for f in fields
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_custom_field(
    data: CustomFieldCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    field = CustomField(
        user_id=current_user.id,
        field_name=data.field_name,
        field_order=data.field_order,
    )
    db.add(field)
    await db.commit()
    await db.refresh(field)
    return {"id": field.id, "field_name": field.field_name, "field_order": field.field_order}


@router.put("/{field_id}")
async def update_custom_field(
    field_id: int,
    data: CustomFieldUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CustomField).where(CustomField.id == field_id, CustomField.user_id == current_user.id)
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    if data.field_name is not None:
        field.field_name = data.field_name
    if data.field_order is not None:
        field.field_order = data.field_order
    await db.commit()
    await db.refresh(field)
    return {"id": field.id, "field_name": field.field_name, "field_order": field.field_order}


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_field(
    field_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CustomField).where(CustomField.id == field_id, CustomField.user_id == current_user.id)
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    await db.delete(field)
    await db.commit()
