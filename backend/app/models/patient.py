import uuid
from datetime import datetime, date
from sqlalchemy import Integer, String, Date, DateTime, Text, func, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True, server_default=text("nextval('patients_display_id_seq')"))
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    id_number: Mapped[str] = mapped_column(String(500), nullable=True)
    id_number_hash: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    dob: Mapped[date | None] = mapped_column(Date, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    blood_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    allergies: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    profession: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    insurance_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    visits = relationship("Visit", back_populates="patient", lazy="selectin")
