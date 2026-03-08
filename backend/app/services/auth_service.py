import time
import uuid
import bcrypt
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.config import settings
from app.models.user import User
from app.utils.jwt import create_access_token, create_refresh_token, decode_token
from app.services import redis_service


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


async def verify_google_token(token: str, token_type: str = "id_token") -> dict:
    if token_type == "access_token":
        return await _verify_access_token(token)
    return _verify_id_token(token)


def _verify_id_token(token: str) -> dict:
    try:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
        if idinfo["iss"] not in ("accounts.google.com", "https://accounts.google.com"):
            raise ValueError("Invalid issuer")
        return idinfo
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")


async def _verify_access_token(token: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google access token")
    data = resp.json()
    if not data.get("email_verified", False):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified")
    return data


async def authenticate_local(db: AsyncSession, username: str, password: str) -> User:
    result = await db.execute(select(User).where(User.username == username, User.is_active == True))  # noqa: E712
    user = result.scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="שם משתמש או סיסמה שגויים")
    return user


async def get_or_create_user(db: AsyncSession, google_info: dict) -> User:
    result = await db.execute(select(User).where(User.google_id == google_info["sub"]))
    user = result.scalar_one_or_none()
    if user:
        return user

    result = await db.execute(select(User).where(User.email == google_info["email"]))
    user = result.scalar_one_or_none()
    if user:
        user.google_id = google_info["sub"]
        user.avatar_url = google_info.get("picture")
        await db.commit()
        await db.refresh(user)
        return user

    user = User(
        id=uuid.uuid4(),
        email=google_info["email"],
        name=google_info.get("name", google_info["email"]),
        google_id=google_info["sub"],
        avatar_url=google_info.get("picture"),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def generate_tokens(user: User) -> dict:
    access = create_access_token(user.id, user.role.value)
    refresh = create_refresh_token(user.id)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "avatar_url": user.avatar_url,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
    }


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    jti = payload.get("jti")
    if jti and await redis_service.is_refresh_token_used(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token already used")
    user_id = uuid.UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))  # noqa: E712
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if jti:
        exp = payload.get("exp")
        ttl = max(int(exp - time.time()), 1) if exp else settings.JWT_REFRESH_EXPIRE_DAYS * 86400
        await redis_service.mark_refresh_token_used(jti, ttl)
    return generate_tokens(user)


async def logout_user(access_token: str) -> None:
    payload = decode_token(access_token)
    jti = payload.get("jti")
    exp = payload.get("exp")
    if jti and exp:
        ttl = max(int(exp - time.time()), 1)
        await redis_service.blacklist_access_token(jti, ttl)
