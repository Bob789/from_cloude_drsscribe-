from datetime import datetime
from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    id: int
    patient_id: str
    file_name: str
    file_size: int | None
    mime_type: str | None
    category: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FileListResponse(BaseModel):
    files: list[FileUploadResponse]
    total: int


class FileUpdateRequest(BaseModel):
    category: str | None = None
    description: str | None = None
    visit_id: str | None = None
