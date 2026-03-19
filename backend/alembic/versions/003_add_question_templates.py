"""add question_templates table and questionnaire_data column

Revision ID: 003_add_question_templates
Revises: 002_add_recording_chunks
Create Date: 2026-02-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "003_add_question_templates"
down_revision = "002_add_recording_chunks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "question_templates",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("icon", sa.String(50), server_default="clipboard"),
        sa.Column("color", sa.String(7), server_default="#3B82F6"),
        sa.Column("questions", JSONB, nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("is_shared", sa.Boolean, server_default="false"),
        sa.Column("usage_count", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.add_column("summaries", sa.Column("questionnaire_data", JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column("summaries", "questionnaire_data")
    op.drop_table("question_templates")
