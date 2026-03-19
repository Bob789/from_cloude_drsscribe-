from pydantic import BaseModel
from datetime import datetime


class TagCreate(BaseModel):
    tag_type: str
    tag_code: str | None = None
    tag_label: str
    entity_type: str
    entity_id: str


class TagUpdate(BaseModel):
    tag_label: str | None = None
    tag_code: str | None = None


class TagResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    tag_type: str
    tag_code: str | None = None
    tag_label: str
    confidence: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True
