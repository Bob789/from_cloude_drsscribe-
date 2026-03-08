import uuid
from datetime import datetime
from pydantic import BaseModel


class RecordingResponse(BaseModel):
    id: uuid.UUID
    visit_id: uuid.UUID
    audio_url: str
    duration_seconds: float | None = None
    format: str
    file_size: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecordingUploadResponse(BaseModel):
    id: uuid.UUID
    message: str = "Upload successful"


class ChunkUploadResponse(BaseModel):
    chunk_id: int
    chunk_index: int
    message: str = "Chunk uploaded"


class FinalizeResponse(BaseModel):
    recording_id: uuid.UUID
    chunk_count: int
    total_size: int
    message: str = "Recording finalized, processing started"
