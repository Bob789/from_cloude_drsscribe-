"""
Articles router — public article serving + admin CRUD + AI generation triggers.
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, Body, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.permissions import require_admin
from app.models.user import User
from app.models.article import (
    Article, ArticleStatus, FactCheckStatus,
    ArticleGenerationJob, ArticleJobStatus,
    TrendingTopic,
)
from app.exceptions import NotFoundError

router = APIRouter(tags=["articles"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _article_card(a: Article) -> dict:
    return {
        "id": str(a.id),
        "slug": a.slug,
        "title": a.title,
        "subtitle": a.subtitle,
        "summary": a.summary,
        "category": a.category,
        "tags": a.tags or [],
        "author_name": a.author_name,
        "author_title": a.author_title,
        "hero_image_url": a.hero_image_url,
        "hero_image_alt": a.hero_image_alt,
        "read_time_minutes": a.read_time_minutes,
        "views": a.views,
        "likes": a.likes,
        "status": a.status.value if a.status else "draft",
        "fact_check_status": a.fact_check_status.value if a.fact_check_status else "unchecked",
        "published_at": a.published_at.isoformat() if a.published_at else None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def _article_full(a: Article) -> dict:
    d = _article_card(a)
    d.update({
        "content_html": a.content_html,
        "content_markdown": a.content_markdown,
        "seo_title": a.seo_title,
        "seo_description": a.seo_description,
        "seo_keywords": a.seo_keywords or [],
        "source_topic": a.source_topic,
        "source_type": a.source_type,
        "fact_check_notes": a.fact_check_notes,
        "generation_prompt": a.generation_prompt,
    })
    return d


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC ENDPOINTS (no auth)
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/articles")
async def list_articles(
    category: str | None = Query(None),
    tag: str | None = Query(None),
    search: str | None = Query(None),
    sort: str = Query("newest"),  # newest, popular, views
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """List published articles for public consumption."""
    stmt = select(Article).where(Article.status == ArticleStatus.published)

    if category:
        stmt = stmt.where(Article.category == category)
    if tag:
        stmt = stmt.where(Article.tags.contains([tag]))
    if search:
        stmt = stmt.where(or_(
            Article.title.ilike(f"%{search}%"),
            Article.summary.ilike(f"%{search}%"),
        ))

    # Sort
    if sort == "popular":
        stmt = stmt.order_by(Article.likes.desc(), Article.views.desc())
    elif sort == "views":
        stmt = stmt.order_by(Article.views.desc())
    else:
        stmt = stmt.order_by(Article.published_at.desc())

    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    articles = (await db.execute(stmt)).scalars().all()

    return {
        "items": [_article_card(a) for a in articles],
        "total": total,
        "page": page,
        "pages": (total + per_page - 1) // per_page,
    }


@router.get("/articles/{slug}")
async def get_article(slug: str, preview: str = Query(None), db: AsyncSession = Depends(get_db)):
    """Get article by slug. Published articles are public. Drafts require ?preview=1."""
    if preview:
        # Preview mode — show any status
        article = (await db.execute(select(Article).where(Article.slug == slug))).scalars().first()
    else:
        article = (await db.execute(
            select(Article).where(Article.slug == slug, Article.status == ArticleStatus.published)
        )).scalars().first()
    if not article:
        raise NotFoundError("מאמר", slug)

    article.views += 1
    await db.commit()

    return _article_full(article)


@router.post("/articles/{slug}/like")
async def like_article(slug: str, db: AsyncSession = Depends(get_db)):
    """Like an article."""
    article = (await db.execute(
        select(Article).where(Article.slug == slug, Article.status == ArticleStatus.published)
    )).scalars().first()
    if not article:
        raise NotFoundError("מאמר", slug)
    article.likes += 1
    await db.commit()
    return {"likes": article.likes}


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/admin/articles")
async def admin_list_articles(
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all articles for admin management."""
    stmt = select(Article)
    if status_filter:
        try:
            stmt = stmt.where(Article.status == ArticleStatus(status_filter))
        except ValueError:
            pass
    stmt = stmt.order_by(Article.created_at.desc())
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    articles = (await db.execute(stmt)).scalars().all()
    return {"items": [_article_card(a) for a in articles], "total": total}


