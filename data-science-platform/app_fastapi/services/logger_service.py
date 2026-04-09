# File: Final_Project_v003/app_fastapi/services/logger_service.py
"""
Centralized logging service with file rotation.
Logs all important operations: auth, training, predictions, token changes, errors.
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = "app_fastapi/logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure logger
logger = logging.getLogger("ml_platform")
logger.setLevel(logging.INFO)

# File handler with rotation (10MB max, keep 5 backup files)
log_file = os.path.join(LOGS_DIR, "server.log")
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)

# Format: timestamp | level | message
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def log_info(message: str):
    """Log informational message."""
    logger.info(message)

def log_warning(message: str):
    """Log warning message."""
    logger.warning(message)

def log_error(message: str):
    """Log error message."""
    logger.error(message)

def log_registration(username: str, success: bool):
    """Log user registration attempt."""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"REGISTRATION | User: {username} | Status: {status}")

def log_login(username: str, success: bool):
    """Log user login attempt."""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"LOGIN | User: {username} | Status: {status}")

def log_token_operation(username: str, operation: str, tokens: int, success: bool):
    """Log token add/deduct operation."""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"TOKEN_{operation.upper()} | User: {username} | Tokens: {tokens} | Status: {status}")

def log_model_training(username: str, model_name: str, success: bool, details: str = ""):
    """Log model training operation."""
    status = "SUCCESS" if success else "FAILED"
    msg = f"TRAINING | User: {username} | Model: {model_name} | Status: {status}"
    if details:
        msg += f" | Details: {details}"
    logger.info(msg)

def log_prediction(username: str, model_name: str, success: bool, details: str = ""):
    """Log prediction operation."""
    status = "SUCCESS" if success else "FAILED"
    msg = f"PREDICTION | User: {username} | Model: {model_name} | Status: {status}"
    if details:
        msg += f" | Details: {details}"
    logger.info(msg)

def log_validation_error(operation: str, error: str):
    """Log validation error."""
    logger.warning(f"VALIDATION_ERROR | Operation: {operation} | Error: {error}")

def log_insufficient_tokens(username: str, operation: str, required: int, available: int):
    """Log insufficient token error."""
    logger.warning(
        f"INSUFFICIENT_TOKENS | User: {username} | Operation: {operation} | "
        f"Required: {required} | Available: {available}"
    )