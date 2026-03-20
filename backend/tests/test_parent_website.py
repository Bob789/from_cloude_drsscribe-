"""
Regression tests for bugs found during parent-website (localhost:3001) integration.

INC-006: CORS_ORIGINS in .env didn't include http://localhost:3001
INC-007: Next.js NEXT_PUBLIC_API_URL baked at build time, not runtime
INC-008: Admin user gets 403 because Google OAuth creates users with role='doctor'
"""
import os
import pytest
from unittest.mock import MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.user import User, UserRole


# ── INC-006: CORS regression ──────────────────────────────────────────────────

def test_cors_localhost_3001_in_config():
    """INC-006: Verify that localhost:3001 is in allowed CORS origins (config default)."""
    from app.config import settings
    origins = settings.cors_origins_list
    assert "http://localhost:3001" in origins, (
        "http://localhost:3001 must be in CORS_ORIGINS. "
        "If .env overrides the default, make sure to include 3001 there too."
    )


@pytest.mark.asyncio
async def test_cors_localhost_3001_allowed():
    """INC-006: Backend must respond with ACAO header for http://localhost:3001 origin."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Origin": "http://localhost:3001"},
    ) as client:
        response = await client.get("/api/articles")
    
    acao = response.headers.get("access-control-allow-origin", "")
    assert acao == "http://localhost:3001", (
        f"Expected CORS header 'http://localhost:3001', got '{acao}'. "
        "Add http://localhost:3001 to CORS_ORIGINS in .env and restart backend."
    )


@pytest.mark.asyncio
async def test_cors_preflight_localhost_3001():
    """INC-006: OPTIONS preflight for localhost:3001 must return 200 with correct headers."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={
            "Origin": "http://localhost:3001",
            "Access-Control-Request-Method": "GET",
        },
    ) as client:
        response = await client.options("/api/articles")
    
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


# ── INC-007: Next.js build-time env var regression ───────────────────────────

def test_nextjs_dockerfile_has_api_url_arg():
    """INC-007: parent-website/Dockerfile must declare ARG NEXT_PUBLIC_API_URL before npm run build."""
    dockerfile_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "parent-website", "Dockerfile"
    )
    dockerfile_path = os.path.normpath(dockerfile_path)
    
    if not os.path.exists(dockerfile_path):
        pytest.skip(
            "parent-website/Dockerfile not accessible from inside the backend container. "
            "Verify manually that ARG NEXT_PUBLIC_API_URL is present before 'npm run build'."
        )
    
    content = open(dockerfile_path).read()
    
    assert "ARG NEXT_PUBLIC_API_URL" in content, (
        "Dockerfile must have 'ARG NEXT_PUBLIC_API_URL' before npm run build. "
        "Without this, NEXT_PUBLIC_* vars are not available at build time."
    )
    assert "ENV NEXT_PUBLIC_API_URL" in content, (
        "Dockerfile must set 'ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL' "
        "so it is baked into the Next.js bundle during build."
    )
    
    # Ensure ARG appears before the build command
    arg_pos = content.index("ARG NEXT_PUBLIC_API_URL")
    build_pos = content.index("npm run build")
    assert arg_pos < build_pos, (
        "ARG NEXT_PUBLIC_API_URL must appear BEFORE 'npm run build' in Dockerfile."
    )


def test_docker_compose_passes_api_url_build_arg():
    """INC-007: docker-compose.yml must pass NEXT_PUBLIC_API_URL as build arg to parent-website."""
    compose_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "docker-compose.yml"
    )
    compose_path = os.path.normpath(compose_path)
    
    if not os.path.exists(compose_path):
        pytest.skip(
            "docker-compose.yml not accessible from inside the backend container. "
            "Verify manually that NEXT_PUBLIC_API_URL is passed as build arg for parent-website."
        )
    
    content = open(compose_path).read()
    
    assert "NEXT_PUBLIC_API_URL" in content, (
        "docker-compose.yml must pass NEXT_PUBLIC_API_URL as a build arg "
        "under parent-website.build.args so the URL is baked at build time."
    )


# ── INC-008: Admin role 403 regression ───────────────────────────────────────

@pytest.mark.asyncio
async def test_doctor_role_cannot_access_admin_endpoints():
    """INC-008: A user with role='doctor' must get 403 on /admin/* endpoints."""
    import uuid
    from app.middleware.auth import get_current_user

    doctor_user = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        email="doctor@test.com",
        name="Test Doctor",
        role=UserRole.doctor,
        is_active=True,
    )

    async def _mock_doctor():
        return doctor_user

    app.dependency_overrides[get_current_user] = _mock_doctor
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/admin/articles/generate",
                json={"topic": "test", "config": {}},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403, (
        f"Expected 403 for doctor role on /admin/articles/generate, got {response.status_code}. "
        "require_admin dependency must reject non-admin users."
    )


@pytest.mark.asyncio
async def test_admin_role_can_access_admin_endpoint_structure():
    """INC-008: A user with role='admin' must NOT get 403 (may get other errors if DB not available)."""
    import uuid
    from unittest.mock import AsyncMock, MagicMock
    from app.middleware.auth import get_current_user
    from app.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    admin_user = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        email="admin@test.com",
        name="Test Admin",
        role=UserRole.admin,
        is_active=True,
    )

    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    async def _mock_admin():
        return admin_user

    async def _mock_get_db():
        yield mock_session

    app.dependency_overrides[get_current_user] = _mock_admin
    app.dependency_overrides[get_db] = _mock_get_db
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/admin/articles")
    finally:
        app.dependency_overrides.clear()

    # Must NOT be 403 (auth passed). May be 500 if DB mock incomplete.
    assert response.status_code != 403, (
        f"Admin user should not get 403. Got {response.status_code}. "
        "require_admin must allow UserRole.admin through."
    )


def test_google_oauth_default_role_is_documented():
    """INC-008: User model default role must be 'doctor', ensuring OAuth users can never get admin via login."""
    from app.models import user as user_module
    import inspect
    source = inspect.getsource(user_module)
    
    # The User model must default to UserRole.doctor (not admin)
    assert "default=UserRole.doctor" in source, (
        "User model must have role default=UserRole.doctor. "
        "This prevents Google OAuth from ever creating admin users automatically. "
        "Admin role must be granted manually via: UPDATE users SET role='admin' WHERE email='...';"
    )
