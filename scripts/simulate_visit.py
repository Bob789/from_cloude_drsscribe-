"""Simulation runner: creates a patient + manual visit via the backend API.

Usage:
    python simulate_visit.py              # uses default story
    python simulate_visit.py story.json   # uses custom story file

The script:
1. Generates a JWT token for a real user in the DB
2. Creates a new patient via POST /api/patients
3. Creates a manual visit with summary via POST /api/visits/manual
4. Fetches the visit back via GET /api/visits/patient/{patient_id}
5. Prints the summary as returned by the API (decrypted)
"""
import asyncio
import json
import sys
import os
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.config import settings
from app.utils.jwt import create_access_token
from app.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

BASE_URL = os.environ.get("API_URL", "http://localhost:8000/api")

# Default story if no file provided
DEFAULT_STORY = {
    "patient": {
        "name": "דוד כהן (סימולציה)",
        "id_number": "111222333",
        "phone": "0501234567",
        "dob": "1975-06-15",
    },
    "visit": {
        "chief_complaint": 'כאבים חזקים בחזה מהבוקר, מוחמרים בתנועה. ביצוע אק"ג דחוף.',
        "findings": "כאב לוחץ בבית החזה, מקרין ליד שמאל ולגב העליון. דופק 88, לחץ דם 145/90.",
        "diagnosis": [
            {"code": "R07.9", "description": "כאב בחזה, לא מפורט"},
            {"code": "I20.9", "description": "תעוקת חזה, לא מפורטת"},
        ],
        "treatment_plan": 'ביצוע אק"ג ובדיקות דם דחופות (טרופונין, CK-MB) לבירור קרדיאלי',
        "recommendations": "מעקב במיון, חזרה לרופא עם תוצאות. הפניה דחופה במקרה של החמרה.",
        "urgency": "high",
        "notes": "המטופל מעשן 20 סיגריות ביום, היסטוריה משפחתית של מחלות לב.",
        "tags": [
            {"tag_type": "symptom", "tag_label": "כאב בחזה", "tag_code": "R07.9"},
            {"tag_type": "procedure", "tag_label": 'אק"ג', "tag_code": ""},
            {"tag_type": "condition", "tag_label": "חשד לתעוקת חזה", "tag_code": "I20.9"},
        ],
    },
}


async def get_first_doctor_token() -> tuple[str, str]:
    """Get JWT token for the first doctor user in the DB."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.is_active.is_(True)).limit(1)
        )
        user = result.scalar_one_or_none()
        if not user:
            print("ERROR: No active user found in DB")
            sys.exit(1)
        token = create_access_token(user.id, user.role.value)
        print(f"Authenticated as: {user.name} ({user.email})")
        return token, str(user.id)


async def run_simulation(story: dict):
    token, user_id = await get_first_doctor_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=30) as client:
        # 1. Create patient
        print("\n--- Step 1: Creating patient ---")
        patient_data = story["patient"]
        resp = await client.post("/patients", json=patient_data)
        if resp.status_code not in (200, 201):
            print(f"ERROR creating patient: {resp.status_code} {resp.text}")
            sys.exit(1)
        patient = resp.json()
        patient_id = patient["id"]
        print(f"Patient created: {patient.get('name')} (ID: {patient.get('display_id')}, UUID: {patient_id})")

        # 2. Create manual visit with summary
        print("\n--- Step 2: Creating manual visit with summary ---")
        visit_data = {**story["visit"], "patient_id": patient_id}
        resp = await client.post("/visits/manual", json=visit_data)
        if resp.status_code not in (200, 201):
            print(f"ERROR creating visit: {resp.status_code} {resp.text}")
            sys.exit(1)
        visit_result = resp.json()
        print(f"Visit created: display_id={visit_result.get('visit_display_id')}, summary_id={visit_result.get('summary_id')}")

        # 3. Fetch visit back to verify
        print("\n--- Step 3: Fetching patient visits (verifying decryption) ---")
        resp = await client.get(f"/visits/patient/{patient_id}")
        if resp.status_code != 200:
            print(f"ERROR fetching visits: {resp.status_code} {resp.text}")
            sys.exit(1)
        visits = resp.json()

        if not visits:
            print("ERROR: No visits found!")
            sys.exit(1)

        visit = visits[0]
        summary = visit.get("summary")

        print("\n" + "=" * 60)
        print("SIMULATION RESULT")
        print("=" * 60)

        if not summary:
            print("ERROR: No summary attached to visit!")
            sys.exit(1)

        fields = [
            ("chief_complaint", "תסמין עיקרי"),
            ("findings", "ממצאים"),
            ("diagnosis", "אבחנות"),
            ("treatment_plan", "תוכנית טיפול"),
            ("recommendations", "המלצות"),
            ("urgency", "דחיפות"),
            ("notes", "הערות"),
            ("source", "מקור"),
        ]

        all_ok = True
        for key, label in fields:
            value = summary.get(key)
            if key == "diagnosis":
                if isinstance(value, list) and value:
                    diag_str = ", ".join(
                        f"{d.get('code', '')} - {d.get('description', d.get('label', ''))}"
                        for d in value
                    )
                    print(f"  {label}: {diag_str}")
                else:
                    print(f"  {label}: (empty)")
            else:
                display = value if value else "(empty)"
                print(f"  {label}: {display}")

            # Verify no encrypted garbage
            if isinstance(value, str) and len(value) > 50 and " " not in value[:40]:
                print(f"  *** WARNING: {label} looks encrypted! ***")
                all_ok = False

        # Check tags
        tags = summary.get("tags", [])
        if tags:
            print(f"\n  Tags ({len(tags)}):")
            for t in tags:
                print(f"    [{t.get('tag_type')}] {t.get('tag_label')} ({t.get('tag_code', '')})")

        print("\n" + "=" * 60)
        if all_ok:
            print("SUCCESS: All fields are readable (not encrypted)")
        else:
            print("FAILURE: Some fields appear encrypted!")
        print("=" * 60)

        return all_ok


def main():
    story = DEFAULT_STORY
    if len(sys.argv) > 1:
        story_file = sys.argv[1]
        with open(story_file, "r", encoding="utf-8") as f:
            story = json.load(f)
        print(f"Loaded story from: {story_file}")
    else:
        print("Using default story")

    result = asyncio.run(run_simulation(story))
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
