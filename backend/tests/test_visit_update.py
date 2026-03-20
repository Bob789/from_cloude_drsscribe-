import os
import uuid
import pytest
from datetime import datetime, timezone, date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.visit import Visit, VisitStatus
from app.models.summary import Summary, SummaryStatus


# Use PostgreSQL from environment — SQLite doesn't support JSONB columns
_DB_URL = os.environ.get("DATABASE_URL", "")
if not _DB_URL:
    pytest.skip("DATABASE_URL not set — skipping PostgreSQL-dependent tests", allow_module_level=True)

test_engine = create_async_engine(_DB_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture
async def db_session():
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestAsyncSessionLocal() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        name="Test User",
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def other_doctor(db_session: AsyncSession):
    """Create another doctor user."""
    user = User(
        id=uuid.uuid4(),
        email="other@example.com",
        name="Other Doctor",
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    """Create an admin user."""
    user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        name="Admin User",
        role=UserRole.admin,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_patient(db_session: AsyncSession):
    """Create a test patient."""
    patient = Patient(
        id=uuid.uuid4(),
        name="Test Patient",
        dob=date(1990, 1, 1),
    )
    db_session.add(patient)
    await db_session.commit()
    await db_session.refresh(patient)
    return patient


@pytest.fixture
async def test_visit(db_session: AsyncSession, test_user: User, test_patient: Patient):
    """Create a test visit."""
    visit = Visit(
        id=uuid.uuid4(),
        patient_id=test_patient.id,
        doctor_id=test_user.id,
        start_time=datetime.now(timezone.utc),
        status=VisitStatus.in_progress,
    )
    db_session.add(visit)
    await db_session.commit()
    await db_session.refresh(visit)
    return visit


@pytest.fixture
async def test_summary(db_session: AsyncSession, test_visit: Visit):
    """Create a test summary."""
    summary = Summary(
        id=uuid.uuid4(),
        visit_id=test_visit.id,
        chief_complaint="Test complaint",
        findings="Test findings",
        diagnosis=["Test diagnosis"],
        treatment_plan="Test treatment",
        recommendations="Test recommendations",
        urgency="low",
        status=SummaryStatus.completed,
    )
    db_session.add(summary)
    await db_session.commit()
    await db_session.refresh(summary)
    return summary


@pytest.fixture
def auth_token(test_user: User):
    """Create an authentication token."""
    from app.utils.jwt import create_access_token
    return create_access_token(test_user.id, test_user.role.value)


@pytest.fixture
async def client(db_session: AsyncSession):
    """Create a test client with dependency overrides."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_visit_success(
    client: AsyncClient,
    db_session: AsyncSession,
    test_visit: Visit,
    auth_token: str,
):
    """Test successful visit update."""
    update_data = {
        "status": "completed",
        "end_time": datetime.now(timezone.utc).isoformat(),
    }
    
    response = await client.put(
        f"/api/visits/{test_visit.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_visit.id)
    assert data["status"] == "completed"
    assert data["end_time"] is not None
    
    # Verify database was updated
    result = await db_session.execute(select(Visit).where(Visit.id == test_visit.id))
    updated_visit = result.scalar_one()
    assert updated_visit.status == VisitStatus.completed
    assert updated_visit.end_time is not None


@pytest.mark.asyncio
async def test_update_visit_not_found(
    client: AsyncClient,
    auth_token: str,
):
    """Test update of non-existent visit returns 404."""
    fake_id = uuid.uuid4()
    update_data = {"status": "completed"}
    
    response = await client.put(
        f"/api/visits/{fake_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_visit_partial(
    client: AsyncClient,
    db_session: AsyncSession,
    test_visit: Visit,
    auth_token: str,
):
    """Test partial update (only some fields)."""
    original_start_time = test_visit.start_time
    update_data = {
        "status": "completed",
    }
    
    response = await client.put(
        f"/api/visits/{test_visit.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    
    # Verify start_time was not changed
    result = await db_session.execute(select(Visit).where(Visit.id == test_visit.id))
    updated_visit = result.scalar_one()
    assert updated_visit.status == VisitStatus.completed
    assert updated_visit.start_time == original_start_time


@pytest.mark.asyncio
async def test_update_visit_with_summary(
    client: AsyncClient,
    db_session: AsyncSession,
    test_visit: Visit,
    test_summary: Summary,
    auth_token: str,
):
    """Test updating visit with summary fields."""
    update_data = {
        "status": "completed",
        "chief_complaint": "Updated complaint",
        "findings": "Updated findings",
        "diagnosis": ["Updated diagnosis"],
    }
    
    response = await client.put(
        f"/api/visits/{test_visit.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    
    # Verify summary was updated
    result = await db_session.execute(select(Summary).where(Summary.visit_id == test_visit.id))
    updated_summary = result.scalar_one()
    assert updated_summary.chief_complaint == "Updated complaint"
    assert updated_summary.findings == "Updated findings"
    assert updated_summary.diagnosis == ["Updated diagnosis"]


@pytest.mark.asyncio
async def test_update_visit_unauthorized(
    client: AsyncClient,
    test_visit: Visit,
):
    """Test update without authentication fails."""
    update_data = {"status": "completed"}
    
    response = await client.put(
        f"/api/visits/{test_visit.id}",
        json=update_data,
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_visit_forbidden_different_doctor(
    client: AsyncClient,
    db_session: AsyncSession,
    test_visit: Visit,
    other_doctor: User,
):
    """Test that a different doctor cannot edit another doctor's visit."""
    from app.utils.jwt import create_access_token
    other_token = create_access_token(other_doctor.id, other_doctor.role.value)
    
    update_data = {"status": "completed"}
    
    response = await client.put(
        f"/api/visits/{test_visit.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {other_token}"},
    )
    
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()
    
    # Verify visit was not updated
    result = await db_session.execute(select(Visit).where(Visit.id == test_visit.id))
    unchanged_visit = result.scalar_one()
    assert unchanged_visit.status == VisitStatus.in_progress


@pytest.mark.asyncio
async def test_update_visit_allowed_for_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    test_visit: Visit,
    admin_user: User,
):
    """Test that an admin can edit any visit."""
    from app.utils.jwt import create_access_token
    admin_token = create_access_token(admin_user.id, admin_user.role.value)
    
    update_data = {
        "status": "completed",
        "end_time": datetime.now(timezone.utc).isoformat(),
    }
    
    response = await client.put(
        f"/api/visits/{test_visit.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    
    # Verify visit was updated
    result = await db_session.execute(select(Visit).where(Visit.id == test_visit.id))
    updated_visit = result.scalar_one()
    assert updated_visit.status == VisitStatus.completed


@pytest.mark.asyncio
async def test_complete_visit_forbidden_different_doctor(
    client: AsyncClient,
    db_session: AsyncSession,
    test_visit: Visit,
    other_doctor: User,
):
    """Test that a different doctor cannot complete another doctor's visit."""
    from app.utils.jwt import create_access_token
    other_token = create_access_token(other_doctor.id, other_doctor.role.value)
    
    response = await client.put(
        f"/api/visits/{test_visit.id}/complete",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()
    
    # Verify visit was not completed
    result = await db_session.execute(select(Visit).where(Visit.id == test_visit.id))
    unchanged_visit = result.scalar_one()
    assert unchanged_visit.status == VisitStatus.in_progress


@pytest.mark.asyncio
async def test_complete_visit_allowed_for_owner(
    client: AsyncClient,
    db_session: AsyncSession,
    test_visit: Visit,
    auth_token: str,
):
    """Test that the doctor who created a visit can complete it."""
    response = await client.put(
        f"/api/visits/{test_visit.id}/complete",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["end_time"] is not None
    
    # Verify visit was completed
    result = await db_session.execute(select(Visit).where(Visit.id == test_visit.id))
    completed_visit = result.scalar_one()
    assert completed_visit.status == VisitStatus.completed
    assert completed_visit.end_time is not None


@pytest.mark.asyncio
async def test_complete_visit_allowed_for_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    test_visit: Visit,
    admin_user: User,
):
    """Test that an admin can complete any visit."""
    from app.utils.jwt import create_access_token
    admin_token = create_access_token(admin_user.id, admin_user.role.value)
    
    response = await client.put(
        f"/api/visits/{test_visit.id}/complete",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    
    # Verify visit was completed
    result = await db_session.execute(select(Visit).where(Visit.id == test_visit.id))
    completed_visit = result.scalar_one()
    assert completed_visit.status == VisitStatus.completed
