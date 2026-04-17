from pydantic import BaseModel, Field
from typing import Optional


class PageViewIn(BaseModel):
    session_id: str = Field(..., max_length=64)
    visitor_id: Optional[str] = Field(None, max_length=64)
    page_path: str = Field(..., max_length=500)
    article_slug: Optional[str] = Field(None, max_length=300)
    duration_seconds: Optional[int] = None
    referrer: Optional[str] = None
    device_type: Optional[str] = Field(None, max_length=20)
    utm_source: Optional[str] = Field(None, max_length=100)
    utm_medium: Optional[str] = Field(None, max_length=100)
    utm_campaign: Optional[str] = Field(None, max_length=100)


class SearchLogIn(BaseModel):
    session_id: str = Field(..., max_length=64)
    visitor_id: Optional[str] = Field(None, max_length=64)
    query: str = Field(..., max_length=500)
    results_count: int = 0
    clicked_article_slug: Optional[str] = Field(None, max_length=300)


class EventIn(BaseModel):
    session_id: str = Field(..., max_length=64)
    visitor_id: Optional[str] = Field(None, max_length=64)
    event_type: str = Field(..., max_length=50)
    event_data: Optional[dict] = None
    page_path: Optional[str] = Field(None, max_length=500)
