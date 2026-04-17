"""hero_image_url_to_text

Revision ID: c3d4e5f6a7b8
Revises: 8ffbaf51245b
Create Date: 2026-04-17 19:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = '8ffbaf51245b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE articles ALTER COLUMN hero_image_url TYPE TEXT")


def downgrade() -> None:
    op.execute("ALTER TABLE articles ALTER COLUMN hero_image_url TYPE VARCHAR(1000) USING hero_image_url::VARCHAR(1000)")
