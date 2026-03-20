"""
Permission tests for visit endpoints.
These tests verify that access control works correctly for update and complete operations.
"""
import os
import uuid
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.database import get_db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.visit import Visit, VisitStatus
from app.utils.jwt import create_access_token
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Use PostgreSQL from environment — SQLite doesn't support JSONB columns
_DB_URL = os.environ.get("DATABASE_URL", "")
if not _DB_URL:
    pytest.skip("DATABASE_URL not set — skipping PostgreSQL-dependent tests", allow_module_level=True)


@pytest.fixture
async def db_session():
    """Create a per-test engine+session to avoid asyncio event loop conflicts.
    Tables are assumed to exist (run alembic upgrade head before pytest).
    All changes are rolled back after each test.
    """
    engine = create_async_engine(_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()
    await engine.dispose()


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
async def test_update_visit_forbidden_different_doctor(client: AsyncClient, db_session: AsyncSession):
    """Test that a different doctor cannot edit another doctor's visit."""
    # Create first doctor
    doctor1 = User(
        id=uuid.uuid4(),
        email="d1-updforbid@test.com",
        name="Doctor One",
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(doctor1)
    
    # Create second doctor
    doctor2 = User(
        id=uuid.uuid4(),
        email="d2-updforbid@test.com",
        name="Doctor Two",
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(doctor2)
    
    # Create patient
    patient = Patient(
        id=uuid.uuid4(),
        name="Test Patient",
        dob=datetime(1990, 1, 1).date(),
    )
    db_session.add(patient)
    
    # Create visit owned by doctor1
    visit = Visit(
        id=uuid.uuid4(),
        patient_id=patient.id,
        doctor_id=doctor1.id,
        start_time=datetime.now(timezone.utc),
        status=VisitStatus.in_progress,
    )
    db_session.add(visit)
    await db_session.commit()
    await db_session.refresh(visit)
    
    # Try to update with doctor2's token
    doctor2_token = create_access_token(doctor2.id, doctor2.role.value)
    update_data = {"status": "completed"}
    
    response = await client.put(
        f"/api/visits/{visit.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {doctor2_token}"},
    )
    
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()
    
    # Verify visit was not updated
    result = await db_session.execute(select(Visit).where(Visit.id == visit.id))
    unchanged_visit = result.scalar_one()
    assert unchanged_visit.status == VisitStatus.in_progress


@pytest.mark.asyncio
async def test_update_visit_allowed_for_owner(client: AsyncClient, db_session: AsyncSession):
    """Test that the doctor who created a visit can edit it."""
    # Create doctor
    doctor = User(
        id=uuid.uuid4(),
        email="doc-updowner@test.com",
        name="Doctor",
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(doctor)
    
    # Create patient
    patient = Patient(
        id=uuid.uuid4(),
        name="Test Patient",
        dob=datetime(1990, 1, 1).date(),
    )
    db_session.add(patient)
    
    # Create visit owned by doctor
    visit = Visit(
        id=uuid.uuid4(),
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_time=datetime.now(timezone.utc),
        status=VisitStatus.in_progress,
    )
    db_session.add(visit)
    await db_session.commit()
    await db_session.refresh(visit)
    
    # Update with doctor's token
    doctor_token = create_access_token(doctor.id, doctor.role.value)
    update_data = {"status": "completed"}
    
    response = await client.put(
        f"/api/visits/{visit.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_update_visit_allowed_for_admin(client: AsyncClient, db_session: AsyncSession):
    """Test that an admin can edit any visit."""
    # Create doctor
    doctor = User(
        id=uuid.uuid4(),
        email="doc-updadmin@test.com",
        name="Doctor",
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(doctor)
    
    # Create admin
    admin = User(
        id=uuid.uuid4(),
        email="admin-updadmin@test.com",
        name="Admin",
        role=UserRole.admin,
        is_active=True,
    )
    db_session.add(admin)
    
    # Create patient
    patient = Patient(
        id=uuid.uuid4(),
        name="Test Patient",
        dob=datetime(1990, 1, 1).date(),
    )
    db_session.add(patient)
    
    # Create visit owned by doctor
    visit = Visit(
        id=uuid.uuid4(),
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_time=datetime.now(timezone.utc),
        status=VisitStatus.in_progress,
    )
    db_session.add(visit)
    await db_session.commit()
    await db_session.refresh(visit)
    
    # Update with admin's token
    admin_token = create_access_token(admin.id, admin.role.value)
    update_data = {"status": "completed"}
    
    response = await client.put(
        f"/api/visits/{visit.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_complete_visit_forbidden_different_doctor(client: AsyncClient, db_session: AsyncSession):
    """Test that a different doctor cannot complete another doctor's visit."""
    # Create first doctor
    doctor1 = User(
        id=uuid.uuid4(),
        email="d1-cmpforbid@test.com",
        name="Doctor One",
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(doctor1)
    
    # Create second doctor
    doctor2 = User(
        id=uuid.uuid4(),
        email="d2-cmpforbid@test.com",
        name="Doctor Two",
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(doctor2)
    
    # Create patient
    patient = Patient(
        id=uuid.uuid4(),
        name="Test Patient",
        dob=datetime(1990, 1, 1).date(),
    )
    db_session.add(patient)
    
    # Create visit owned by doctor1
    visit = Visit(
        id=uuid.uuid4(),
        patient_id=patient.id,
        doctor_id=doctor1.id,
        start_time=datetime.now(timezone.utc),
        status=VisitStatus.in_progress,
    )
    db_session.add(visit)
    await db_session.commit()
    await db_session.refresh(visit)
    
    # Try to complete with doctor2's token
    doctor2_token = create_access_token(doctor2.id, doctor2.role.value)
    
    response = await client.put(
        f"/api/visits/{visit.id}/complete",
        headers={"Authorization": f"Bearer {doctor2_token}"},
    )
    
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()
    
    # Verify visit was not completed
    result = await db_session.execute(select(Visit).where(Visit.id == visit.id))
    unchanged_visit = result.scalar_one()
    assert unchanged_visit.status == VisitStatus.in_progress


@pytest.mark.asyncio
async def test_complete_visit_allowed_for_owner(client: AsyncClient, db_session: AsyncSession):
    """Test that the doctor who created a visit can complete it."""
    # Create doctor
    doctor = User(
        id=uuid.uuid4(),
        email="doc-cmpowner@test.com",
        name="Doctor",
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(doctor)
    
    # Create patient
    patient = Patient(
        id=uuid.uuid4(),
        name="Test Patient",
        dob=datetime(1990, 1, 1).date(),
    )
    db_session.add(patient)
    
    # Create visit owned by doctor
    visit = Visit(
        id=uuid.uuid4(),
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_time=datetime.now(timezone.utc),
        status=VisitStatus.in_progress,
    )
    db_session.add(visit)
    await db_session.commit()
    await db_session.refresh(visit)
    
    # Complete with doctor's token
    doctor_token = create_access_token(doctor.id, doctor.role.value)
    
    response = await client.put(
        f"/api/visits/{visit.id}/complete",
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["end_time"] is not None


@pytest.mark.asyncio
async def test_complete_visit_allowed_for_admin(client: AsyncClient, db_session: AsyncSession):
    """Test that an admin can complete any visit."""
    # Create doctor
    doctor = User(
        id=uuid.uuid4(),
        email="doc-cmpadmin@test.com",
        name="Doctor",
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(doctor)
    
    # Create admin
    admin = User(
        id=uuid.uuid4(),
        email="admin-cmpadmin@test.com",
        name="Admin",
        role=UserRole.admin,
        is_active=True,
    )
    db_session.add(admin)
    
    # Create patient
    patient = Patient(
        id=uuid.uuid4(),
        name="Test Patient",
        dob=datetime(1990, 1, 1).date(),
    )
    db_session.add(patient)
    
    # Create visit owned by doctor
    visit = Visit(
        id=uuid.uuid4(),
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_time=datetime.now(timezone.utc),
        status=VisitStatus.in_progress,
    )
    db_session.add(visit)
    await db_session.commit()
    await db_session.refresh(visit)
    
    # Complete with admin's token
    admin_token = create_access_token(admin.id, admin.role.value)
    
    response = await client.put(
        f"/api/visits/{visit.id}/complete",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
