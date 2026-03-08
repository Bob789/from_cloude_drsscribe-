import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
import re


class PatientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    id_number: str | None = None
    dob: date | None = None
    phone: str | None = None
    email: str | None = None
    profession: str | None = None
    address: str | None = None
    insurance_info: str | None = None
    notes: str | None = None

    @field_validator("id_number")
    @classmethod
    def validate_id_number(cls, v):
        if v and not re.match(r"^\d{9}$", v):
            raise ValueError("ID number must be 9 digits")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r"^[\d\-+() ]{7,20}$", v):
            raise ValueError("Invalid phone format")
        return v


class PatientUpdate(BaseModel):
    name: str | None = None
    id_number: str | None = None
    dob: date | None = None
    phone: str | None = None
    email: str | None = None
    profession: str | None = None
    address: str | None = None
    insurance_info: str | None = None
    notes: str | None = None


class PatientResponse(BaseModel):
    id: uuid.UUID
    display_id: int
    name: str
    id_number: str | None = None
    dob: date | None = None
    phone: str | None = None
    email: str | None = None
    blood_type: str | None = None
    allergies: list[str] | None = None
    profession: str | None = None
    address: str | None = None
    insurance_info: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatientListResponse(BaseModel):
    items: list[PatientResponse]
    total: int
    page: int
    per_page: int
    pages: int
