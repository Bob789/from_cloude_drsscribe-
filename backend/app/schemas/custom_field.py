from pydantic import BaseModel
from datetime import datetime


class CustomFieldCreate(BaseModel):
    field_name: str


class CustomFieldUpdate(BaseModel):
    field_name: str | None = None
    field_order: int | None = None


class CustomFieldResponse(BaseModel):
    id: int
    field_name: str
    field_order: int
    created_at: datetime

    class Config:
        from_attributes = True
