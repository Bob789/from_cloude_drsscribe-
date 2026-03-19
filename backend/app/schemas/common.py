from pydantic import BaseModel
from typing import Any, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class ApiResponse(BaseModel):
    status: str = "ok"
    message: str = ""
    data: Any = None


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    per_page: int
    pages: int


class IdResponse(BaseModel):
    id: str
    message: str = ""


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
