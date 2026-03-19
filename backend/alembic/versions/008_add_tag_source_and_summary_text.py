"""add tag source column and summary_text column

Revision ID: 008
Revises: 007
"""
from alembic import op
import sqlalchemy as sa

revision = "008_tag_source_summary"
down_revision = "007_add_patient_key_type"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('tags', sa.Column('source', sa.String(20), nullable=False, server_default='manual'))
    op.create_index('ix_tags_source', 'tags', ['source'])
    op.add_column('summaries', sa.Column('summary_text', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('summaries', 'summary_text')
    op.drop_index('ix_tags_source', table_name='tags')
    op.drop_column('tags', 'source')
