import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, status
from app.config import settings


def _signing_key() -> str:
    """Return the key used for signing JWTs (private key for RS256, secret for HS256)."""
    if settings.JWT_ALGORITHM == "RS256":
        if not settings.JWT_PRIVATE_KEY:
            raise ValueError("JWT_PRIVATE_KEY must be set when JWT_ALGORITHM=RS256")
        return settings.JWT_PRIVATE_KEY
    return settings.JWT_SECRET


def _verify_key() -> str:
    """Return the key used for verifying JWTs (public key for RS256, secret for HS256)."""
    if settings.JWT_ALGORITHM == "RS256":
        if not settings.JWT_PUBLIC_KEY:
            raise ValueError("JWT_PUBLIC_KEY must be set when JWT_ALGORITHM=RS256")
        return settings.JWT_PUBLIC_KEY
    return settings.JWT_SECRET


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _signing_key(), algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _signing_key(), algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, _verify_key(), algorithms=[settings.JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
