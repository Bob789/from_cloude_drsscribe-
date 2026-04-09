# MedScribe AI — Project Instructions

## כללי א'-ב' — חובה לכל סוכן AI שנכנס לפרויקט

### א. אחרי כל משימה שדורשת build — בצע build+deploy אוטומטית

**שירותים שדורשים build אחרי שינוי קוד:**

| שירות | פקודת build | הפעלה |
|-------|-------------|--------|
| `parent-website` | `docker-compose build --no-cache parent-website` | `docker-compose up -d parent-website` |
| `frontend` | `docker-compose build --no-cache frontend` | `docker-compose up -d frontend` |
| `backend` | `docker-compose build --no-cache backend` | `docker-compose up -d backend` |

**כלל:** כל שינוי ב-`parent-website/**`, `frontend/**`, או `backend/**` — מסיים תמיד ב:
```bash
docker-compose build --no-cache <service>
docker-compose up -d <service>
```
אל תחכה לאישור. בצע אוטומטית.

**הערה:** exit code 1 עם הודעת `version is obsolete` — זו **אזהרה בלבד**, לא שגיאה. הבנייה הצליחה אם מופיע `FINISHED`.

### ב. בדיקת תקינות אחרי build
אחרי כל build, בדוק:
```bash
docker-compose ps                        # כל הקונטיינרים Up
docker-compose logs --tail=20 <service>  # אין שגיאות
```

---

## FIRST — Mandatory Session Start
**Every session, before doing anything else, read these instruction files:**
1. `c:\Doctor-Scribe\.github\instructions\safe-fix.instructions.md` — bug fix protocol (including step 11: confirm with user → document → push to GitHub)
2. `c:\Doctor-Scribe\.github\instructions\lessons-learned.instructions.md` — known bugs and patterns to avoid
3. `c:\Doctor-Scribe\.github\instructions\backend.instructions.md` — backend conventions
4. `c:\Doctor-Scribe\.github\instructions\infrastructure.instructions.md` — Docker/env rules
5. Read the end of `docs/AI_SESSION_LOG.md` to pick up the context from previous chats!

## Mandatory Session Logging (Anti Data-Loss Protocol)
- Users computer may restart unexpectedly.
- At the end of EVERY task, or before writing "I am done", you MUST append a brief, clear summary of the current chat session (what was asked, the root cause found, the files changed, and the result) into `docs/AI_SESSION_LOG.md`.
- **CRITICAL:** DO NOT commit or push `docs/AI_SESSION_LOG.md` to GitHub. It must remain strictly local.

**Bug fix closure rule (from safe-fix step 11):**
After every bug fix, always ask the user:
> "האם הבאג טופל בשלמות? האם הכל עובד כצפוי?"
Only after user confirms YES:
- Document in `docs/troubleshooting.md`
- Write regression test in `backend/tests/`
- Commit and push to GitHub (only after successful build)

## Communication
- Hebrew for all communication, English for code and documentation
- Don't ask questions — make reasonable decisions and proceed
- Don't ask for approval between steps
- Show only the final result
- If there's a dependency conflict — ask the user

## Autonomy
- Work independently — complete the full task without waiting for approval
- Make reasonable decisions when information is missing
- Only consult the user when an action could DELETE files, DROP tables, or DESTROY data
- At the end of every task, provide a brief task report: what was done, what files changed, and any issues found
- Never ask "should I proceed?" — just do it
- If a step fails, try an alternative approach before reporting failure

## Project Structure
- **Backend**: Python 3.11+ / FastAPI at `backend/app/`
- **Frontend**: Flutter Web + Dart 3 at `frontend/lib/`
- **Infrastructure**: Docker Compose, Nginx, PostgreSQL, Redis, MinIO
- **Config**: `.env` (gitignored), `docker-compose.yml`

## Architecture
- SaaS model — browser-only access
- All logic on the server — Frontend is UI only
- Pipeline: Recording → STT (Whisper) → Summary (LLM) → Tags → DB
- Auth: Google OAuth → JWT
- Call chain (backend): Request → Middleware → Router → Service → DB
- Call chain (frontend): Screen → Provider (Riverpod) → ApiService (Dio) → API

## Key Technologies
| Layer | Stack |
|-------|-------|
| Backend | FastAPI, SQLAlchemy, Alembic, Celery, structlog, pytest |
| Frontend | Flutter Web, Riverpod, Dio, easy_localization, Material 3 |
| DB | PostgreSQL, Redis |
| Storage | MinIO/S3 |
| Infra | Docker Compose, Nginx |

## Token Optimization
- Don't read files that aren't relevant to the current task
- Use `grep_search` or `rg` for targeted searches — never scan whole directories
- Read only the relevant portion of large files (use line ranges)
- Write concise, clean code — no unnecessary comments
- Don't display unchanged code

## Dependency Changes
- Backend: update `requirements.txt`
- Frontend: update `pubspec.yaml`

## Docker Commands
```bash
# Build & deploy frontend
docker-compose build --no-cache frontend && docker-compose up -d frontend

# Run migrations
docker-compose exec backend bash -c "cd /app && PYTHONPATH=/app python -m alembic upgrade head"

# Access DB
docker-compose exec postgres psql -U medscribe -d medscribe
```

## Git
- `docs/` is gitignored (contains private documentation)
- `private/` is gitignored (secrets, deployment notes)
- Never commit `.env`, `client_secret.json`, `*.pem`, `*.key`
- `pubspec.lock` SHOULD be committed (pinned dependency versions)
- `.vscode/settings.json` is workspace-specific — OK to commit

## Security Rules
- Never log tokens, passwords, or PII
- All patient data is encrypted (AES-256)
- RBAC on every endpoint — check `doctor_id == current_user.id`
- Audit log for all mutating operations
