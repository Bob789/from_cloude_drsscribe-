"""Create demo user and copy data from existing doctor account."""
import asyncio
import uuid
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, text
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.summary import Summary
from app.models.tag import Tag
from app.services.auth_service import hash_password

DEMO_USERNAME = "bet_hoven"
DEMO_PASSWORD = "bet.123"
DEMO_NAME = "Dr. Demo"
DEMO_EMAIL = "demo@medscribe-ai.com"


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == DEMO_USERNAME))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Demo user already exists: {existing.id}")
            return

        result = await db.execute(
            select(User).where(User.role == UserRole.doctor, User.username.is_(None)).limit(1)
        )
        source_user = result.scalar_one_or_none()

        demo_user = User(
            id=uuid.uuid4(),
            email=DEMO_EMAIL,
            name=DEMO_NAME,
            username=DEMO_USERNAME,
            password_hash=hash_password(DEMO_PASSWORD),
            auth_method="local",
            role=UserRole.doctor,
            is_active=True,
        )
        db.add(demo_user)
        await db.flush()
        print(f"Created demo user: {demo_user.id}")

        if not source_user:
            print("No source user found to copy data from. Demo user created without data.")
            await db.commit()
            return

        print(f"Copying data from: {source_user.name} ({source_user.id})")

        result = await db.execute(select(Patient).where(Patient.created_by == source_user.id))
        source_patients = result.scalars().all()
        patient_id_map = {}

        for sp in source_patients:
            new_id = uuid.uuid4()
            patient_id_map[sp.id] = new_id
            new_patient = Patient(
                id=new_id,
                created_by=demo_user.id,
                name=sp.name,
                id_number=sp.id_number,
                dob=sp.dob,
                phone=sp.phone,
                email=sp.email,
                blood_type=sp.blood_type,
                allergies=sp.allergies,
                profession=sp.profession,
                address=sp.address,
                insurance_info=sp.insurance_info,
                notes=sp.notes,
            )
            db.add(new_patient)

        await db.flush()
        print(f"Copied {len(patient_id_map)} patients")

        result = await db.execute(select(Visit).where(Visit.doctor_id == source_user.id))
        source_visits = result.scalars().all()
        visit_id_map = {}

        for sv in source_visits:
            new_id = uuid.uuid4()
            visit_id_map[sv.id] = new_id
            new_patient_id = patient_id_map.get(sv.patient_id, sv.patient_id)
            new_visit = Visit(
                id=new_id,
                patient_id=new_patient_id,
                doctor_id=demo_user.id,
                start_time=sv.start_time,
                end_time=sv.end_time,
                status=sv.status,
                source=sv.source,
            )
            db.add(new_visit)

        await db.flush()
        print(f"Copied {len(visit_id_map)} visits")

        summary_id_map = {}
        for old_visit_id, new_visit_id in visit_id_map.items():
            result = await db.execute(select(Summary).where(Summary.visit_id == old_visit_id))
            for ss in result.scalars().all():
                new_sum_id = uuid.uuid4()
                summary_id_map[ss.id] = new_sum_id
                new_summary = Summary(
                    id=new_sum_id,
                    visit_id=new_visit_id,
                    chief_complaint=ss.chief_complaint,
                    findings=ss.findings,
                    diagnosis=ss.diagnosis,
                    treatment_plan=ss.treatment_plan,
                    recommendations=ss.recommendations,
                    urgency=ss.urgency,
                    source=ss.source,
                    notes=ss.notes,
                    questionnaire_data=ss.questionnaire_data,
                    custom_fields=ss.custom_fields,
                    status=ss.status,
                )
                db.add(new_summary)

        await db.flush()
        print(f"Copied {len(summary_id_map)} summaries")

        tag_count = 0
        for old_sum_id, new_sum_id in summary_id_map.items():
            result = await db.execute(
                select(Tag).where(Tag.entity_type == "summary", Tag.entity_id == str(old_sum_id))
            )
            for st in result.scalars().all():
                new_tag = Tag(
                    entity_type="summary",
                    entity_id=str(new_sum_id),
                    tag_type=st.tag_type,
                    tag_code=st.tag_code,
                    tag_label=st.tag_label,
                )
                db.add(new_tag)
                tag_count += 1

        await db.commit()
        print(f"Copied {tag_count} tags")
        print(f"\nDemo account ready:")
        print(f"  Username: {DEMO_USERNAME}")
        print(f"  Password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
