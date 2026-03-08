from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.search import SearchResult
from app.services.search_service import combined_search, search_by_tags, search_db_text
from app.services.search_indexer import reindex_all

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResult)
async def search_all(
    q: str | None = Query(None),
    tags: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    offset = (page - 1) * per_page

    # Tag-only search (no text query) → use PostgreSQL
    if not q and tag_list:
        result = await search_by_tags(db, tag_list, date_from, date_to, offset, per_page)
        return SearchResult(hits=result["hits"], total=result["total"], page=page, per_page=per_page)

    if not q:
        return SearchResult(hits=[], total=0, page=page, per_page=per_page)

    # Try Meilisearch first, fallback to PostgreSQL
    try:
        result = await combined_search(q, tag_list, date_from, date_to, offset, per_page)
        if result["total"] > 0:
            return SearchResult(hits=result["hits"], total=result["total"], page=page, per_page=per_page)
    except Exception:
        pass

    # Fallback: PostgreSQL text search
    result = await search_db_text(db, q, tag_list, date_from, date_to, offset, per_page)
    return SearchResult(hits=result["hits"], total=result["total"], page=page, per_page=per_page)


@router.post("/reindex")
async def reindex(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await reindex_all(db)
    return {"message": "Reindex completed", **result}
