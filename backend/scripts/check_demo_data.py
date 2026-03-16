import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.visit import Visit
from app.models.summary import Summary

USER_EMAIL = "yossil1306@gmail.com"

async def main():
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.email == USER_EMAIL)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"User {USER_EMAIL} not found")
            return

        stmt = select(Visit).where(Visit.doctor_id == user.id).options(selectinload(Visit.patient)).order_by(Visit.created_at.desc()).limit(1)
        result = await db.execute(stmt)
        visit = result.scalar_one_or_none()

        if visit:
            stmt = select(Summary).where(Summary.visit_id == visit.id)
            result = await db.execute(stmt)
            summary = result.scalar_one_or_none()
            
            print(f"--- Latest Case for {USER_EMAIL} ---")
            print(f"Patient: {visit.patient.name}")
            print(f"Date: {visit.start_time}")
            if summary:
                print(f"Complaint: {summary.chief_complaint}")
                print(f"Diagnosis: {summary.diagnosis}")
        else:
            print("No visits found.")

if __name__ == "__main__":
    asyncio.run(main())
