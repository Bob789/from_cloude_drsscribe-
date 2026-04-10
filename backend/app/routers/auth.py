from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import GoogleAuthRequest, TokenResponse, RefreshRequest, UserResponse, LocalLoginRequest, PatientKeyTypeUpdate, LanguageUpdate, ProfileUpdate
from app.services.auth_service import verify_google_token, get_or_create_user, generate_tokens, refresh_access_token, authenticate_local, logout_user
from app.middleware.auth import get_current_user, security
from app.middleware.rate_limit import limiter
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google", response_model=TokenResponse)
@limiter.limit("20/minute")
async def google_auth(request: Request, body: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    google_info = await verify_google_token(body.token, body.token_type)
    user = await get_or_create_user(db, google_info)
    return generate_tokens(user)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def local_login(request: Request, body: LocalLoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_local(db, body.username, body.password)
    return generate_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
async def refresh_token(request: Request, body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await refresh_access_token(db, body.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
):
    await logout_user(credentials.credentials)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me/language", response_model=UserResponse)
async def update_language(
    data: LanguageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.preferred_language = data.language
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.put("/me/patient-key-type", response_model=UserResponse)
async def update_patient_key_type(
    data: PatientKeyTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.patient_key_type = data.patient_key_type
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.put("/me/profile", response_model=UserResponse)
async def update_profile(
    data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.nickname is not None:
        current_user.nickname = data.nickname.strip() if data.nickname.strip() else None
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url.strip() if data.avatar_url.strip() else None
    await db.commit()
    await db.refresh(current_user)
    return current_user
