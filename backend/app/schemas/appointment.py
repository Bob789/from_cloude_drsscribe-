from datetime import datetime
from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    patient_id: str | None = None
    title: str
    description: str | None = None
    start_time: datetime
    duration_minutes: int = 20
    reminder_minutes: int = 60
    sync_to_google: bool = True


class AppointmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_time: datetime | None = None
    duration_minutes: int | None = None
    status: str | None = None
    reminder_minutes: int | None = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: str | None = None
    patient_name: str | None = None
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    status: str
    reminder_minutes: int
    synced_to_google: bool
    google_event_id: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
