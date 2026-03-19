# דוח קבצים מיותרים בפרויקט DoctorScribe
**תאריך סריקה:** 19/03/2026

---

## סיכום

| קטגוריה | נפח | בטוח למחיקה |
|----------|------|-------------|
| Backend Archive | 36 KB | כן |
| Frontend Archive | 20 KB | כן |
| node_modules | 519 MB | כן (ישוחזר עם npm install) |
| גיבויים ישנים | 200 KB | כן |
| קבצי demo/test | 13 KB | כן |
| קבצי mockup | 97 KB | כן |
| קבצי .bak | 21 KB | כן |
| לוגואים כפולים | 332 KB | כן (לשמור עותק 1) |
| Monitoring (לא פעיל) | 20 KB | כן |
| סקריפטים ישנים | 40 KB | חלקי |
| **סה"כ לחיסכון** | **~520 MB** | |

---

## רשימה מפורטת

### 1. Backend Archive — 36 KB (בטוח למחיקה)
תיקייה שלמה של קוד ישן שלא בשימוש

| קובץ | נפח | תיאור |
|-------|------|--------|
| `backend/_archive/diarization_service.py` | 1 KB | שירות זיהוי דוברים ישן |
| `backend/_archive/error_handler.py` | 1.3 KB | מטפל שגיאות ישן |
| `backend/_archive/events.py` | 522 B | מערכת אירועים ישנה |
| `backend/_archive/file_validator.py` | 2.2 KB | מאמת קבצים ישן |
| `backend/_archive/pipeline_service.py` | 645 B | שירות pipeline ישן |
| `backend/_archive/recommendations_service.py` | 1.2 KB | שירות המלצות ישן |
| `backend/_archive/secrets.py` | 873 B | מטפל סודות ישן |
| `backend/_archive/session.py` | 1.6 KB | ניהול sessions ישן |

### 2. Frontend Archive — 20 KB (בטוח למחיקה)
קוד Flutter ישן שלא מיובא בשום מקום

| קובץ | נפח | תיאור |
|-------|------|--------|
| `frontend/_archive/notification_bell.dart` | 2.0 KB | רכיב UI התראות ישן |
| `frontend/_archive/notification_service.dart` | 1.3 KB | שירות התראות ישן |
| `frontend/_archive/offline_service.dart` | 1.5 KB | שירות offline ישן |
| `frontend/_archive/websocket_service.dart` | 1.3 KB | שירות websocket ישן |

### 3. node_modules — 519 MB (בטוח למחיקה)
תלויות NPM — נבנות מחדש אוטומטית עם `npm install`

| תיקייה | נפח | תיאור |
|---------|------|--------|
| `parent-website/node_modules/` | 519 MB | חבילות NPM של Next.js |

### 4. גיבויים ישנים — 200 KB (בטוח למחיקה)

| קובץ | נפח | תיאור |
|-------|------|--------|
| `backups/20260316_162409/drscribe.dump` | 83 KB | גיבוי DB מ-16/03 |
| `backups/20260316_162409/docker-compose.prod.yml` | 3.3 KB | העתק docker-compose |
| `backups/20260316_162409/nginx.conf` | 3.3 KB | העתק nginx |
| `backups/20260318_113919/drscribe.dump` | 91 KB | גיבוי DB מ-18/03 |
| `backups/20260318_113919/docker-compose.prod.yml` | 3.3 KB | העתק docker-compose |
| `backups/20260318_113919/nginx.conf` | 3.3 KB | העתק nginx |

### 5. קבצי demo/test — 13 KB (בטוח למחיקה)

| קובץ | נפח | תיאור |
|-------|------|--------|
| `docs/osteopathy_case_1.csv` | 1.1 KB | נתוני בדיקה אוסטאופתיה |
| `docs/osteopathy_case_1_fields.txt` | 1.1 KB | מיפוי שדות לנתוני בדיקה |
| `docs/osteopathy_demo_cases.txt` | 8.2 KB | 10 מקרי דמו אוסטאופתיה |

### 6. קבצי mockup — 97 KB (בטוח למחיקה)
תבניות HTML/TSX לעיצוב מקומי — כבר יושמו או לא בשימוש

