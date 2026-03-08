"""add username, password_hash, auth_method to users

Revision ID: 004_add_local_auth_fields
Revises: 003_add_question_templates
Create Date: 2026-02-17
"""
from alembic import op
import sqlalchemy as sa

revision = "004_add_local_auth_fields"
down_revision = "003_add_question_templates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(100), unique=True, nullable=True))
    op.add_column("users", sa.Column("password_hash", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("auth_method", sa.String(20), server_default="google", nullable=False))


def downgrade() -> None:
    op.drop_column("users", "auth_method")
    op.drop_column("users", "password_hash")
    op.drop_column("users", "username")
