import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user, security
from app.models.user import User
from app.schemas.forum import (
    ForumPostCreate, ForumPostUpdate, ForumPostResponse, ForumPostListResponse,
    ForumReplyCreate, ForumReplyResponse, ForumVoteRequest, ForumStatsResponse,
)
from app.services import forum_service

router = APIRouter(tags=["forum"])


# ── Posts (public read) ──────────────────────────────────

@router.get("/forum/posts", response_model=ForumPostListResponse)
async def list_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    sort: str = Query("hot"),
    tag: str | None = None,
    search: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    posts, total = await forum_service.list_posts(
        db, page=page, per_page=per_page, sort=sort,
        tag=tag, search=search, status=status_filter,
    )
    return {"posts": posts, "total": total, "page": page, "per_page": per_page}


@router.get("/forum/posts/{post_id}", response_model=ForumPostResponse)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    post = await forum_service.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/forum/stats", response_model=ForumStatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    return await forum_service.get_stats(db)


@router.get("/forum/leaderboard")
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    return await forum_service.get_leaderboard(db, limit=limit)


# ── Posts (auth required) ────────────────────────────────

@router.post("/forum/posts", response_model=ForumPostResponse, status_code=201)
async def create_post(
    data: ForumPostCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = await forum_service.create_post(db, user.id, data.title, data.body, data.tags)
    await db.commit()
    return post


@router.put("/forum/posts/{post_id}", response_model=ForumPostResponse)
async def update_post(
    post_id: uuid.UUID,
    data: ForumPostUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await forum_service.update_post(
        db, post_id, user.id, data.model_dump(exclude_none=True)
    )
    if not result:
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")
    await db.commit()
    return result


@router.delete("/forum/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = await forum_service.delete_post(db, post_id, user.id)
    if not ok:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    await db.commit()


# ── Replies ──────────────────────────────────────────────

@router.get("/forum/posts/{post_id}/replies", response_model=list[ForumReplyResponse])
async def list_replies(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await forum_service.list_replies(db, post_id)


@router.post("/forum/posts/{post_id}/replies", response_model=ForumReplyResponse, status_code=201)
async def create_reply(
    post_id: uuid.UUID,
    data: ForumReplyCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    reply = await forum_service.create_reply(db, post_id, user.id, data.body)
    await db.commit()
    return reply


@router.delete("/forum/replies/{reply_id}", status_code=204)
async def delete_reply(
    reply_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = await forum_service.delete_reply(db, reply_id, user.id)
    if not ok:
        raise HTTPException(status_code=403, detail="Not authorized to delete this reply")
    await db.commit()


@router.post("/forum/replies/{reply_id}/accept", status_code=200)
async def accept_reply(
    reply_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = await forum_service.accept_reply(db, reply_id, user.id)
    if not ok:
        raise HTTPException(status_code=403, detail="Not authorized or reply not found")
    await db.commit()
    return {"status": "accepted"}


# ── Votes ────────────────────────────────────────────────

@router.post("/forum/posts/{post_id}/vote")
async def vote_post(
    post_id: uuid.UUID,
    data: ForumVoteRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    new_votes = await forum_service.vote(db, user.id, post_id=post_id, reply_id=None, value=data.value)
    await db.commit()
    return {"votes": new_votes}


@router.post("/forum/replies/{reply_id}/vote")
async def vote_reply(
    reply_id: uuid.UUID,
    data: ForumVoteRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    new_votes = await forum_service.vote(db, user.id, post_id=None, reply_id=reply_id, value=data.value)
    await db.commit()
    return {"votes": new_votes}