| קובץ | נפח | תיאור |
|-------|------|--------|
| `docs/specs/articles-list-mockup.html` | 20 KB | mockup רשימת מאמרים |
| `docs/specs/glucose-level-imbalance-mockup.html` | 17 KB | mockup מאמר גלוקוז |
| `docs/specs/glucose-level-imbalance-mockup.tsx` | 15 KB | mockup React מאמר גלוקוז |
| `docs/specs/homepage-mockup.html` | 50 KB | mockup דף הבית |
| `docs/specs/manual-note-mockup.html` | 22 KB | mockup סיכום ידני |
| `docs/specs/file.txt` | 4.1 KB | קובץ טקסט לא ידוע |

### 7. קבצי .bak — 21 KB (בטוח למחיקה)
גיבויים ידניים של קבצים שכבר בגרסה הנוכחית

| קובץ | נפח | תיאור |
|-------|------|--------|
| `parent-website/app/page.tsx.bak` | 12 KB | גיבוי דף הבית מ-16/03 |
| `parent-website/app/privacy/page.tsx.bak` | 8.8 KB | גיבוי דף פרטיות |

### 8. לוגואים כפולים — 332 KB (למחוק 2 מתוך 3)
אותו קובץ בדיוק (MD5 זהה) ב-3 מקומות

| קובץ | נפח | תיאור |
|-------|------|--------|
| `logo.png` | 166 KB | לוגו בשורש הפרויקט — **לשמור** |
| `parent-website/public/logo.png` | 166 KB | נדרש ל-Next.js — **לשמור** |
| `frontend/web/logo.png` | 166 KB | נדרש ל-Flutter — **לשמור** |

> הערה: כל ה-3 נדרשים כי כל אפליקציה קוראת מהתיקייה שלה. אין מה למחוק כאן.

### 9. Monitoring (לא פעיל) — 20 KB (בטוח למחיקה)
תשתית monitoring שלא הופעלה

| קובץ | נפח | תיאור |
|-------|------|--------|
| `monitoring/grafana/dashboards/` | 18 KB | תבניות Grafana dashboard |
| `monitoring/prometheus/alerts.yml` | 1.2 KB | חוקי התראות Prometheus |

> לא מוגדר ב-docker-compose.yml — אף שירות monitoring לא רץ

### 10. סקריפטים ישנים — 40 KB (חלקי)

| קובץ | נפח | תיאור | למחוק? |
|-------|------|--------|--------|
| `scripts/auto_run.sh` | 19 KB | Task runner ל-Claude | **לשמור** |
| `scripts/load-secrets.sh` | 1.9 KB | טעינת secrets | **לשמור** |
| `scripts/backup.sh` | 2 KB | סקריפט גיבוי ישן | כן |
| `scripts/deploy.sh` | 3 KB | סקריפט deploy ישן | כן |
| `scripts/generate_rsa_keys.sh` | 1 KB | יצירת מפתחות RSA | כן |
| `scripts/restore.sh` | 2 KB | סקריפט שחזור ישן | כן |
| `scripts/run_task.sh` | 1 KB | הרצת משימות ישן | כן |
| `scripts/setup_ssl.sh` | 2 KB | הקמת SSL ישן | כן |

### 11. קבצי .gitkeep — 0 KB (בטוח למחיקה)
קבצי placeholder ריקים — התיקיות כבר מכילות קבצים אמיתיים

| קובץ | תיאור |
|-------|--------|
| `parent-website/public/.gitkeep` | placeholder |
| `frontend/lib/services/.gitkeep` | placeholder |
| `frontend/lib/models/.gitkeep` | placeholder |
| `frontend/lib/screens/.gitkeep` | placeholder |
| `frontend/lib/utils/.gitkeep` | placeholder |
| `frontend/lib/widgets/.gitkeep` | placeholder |
| `frontend/lib/providers/.gitkeep` | placeholder |
| `frontend/test/.gitkeep` | placeholder |

---

## המלצה לפעולה

**שלב 1 — מחיקה מיידית (בטוחה):**
```bash
rm -rf backend/_archive/
rm -rf frontend/_archive/
rm -rf backups/
rm -f parent-website/app/page.tsx.bak
rm -f parent-website/app/privacy/page.tsx.bak
rm -rf monitoring/
```

**שלב 2 — ניקוי node_modules (ישוחזר בבילד):**
```bash
rm -rf parent-website/node_modules/
```

**שלב 3 — סקריפטים ישנים:**
```bash
rm scripts/backup.sh scripts/deploy.sh scripts/generate_rsa_keys.sh
rm scripts/restore.sh scripts/run_task.sh scripts/setup_ssl.sh
```

**סה"כ חיסכון: ~520 MB**
