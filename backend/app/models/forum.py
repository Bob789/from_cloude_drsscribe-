import enum
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Text, func, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PostStatus(str, enum.Enum):
    open = "open"
    answered = "answered"
    closed = "closed"


class ForumPost(Base):
    __tablename__ = "forum_posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PostStatus] = mapped_column(default=PostStatus.open, server_default="open")
    tags: Mapped[str | None] = mapped_column(nullable=True)  # comma-separated
    views: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    votes: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now(), nullable=True)


class ForumReply(Base):
    __tablename__ = "forum_replies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    votes: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_accepted: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now(), nullable=True)


class ForumVote(Base):
    __tablename__ = "forum_votes"
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_vote_user_post"),
        UniqueConstraint("user_id", "reply_id", name="uq_vote_user_reply"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    post_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=True)
    reply_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("forum_replies.id", ondelete="CASCADE"), nullable=True)
    value: Mapped[int] = mapped_column(Integer, nullable=False)  # +1 or -1
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
