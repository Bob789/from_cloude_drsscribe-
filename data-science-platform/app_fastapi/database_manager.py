# File: app_fastapi/database_manager.py
"""
Database manager module - backward compatible interface.

This module provides a unified interface to all database operations,
delegating to specialized modules in the database package.
"""

from app_fastapi.database.connection import (
    get_connection, connect_to_db, create_database_if_not_exists, DB_CONFIG
)
from app_fastapi.database.user_operations import (
    create_users_table, select_all_users, add_user, update_user,
    update_user_full, delete_user, get_user_tokens, update_user_tokens,
    check_user_is_admin, set_user_admin, get_user_by_name
)
from app_fastapi.database.logging_operations import (
    create_usage_logs_table, add_usage_log, get_usage_logs, clear_usage_logs
)

__all__ = [
    'get_connection', 'connect_to_db', 'create_database_if_not_exists', 'DB_CONFIG',
    'create_users_table', 'select_all_users', 'add_user', 'update_user',
    'update_user_full', 'delete_user', 'get_user_tokens', 'update_user_tokens',
    'check_user_is_admin', 'set_user_admin', 'get_user_by_name',
    'create_usage_logs_table', 'add_usage_log', 'get_usage_logs', 'clear_usage_logs'
]