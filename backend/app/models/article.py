import uuid
import enum
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, Enum, Float, Boolean, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ArticleStatus(str, enum.Enum):
    draft = "draft"
    review = "review"
    published = "published"
    archived = "archived"


class FactCheckStatus(str, enum.Enum):
    unchecked = "unchecked"
    flagged = "flagged"
    verified = "verified"


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="general", server_default="general")
    tags: Mapped[list | None] = mapped_column(JSONB, default=list, server_default="[]")
    author_name: Mapped[str] = mapped_column(String(255), default="Doctor Scribe AI", server_default="Doctor Scribe AI")
    author_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hero_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    hero_image_alt: Mapped[str | None] = mapped_column(String(500), nullable=True)
    seo_title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    seo_keywords: Mapped[list | None] = mapped_column(JSONB, default=list, server_default="[]")
    status: Mapped[ArticleStatus] = mapped_column(Enum(ArticleStatus), default=ArticleStatus.draft, server_default="draft")
    source_topic: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), default="manual", server_default="manual")
    generation_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    fact_check_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    fact_check_status: Mapped[FactCheckStatus] = mapped_column(Enum(FactCheckStatus), default=FactCheckStatus.unchecked, server_default="unchecked")
    read_time_minutes: Mapped[int] = mapped_column(Integer, default=5, server_default="5")
    views: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    likes: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ArticleJobStatus(str, enum.Enum):
    queued = "queued"
    generating = "generating"
    image_search = "image_search"
    seo_gen = "seo_gen"
    done = "done"
    error = "error"


class ArticleGenerationJob(Base):
    __tablename__ = "article_generation_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=True)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[ArticleJobStatus] = mapped_column(Enum(ArticleJobStatus), default=ArticleJobStatus.queued)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_config: Mapped[dict | None] = mapped_column(JSONB, default=dict, server_default="{}")
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TrendingTopic(Base):
    __tablename__ = "trending_topics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="manual", server_default="manual")
    relevance_score: Mapped[float] = mapped_column(Float, default=0.5, server_default="0.5")
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    used: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    article_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=True)