@router.get("/admin/articles/{article_id}")
async def admin_get_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    article = (await db.execute(select(Article).where(Article.id == article_id))).scalars().first()
    if not article:
        raise NotFoundError("מאמר", str(article_id))
    return _article_full(article)


@router.put("/admin/articles/{article_id}")
async def admin_update_article(
    article_id: uuid.UUID,
    updates: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Edit an article. Accepts any subset of article fields."""
    article = (await db.execute(select(Article).where(Article.id == article_id))).scalars().first()
    if not article:
        raise NotFoundError("מאמר", str(article_id))

    allowed = {
        "title", "subtitle", "content_html", "content_markdown", "summary",
        "category", "tags", "author_name", "author_title",
        "hero_image_url", "hero_image_alt",
        "seo_title", "seo_description", "seo_keywords",
        "fact_check_notes",
    }
    for key, val in updates.items():
        if key in allowed:
            setattr(article, key, val)

    await db.commit()
    return _article_full(article)


@router.put("/admin/articles/{article_id}/status")
async def admin_change_status(
    article_id: uuid.UUID,
    new_status: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Change article status (draft/review/published/archived)."""
    article = (await db.execute(select(Article).where(Article.id == article_id))).scalars().first()
    if not article:
        raise NotFoundError("מאמר", str(article_id))

    try:
        article.status = ArticleStatus(new_status)
    except ValueError:
        return {"error": f"סטטוס לא תקין: {new_status}"}

    if new_status == "published" and not article.published_at:
        article.published_at = datetime.now(timezone.utc)

    await db.commit()
    return {"ok": True, "status": article.status.value}


@router.put("/admin/articles/{article_id}/fact-check")
async def admin_fact_check(
    article_id: uuid.UUID,
    fact_check_status: str = Body(...),
    fact_check_notes: str = Body(""),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    article = (await db.execute(select(Article).where(Article.id == article_id))).scalars().first()
    if not article:
        raise NotFoundError("מאמר", str(article_id))

    try:
        article.fact_check_status = FactCheckStatus(fact_check_status)
    except ValueError:
        pass
    article.fact_check_notes = fact_check_notes
    await db.commit()
    return {"ok": True}


@router.delete("/admin/articles/{article_id}")
async def admin_delete_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    article = (await db.execute(select(Article).where(Article.id == article_id))).scalars().first()
    if not article:
        raise NotFoundError("מאמר", str(article_id))
    article.status = ArticleStatus.archived
    await db.commit()
    return {"ok": True}


@router.post("/admin/articles/{article_id}/generate-image")
async def admin_regenerate_article_image(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Generate (or regenerate) the hero image for an existing article."""
    from app.services.image_service import find_hero_image

    article = (await db.execute(select(Article).where(Article.id == article_id))).scalars().first()
    if not article:
        raise NotFoundError("מאמר", str(article_id))

    topic = article.source_topic or article.title
    image = await find_hero_image(topic, article.category or "general")
    if not image:
        return {"ok": False, "error": "Failed to generate image — check API keys and MinIO"}

    article.hero_image_url = image["url"]
    article.hero_image_alt = image.get("alt", article.title)
    await db.commit()
    return {"ok": True, "hero_image_url": image["url"], "attribution": image.get("attribution")}


# ── Generation endpoints ──────────────────────────────────────────────────────

@router.post("/admin/articles/generate", status_code=status.HTTP_201_CREATED)
async def admin_generate_article(
    topic: str = Body(...),
    config: dict = Body({}),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Trigger AI article generation. Runs synchronously for now (fast enough for single articles)."""
    from app.services.content_service import generate_article, generate_seo_metadata
    from app.services.image_service import find_hero_image

    # Create job record
    job = ArticleGenerationJob(
        topic=topic,
        status=ArticleJobStatus.generating,
        generation_config=config,
        created_by=current_user.id,
    )
    db.add(job)
    await db.flush()

    try:
        # Step 1: Generate article content
        result = await generate_article(topic, config)

        # Step 2: Generate SEO metadata
        job.status = ArticleJobStatus.seo_gen
        await db.flush()
        seo = await generate_seo_metadata(result.get("title", ""), result.get("content_markdown", ""))

        # Step 3: Find hero image
        job.status = ArticleJobStatus.image_search
        await db.flush()
        image = await find_hero_image(topic, result.get("category", "general"))

        # Ensure unique slug
        base_slug = seo.get("slug", f"article-{uuid.uuid4().hex[:8]}")
        slug = base_slug
        counter = 1
        while (await db.execute(select(Article).where(Article.slug == slug))).scalars().first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Create article
        article = Article(
            slug=slug,
            title=result.get("title", topic),
            subtitle=result.get("subtitle"),
            content_html=result.get("content_html"),
            content_markdown=result.get("content_markdown"),
            summary=result.get("summary"),
            category=result.get("category", "general"),
            tags=result.get("tags", []),
            author_name=result.get("author_name", "צוות Medical Hub"),
            author_title=result.get("author_title"),
            hero_image_url=image["url"] if image else None,
            hero_image_alt=image["alt"] if image else None,
            seo_title=seo.get("seo_title"),
            seo_description=seo.get("seo_description"),
            seo_keywords=seo.get("seo_keywords", []),
            status=ArticleStatus.draft,
            source_topic=topic,
            source_type="manual",
            generation_prompt=result.get("generation_prompt"),
            read_time_minutes=result.get("read_time_minutes", 5),
            created_by=current_user.id,
        )
        db.add(article)
        await db.flush()

        job.article_id = article.id
        job.status = ArticleJobStatus.done
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()

        return {
            "ok": True,
            "job_id": str(job.id),
            "article_id": str(article.id),
            "title": article.title,
            "slug": article.slug,
        }

    except Exception as e:
        job.status = ArticleJobStatus.error
        job.error_message = str(e)[:500]
        await db.commit()
        return {"ok": False, "error": str(e)[:200], "job_id": str(job.id)}


@router.get("/admin/articles/jobs")
async def admin_list_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    jobs = (await db.execute(
        select(ArticleGenerationJob).order_by(ArticleGenerationJob.created_at.desc()).limit(20)
    )).scalars().all()
    return [
        {
            "id": str(j.id),
            "topic": j.topic,
            "status": j.status.value,
            "error_message": j.error_message,
            "article_id": str(j.article_id) if j.article_id else None,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        }
        for j in jobs
    ]


@router.get("/admin/articles/stats")
async def admin_articles_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    total = (await db.execute(select(func.count()).select_from(Article))).scalar() or 0
    published = (await db.execute(select(func.count()).select_from(Article).where(Article.status == ArticleStatus.published))).scalar() or 0
    drafts = (await db.execute(select(func.count()).select_from(Article).where(Article.status == ArticleStatus.draft))).scalar() or 0
    review = (await db.execute(select(func.count()).select_from(Article).where(Article.status == ArticleStatus.review))).scalar() or 0
    total_views = (await db.execute(select(func.sum(Article.views)))).scalar() or 0
    total_likes = (await db.execute(select(func.sum(Article.likes)))).scalar() or 0

    return {
        "total": total,
        "published": published,
        "drafts": drafts,
        "review": review,
        "total_views": total_views,
        "total_likes": total_likes,
    }


# ── Trending topics ───────────────────────────────────────────────────────────

@router.get("/admin/articles/trends")
async def admin_list_trends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    topics = (await db.execute(
        select(TrendingTopic).order_by(TrendingTopic.relevance_score.desc()).limit(30)
    )).scalars().all()
    return [
        {
            "id": str(t.id),
            "topic": t.topic,
            "source": t.source,
            "relevance_score": t.relevance_score,
            "used": t.used,
            "fetched_at": t.fetched_at.isoformat() if t.fetched_at else None,
        }
        for t in topics
    ]


@router.post("/admin/articles/trends/add")
async def admin_add_trend(
    topic: str = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    t = TrendingTopic(topic=topic, source="manual", relevance_score=1.0)
    db.add(t)
    await db.commit()
    return {"ok": True, "id": str(t.id)}
