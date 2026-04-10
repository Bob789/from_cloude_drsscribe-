import uuid
from sqlalchemy import select, func, update, delete, case, literal_column
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.forum import ForumPost, ForumReply, ForumVote, PostStatus
from app.models.user import User

# Helper: display name = nickname if set, otherwise real name
_display_name = func.coalesce(User.nickname, User.name).label("author_name")


async def list_posts(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 12,
    sort: str = "hot",
    tag: str | None = None,
    search: str | None = None,
    status: str | None = None,
) -> tuple[list[dict], int]:
    stmt = select(ForumPost, _display_name).join(
        User, ForumPost.author_id == User.id
    )

    if tag:
        stmt = stmt.where(ForumPost.tags.ilike(f"%{tag}%"))
    if search:
        stmt = stmt.where(
            ForumPost.title.ilike(f"%{search}%") | ForumPost.body.ilike(f"%{search}%")
        )
    if status:
        stmt = stmt.where(ForumPost.status == status)

    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # Sort
    if sort == "new":
        stmt = stmt.order_by(ForumPost.created_at.desc())
    elif sort == "top":
        stmt = stmt.order_by(ForumPost.votes.desc())
    elif sort == "unanswered":
        stmt = stmt.where(ForumPost.status == PostStatus.open)
        stmt = stmt.order_by(ForumPost.created_at.desc())
    else:  # hot — by views + votes
        stmt = stmt.order_by((ForumPost.views + ForumPost.votes).desc())

    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    rows = (await db.execute(stmt)).all()

    # Get reply counts
    post_ids = [row.ForumPost.id for row in rows]
    reply_counts = {}
    if post_ids:
        rc_stmt = (
            select(ForumReply.post_id, func.count().label("cnt"))
            .where(ForumReply.post_id.in_(post_ids))
            .group_by(ForumReply.post_id)
        )
        for r in (await db.execute(rc_stmt)).all():
            reply_counts[r.post_id] = r.cnt

    posts = []
    for row in rows:
        p = row.ForumPost
        posts.append({
            "id": p.id,
            "author_id": p.author_id,
            "author_name": row.author_name,
            "title": p.title,
            "body": p.body,
            "status": p.status.value if isinstance(p.status, PostStatus) else p.status,
            "tags": p.tags,
            "views": p.views,
            "votes": p.votes,
            "replies_count": reply_counts.get(p.id, 0),
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        })

    return posts, total


async def get_post(db: AsyncSession, post_id: uuid.UUID) -> dict | None:
    stmt = select(ForumPost, _display_name).join(
        User, ForumPost.author_id == User.id
    ).where(ForumPost.id == post_id)
    row = (await db.execute(stmt)).first()
    if not row:
        return None

    # Increment views
    await db.execute(
        update(ForumPost).where(ForumPost.id == post_id).values(views=ForumPost.views + 1)
    )
    await db.flush()

    # Reply count
    rc = (await db.execute(
        select(func.count()).where(ForumReply.post_id == post_id)
    )).scalar() or 0

    p = row.ForumPost
    return {
        "id": p.id,
        "author_id": p.author_id,
        "author_name": row.author_name,
        "title": p.title,
        "body": p.body,
        "status": p.status.value if isinstance(p.status, PostStatus) else p.status,
        "tags": p.tags,
        "views": p.views + 1,
        "votes": p.votes,
        "replies_count": rc,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }


async def create_post(db: AsyncSession, author_id: uuid.UUID, title: str, body: str, tags: str | None) -> dict:
    post = ForumPost(author_id=author_id, title=title, body=body, tags=tags)
    db.add(post)
    await db.flush()
    await db.refresh(post)

    display = (await db.execute(select(func.coalesce(User.nickname, User.name)).where(User.id == author_id))).scalar()
    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_name": display or "Unknown",
        "title": post.title,
        "body": post.body,
        "status": post.status.value if isinstance(post.status, PostStatus) else post.status,
        "tags": post.tags,
        "views": post.views,
        "votes": post.votes,
        "replies_count": 0,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }


async def update_post(db: AsyncSession, post_id: uuid.UUID, user_id: uuid.UUID, data: dict) -> dict | None:
    post = (await db.execute(select(ForumPost).where(ForumPost.id == post_id))).scalar_one_or_none()
    if not post or post.author_id != user_id:
        return None

    for k, v in data.items():
        if v is not None:
            setattr(post, k, v)
    await db.flush()
    await db.refresh(post)

    user = (await db.execute(select(func.coalesce(User.nickname, User.name)).where(User.id == user_id))).scalar()
    rc = (await db.execute(select(func.count()).where(ForumReply.post_id == post_id))).scalar() or 0
    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_name": user or "Unknown",
        "title": post.title,
        "body": post.body,
        "status": post.status.value if isinstance(post.status, PostStatus) else post.status,
        "tags": post.tags,
        "views": post.views,
        "votes": post.votes,
        "replies_count": rc,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }


