# File: app_fastapi/database/__init__.py
"""
Database package for PostgreSQL operations.

This package provides modular database functionality including
connection management, user operations, and logging.
"""

from .connection import get_connection, connect_to_db, create_database_if_not_exists, DB_CONFIG
from .user_operations import (
    create_users_table, select_all_users, add_user, update_user,
    update_user_full, delete_user, get_user_tokens, update_user_tokens,
    check_user_is_admin, set_user_admin, get_user_by_name
)
from .logging_operations import (
    create_usage_logs_table, add_usage_log, get_usage_logs, clear_usage_logs
)

__all__ = [
    'get_connection', 'connect_to_db', 'create_database_if_not_exists', 'DB_CONFIG',
    'create_users_table', 'select_all_users', 'add_user', 'update_user',
    'update_user_full', 'delete_user', 'get_user_tokens', 'update_user_tokens',
    'check_user_is_admin', 'set_user_admin', 'get_user_by_name',
    'create_usage_logs_table', 'add_usage_log', 'get_usage_logs', 'clear_usage_logs'
]
