# DoctorScribe AI — תרשימי זרימה

## תוכן עניינים
1. [תרשים זרימה: מרגע תחילת ההקלטה עד שמירה](#1-תרשים-זרימה-הקלטה)
2. [תרשים זרימה: מה נשמר ואיפה אחרי שהכל מוכן](#2-מה-נשמר-ואיפה)
3. [תרשים זרימה: חיפוש טקסט בתמלול או תווית](#3-תרשים-זרימה-חיפוש)

---

## 1. תרשים זרימה: הקלטה

### שלב A — הקלטה בדפדפן

```
┌─────────────────────────────────────────────────────────────────┐
│                        דפדפן (Browser)                          │
│                                                                  │
│  [1] הרופא בוחר מטופל                                            │
│      │                                                           │
│      ▼                                                           │
│  [2] הרופא לוחץ "התחל הקלטה"                                    │
│      │                                                           │
│      ▼                                                           │
│  [3] MediaRecorder API מתחיל הקלטה מהמיקרופון                    │
│      │  טיימר מציג: 00:00 → 00:01 → 00:02 ...                   │
│      │  פורמט: WebM (Opus codec)                                 │
│      │                                                           │
│      ▼                                                           │
│  [4] הרופא לוחץ "עצור הקלטה"                                    │
│      │                                                           │
│      ▼                                                           │
│  [5] MediaRecorder.stop() → Blob (קובץ אודיו בזיכרון הדפדפן)    │
│      │                                                           │
│      ▼                                                           │
│  [6] Provider: recordingNotifier.startRecording()                │
│      שולח POST /api/visits → יוצר Visit חדש                     │
│      מקבל visit_id                                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
```

### שלב B — העלאה (Chunked Upload)

```
┌─────────────────────────────────────────────────────────────────┐
│                   העלאה בחתיכות (Chunks)                         │
│                                                                  │
│  [7] הקובץ נחתך לחתיכות של ~5MB:                                │
│      chunk_0 (5MB) → chunk_1 (5MB) → chunk_2 (2.3MB, אחרון)    │
│                                                                  │
│  [8] לכל chunk:                                                  │
│      POST /api/recordings/upload-chunk                           │
│      Body: { file: chunk, visit_id, chunk_index, is_final }     │
│      Header: Authorization: Bearer eyJhb...                      │
│                                                                  │
│      UI מציג progress bar:                                       │
│      ████░░░░░░ 33% → ████████░░ 66% → ██████████ 100%          │
│                                                                  │
│  [9] chunk אחרון נשלח עם is_final=true                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
```

### שלב C — קבלה בשרת, הצפנה, שמירה

```
┌─────────────────────────────────────────────────────────────────┐
│               Backend (routers/recordings.py)                    │
│                                                                  │
│  [10] Middleware chain:                                           │
│       CORS ✓ → Auth (JWT decode + Redis blacklist) ✓             │
│       → Rate limit (100/min) ✓ → Audit log                      │
│                                                                  │
│  [11] מרכיב את כל ה-chunks לקובץ אחד:                           │
│       chunk_0 + chunk_1 + chunk_2 → raw_audio (12.3MB)           │
│                                                                  │
│  [12] הצפנת הקובץ (Envelope Encryption):                         │
│       ┌─────────────────────────────────────────────┐            │
│       │ DEK = os.urandom(32)    ← מפתח ייחודי לקובץ │            │
│       │                                              │            │
│       │ encrypted_audio = AES-256-GCM(DEK, raw_audio)│            │
│       │   → nonce(12 bytes) + ciphertext             │            │
│       │                                              │            │
│       │ encrypted_dek = AES-256-GCM(MasterKey, DEK)  │            │
│       │   → DEK עטוף עם מפתח ראשי                    │            │
│       └─────────────────────────────────────────────┘            │
│                                                                  │
│  [13] שמירה:                                                     │
│       encrypted_audio ──────→ MinIO (S3)                         │
│                                  key: "recordings/uuid-abc.webm" │
│                                                                  │
│       Recording row ────────→ PostgreSQL                          │
│         audio_url: "recordings/uuid-abc.webm"                    │
│         encryption_key: "aX7f9k2..." (DEK מוצפן)                │
│         duration_seconds: 185.4                                  │
│         format: "webm"                                           │
│         file_size: 12300000                                      │
│         visit_id: uuid-visit-123                                 │
│                                                                  │
│  [14] מפעיל Celery task:                                         │
│       process_transcription.delay(recording_id=uuid-abc)         │
│                                                                  │
│  [15] מחזיר HTTP 202 Accepted                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
```

### שלב D — תמלול (Celery Worker, ברקע)

```
┌─────────────────────────────────────────────────────────────────┐
│            Celery Worker: process_transcription()                │
│                                                                  │
│  [16] קורא Recording מ-PostgreSQL                                │
│       → מקבל audio_url + encrypted_dek                           │
│                                                                  │
│  [17] מוריד אודיו מוצפן מ-MinIO                                 │
│       GET "recordings/uuid-abc.webm" → encrypted_bytes           │
│                                                                  │
│  [18] פענוח:                                                     │
│       DEK = decrypt(MasterKey, encrypted_dek)                    │
│       raw_audio = AES-256-GCM.decrypt(DEK, encrypted_bytes)     │
│                                                                  │
│  [19] PII Masking — לא בשלב הזה (רק בסיכום)                     │
│                                                                  │
│  [20] שליחה ל-OpenAI Whisper API:                                │
│       ┌──────────────────────────────────────────┐               │
│       │ model: "whisper-1"                        │               │
│       │ language: "he" (עברית)                    │               │
│       │ response_format: "verbose_json"           │               │
│       │ file: raw_audio                           │               │
│       │                                           │               │
│       │ Retry: עד 3 ניסיונות                      │               │
│       │   ניסיון 1 נכשל → המתנה 2 שניות          │               │
│       │   ניסיון 2 נכשל → המתנה 4 שניות          │               │
│       │   ניסיון 3 → הצלחה/כישלון סופי            │               │
│       └──────────────────────────────────────────┘               │
│                                                                  │
│  [21] תשובה מ-Whisper:                                           │
│       {                                                          │
│         text: "המטופל מתלונן על כאבי ראש חזקים...",               │
│         segments: [                                               │
│           {start: 0.0, end: 2.5, text: "שלום דוקטור"},           │
│           {start: 2.5, end: 8.1, text: "אני סובל מכאבי ראש..."}│
│         ],                                                       │
│         language: "he",                                           │
│         confidence: 0.94                                          │
│       }                                                          │
│                                                                  │
│  [22] הצפנת התמלול:                                               │
│       encrypted_text = AES-256-GCM(MasterKey, full_text)         │
│                                                                  │
│  [23] שמירה ב-PostgreSQL:                                        │
│       Transcription row:                                          │
│         recording_id: uuid-abc                                   │
│         full_text: "bY8g0l3mN..." (מוצפן)                       │
│         speakers_json: [{start, end, text, speaker}]             │
│         language: "he"                                            │
│         confidence_score: 0.94                                    │
│         status: "done"                                            │
│                                                                  │
│  [24] מפעיל: process_summary.delay(visit_id=uuid-visit-123)     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
```

### שלב E — סיכום AI (Celery Worker, ברקע)

```
┌─────────────────────────────────────────────────────────────────┐
│              Celery Worker: process_summary()                    │
│                                                                  │
│  [25] קורא Transcription → מפענח full_text                      │
│       "המטופל מתלונן על כאבי ראש חזקים בצד שמאל..."             │
│                                                                  │
│  [26] PII Masking (לפני שליחה ל-GPT):                            │
│       ┌──────────────────────────────────────────┐               │
│       │ mask_pii(text):                           │               │
│       │                                           │               │
│       │ קלט: "ת.ז 123456789, טלפון 0501234567"   │               │
│       │   ↓                                       │               │
│       │ פלט: "ת.ז [ID_NUMBER_0], טלפון [MOBILE_1]"│              │
│       │   +                                       │               │
│       │ pii_map: {                                │               │
│       │   "[ID_NUMBER_0]": "123456789",           │               │
│       │   "[MOBILE_1]": "0501234567"              │               │
│       │ }                                         │               │
│       └──────────────────────────────────────────┘               │
│                                                                  │
│  [27] שליחה ל-OpenAI GPT-4.1 (טקסט ממוסך בלבד!):                │
│       ┌──────────────────────────────────────────┐               │
│       │ System: "אתה רופא מומחה. סכם את הביקור   │               │
│       │          הרפואי הבא בפורמט JSON מובנה."   │               │
│       │                                           │               │
│       │ User: "המטופל עם ת.ז [ID_NUMBER_0]       │               │
│       │        מתלונן על כאבי ראש חזקים בצד       │               │
│       │        שמאל. בדיקה גופנית: רגישות באזור   │               │
│       │        הרקה השמאלית..."                    │               │
│       │                                           │               │
│       │ → OpenAI לא רואה מספרי ת.ז. אמיתיים!     │               │
│       └──────────────────────────────────────────┘               │
│                                                                  │
│  [28] תשובה מ-GPT-4.1 (JSON מובנה):                              │
│       {                                                          │
│         summary_text: "ביקור רפואי — כאבי ראש...",               │
│         chief_complaint: "כאבי ראש חזקים בצד שמאל",             │
│         findings: "רגישות באזור הרקה השמאלית",                   │
│         diagnosis: [                                              │
│           {code: "R51", description: "כאב ראש"}                  │
│         ],                                                       │
│         treatment_plan: "איבופרופן 400mg x3 ביום",              │
│         recommendations: "MRI מוח אם לא משתפר תוך שבוע",       │
│         urgency: "moderate"                                       │
│       }                                                          │
│                                                                  │
│  [29] post_redact — בטיחות נוספת:                                 │
│       בודק שה-GPT לא "המציא" מספרי ת.ז. → מחליף ב-[REDACTED]   │
│                                                                  │
│  [30] restore_pii — מחזיר ערכים אמיתיים:                          │
│       "[ID_NUMBER_0]" → "123456789"                               │
│       "[MOBILE_1]" → "0501234567"                                 │
│                                                                  │
│  [31] הצפנה של כל שדות הטקסט:                                     │
│       chief_complaint = AES-256-GCM(MasterKey, "כאבי ראש...")    │
│       findings        = AES-256-GCM(MasterKey, "רגישות...")      │
│       treatment_plan  = AES-256-GCM(MasterKey, "איבופרופן...")   │
│       recommendations = AES-256-GCM(MasterKey, "MRI מוח...")     │
│       summary_text    = AES-256-GCM(MasterKey, "ביקור...")       │
│                                                                  │
│  [32] שמירה ב-PostgreSQL:                                        │
│       Summary row:                                                │
│         visit_id: uuid-visit-123                                 │
│         chief_complaint: "cZ9h1m4..." (מוצפן)                   │
│         findings: "dW0i2n5..." (מוצפן)                           │
│         diagnosis: [{code: "R51", description: "כאב ראש"}]      │
│         treatment_plan: "eX1j3o6..." (מוצפן)                    │
│         recommendations: "fY2k4p7..." (מוצפן)                   │
│         urgency: "moderate"                                       │
│         status: "done"                                            │
│         source: "ai"                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
```

### שלב F — תיוג + אינדוקס + עדכון Frontend

```
┌─────────────────────────────────────────────────────────────────┐
│                    תיוג רפואי (Tags)                             │
│                                                                  │
│  [33] GPT מחלץ תוויות רפואיות:                                   │
│       [                                                          │
│         {type: "medication", code: "M01AE01",                    │
│          label: "Ibuprofen", confidence: 0.95},                  │
│         {type: "symptom",    code: "R51",                        │
│          label: "Headache",  confidence: 0.98},                  │
│         {type: "procedure",  code: "MRI",                        │
│          label: "MRI Brain", confidence: 0.90}                   │
│       ]                                                          │
│                                                                  │
│  [34] שמירה ב-PostgreSQL (tags table):                           │
│       entity_type: "summary"                                     │
│       entity_id: uuid-summary-456                                │
│       tag_type: "medication" / "symptom" / "procedure"           │
│       tag_code: "M01AE01" / "R51" / "MRI"                       │
│       tag_label: "Ibuprofen" / "Headache" / "MRI Brain"         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              אינדוקס ל-Meilisearch (חיפוש מהיר)                 │
│                                                                  │
│  [35] מפענח את הסיכום ושולח עותק לא-מוצפן ל-Meilisearch:       │
│       summaries index ← {                                        │
│         id: uuid-summary-456,                                    │
│         visit_id: uuid-visit-123,                                │
│         doctor_id: uuid-doctor-789,                              │
│         patient_name: "יוסי כהן",       ← מפוענח                │
│         chief_complaint: "כאבי ראש...", ← מפוענח                │
│         findings: "רגישות...",          ← מפוענח                │
│         treatment_plan: "איבופרופן...", ← מפוענח                │
│         tags: ["Ibuprofen", "Headache", "MRI Brain"],            │
│         urgency: "moderate",                                     │
│         created_at: "2026-03-23T14:30:00"                        │
│       }                                                          │
│                                                                  │
│  [36] אינדוקס תמלול:                                             │
│       transcriptions index ← {                                   │
│         id: uuid-trans-789,                                      │
│         patient_name: "יוסי כהן",                                │
│         full_text: "המטופל מתלונן על כאבי ראש...", ← מפוענח     │
│         language: "he",                                           │
│         doctor_id: uuid-doctor-789                                │
│       }                                                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   עדכון Frontend (Polling)                       │
│                                                                  │
│  [37] Frontend polls כל 5 שניות:                                 │
│       GET /api/visits/uuid-visit-123/status                      │
│                                                                  │
│       תגובות לאורך הזמן:                                         │
│       { transcription_status: "processing", summary_status: "pending"  } ← 0:05
│       { transcription_status: "processing", summary_status: "pending"  } ← 0:10
│       { transcription_status: "done",        summary_status: "processing"} ← 0:45
│       { transcription_status: "done",        summary_status: "done"      } ← 1:15
│                                                                  │
│  [38] UI מתעדכן:                                                 │
│       ⏳ מתמלל...           → ✅ תמלול מוכן                      │
│       ⏳ מסכם...            → ✅ סיכום מוכן                       │
│                                                                  │
│       מציג:                                                      │
│       ┌──────────────────────────────────────┐                   │
│       │ תלונה עיקרית: כאבי ראש חזקים בצד שמאל│                  │
│       │ ממצאים: רגישות באזור הרקה השמאלית     │                  │
│       │ אבחנה: R51 — כאב ראש                  │                  │
│       │ טיפול: איבופרופן 400mg x3 ביום        │                  │
│       │ המלצות: MRI מוח אם לא משתפר          │                  │
│       │ דחיפות: ⚠️ בינונית                     │                  │
│       │ תוויות: 💊 Ibuprofen  🩺 Headache      │                  │
│       └──────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### סיכום הזרימה בשורה אחת:

```
🎤 הקלטה → 📤 העלאה (chunks) → 🔐 הצפנה (DEK) → 💾 MinIO
  → ⚙️ Celery: פענוח → 🗣️ Whisper (תמלול) → 🔐 הצפנה → 💾 DB
  → ⚙️ Celery: 🎭 PII mask → 🤖 GPT-4.1 (סיכום) → 🎭 PII restore → 🔐 הצפנה → 💾 DB
  → 🏷️ תיוג → 🔍 Meilisearch index → 📱 UI update
```

---

## 2. מה נשמר ואיפה

### אחרי שהכל מוכן — מפת האחסון:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│                    MinIO (S3-compatible)                          │
│                                                                  │
│    recordings/uuid-abc.webm                                      │
│    ┌────────────────────────────────────────┐                    │
│    │ 🔐 קובץ אודיו מוצפן                    │                    │
│    │    AES-256-GCM עם DEK ייחודי           │                    │
│    │    12.3MB                               │                    │
│    │    ❌ חסר ערך בלי DEK מה-DB              │                    │
│    └────────────────────────────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│                 PostgreSQL (מסד נתונים ראשי)                     │
│                                                                  │
│  visits                                                          │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ id: uuid-visit-123                                      │     │
│  │ patient_id: uuid-patient-456                            │     │
│  │ doctor_id: uuid-doctor-789                              │     │
│  │ status: "completed"                                     │     │
│  │ source: "recording"                                     │     │
│  │ start_time: 2026-03-23 14:00:00+02                     │     │
│  │ end_time: 2026-03-23 14:03:05+02                       │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  recordings                                                      │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ id: uuid-rec-abc                                        │     │
│  │ visit_id: uuid-visit-123                                │     │
│  │ audio_url: "recordings/uuid-abc.webm"  ← מצביע ל-MinIO │     │
│  │ encryption_key: "aX7f9k2mP8..."  🔐 DEK מוצפן         │     │
│  │ duration_seconds: 185.4                                 │     │
│  │ format: "webm"                                          │     │
│  │ file_size: 12300000                                     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  transcriptions                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ id: uuid-trans-def                                      │     │
│  │ recording_id: uuid-rec-abc                              │     │
│  │ full_text: "bY8g0l3mN..."  🔐 מוצפן עם MasterKey      │     │
│  │ speakers_json: [{start, end, text, speaker}, ...]       │     │
│  │ language: "he"                                          │     │
│  │ confidence_score: 0.94                                  │     │
│  │ status: "done"                                          │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  summaries                                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ id: uuid-sum-ghi                                        │     │
│  │ visit_id: uuid-visit-123                                │     │
│  │ chief_complaint: "cZ9h1m4..."  🔐 מוצפן                │     │
│  │ findings: "dW0i2n5..."         🔐 מוצפן                │     │
│  │ diagnosis: [{code:"R51", description:"כאב ראש"}] ← JSON│     │
│  │ treatment_plan: "eX1j3o6..."   🔐 מוצפן                │     │
│  │ recommendations: "fY2k4p7..."  🔐 מוצפן                │     │
│  │ summary_text: "gZ3l5q8..."     🔐 מוצפן                │     │
│  │ urgency: "moderate"            ← לא מוצפן              │     │
│  │ source: "ai"                   ← לא מוצפן              │     │
│  │ status: "done"                 ← לא מוצפן              │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  tags (3 שורות לסיכום הזה)                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ entity_type: "summary"                                  │     │
│  │ entity_id: uuid-sum-ghi                                 │     │
│  │ tag_type: "medication" │ tag_code: "M01AE01"           │     │
│  │ tag_label: "Ibuprofen"                                  │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │ tag_type: "symptom"    │ tag_code: "R51"               │     │
│  │ tag_label: "Headache"                                   │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │ tag_type: "procedure"  │ tag_code: "MRI"               │     │
│  │ tag_label: "MRI Brain"                                  │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  audit_log (2 שורות לפחות)                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ action: "create" │ entity_type: "recording"            │     │
│  │ user_id: uuid-doctor-789 │ ip: "185.x.x.x"            │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │ action: "create" │ entity_type: "visit"                │     │
│  │ user_id: uuid-doctor-789 │ ip: "185.x.x.x"            │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  patients (כבר היה קיים לפני הביקור)                              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ id: uuid-patient-456                                    │     │
│  │ name: "hA4m6r9..."        🔐 מוצפן                     │     │
│  │ id_number: "iB5n7s0..."   🔐 מוצפן                     │     │
│  │ id_number_hash: "e3b0c..."  ← HMAC (לחיפוש מהיר)      │     │
│  │ phone: "jC6o8t1..."       🔐 מוצפן                     │     │
│  │ email: "kD7p9u2..."       🔐 מוצפן                     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│                   Meilisearch (אינדקס חיפוש)                     │
│                                                                  │
│  summaries index                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ id: uuid-sum-ghi                                        │     │
│  │ patient_name: "יוסי כהן"          ← טקסט פתוח!         │     │
│  │ chief_complaint: "כאבי ראש חזקים"  ← טקסט פתוח!        │     │
│  │ findings: "רגישות באזור הרקה"      ← טקסט פתוח!        │     │
│  │ treatment_plan: "איבופרופן 400mg"  ← טקסט פתוח!        │     │
│  │ tags: ["Ibuprofen", "Headache", "MRI Brain"]            │     │
│  │ doctor_id: uuid-doctor-789         ← לסינון             │     │
│  │ urgency: "moderate"                                     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  transcriptions index                                            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ id: uuid-trans-def                                      │     │
│  │ patient_name: "יוסי כהן"                                │     │
│  │ full_text: "המטופל מתלונן על כאבי ראש..."  ← טקסט פתוח!│     │
│  │ doctor_id: uuid-doctor-789                               │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  ⚠️ Meilisearch = שירות פנימי, לא חשוף לאינטרנט                 │
│     מכיל טקסט פתוח לצורך חיפוש מהיר                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│                        Redis                                     │
│                                                                  │
│  (לא שומר נתוני ביקור — רק tokens + task queue)                  │
│  bl:jti-uuid → "1"  (token blacklist)                            │
│  celery task results → task status                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### סיכום — מה מוצפן ומה לא:

```
🔐 = מוצפן AES-256-GCM    🔓 = לא מוצפן    #️⃣ = Hash (חד-כיווני)

PostgreSQL:
  patients.name           🔐  (MasterKey)
  patients.id_number      🔐  (MasterKey)
  patients.id_number_hash #️⃣  (HMAC-SHA256)
  patients.phone          🔐  (MasterKey)
  patients.email          🔐  (MasterKey)
  recordings.encryption_key 🔐  (DEK עטוף עם MasterKey)
  transcriptions.full_text  🔐  (MasterKey)
  summaries.* (6 שדות)      🔐  (MasterKey)
  summaries.diagnosis        🔓  (JSONB, לא מוצפן)
  summaries.urgency          🔓
  tags.*                     🔓
  audit_log.*                🔓

MinIO:
  audio files               🔐  (DEK ייחודי לכל קובץ)

Meilisearch:
  summaries index           🔓  (טקסט פתוח — שירות פנימי)
  transcriptions index      🔓  (טקסט פתוח — שירות פנימי)
```

---

## 3. תרשים זרימה: חיפוש

### חיפוש A — חיפוש טקסט חופשי (למשל "כאבי ראש")

```
┌─────────────────────────────────────────────────────────────────┐
│ שלב 1: BROWSER                                                  │
│                                                                  │
│ הרופא מקליד "כאבי ראש" בשדה חיפוש                               │
│ search_provider.dart:                                            │
│   ref.read(searchProvider.notifier).search("כאבי ראש")          │
│                                                                  │
│ GET /api/search?q=כאבי ראש&page=1&per_page=20                   │
│ Header: Authorization: Bearer eyJhb...                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ שלב 2: BACKEND — routers/search.py                               │
│                                                                  │
│ Auth: JWT → doctor_id = uuid-doctor-789                          │
│                                                                  │
│ מפעיל search_db_text(db, "כאבי ראש", doctor_id=uuid-doctor-789) │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┴────────────────┐
              ▼                             ▼
┌───────────────────────┐      ┌───────────────────────────────┐
│ נתיב 1: Meilisearch   │      │ נתיב 2: PostgreSQL (fallback) │
│ (מהיר, ranked)         │      │ (אם Meilisearch לא זמין)      │
│                        │      │                                │
│ חיפוש באינדקס:         │      │ SELECT summaries + patients    │
│  summaries index       │      │ WHERE doctor_id = :doctor      │
│  filter: doctor_id =   │      │                                │
│    uuid-doctor-789     │      │ לכל שורה:                       │
│                        │      │   decrypt_summary_fields()     │
│ Meilisearch מחזיר:     │      │   decrypt_patient_pii()        │
│  hits ranked by        │      │                                │
│  relevance             │      │ סינון ב-Python:                │
│  + highlighting        │      │   "כאבי ראש" in               │
│  + total count         │      │     decrypted_field.lower()    │
│                        │      │                                │
│ ⚡ מיקרו-שניות          │      │ 🐌 שניות (O(n) decrypt)        │
└───────────┬────────────┘      └──────────────┬────────────────┘
            │                                  │
            └──────────┬───────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ שלב 3: גם חיפוש בתמלולים                                        │
│                                                                  │
│ SELECT transcriptions + patients                                 │
│ WHERE doctor_id = :doctor                                        │
│ AND visit_id NOT IN (כבר נמצאו בסיכומים)                         │
│                                                                  │
│ לכל תמלול:                                                       │
│   decrypt_transcription_fields()                                 │
│   decrypt_patient_pii()                                          │
│   "כאבי ראש" in decrypted_full_text.lower()                     │
│                                                                  │
│ → אם נמצא: מוסיף לתוצאות (snippet של 300 תווים)                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ שלב 4: RESPONSE → BROWSER                                       │
│                                                                  │
│ HTTP 200 OK                                                      │
│ {                                                                │
│   "hits": [                                                      │
│     {                                                            │
│       "id": "uuid-sum-ghi",                                     │
│       "patient_name": "יוסי כהן",                               │
│       "patient_display_id": 42,                                  │
│       "chief_complaint": "כאבי ראש חזקים בצד שמאל",             │
│       "findings": "רגישות באזור הרקה השמאלית",                   │
│       "diagnosis": "R51 — כאב ראש",                              │
│       "treatment_plan": "איבופרופן 400mg x3 ביום",              │
│       "tags": ["Ibuprofen", "Headache", "MRI Brain"],            │
│       "urgency": "moderate",                                     │
│       "created_at": "2026-03-23T14:30:00"                        │
│     },                                                           │
│     { ... תוצאה נוספת ... }                                       │
│   ],                                                             │
│   "total": 5                                                     │
│ }                                                                │
│                                                                  │
│ UI מציג רשימת כרטיסים עם highlight על "כאבי ראש"                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### חיפוש B — חיפוש לפי תווית (Tag) (למשל "Ibuprofen")

```
┌─────────────────────────────────────────────────────────────────┐
│ שלב 1: BROWSER                                                  │
│                                                                  │
│ הרופא בוחר תווית "Ibuprofen" מהרשימה                            │
│ (או מקליד חיפוש עם סינון tags)                                   │
│                                                                  │
│ GET /api/search?q=&tags=Ibuprofen&page=1                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ שלב 2: BACKEND — search_by_tags()                                │
│                                                                  │
│ [1] חיפוש ב-tags table (לא מוצפן!):                              │
│      SELECT entity_id FROM tags                                  │
│      WHERE entity_type = 'summary'                               │
│      AND tag_label ILIKE '%Ibuprofen%'                           │
│                                                                  │
│      → מחזיר: [uuid-sum-ghi, uuid-sum-xyz, ...]                 │
│      ⚡ מהיר — SQL ישיר על טבלה לא מוצפנת                        │
│                                                                  │
│ [2] שליפת הסיכומים לפי IDs:                                      │
│      SELECT summaries JOIN visits JOIN patients                   │
│      WHERE summary.id IN (:found_ids)                            │
│      AND visits.doctor_id = :current_doctor                      │
│                                                                  │
│ [3] פענוח לתצוגה:                                                 │
│      decrypt_summary_fields(summary)                             │
│      decrypt_patient_pii(patient)                                │
│                                                                  │
│ [4] שליפת כל התוויות לכל סיכום:                                   │
│      SELECT * FROM tags WHERE entity_id = :summary_id            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ שלב 3: RESPONSE → BROWSER                                       │
│                                                                  │
│ {                                                                │
│   "hits": [                                                      │
│     {                                                            │
│       "patient_name": "יוסי כהן",                               │
│       "chief_complaint": "כאבי ראש חזקים",                      │
│       "treatment_plan": "איבופרופן 400mg...",                   │
│       "tags": ["Ibuprofen", "Headache", "MRI Brain"],            │
│       ...                                                        │
│     },                                                           │
│     {                                                            │
│       "patient_name": "שרה לוי",                                │
│       "chief_complaint": "כאבי גב תחתון",                      │
│       "treatment_plan": "איבופרופן 200mg + פיזיותרפיה",        │
│       "tags": ["Ibuprofen", "Back Pain"],                        │
│       ...                                                        │
│     }                                                            │
│   ],                                                             │
│   "total": 2                                                     │
│ }                                                                │
│                                                                  │
│ UI: כל הביקורים שקיבלו Ibuprofen                                 │
└─────────────────────────────────────────────────────────────────┘
```

### השוואה — חיפוש טקסט vs חיפוש תווית:

```
┌──────────────────┬──────────────────────┬──────────────────────┐
│                  │ חיפוש טקסט ("כאבי")  │ חיפוש תווית (Ibuprofen)│
├──────────────────┼──────────────────────┼──────────────────────┤
│ מנוע חיפוש       │ Meilisearch          │ PostgreSQL (tags)     │
│                  │ + PostgreSQL fallback│                       │
├──────────────────┼──────────────────────┼──────────────────────┤
│ מחפש ב...        │ סיכומים + תמלולים    │ טבלת tags בלבד       │
├──────────────────┼──────────────────────┼──────────────────────┤
│ צריך פענוח?      │ כן (ב-fallback)      │ כן (לתצוגה בלבד)     │
│                  │ לא (ב-Meilisearch)  │ Tags = לא מוצפנים    │
├──────────────────┼──────────────────────┼──────────────────────┤
│ מהירות           │ ⚡ Meilisearch: מהיר  │ ⚡ מהיר (SQL ישיר)    │
│                  │ 🐌 Fallback: איטי    │                       │
├──────────────────┼──────────────────────┼──────────────────────┤
│ סוג התאמה        │ חלקי + fuzzy         │ חלקי (ILIKE)          │
├──────────────────┼──────────────────────┼──────────────────────┤
│ תומך בפילטרים    │ תאריך, דחיפות, תוויות│ תאריך, דחיפות        │
└──────────────────┴──────────────────────┴──────────────────────┘
```

---

*מסמך זה נוצר אוטומטית מניתוח הקוד של DoctorScribe AI.*
*עדכון אחרון: March 2026*
