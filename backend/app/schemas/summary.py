import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.summary import SummaryStatus


class SummaryResponse(BaseModel):
    id: uuid.UUID
    display_id: int
    visit_id: uuid.UUID
    summary_text: str | None = None
    chief_complaint: str | None = None
    findings: str | None = None
    diagnosis: list | None = None
    treatment_plan: str | None = None
    recommendations: str | None = None
    urgency: str = "low"
    source: str = "ai"
    notes: str | None = None
    status: SummaryStatus
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SummaryUpdate(BaseModel):
    summary_text: str | None = None
    chief_complaint: str | None = None
    findings: str | None = None
    diagnosis: list | None = None
    treatment_plan: str | None = None
    recommendations: str | None = None
    urgency: str | None = None
    notes: str | None = None