async def delete_post(db: AsyncSession, post_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    post = (await db.execute(select(ForumPost).where(ForumPost.id == post_id))).scalar_one_or_none()
    if not post or post.author_id != user_id:
        return False
    await db.execute(delete(ForumPost).where(ForumPost.id == post_id))
    return True


# ── Replies ──────────────────────────────────────────────

async def list_replies(db: AsyncSession, post_id: uuid.UUID) -> list[dict]:
    stmt = select(ForumReply, _display_name).join(
        User, ForumReply.author_id == User.id
    ).where(ForumReply.post_id == post_id).order_by(ForumReply.created_at.asc())
    rows = (await db.execute(stmt)).all()

    return [{
        "id": r.ForumReply.id,
        "post_id": r.ForumReply.post_id,
        "author_id": r.ForumReply.author_id,
        "author_name": r.author_name,
        "body": r.ForumReply.body,
        "votes": r.ForumReply.votes,
        "is_accepted": r.ForumReply.is_accepted,
        "created_at": r.ForumReply.created_at,
        "updated_at": r.ForumReply.updated_at,
    } for r in rows]


async def create_reply(db: AsyncSession, post_id: uuid.UUID, author_id: uuid.UUID, body: str) -> dict:
    reply = ForumReply(post_id=post_id, author_id=author_id, body=body)
    db.add(reply)
    await db.flush()
    await db.refresh(reply)

    user = (await db.execute(select(func.coalesce(User.nickname, User.name)).where(User.id == author_id))).scalar()
    return {
        "id": reply.id,
        "post_id": reply.post_id,
        "author_id": reply.author_id,
        "author_name": user or "Unknown",
        "body": reply.body,
        "votes": reply.votes,
        "is_accepted": reply.is_accepted,
        "created_at": reply.created_at,
        "updated_at": reply.updated_at,
    }


async def delete_reply(db: AsyncSession, reply_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    reply = (await db.execute(select(ForumReply).where(ForumReply.id == reply_id))).scalar_one_or_none()
    if not reply or reply.author_id != user_id:
        return False
    await db.execute(delete(ForumReply).where(ForumReply.id == reply_id))
    return True


async def accept_reply(db: AsyncSession, reply_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    reply = (await db.execute(select(ForumReply).where(ForumReply.id == reply_id))).scalar_one_or_none()
    if not reply:
        return False
    # Only the post author can accept
    post = (await db.execute(select(ForumPost).where(ForumPost.id == reply.post_id))).scalar_one_or_none()
    if not post or post.author_id != user_id:
        return False

    reply.is_accepted = True
    post.status = PostStatus.answered
    await db.flush()
    return True


# ── Votes ────────────────────────────────────────────────

async def vote(db: AsyncSession, user_id: uuid.UUID, post_id: uuid.UUID | None, reply_id: uuid.UUID | None, value: int) -> int:
    # Check existing vote
    stmt = select(ForumVote).where(ForumVote.user_id == user_id)
    if post_id:
        stmt = stmt.where(ForumVote.post_id == post_id)
    else:
        stmt = stmt.where(ForumVote.reply_id == reply_id)

    existing = (await db.execute(stmt)).scalar_one_or_none()

    if existing:
        old_value = existing.value
        if old_value == value:
            # Remove vote
            await db.delete(existing)
            delta = -value
        else:
            existing.value = value
            delta = value - old_value
    else:
        v = ForumVote(user_id=user_id, post_id=post_id, reply_id=reply_id, value=value)
        db.add(v)
        delta = value

    # Update vote count on post/reply
    if post_id:
        await db.execute(
            update(ForumPost).where(ForumPost.id == post_id).values(votes=ForumPost.votes + delta)
        )
        result = (await db.execute(select(ForumPost.votes).where(ForumPost.id == post_id))).scalar()
    else:
        await db.execute(
            update(ForumReply).where(ForumReply.id == reply_id).values(votes=ForumReply.votes + delta)
        )
        result = (await db.execute(select(ForumReply.votes).where(ForumReply.id == reply_id))).scalar()

    await db.flush()
    return result or 0


# ── Stats ────────────────────────────────────────────────

async def get_stats(db: AsyncSession) -> dict:
    total_posts = (await db.execute(select(func.count()).select_from(ForumPost))).scalar() or 0
    total_replies = (await db.execute(select(func.count()).select_from(ForumReply))).scalar() or 0

    # Active users (posted or replied)
    post_authors = select(ForumPost.author_id).distinct()
    reply_authors = select(ForumReply.author_id).distinct()
    all_authors = post_authors.union(reply_authors).subquery()
    active_users = (await db.execute(select(func.count()).select_from(all_authors))).scalar() or 0

    # Hot tags
    all_tags_stmt = select(ForumPost.tags).where(ForumPost.tags.isnot(None))
    rows = (await db.execute(all_tags_stmt)).scalars().all()
    tag_counts: dict[str, int] = {}
    for tags_str in rows:
        for t in tags_str.split(","):
            t = t.strip()
            if t:
                tag_counts[t] = tag_counts.get(t, 0) + 1

    hot_tags = sorted(
        [{"name": k, "count": v} for k, v in tag_counts.items()],
        key=lambda x: x["count"], reverse=True
    )[:10]

    return {
        "total_posts": total_posts,
        "total_replies": total_replies,
        "active_users": active_users,
        "hot_tags": hot_tags,
    }
