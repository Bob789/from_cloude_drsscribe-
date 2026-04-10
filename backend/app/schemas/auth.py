import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole, PatientKeyType


class GoogleAuthRequest(BaseModel):
    token: str
    token_type: str = "id_token"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    nickname: str | None = None
    role: UserRole
    avatar_url: str | None = None
    is_active: bool
    patient_key_type: PatientKeyType = PatientKeyType.national_id
    preferred_language: str = "he"
    created_at: datetime

    model_config = {"from_attributes": True}


class PatientKeyTypeUpdate(BaseModel):
    patient_key_type: PatientKeyType


SUPPORTED_LANGUAGES = {"en", "he", "de", "es", "fr", "pt", "ko", "it"}


class LanguageUpdate(BaseModel):
    language: str

    @classmethod
    def validate_language(cls, v):
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language must be one of: {SUPPORTED_LANGUAGES}")
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshRequest(BaseModel):
    refresh_token: str


class LocalLoginRequest(BaseModel):
    username: str
    password: str


class ProfileUpdate(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None
