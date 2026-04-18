"""add quality_score and quality_notes to articles

Revision ID: e1f2a3b4c5d6
Revises: d1e2f3a4b5c6
Create Date: 2026-04-18
"""
from alembic import op
import sqlalchemy as sa

revision = "e1f2a3b4c5d6"
down_revision = "d1e2f3a4b5c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("articles", sa.Column("quality_score", sa.Integer(), nullable=True))
    op.add_column("articles", sa.Column("quality_notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("articles", "quality_notes")
    op.drop_column("articles", "quality_score")
