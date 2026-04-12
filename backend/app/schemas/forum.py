import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ForumPostCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=300)
    body: str = Field(..., min_length=10)
    tags: str | None = None  # comma-separated


class ForumPostUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    tags: str | None = None
    status: str | None = None  # open / answered / closed


class FirstReplyPreview(BaseModel):
    body: str
    author_name: str


class ForumPostResponse(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    author_name: str
    title: str
    body: str
    status: str
    tags: str | None
    views: int
    votes: int
    replies_count: int
    first_reply: FirstReplyPreview | None = None
    created_at: datetime
    updated_at: datetime | None


class ForumReplyCreate(BaseModel):
    body: str = Field(..., min_length=2)


class ForumReplyUpdate(BaseModel):
    body: str = Field(..., min_length=2)


class ForumReplyResponse(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID
    author_id: uuid.UUID
    author_name: str
    body: str
    votes: int
    is_accepted: bool
    created_at: datetime
    updated_at: datetime | None


class ForumVoteRequest(BaseModel):
    value: int = Field(..., ge=-1, le=1)  # +1 or -1


class ForumPostListResponse(BaseModel):
    posts: list[ForumPostResponse]
    total: int
    page: int
    per_page: int


class ForumStatsResponse(BaseModel):
    total_posts: int
    total_replies: int
    active_users: int
    hot_tags: list[dict]
