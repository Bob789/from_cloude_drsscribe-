# MedScribe AI - הנחיות עבודה קבועות

## פרויקט
- תיקיית עבודה: `/mnt/c/medscribe-ai-project` (C:\medscribe-ai-project)
- תיעוד פרויקט: `/mnt/c/medscribe-ai-project/docs/`
- משימות: `/mnt/c/medscribe-ai-project/.claude/tasks/`

## כללי עבודה
- עובד אך ורק על `/mnt/c/medscribe-ai-project`
- כל ההרשאות מאושרות מראש — קבצים, תלויות, התקנות
- מתקין תלויות ללא שאלה (npm install, pip install וכו')
- לא שואל שאלות מיותרות — מקבל החלטה סבירה וממשיך עד סיום
- מדווח רק על התוצאה הסופית

## אופטימיזציה + חיפוש חכם + חיסכון טוקנים

### קריאת קבצים
- אל תקרא קבצים שלא רלוונטיים למשימה הנוכחית
- קרא רק את החלק הרלוונטי מקובץ גדול (offset + limit בשורות)
- אל תציג קוד שלא השתנה

### חיפוש בקוד
- השתמש ב-`rg` (ripgrep) לחיפוש ממוקד — לא לסרוק תיקיות שלמות
- `rg "pattern" backend/app/` לחיפוש בbackend
- `rg "pattern" frontend/lib/` לחיפוש בfrontend
- חיפוש ממוקד עדיף על קריאת קבצים שלמים

### ניהול היסטוריה
- השתמש ב-`/compact` כשההיסטוריה מתנפחת
- כתוב קוד תמציתי ונקי — בלי הערות מיותרות

### לפני משימה
- קרא נתונים → תכנן → בצע (ללא שאלות בינהם)
- בסיום: עדכן `Project_Structure_System_Architecture.txt` אם המבנה השתנה
- בסיום: עדכן `task_log.csv`

### כלי בדיקה
- Backend: `docker-compose exec backend bash -c "cd /app && PYTHONPATH=/app python -m alembic upgrade head"`
- Frontend: `docker-compose build --no-cache frontend && docker-compose up -d frontend`
- DB: `docker-compose exec postgres psql -U medscribe -d medscribe`
- Tests: `pytest tests/ -v` | `dart analyze`

## parent-website QA Tool (Next.js 15)

### הפעלת QA
```bash
export LD_LIBRARY_PATH="/tmp/playwright_libs/usr/lib/x86_64-linux-gnu:/tmp/playwright_libs/usr/lib:$LD_LIBRARY_PATH"
cd /mnt/c/medscribe-ai-project/parent-website/qa-tool
node qa-runner.js --phase=N --feedback --url=http://localhost:3001
```
- LD_LIBRARY_PATH כבר מוגדר ב-qa-runner.js (שורה 118) — background tasks עובדים גם כן
- **חובה להריץ פאזות בסדר** (1→5) כי Next.js מקמפל דפים on-demand

### בעיית Cold-Start (חשוב!)
Next.js 15 מקמפל דפים רק בגישה ראשונה. לאחר הפעלת שרת חדש:
- background tasks שרצים לפני warm-up יכשלו עם 404 / element not found
- **פתרון ידני:** warm-up לפני QA:
```bash
for path in / /articles /experts /forum /login /register /product /about-medscribe /privacy /terms; do
  curl -s -o /dev/null http://localhost:3001$path; done
```
- **פתרון קבוע (טרם מומש):** להוסיף warm-up loop בתוך `qa-runner.js` לפני `runPhase()` — פונקציה שעוברת על כל הנתיבים ידועים ומכה בהם ב-curl/http.get לפני שמריצים playwright

### WSL2 File Watcher
- Next.js dev על `/mnt/c/` (Windows FS) לא מזהה שינויי קבצים דרך inotify
- CSS/קבצים סטטיים: שינויים לא נלקחים → **פתרון: שנה JSX inline style במקום CSS**
- **כדי לאחד שינויים:** kill server PID + restart: `ss -tlnp | grep 3001 | grep -oP 'pid=\K[0-9]+'` → `kill -9 <PID>`
- **פתרון קבוע (טרם מומש):** הוסף ל-`.env.local` של parent-website:
  ```
  CHOKIDAR_USEPOLLING=true
  CHOKIDAR_INTERVAL=1000
  ```

### Background Tasks — Wrapper Script
- כל background task רץ ללא ה-environment של הסשן הנוכחי
- LD_LIBRARY_PATH כבר מוגדר בתוך qa-runner.js (שורה 118) — זה נפתר
- **פתרון נוסף (טרם מומש):** wrapper script לנוחות:
```bash
# /mnt/c/medscribe-ai-project/parent-website/qa-tool/qa-run.sh
#!/bin/bash
export LD_LIBRARY_PATH="/tmp/playwright_libs/usr/lib/x86_64-linux-gnu:/tmp/playwright_libs/usr/lib:$LD_LIBRARY_PATH"
cd /mnt/c/medscribe-ai-project/parent-website/qa-tool
node qa-runner.js "$@"
```

### בעיות Playwright ידועות
- `locator('h1, h2').toBeVisible()` כשיש כמה תוצאות → השתמש ב-`.first()`
- `localStorage.clear()` לפני `goto()` → SecurityError — תמיד `navigate` ראשון ואז try/catch
- CSS Grid: `1fr` = `minmax(auto,1fr)` → blowout. תיקון: `minWidth:0` inline או `minmax(0,1fr)`

### מצב נוכחי parent-website
- 61/61 טסטים עוברים (5 פאזות, 100%)
- דפים קיימים: /, /articles, /experts, /forum, /login, /register, /profile, /product, /about-medscribe, /about, /privacy, /terms
- /product = MedScribe Dashboard מלא (patient-list, stat-card, record-button, transcript-section, summary-section)
- robots.txt + sitemap.xml קיימים ב-public/
- openGraph metadata על / ו-/about-medscribe
