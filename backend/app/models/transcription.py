import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TranscriptionStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    error = "error"


class Transcription(Base):
    __tablename__ = "transcriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recording_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recordings.id"), nullable=False, index=True)
    full_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    speakers_json: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="he")
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    wer_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[TranscriptionStatus] = mapped_column(Enum(TranscriptionStatus), default=TranscriptionStatus.pending)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recording = relationship("Recording", lazy="selectin")
