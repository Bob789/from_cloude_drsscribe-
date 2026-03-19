from pydantic import BaseModel


class SearchQuery(BaseModel):
    q: str
    tags: list[str] | None = None
    date_from: str | None = None
    date_to: str | None = None
    doctor: str | None = None
    patient: str | None = None
    page: int = 1
    per_page: int = 20


class SearchResult(BaseModel):
    hits: list[dict]
    total: int
    page: int
    per_page: int
