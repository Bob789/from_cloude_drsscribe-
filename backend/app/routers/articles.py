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
    TrendingTopic, ArticleComment,
)
from app.models.glossary import GlossaryTerm
from app.exceptions import NotFoundError
from app.config import settings

router = APIRouter(tags=["articles"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_review_notes(review: dict, attempt: int = 1) -> str | None:
    """Format Mistral review result into a readable string for the admin panel."""
    if review.get("expired"):
        return "⚠️ MISTRAL_API_KEY פג תוקף או לא תקין — יש לעדכן ב-.env"
    if review.get("skipped"):
        return f"Review skipped: {review.get('reason', 'unknown')}"
    prefix = f"[ניסיון {attempt}] " if attempt > 1 else ""
    lines = [
        f"{prefix}ציון כולל: {review.get('total_score')}/100",
        f"  מבנה: {review.get('structure_score')}/15",
        f"  שלמות: {review.get('completeness_score')}/15",
        f"  אחריות רפואית: {review.get('responsibility_score')}/15",
        f"  שפה: {review.get('language_score')}/15",
        f"  דיוק עובדתי: {review.get('factual_score')}/15",
        f"  לוגיקה וסגנון: {review.get('logic_style_score')}/15",
        f"  בטיחות ורלוונטיות: {review.get('safety_score')}/10",
    ]
    issues = review.get("issues") or []
    if issues:
        lines.append("בעיות: " + " | ".join(issues))
    strengths = review.get("strengths") or []
    if strengths:
        lines.append("חוזקות: " + " | ".join(strengths))
    return "\n".join(lines)

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
        "quality_score": a.quality_score,
        "quality_notes": a.quality_notes,
    }

def _article_full(a: Article) -> dict:
    """Card fields + full content + SEO + source/generation metadata."""
    data = _article_card(a)
    data.update({
        "content_html": a.content_html,
        "content_markdown": a.content_markdown,
        "seo_title": a.seo_title,
        "seo_description": a.seo_description,
        "seo_keywords": a.seo_keywords or [],
        "source_topic": a.source_topic,
        "source_type": a.source_type,
        "generation_prompt": a.generation_prompt,
        "fact_check_notes": a.fact_check_notes,
        "updated_at": a.updated_at.isoformat() if a.updated_at else None,
    })
    return data

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
    # Snapshot the response BEFORE commit to avoid MissingGreenlet on lazy refresh
    result = _article_full(article)
    await db.commit()

    return result


@router.get("/articles/tags")
async def list_article_tags(db: AsyncSession = Depends(get_db)):
    """List all unique tags used in published articles with counts."""
    from sqlalchemy import text
    result = await db.execute(
        text("""
            SELECT tag, COUNT(*) as count
            FROM articles, jsonb_array_elements_text(tags) AS tag
            WHERE status = 'published' AND tags IS NOT NULL AND jsonb_array_length(tags) > 0
            GROUP BY tag
            ORDER BY count DESC
            LIMIT 100
        """)
    )
    tags = [{"tag": row[0], "count": int(row[1])} for row in result.all()]
    return {"tags": tags}


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
# COMMENTS ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/articles/{slug}/comments")
async def list_comments(slug: str, db: AsyncSession = Depends(get_db)):
    """List visible comments for an article."""
    article = (await db.execute(
        select(Article).where(Article.slug == slug, Article.status == ArticleStatus.published)
    )).scalars().first()
    if not article:
        raise NotFoundError("מאמר", slug)

    stmt = (
        select(ArticleComment, User)
        .join(User, ArticleComment.author_id == User.id)
        .where(ArticleComment.article_id == article.id, ArticleComment.is_visible == True)
        .order_by(ArticleComment.created_at.asc())
    )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "id": str(c.id),
            "body": c.body,
            "author_name": u.nickname or u.name,
            "author_avatar": u.avatar_url,
            "created_at": c.created_at.isoformat(),
        }
        for c, u in rows
    ]


