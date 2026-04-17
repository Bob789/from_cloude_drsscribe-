"""add site analytics tables

Revision ID: 790b25c42127
Revises: a3f7c8d91e02
Create Date: 2026-04-17 11:24:58.494248
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '790b25c42127'
down_revision: Union[str, None] = 'a3f7c8d91e02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tables using IF NOT EXISTS so this runs cleanly on both
    # fresh databases (CI/CD) and existing local databases.
    op.execute("""
        CREATE TABLE IF NOT EXISTS site_page_views (
            id          SERIAL PRIMARY KEY,
            session_id  VARCHAR(64)  NOT NULL,
            visitor_ip_hash VARCHAR(64) NOT NULL,
            user_agent  TEXT,
            referrer    TEXT,
            page_path   VARCHAR(500) NOT NULL,
            article_slug VARCHAR(300),
            duration_seconds INTEGER,
            device_type VARCHAR(20),
            country     VARCHAR(5),
            utm_source  VARCHAR(100),
            utm_medium  VARCHAR(100),
            utm_campaign VARCHAR(100),
            created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_site_page_views_session_id    ON site_page_views (session_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_site_page_views_visitor_ip_hash ON site_page_views (visitor_ip_hash)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_site_page_views_page_path      ON site_page_views (page_path)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_site_page_views_article_slug   ON site_page_views (article_slug)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_site_page_views_created_at     ON site_page_views (created_at)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS site_search_logs (
            id           SERIAL PRIMARY KEY,
            session_id   VARCHAR(64)  NOT NULL,
            query        VARCHAR(500) NOT NULL,
            results_count INTEGER     NOT NULL DEFAULT 0,
            clicked_article_slug VARCHAR(300),
            created_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_site_search_logs_session_id ON site_search_logs (session_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_site_search_logs_query      ON site_search_logs (query)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_site_search_logs_created_at ON site_search_logs (created_at)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS site_events (
            id          SERIAL PRIMARY KEY,
            session_id  VARCHAR(64)  NOT NULL,
            event_type  VARCHAR(50)  NOT NULL,
            event_data  JSONB,
            page_path   VARCHAR(500),
            created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_site_events_session_id ON site_events (session_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_site_events_event_type ON site_events (event_type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_site_events_created_at ON site_events (created_at)")


def downgrade() -> None:
    op.drop_table('site_events')
    op.drop_table('site_search_logs')
    op.drop_table('site_page_views')
