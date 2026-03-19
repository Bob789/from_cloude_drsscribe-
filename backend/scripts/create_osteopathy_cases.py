import asyncio
import sys
import os
import uuid
import random
from datetime import datetime, timedelta, date

# Add backend directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.visit import Visit, VisitStatus
from app.models.summary import Summary, SummaryStatus
from app.services.auth_service import hash_password

USER_EMAIL = "yossil1306@gmail.com"
USER_NAME = "Yossi Levi"
USER_PASS = "123456"

OSTEOPATHY_CASES = [
    {
        "patient_name": "דני כהן",
        "dob": date(1985, 4, 12),
        "complaint": "כאב גב תחתון חריף המקרין לרגל ימין",
        "findings": "רגישות במישוש L4-L5, הגבלה בכיפוף לפנים, מבחן הרמת רגל ישרה חיובי ב-45 מעלות מימין. מתח שרירים גבוה בזוקפי הגב.",
        "diagnosis": ["Lumbago with Sciatica", "Muscle Spasm"],
        "treatment": "שחרור רקמות רכות (Soft Tissue) באזור הגב התחתון והישבן. מניפולציה עדינה (Articulation) לאגן ולחוליות המותניות. טכניקת אנרגיית שריר (Muscle Energy) לשריר הפיריפורמיס.",
        "recommendations": "מנוחה יחסית, הימנעות מהרמת משאות כבדים. תרגילי מתיחה עדינים לשרירי הירך האחוריים. קומפרסים חמים.",
        "urgency": "medium"
    },
    {
        "patient_name": "שרה לוי",
        "dob": date(1992, 8, 25),
        "complaint": "כאבי צוואר וראש, תחושת 'תפיסות' בכתפיים",
        "findings": "הגבלה בסיבוב צוואר לשמאל. רגישות בשרירי הטרפז העליון וה-Levator Scapulae. נקודות הדק (Trigger Points) פעילות.",
        "diagnosis": ["Cervicalgia", "Tension Headache", "Somatic Dysfunction of Cervical Spine"],
        "treatment": "עיסוי עמוק לשרירי הצוואר והשכמות. טכניקת שחרור תת-עורפי (Suboccipital Release). מתיחות צוואריות עדינות. התייחסות לצלעות ראשונות.",
        "recommendations": "שיפור ארגונומיה בעבודה מול מחשב. הפסקות יזומות למתיחות כל שעה. כרית אורתופדית לשינה.",
        "urgency": "low"
    },
    {
        "patient_name": "יוסי מזרחי",
        "dob": date(1978, 11, 3),
        "complaint": "כאב בכתף ימין, קושי להרים את היד מעל הראש",
        "findings": "טווח תנועה מוגבל באבדוקציה (90 מעלות). מבחן 'קשת כואבת' חיובי. רגישות בגיד ה-Supraspinatus.",
        "diagnosis": ["Rotator Cuff Tendinopathy", "Shoulder Impingement Syndrome"],
        "treatment": "טכניקת ספנסר (Spencer Technique) להגדלת טווח תנועה בכתף. שחרור מיופציאלי לשרירי החזה (Pectoralis) והשכמה. ניוד מפרק הכתף.",
        "recommendations": "חיזוק שרירי מייצבי כתף (Rotator Cuff) עם גומייה. להימנע משינה על צד ימין. קרח מקומי לאחר מאמץ.",
        "urgency": "medium"
    },
    {
        "patient_name": "רבקה אברהם",
        "dob": date(1965, 2, 18),
        "complaint": "כאבים בברך שמאל במיוחד בעלייה במדרגות",
        "findings": "נפיחות קלה בברך. רגישות בקו המפרק הפנימי. מבחן מגירה שלילי. חוסר איזון באגן שמאל.",
        "diagnosis": ["Patellofemoral Pain Syndrome", "Osteoarthritis of Knee"],
        "treatment": "איזון אגן ועצם העצה (Sacrum). שחרור שרירי הארבע-ראשי והמקרבים. מוביליזציה של הפיקה (Patella).",
        "recommendations": "הליכה עם נעליים תומכות. חיזוק שריר VMO. ירידה במשקל להפחתת עומס. תוסף כורכומין.",
        "urgency": "low"
    },
    {
        "patient_name": "איתי גולן",
        "dob": date(1999, 6, 30),
        "complaint": "כאבים בלסת, 'קליקים' בפתיחת הפה, חריקת שיניים בלילה",
        "findings": "פתיחת פה מוגבלת (30 מ\"מ). סטייה בפתיחת הפה לשמאל. רגישות בשרירי המלעס (Masseter) והרקה (Temporalis).",
        "diagnosis": ["Temporomandibular Joint Disorder (TMJ)", "Bruxism"],
        "treatment": "טכניקות תוך-פיות לשחרור שרירי הלעיסה (Pterygoids). שחרור סרעפת וצוואר קדמי. טכניקות קרניאליות (Cranial Osteopathy) לעצם הטמפורלית.",
        "recommendations": "סד לילה (Night Guard). להימנע מלעיסת מסטיק ומאכלים קשים. תרגילי הרפיה ללסת. הפחתת סטרס.",
        "urgency": "medium"
    },
    {
        "patient_name": "מיכל שפירא",
        "dob": date(1988, 1, 15),
        "complaint": "כאבי אגן לאחר לידה (לפני 4 חודשים)",
        "findings": "רגישות במפרקי ה-SIJ. חוסר סימטריה בגובה האגן בעמידה. חולשה של שרירי הבטן הרוחביים.",
        "diagnosis": ["Postpartum Pelvic Pain", "Sacroiliac Joint Dysfunction"],
        "treatment": "איזון אגן בטכניקות עדינות (Balanced Ligamentous Tension). עבודה על רצפת האגן והסרעפת. חיזוק שרירי ליבה.",
        "recommendations": "תרגילי קגל ופילאטיס שיקומי. להימנע מנשיאת התינוק על צד אחד בלבד. חגורת אגן במידת הצורך.",
        "urgency": "medium"
    },
    {
        "patient_name": "דוד ביטון",
        "dob": date(1972, 9, 9),
        "complaint": "צרבות חוזרות, תחושת מלאות ונפיחות בבטן",
        "findings": "מתח באזור רום הבטן (Epigastrium). הגבלה בתנועתיות הסרעפת. רגישות באזור חוליות T5-T9.",
        "diagnosis": ["GERD (Gastroesophageal Reflux Disease)", "Functional Dyspepsia"],
        "treatment": "אוסטיאופתיה ויסרלית (Visceral Manipulation) לקיבה ולשער הקיבה (Hiatal Hernia release). שחרור סרעפת. מניפולציה לחוליות הגב האמצעי.",
        "recommendations": "לא לשכב מיד אחרי האוכל. ארוחות קטנות ותכופות. להימנע מקפאין, אלכוהול ומזון חריף. להגביה את ראש המיטה.",
        "urgency": "low"
    },
    {
        "patient_name": "נועה ברק",
        "dob": date(2005, 5, 21),
        "complaint": "כאבי ראש תעוקתיים, לחץ ברקות ובמצח",
        "findings": "מתח שרירי גבוה בצוואר האחורי. נשימה שטוחה (בית חזה עליון). הגבלה בתנועת עצמות הגולגולת (SBS compression).",
        "diagnosis": ["Tension Type Headache", "Somatic Dysfunction of Head Region"],
        "treatment": "טיפול קרניו-סאקרלי (Craniosacral Therapy) לאיזון מקצב הנוזל השדרתי. שחרור בסיס הגולגולת (C0-C1). עבודה על מערכת העצבים האוטונומית.",
        "recommendations": "שתיית מים מרובה. הפחתת זמן מסך. תרגילי נשימה סרעפתית להרגעה. יוגה.",
        "urgency": "low"
    },
    {
        "patient_name": "גיא רוזן",
        "dob": date(1980, 12, 12),
        "complaint": "כאב בכף רגל ימין בצעדים ראשונים בבוקר",
        "findings": "רגישות חזקה בבסיס העקב ובקשת כף הרגל. הגבלה בדורסי-פלקסיה בקרסול. שרירי תאומים מקוצרים.",
        "diagnosis": ["Plantar Fasciitis", "Calcaneal Spur"],
        "treatment": "שחרור מיופציאלי של הפלנטר פציה (Plantar Fascia) ושרירי השוק האחוריים. מניפולציה למפרקי כף הרגל והקרסול. טכניקת Counterstrain.",
        "recommendations": "מדרסים או תמיכת קשת. גלגול בקבוק קרח עם כף הרגל. מתיחות לשרירי השוק מספר פעמים ביום.",
        "urgency": "medium"
    },
    {
        "patient_name": "אורית קורן",
        "dob": date(1995, 3, 28),
        "complaint": "כאבים בשורש כף היד ונימול באצבעות (תסמונת התעלה הקרפלית)",
        "findings": "מבחן טינל ופאלן חיוביים. מתח בשרירי האמה (Forearm flexors). הגבלה בתנועת עצמות שורש כף היד.",
        "diagnosis": ["Carpal Tunnel Syndrome"],
        "treatment": "פתיחת התעלה הקרפלית בטכניקות מתיחה. שחרור שרירי האמה. מוביליזציה של עצמות הקרפוס (Carpal bones) והמרפק.",
        "recommendations": "סד מנוחה ללילה. הפסקות בעבודה מול מקלדת. תרגיל 'עצב' (Nerve gliding). ויטמין B6.",
        "urgency": "low"
    }
]

