import os
import re
import structlog

logger = structlog.get_logger()

SENSITIVE_KEYS = {"password", "secret", "token", "api_key", "encryption_key", "authorization"}


def get_secret(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def redact_sensitive(data: dict) -> dict:
    redacted = {}
    for key, value in data.items():
        if any(s in key.lower() for s in SENSITIVE_KEYS):
            redacted[key] = "***REDACTED***"
        elif isinstance(value, dict):
            redacted[key] = redact_sensitive(value)
        else:
            redacted[key] = value
    return redacted


def redact_log_message(message: str) -> str:
    message = re.sub(r'(?i)(password|secret|token|api_key)\s*[=:]\s*\S+', r'\1=***REDACTED***', message)
    message = re.sub(r'Bearer\s+[\w\-._~+/]+=*', 'Bearer ***REDACTED***', message)
    return message
