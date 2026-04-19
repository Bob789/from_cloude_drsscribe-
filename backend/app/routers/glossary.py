"""
Glossary router — public terms list + admin CRUD.
"""
import uuid
from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.permissions import require_admin
from app.models.glossary import GlossaryTerm

router = APIRouter(tags=["glossary"])


# ── Public ────────────────────────────────────────────────────────────────────

@router.get("/glossary")
async def list_glossary(db: AsyncSession = Depends(get_db)):
    """Return all glossary terms (public)."""
    terms = (await db.execute(
        select(GlossaryTerm).order_by(GlossaryTerm.term)
    )).scalars().all()
    return [
        {"id": str(t.id), "term": t.term, "definition": t.definition, "category": t.category}
        for t in terms
    ]


# ── Admin CRUD ────────────────────────────────────────────────────────────────

@router.post("/admin/glossary")
async def create_glossary_term(
    body: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_admin),
):
    """Add a new glossary term."""
    term_text = (body.get("term") or "").strip()
    definition = (body.get("definition") or "").strip()
    if not term_text or not definition:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="term and definition required")

    # Check uniqueness
    existing = (await db.execute(
        select(GlossaryTerm).where(GlossaryTerm.term == term_text)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="term already exists")

    entry = GlossaryTerm(
        term=term_text,
        definition=definition,
        category=body.get("category") or None,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return {"id": str(entry.id), "term": entry.term, "definition": entry.definition, "category": entry.category}


@router.delete("/admin/glossary/{term_id}")
async def delete_glossary_term(
    term_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_admin),
):
    """Delete a glossary term by ID."""
    entry = (await db.execute(
        select(GlossaryTerm).where(GlossaryTerm.id == term_id)
    )).scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="term not found")
    await db.delete(entry)
    await db.commit()
    return {"ok": True}