async def main():
    async with AsyncSessionLocal() as db:
        # Check if user exists
        stmt = select(User).where(User.email == USER_EMAIL)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"User '{USER_EMAIL}' not found. Creating...")
            user = User(
                id=uuid.uuid4(),
                email=USER_EMAIL,
                name=USER_NAME,
                username=USER_EMAIL.split("@")[0],
                password_hash=hash_password(USER_PASS),
                role=UserRole.doctor,
                is_active=True,
                auth_method="local"
            )
            db.add(user)
            await db.flush()
            print(f"Created new user: {user.name} ({user.id})")
        else:
            print(f"Found user: {user.name} ({user.id})")

        case_count = 0
        for case in OSTEOPATHY_CASES:
            # Create Patient
            patient = Patient(
                id=uuid.uuid4(),
                name=case["patient_name"],
                dob=case["dob"],
                created_by=user.id,
                email=f"{uuid.uuid4().hex[:8]}@example.com", # Dummy unique email
                phone=f"05{random.randint(0,9)}-{random.randint(1000000, 9999999)}"
            )
            db.add(patient)
            
            # Create Visit
            # Random date in the last 60 days
            days_ago = random.randint(1, 60)
            visit_date = datetime.now() - timedelta(days=days_ago)
            
            visit = Visit(
                id=uuid.uuid4(),
                patient_id=patient.id,
                doctor_id=user.id,
                start_time=visit_date,
                end_time=visit_date + timedelta(minutes=45),
                status=VisitStatus.completed,
                source="manual_entry"
            )
            db.add(visit)
            
            # Create Summary
            summary = Summary(
                id=uuid.uuid4(),
                visit_id=visit.id,
                summary_text=f"תלונת המטופל: {case['complaint']}\n\nממצאים:\n{case['findings']}\n\nאבחנה: {', '.join(case['diagnosis'])}\n\nטיפול:\n{case['treatment']}\n\nהמלצות:\n{case['recommendations']}",
                chief_complaint=case['complaint'],
                findings=case['findings'],
                diagnosis=case['diagnosis'],
                treatment_plan=case['treatment'],
                recommendations=case['recommendations'],
                urgency=case['urgency'],
                status=SummaryStatus.done,
                source="human"
            )
            db.add(summary)
            
            case_count += 1

        await db.commit()
        print(f"Successfully created {case_count} osteopathy cases for user {USER_EMAIL}")

if __name__ == "__main__":
    asyncio.run(main())
