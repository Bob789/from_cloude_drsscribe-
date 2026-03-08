import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.transcription import TranscriptionStatus


class TranscriptionResponse(BaseModel):
    id: uuid.UUID
    recording_id: uuid.UUID
    full_text: str | None = None
    speakers_json: list | None = None
    language: str = "he"
    confidence_score: float | None = None
    status: TranscriptionStatus
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TranscriptionUpdate(BaseModel):
    full_text: str | None = None
    speakers_json: list | None = None
