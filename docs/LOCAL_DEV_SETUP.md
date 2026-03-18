# מדריך הקמת סביבת פיתוח מקומית — DoctorScribe

## סקירה כללית

```
היום:     VS Code ──SSH──> שרת GCP ──> עריכה ישירה על production ⚠️

אחרי:    VS Code מקומי → localhost → git push → GitHub Actions → deploy אוטומטי ✅
```

המדריך הזה **לא נוגע** בשרת הקיים. הכל מתבצע מהמחשב האישי שלך.

---

## שלב 0: דרישות מוקדמות

התקן על המחשב האישי:

| כלי | קישור | הערות |
|-----|--------|-------|
| **Docker Desktop** | https://www.docker.com/products/docker-desktop/ | חובה — מריץ את כל הפרויקט |
| **Git** | https://git-scm.com/download/win | ניהול קוד |
| **VS Code** | כבר מותקן | |

### בדיקה שהכל מותקן
```powershell
docker --version        # Docker version 24+
docker compose version  # Docker Compose v2+
git --version           # git version 2+
```

---

## שלב 1: Clone הפרויקט מהשרת

**חשוב: זה לא נוגע בשרת. רק מוריד עותק.**

### אופציה א — Clone מ-GitHub (מומלץ)
```powershell
cd C:\Users\Yossi\Projects
git clone https://github.com/Bob789/medscribe-ai-project.git drscribe
cd drscribe
```

### אופציה ב — Clone ישירות מהשרת
```powershell
cd C:\Users\Yossi\Projects
scp -r -i C:\Users\Yossi\.ssh\id_rsa centerwow_com_gmail_com@34.140.74.189:/opt/drscribe ./drscribe
cd drscribe
git init
```

---

## שלב 2: הגדרת קובץ .env מקומי

צור קובץ `.env` בתיקיית הפרויקט. **העתק מהשרת ושנה רק את מה שצריך:**

```powershell
# העתק .env מהשרת
scp -i C:\Users\Yossi\.ssh\id_rsa centerwow_com_gmail_com@34.140.74.189:/opt/drscribe/.env .\.env
```

### שנה את הערכים הבאים ב-.env:

```env
# ── שנה ל-local ──
ENV_MODE=development
DEBUG=true
BACKEND_HOST=0.0.0.0
DB_HOST=postgres
REDIS_HOST=redis
DATABASE_URL=postgresql+asyncpg://medscribe:changeme_db_password@postgres:5432/medscribe
REDIS_URL=redis://redis:6379/0

# ── השאר כמו שהם (API keys) ──
OPENAI_API_KEY=sk-...          # אותו מפתח
WHISPER_API_KEY=sk-...         # אותו מפתח
GOOGLE_CLIENT_ID=...           # אותו
GOOGLE_CLIENT_SECRET=...       # אותו
ENCRYPTION_KEY=...             # אותו — כדי לקרוא data מוצפן

# ── שנה redirect URIs ──
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
GOOGLE_CALENDAR_REDIRECT_URI=http://localhost:8000/api/calendar/callback

# ── הוסף (אם חסר) ──
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8000
```

### הוסף localhost ב-Google Cloud Console
1. לך ל-https://console.cloud.google.com → APIs & Services → Credentials
2. ערוך את ה-OAuth 2.0 Client
3. הוסף ל-**Authorized redirect URIs**:
   - `http://localhost:8000/api/auth/google/callback`
   - `http://localhost:8000/api/calendar/callback`
4. הוסף ל-**Authorized JavaScript origins**:
   - `http://localhost:3000`
   - `http://localhost:8000`

---

## שלב 3: הרצה מקומית

```powershell
# בתיקיית הפרויקט
cd C:\Users\Yossi\Projects\drscribe

# הרץ הכל (בפעם הראשונה ייקח 5-10 דקות לבנות images)
docker compose up --build
```

### מה רץ ואיפה:

| שירות | כתובת מקומית | מה זה |
|--------|-------------|--------|
| **Frontend** | http://localhost:3000 | אפליקציית Flutter |
| **Backend API** | http://localhost:8000 | FastAPI + Swagger |
| **Parent Website** | http://localhost:3001 | אתר Next.js |
| **MinIO Console** | http://localhost:9001 | ניהול קבצים (S3) |
| **Meilisearch** | http://localhost:7700 | מנוע חיפוש |
| **PostgreSQL** | localhost:5432 | בסיס נתונים |
| **Redis** | localhost:6379 | תורים + cache |

### בדיקה שהכל עובד:
```powershell
# בדוק שכל הcontainers רצים
docker compose ps

# בדוק API
curl http://localhost:8000/api/health

# פתח בדפדפן
start http://localhost:3000
```

---

## שלב 4: הגדרת GitHub (פעם אחת)

