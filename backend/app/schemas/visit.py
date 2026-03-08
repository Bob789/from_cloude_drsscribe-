import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.visit import VisitStatus


class VisitCreate(BaseModel):
    patient_id: uuid.UUID
    start_time: datetime | None = None


class VisitResponse(BaseModel):
    id: uuid.UUID
    display_id: int
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    clinic_id: uuid.UUID | None = None
    start_time: datetime
    end_time: datetime | None = None
    status: VisitStatus
    source: str = "recording"
    created_at: datetime

    model_config = {"from_attributes": True}


class VisitUpdate(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: VisitStatus | None = None


class VisitUpdateWithSummary(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: VisitStatus | None = None
    chief_complaint: str | None = None
    findings: str | None = None
    diagnosis: list[str] | None = None
    treatment_plan: str | None = None
    recommendations: str | None = None
    urgency: str | None = None


class ManualVisitCreate(BaseModel):
    patient_id: uuid.UUID
    chief_complaint: str | None = None
    findings: str | None = None
    diagnosis: list[dict] | None = None
    treatment_plan: str | None = None
    recommendations: str | None = None
    urgency: str = "low"
    notes: str | None = None
    tags: list[dict] | None = None
    custom_fields: list[dict] | None = None
    questionnaire_data: list[dict] | None = None


class VisitListResponse(BaseModel):
    items: list[VisitResponse]
    total: int
