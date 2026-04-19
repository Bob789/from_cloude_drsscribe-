"""add_glossary_terms

Revision ID: d1e2f3a4b5c6
Revises: c3d4e5f6a7b8
Create Date: 2026-04-18 22:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'glossary_terms',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('term', sa.String(200), nullable=False, unique=True),
        sa.Column('definition', sa.Text, nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_glossary_terms_term', 'glossary_terms', ['term'])


def downgrade() -> None:
    op.drop_index('ix_glossary_terms_term', table_name='glossary_terms')
    op.drop_table('glossary_terms')
