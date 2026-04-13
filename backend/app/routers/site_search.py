"""
Unified site search — searches articles + forum posts in a single query.
Public endpoint, no auth required.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, or_, case, literal
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.article import Article, ArticleStatus
from app.models.forum import ForumPost
from app.models.user import User

router = APIRouter()


@router.get("/site/search")
async def site_search(
    q: str = Query(..., min_length=2, max_length=200),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Search articles and forum posts together, ranked by relevance."""
    term = f"%{q}%"

    # Search articles
    art_stmt = (
        select(Article)
        .where(Article.status == ArticleStatus.published)
        .where(or_(
            Article.title.ilike(term),
            Article.summary.ilike(term),
            Article.content_markdown.ilike(term),
        ))
    )
    articles = (await db.execute(art_stmt)).scalars().all()

    # Search forum posts
    display_name = func.coalesce(User.nickname, User.name).label("author_name")
    forum_stmt = (
        select(ForumPost, display_name)
        .join(User, ForumPost.author_id == User.id)
        .where(or_(
            ForumPost.title.ilike(term),
            ForumPost.body.ilike(term),
        ))
    )
    forum_rows = (await db.execute(forum_stmt)).all()

    # Build unified results with relevance scoring
    results = []

    for a in articles:
        score = 0
        q_lower = q.lower()
        if a.title and q_lower in a.title.lower():
            score += 10
        if a.summary and q_lower in a.summary.lower():
            score += 5
        if a.content_markdown and q_lower in a.content_markdown.lower():
            score += 2
        score += min((a.views or 0) / 100, 5)  # bonus for popular articles
        score += min((a.likes or 0) / 10, 3)

        results.append({
            "type": "article",
            "id": str(a.id),
            "title": a.title,
            "snippet": (a.summary or "")[:200],
            "url": f"/articles/{a.slug}",
            "category": a.category,
            "author_name": a.author_name,
            "views": a.views or 0,
            "likes": a.likes or 0,
            "date": a.published_at.isoformat() if a.published_at else None,
            "read_time_minutes": a.read_time_minutes,
            "score": round(score, 1),
        })

    for row in forum_rows:
        post = row.ForumPost
        author = row.author_name
        score = 0
        q_lower = q.lower()
        if post.title and q_lower in post.title.lower():
            score += 10
        if post.body and q_lower in post.body.lower():
            score += 3
        score += min((post.views or 0) / 100, 3)
        score += min((post.votes or 0) / 5, 3)

        # Build snippet from body
        body_text = (post.body or "")
        snippet = body_text[:200]
        # Try to find snippet around the search term
        idx = body_text.lower().find(q_lower)
        if idx > 0:
            start = max(0, idx - 60)
            snippet = ("..." if start > 0 else "") + body_text[start:start + 200]

        results.append({
            "type": "forum",
            "id": str(post.id),
            "title": post.title,
            "snippet": snippet,
            "url": f"/forum/{post.id}",
            "category": None,
            "author_name": author,
            "views": post.views or 0,
            "likes": post.votes or 0,
            "date": post.created_at.isoformat() if post.created_at else None,
            "read_time_minutes": None,
            "score": round(score, 1),
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    total = len(results)
    start = (page - 1) * per_page
    paged = results[start:start + per_page]

    return {
        "items": paged,
        "total": total,
        "page": page,
        "pages": (total + per_page - 1) // per_page if total else 0,
        "query": q,
    }


@router.get("/site/stats")
async def site_stats(db: AsyncSession = Depends(get_db)):
    """Public stats for the homepage: article count, forum post count, expert count."""
    articles_count = (
        await db.execute(
            select(func.count()).select_from(Article).where(Article.status == ArticleStatus.published)
        )
    ).scalar() or 0

    forum_count = (
        await db.execute(select(func.count()).select_from(ForumPost))
    ).scalar() or 0

    # Experts are currently hardcoded in frontend (8 doctors)
    experts_count = 8

    return {
        "articles": articles_count,
        "forum_posts": forum_count,
        "experts": experts_count,
    }
