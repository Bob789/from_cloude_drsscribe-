"""add reputation to users

Revision ID: a3f7c8d91e02
Revises: 9a262f8f6683
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'a3f7c8d91e02'
down_revision: Union[str, None] = '9a262f8f6683'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('reputation', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('users', 'reputation')
