import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class UserRole(str, enum.Enum):
    doctor = "doctor"
    admin = "admin"
    receptionist = "receptionist"


class PatientKeyType(str, enum.Enum):
    national_id = "national_id"
    phone = "phone"
    email = "email"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    google_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    auth_method: Mapped[str] = mapped_column(String(20), default="google", server_default="google")
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.doctor, nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    patient_key_type: Mapped[PatientKeyType] = mapped_column(
        Enum(PatientKeyType), default=PatientKeyType.national_id, server_default="national_id", nullable=False
    )
    preferred_language: Mapped[str] = mapped_column(String(5), default="he", server_default="he", nullable=False)
    calendar_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    calendar_connected: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    calendar_connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User {self.email}>"
