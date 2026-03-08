import uuid
import enum
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, Enum, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class SummaryStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    error = "error"


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True, server_default=text("nextval('summaries_display_id_seq')"))
    visit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("visits.id"), nullable=False, index=True)
    summary_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    chief_complaint: Mapped[str | None] = mapped_column(Text, nullable=True)
    findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    treatment_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)
    urgency: Mapped[str] = mapped_column(String(20), default="low")
    source: Mapped[str] = mapped_column(String(20), default="ai", server_default="ai")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    questionnaire_data: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    custom_fields: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[SummaryStatus] = mapped_column(Enum(SummaryStatus), default=SummaryStatus.pending)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    visit = relationship("Visit", lazy="selectin")
