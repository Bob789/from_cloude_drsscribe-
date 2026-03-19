"""add display_id to patients, visits, summaries

Revision ID: 001_add_display_id
Revises:
Create Date: 2026-02-15
"""
from alembic import op
import sqlalchemy as sa

revision = "001_add_display_id"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    for table in ("patients", "visits", "summaries"):
        seq = f"{table}_display_id_seq"
        op.execute(f"CREATE SEQUENCE IF NOT EXISTS {seq}")
        op.add_column(table, sa.Column("display_id", sa.Integer(), server_default=sa.text(f"nextval('{seq}')"), nullable=True))
        op.execute(f"UPDATE {table} SET display_id = nextval('{seq}') WHERE display_id IS NULL")
        op.alter_column(table, "display_id", nullable=False)
        op.create_unique_constraint(f"uq_{table}_display_id", table, ["display_id"])
        op.create_index(f"ix_{table}_display_id", table, ["display_id"])


def downgrade():
    for table in ("patients", "visits", "summaries"):
        seq = f"{table}_display_id_seq"
        op.drop_index(f"ix_{table}_display_id", table_name=table)
        op.drop_constraint(f"uq_{table}_display_id", table, type_="unique")
        op.drop_column(table, "display_id")
        op.execute(f"DROP SEQUENCE IF EXISTS {seq}")