### 4.1 — צור repo פרטי ב-GitHub
1. לך ל-https://github.com/new
2. שם: `drscribe` (או כל שם)
3. **Private** ✓
4. ללא README/gitignore (כבר יש)

### 4.2 — חבר את הפרויקט המקומי ל-GitHub
```powershell
cd C:\Users\Yossi\Projects\drscribe

# הוסף remote חדש (שמור את הישן כ-origin-server)
git remote rename origin origin-server 2>$null
git remote add origin https://github.com/YOUR_USER/drscribe.git

# דחוף את הקוד
git push -u origin master
git push -u origin feature/medical-content-automation-spec
```

### 4.3 — הגדר Secrets ב-GitHub
לך ל-GitHub → Settings → Secrets and variables → Actions

הוסף:
| Secret | ערך |
|--------|-----|
| `GCP_SSH_KEY` | תוכן הקובץ `C:\Users\Yossi\.ssh\id_rsa` |
| `GCP_HOST` | `34.140.74.189` |
| `GCP_USER` | `centerwow_com_gmail_com` |

---

## שלב 5: GitHub Actions — CI/CD

צור את הקובץ הבא בפרויקט:

### `.github/workflows/deploy.yml`
```yaml
name: Build, Test & Deploy

on:
  push:
    branches: [master]

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Backend
        run: docker build ./backend -t drscribe-backend-test

      - name: Build Frontend
        run: docker build ./frontend -t drscribe-frontend-test

      - name: Build Parent Website
        run: docker build ./parent-website -t drscribe-parent-test

      # הוסף בדיקות כאן בעתיד:
      # - name: Run Backend Tests
      #   run: docker run drscribe-backend-test pytest

  deploy:
    needs: build-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/master'
    steps:
      - name: Deploy to GCP
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.GCP_HOST }}
          username: ${{ secrets.GCP_USER }}
          key: ${{ secrets.GCP_SSH_KEY }}
          script: |
            cd /opt/drscribe
            git pull origin master
            docker compose -f docker-compose.prod.yml build backend celery-worker frontend parent-website
            docker compose -f docker-compose.prod.yml up -d --force-recreate backend celery-worker frontend parent-website
            echo "Deploy completed at $(date)"
```

---

## שלב 6: Flow עבודה יומיומי

### פיתוח רגיל:
```powershell
# 1. עדכן מ-GitHub
git pull origin master

# 2. צור branch חדש למשימה
git checkout -b design/patients-new-look

# 3. ערוך קוד ב-VS Code

# 4. בדוק מקומית
docker compose up --build frontend    # רק מה ששינית

# 5. פתח http://localhost:3000 ובדוק

# 6. אם עובד — commit + push
git add -A
git commit -m "Redesign patients screen"
git push origin design/patients-new-look

# 7. ב-GitHub — פתח Pull Request ל-master

# 8. Merge ← GitHub Actions מריץ build ← אם עבר ← deploy אוטומטי לשרת
```

### תיקון באג דחוף (hotfix):
```powershell
git checkout master
git checkout -b hotfix/fix-summary-decrypt
# תקן...
git push origin hotfix/fix-summary-decrypt
# Merge to master → auto deploy
```

---

## שלב 7: העברת Data (אופציונלי)

אם רוצים לעבוד עם data אמיתי מקומית:

```powershell
# העתק גיבוי DB מהשרת
scp -i C:\Users\Yossi\.ssh\id_rsa centerwow_com_gmail_com@34.140.74.189:/opt/drscribe/backups/20260318_113909/drscribe.dump .\backup.dump

# שחזר מקומית
docker compose exec -T postgres pg_restore -U medscribe -d medscribe --clean < backup.dump
```

**שים לב:** ה-data מוצפן עם `ENCRYPTION_KEY`. חייב להשתמש באותו מפתח מה-.env של השרת.

---

## סיכום — מה משתנה

| לפני | אחרי |
|-------|-------|
| עריכה ישירה על production | עריכה מקומית + בדיקה |
| שינוי אחד שובר אחר | branch נפרד לכל משימה |
| deploy ידני | deploy אוטומטי אחרי merge |
| אין בדיקות | build check לפני deploy |
| גיבוי ידני | git = הגיבוי |

---

## פקודות שימושיות

```powershell
# הרץ רק backend (מהיר לפיתוח)
docker compose up backend postgres redis celery-worker

# הרץ רק frontend
docker compose up frontend

# ראה logs
docker compose logs -f backend

# מחק הכל והתחל מחדש
docker compose down -v
docker compose up --build

# בדוק מה רץ
docker compose ps
```

---

## ⚠️ אזהרות

1. **לעולם אל תדחוף .env ל-GitHub** — כבר ב-.gitignore
2. **לעולם אל תעשה git push --force ל-master**
3. **תמיד בדוק מקומית לפני merge ל-master**
4. **שרת GCP לא נפגע** — כל העבודה המקומית היא עותק נפרד
