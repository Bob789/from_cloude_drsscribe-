"""add recording_chunks table

Revision ID: 002_add_recording_chunks
Revises: 001_add_display_id
Create Date: 2026-02-15
"""
from alembic import op
import sqlalchemy as sa

revision = "002_add_recording_chunks"
down_revision = "001_add_display_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recording_chunks",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("visit_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("visits.id"), nullable=False, index=True),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("audio_url", sa.String(1000), nullable=False),
        sa.Column("duration_seconds", sa.Float, nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_recording_chunks_visit_chunk", "recording_chunks", ["visit_id", "chunk_index"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_recording_chunks_visit_chunk", table_name="recording_chunks")
    op.drop_table("recording_chunks")
