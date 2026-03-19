"""add calendar fields to users

Revision ID: 005
Revises: 004
"""
from alembic import op
import sqlalchemy as sa

revision = "005_add_calendar_fields"
down_revision = "004_add_local_auth_fields"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("calendar_refresh_token", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("calendar_connected", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("users", sa.Column("calendar_connected_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("users", "calendar_connected_at")
    op.drop_column("users", "calendar_connected")
    op.drop_column("users", "calendar_refresh_token")
