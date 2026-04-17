import json
from pydantic import BaseModel, Field, field_validator
from typing import Optional

_MAX_EVENT_DATA_BYTES = 1024  # 1 KB max for arbitrary JSON


class PageViewIn(BaseModel):
    session_id: str = Field(..., max_length=64)
    visitor_id: Optional[str] = Field(None, max_length=64)
    page_path: str = Field(..., max_length=500)
    article_slug: Optional[str] = Field(None, max_length=300)
    duration_seconds: Optional[int] = Field(None, ge=0, le=86400)
    referrer: Optional[str] = Field(None, max_length=500)
    device_type: Optional[str] = Field(None, max_length=20)
    utm_source: Optional[str] = Field(None, max_length=100)
    utm_medium: Optional[str] = Field(None, max_length=100)
    utm_campaign: Optional[str] = Field(None, max_length=100)


class SearchLogIn(BaseModel):
    session_id: str = Field(..., max_length=64)
    visitor_id: Optional[str] = Field(None, max_length=64)
    query: str = Field(..., max_length=500)
    results_count: int = Field(0, ge=0, le=10000)
    clicked_article_slug: Optional[str] = Field(None, max_length=300)


class EventIn(BaseModel):
    session_id: str = Field(..., max_length=64)
    visitor_id: Optional[str] = Field(None, max_length=64)
    event_type: str = Field(..., max_length=50)
    event_data: Optional[dict] = None
    page_path: Optional[str] = Field(None, max_length=500)

    @field_validator("event_data")
    @classmethod
    def event_data_size(cls, v: Optional[dict]) -> Optional[dict]:
        if v is not None and len(json.dumps(v)) > _MAX_EVENT_DATA_BYTES:
            raise ValueError(f"event_data exceeds {_MAX_EVENT_DATA_BYTES} bytes")
        return v
