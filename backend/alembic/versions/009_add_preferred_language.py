"""add preferred_language to users

Revision ID: 009
Revises: 008
"""
from alembic import op
import sqlalchemy as sa

revision = "009_add_preferred_language"
down_revision = "008_tag_source_summary"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('preferred_language', sa.String(5), server_default='he', nullable=False))

def downgrade():
    op.drop_column('users', 'preferred_language')