@router.post("/articles/{slug}/comments", status_code=201)
async def add_comment(
    slug: str,
    body: str = Body(..., embed=True, min_length=2, max_length=2000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a comment to an article. Requires authentication."""
    article = (await db.execute(
        select(Article).where(Article.slug == slug, Article.status == ArticleStatus.published)
    )).scalars().first()
    if not article:
        raise NotFoundError("מאמר", slug)

    comment = ArticleComment(article_id=article.id, author_id=current_user.id, body=body)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return {
        "id": str(comment.id),
        "body": comment.body,
        "author_name": current_user.nickname or current_user.name,
        "author_avatar": current_user.avatar_url,
        "created_at": comment.created_at.isoformat(),
    }


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
    from app.services.review_service import review_article, fix_article_with_gpt

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

        # Step 2: Quality review by Mistral (attempt 1)
        job.status = ArticleJobStatus.seo_gen
        await db.flush()
        review = await review_article(
            title=result.get("title", topic),
            content_markdown=result.get("content_markdown", ""),
        )

        score = review.get("total_score")
        retry_attempted = False
        retry_score = None
        mistral_expired = review.get("expired", False)

        # Step 2b: If score < threshold and Mistral gave issues → ask GPT to fix, re-review
        threshold = settings.ARTICLE_QUALITY_THRESHOLD
        if (
            score is not None
            and score < threshold
            and not review.get("skipped")
            and review.get("issues")
        ):
            retry_attempted = True
            issues = review.get("issues", [])
            fixed = await fix_article_with_gpt(
                title=result.get("title", topic),
                content_markdown=result.get("content_markdown", ""),
                issues=issues,
            )
            if fixed and fixed.get("content_markdown"):
                # Merge fixed fields back into result
                for field in ("title", "subtitle", "content_markdown", "summary"):
                    if fixed.get(field):
                        result[field] = fixed[field]

                # Re-review fixed article
                review2 = await review_article(
                    title=result.get("title", topic),
                    content_markdown=result.get("content_markdown", ""),
                )
                retry_score = review2.get("total_score")
                if retry_score is not None and retry_score > (score or 0):
                    # Use better review result
                    review = review2
                    score = retry_score

        # Step 3: Generate SEO metadata
        job.status = ArticleJobStatus.seo_gen
        await db.flush()
        seo = await generate_seo_metadata(result.get("title", ""), result.get("content_markdown", ""))

        # Step 4: Find hero image
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

        # Build quality notes — include retry info if applicable
        quality_notes_parts = [_format_review_notes(review, attempt=2 if retry_attempted else 1)]
        if retry_attempted:
            if retry_score is not None and retry_score >= threshold:
                quality_notes_parts.insert(0, f"✅ תוקן אוטומטית ע\"י GPT | ציון לפני תיקון: {score}/100")
            else:
                quality_notes_parts.insert(0, f"⚠️ לא תוקן בהצלחה | ציון לפני תיקון: {score}/100")

        # Mistral key expiry alert
        if mistral_expired:
            quality_notes_parts.insert(0, "🔑 MISTRAL_API_KEY פג תוקף — יש לעדכן ב-.env")

        quality_notes = "\n\n".join(quality_notes_parts)

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
            quality_score=score,
            quality_notes=quality_notes,
        )
        db.add(article)
        await db.flush()

        job.article_id = article.id
        job.status = ArticleJobStatus.done
        job.completed_at = datetime.now(timezone.utc)

        # Auto-publish if quality score meets threshold
        auto_published = False
        if score is not None and not review.get("skipped") and score >= threshold:
            article.status = ArticleStatus.published
            article.published_at = datetime.now(timezone.utc)
            auto_published = True

        # Save glossary terms extracted by AI (skip already-existing terms)
        for item in (result.get("glossary") or []):
            term_text = (item.get("term") or "").strip()[:200]
            definition = (item.get("definition") or "").strip()
            if not term_text or not definition:
                continue
            exists = (await db.execute(
                select(GlossaryTerm).where(GlossaryTerm.term == term_text)
            )).scalar_one_or_none()
            if not exists:
                db.add(GlossaryTerm(
                    term=term_text,
                    definition=definition,
                    category=result.get("category") or None,
                ))

        await db.commit()

        return {
            "ok": True,
            "job_id": str(job.id),
            "article_id": str(article.id),
            "title": article.title,
            "slug": article.slug,
            "quality_score": score,
            "auto_published": auto_published,
            "retry_attempted": retry_attempted,
            "retry_score": retry_score,
            "mistral_expired": mistral_expired,
            "issues": review.get("issues") or [],
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
