from datetime import datetime
from pydantic import BaseModel


class QuestionTemplateCreate(BaseModel):
    name: str
    description: str | None = None
    icon: str = "clipboard"
    color: str = "#3B82F6"
    questions: list[dict]
    is_shared: bool = False


class QuestionTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    questions: list[dict] | None = None
    is_shared: bool | None = None


class QuestionTemplateResponse(BaseModel):
    id: int
    name: str
    description: str | None
    icon: str
    color: str
    questions: list[dict]
    is_shared: bool
    usage_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
