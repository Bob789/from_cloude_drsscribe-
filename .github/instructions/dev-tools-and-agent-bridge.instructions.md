---
description: "Dev Tools, Agent Bridge, and collaborative local↔cloud workflow. Read at the start of every session — both local (Copilot) and cloud agents."
---

# Dev Tools & Agent Bridge — Collaborative AI Protocol

> **Every agent (local or cloud) MUST read this file at the start of each session.**
> This is the shared operating manual for how the two agents collaborate, validate work, and avoid repeating mistakes.

---

## 1. The Two-Agent System

This project runs two AI agents simultaneously:

| Agent | Environment | Strengths | Limitations |
|-------|-------------|-----------|-------------|
| **Copilot (local)** | Developer's PC (`c:\Doctor-Scribe`) | File editing, git, Docker, VS Code | No browser, limited runtime visibility |
| **Cloud Agent** | GCP `drscribe-prod` | Running services, live DB, logs | No local files, no git access |

**The key insight:** Neither agent can do everything alone. Together they cover each other's blind spots.
The Agent Bridge is the communication channel between them.

---

## 2. Dev Tools Service

The `dev-tools` service runs at:
- **Local:** `http://localhost:8090` (requires `X-Dev-Token: dev-token-change-me`)
- **Production:** `https://drsscribe.com/dev-tools/?token=dev-token-change-me`

### 2a. Screenshot Tool — Visual Validation

Use this to verify **design, layout, and content** are correct before deploying.
Never assume a page looks right — take a screenshot.

```powershell
# Screenshot any page
Invoke-WebRequest -UseBasicParsing -Method Post `
  -Uri 'http://localhost:8090/capture/screenshot' `
  -Headers @{ 'X-Dev-Token'='dev-token-change-me'; 'Content-Type'='application/json' } `
  -Body '{"url":"http://localhost:3001/","wait_ms":3000,"locale":"he-IL","full_page":true}' `
  -OutFile 'docs/screenshot.png'
```

**When to use:**
- After any CSS/layout change
- After adding new UI components
- Before marking a frontend task as complete
- When the user reports a visual bug

### 2b. Flatten Tool — Static HTML for Content & Style Debugging

Converts a live page to a flat static HTML file with all CSS inlined.
Use this to debug **content issues, missing text, broken styles, wrong language**.

```powershell
# Flatten a page to static HTML
$body = '{"url":"http://localhost:3001/articles","wait_ms":5000,"locale":"he-IL"}'
Invoke-WebRequest -UseBasicParsing -Method Post `
  -Uri 'http://localhost:8090/capture/flatten' `
  -Headers @{ 'X-Dev-Token'='dev-token-change-me'; 'Content-Type'='application/json' } `
  -Body $body | Select-Object -ExpandProperty Content | Out-File 'docs/page-debug.html'
```

Then search the output:
```powershell
# Check specific elements
Select-String -Path 'docs/page-debug.html' -Pattern "nav|hero|h1|error" | Select-Object -First 20
```

**When to use:**
- Page renders but content looks wrong
- Checking RTL/LTR rendering
- Verifying i18n translations appear correctly
- Debugging CSS that doesn't match design

### 2c. Framework Validation — Dynamic Test Runner

At the end of every implementation task, run the validation framework:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify_task.ps1 `
  -Framework pytest `
  -Target backend/tests/ `
  -Services backend
```

**Rule:** Never mark a task as DONE if framework validation failed.

**Framework selection by task type:**
| Task type | Framework |
|-----------|-----------|
| Backend Python | `pytest` |
| Frontend Dart | `dart analyze` + `flutter test` |
| API endpoints | `pytest` (integration tests) |
| Visual/UI | Dev Tools screenshot |
| Infrastructure | `docker-compose ps` + health checks |

---

## 3. Agent Bridge — Local ↔ Cloud Communication

The Agent Bridge is a **shared message queue** (SQLite in dev-tools container).
Both agents read and write to it. Think of it as a shared whiteboard.

### Bridge Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/agent/messages` | Read all pending messages |
| `POST` | `/agent/messages` | Send a message |
| `DELETE` | `/agent/messages` | Clear all messages |
| `GET` | `/agent/status` | Check if bridge is enabled |
| `POST` | `/agent/status` | Enable/disable bridge |

All endpoints require header: `X-Dev-Token: dev-token-change-me`

### Reading Messages (Every Session Start — MANDATORY)

```python
# Cloud agent (Python/httpx)
import httpx
resp = httpx.get(
    "https://drsscribe.com/dev-tools/agent/messages",
    headers={"X-Dev-Token": "dev-token-change-me"}
)
messages = resp.json()
# Process any messages before doing anything else
```

```powershell
# Local agent (Copilot/PowerShell)
Invoke-WebRequest -Uri 'https://drsscribe.com/dev-tools/agent/messages' `
  -Headers @{ 'X-Dev-Token'='dev-token-change-me' } `
  -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Sending Messages

```python
# Cloud agent reporting an error to local agent
httpx.post(
    "https://drsscribe.com/dev-tools/agent/messages",
    headers={"X-Dev-Token": "dev-token-change-me"},
    json={"role": "cloud", "content": "Celery task failed: OpenAI timeout in summarize_visit(visit_id=42)"}
)

# Local agent sending a task/instruction to cloud agent
httpx.post(
    "https://drsscribe.com/dev-tools/agent/messages",
    headers={"X-Dev-Token": "dev-token-change-me"},
    json={"role": "local", "content": "Please run: docker logs drscribe-celery --tail=50 and report back"}
)
```

### Message Roles

| Role | Sender | Meaning |
|------|--------|---------|
| `cloud` | Cloud agent | Error report, log excerpt, status update |
| `local` | Copilot | Task instruction, question, fix to apply |
| `system` | Either | Important state change (deploy done, migration applied) |

### When to Use the Bridge

**Cloud → Local:** Report errors you can't fix alone (need code changes, git access)
**Local → Cloud:** Send instructions that need runtime execution (run migration, check logs, restart service)
**Both:** Coordinate before deploy — local validates locally, cloud validates on prod

---

## 4. Troubleshooting Protocol — Shared Knowledge Base

### Location
```
docs/troubleshooting/          ← shared via git (both agents read this)
├── README.md                  ← index of all issues
├── nginx_proxy_issues.md
├── article_images_disappearing.md
├── cpanel_devtools_503_502.md
├── local_setup_issues.md
└── security_fixes.md
```

### Rule: Before Fixing ANY Bug — Read the Troubleshooting Folder

```powershell
# Search for similar past issues
Select-String -Path 'docs/troubleshooting/*.md' -Pattern "nginx|proxy|500|401" | Select-Object -First 10
```

### Rule: After Fixing ANY Bug — Document It

Every bug fix MUST produce a new entry in the relevant troubleshooting file:

```markdown
## Bug: [Short title]
**Date:** YYYY-MM-DD
**Symptom:** What the user saw / what error appeared
**Root Cause:** Why it happened (technical explanation)
**Fix:** What was changed (files + code)
**Prevention:** How to avoid this in the future (code guard, validation, etc.)
**Regression Test:** `pytest tests/test_xxx.py::test_yyy` or describe the test
```

**Never close a bug without:**
1. Documenting in `docs/troubleshooting/`
2. Writing a regression test in `backend/tests/`
3. Adding a prevention note (code-level guard if possible)

### Rule: Ask the User Before Closing

After every bug fix, ask:
> "האם הבאג טופל בשלמות? האם הכל עובד כצפוי?"

Only after YES: document → write test → commit → push.

---

## 5. The Validation Checklist Before Deploy

Before pushing to GitHub and triggering cloud deploy, verify **all three layers**:

### Layer 1 — Functional (pytest)
```bash
cd backend && pytest tests/ -v --tb=short
```

### Layer 2 — Visual (Dev Tools screenshot)
```powershell
# Screenshot key pages: home, cpanel, articles
Invoke-WebRequest -UseBasicParsing -Method Post `
  -Uri 'http://localhost:8090/capture/screenshot' `
  -Headers @{ 'X-Dev-Token'='dev-token-change-me'; 'Content-Type'='application/json' } `
  -Body '{"url":"http://localhost:3001/cpanel","wait_ms":4000,"locale":"he-IL","full_page":true}' `
  -OutFile 'docs/pre-deploy-cpanel.png'
```
View the image. If anything looks wrong — fix before pushing.

### Layer 3 — Infrastructure
```bash
docker-compose ps          # all containers: Up
docker-compose logs --tail=10 backend nginx frontend  # no errors
```

**Only after all 3 layers pass → `git push origin main`**

---

## 6. CI/CD Flow: Local → GitHub → Cloud

```
Local (Copilot edits code)
  ↓
Dev Tools validation (screenshots + pytest)
  ↓
git push origin main
  ↓
GitHub Actions CI (automated tests)
  ↓  [if all pass]
Cloud auto-deploy OR manual:
  gcloud compute ssh drscribe-prod ... "git pull pc main && docker-compose build && up -d"
  ↓
Cloud Agent validates on prod (curl health checks, logs)
  ↓
Cloud Agent posts result to Agent Bridge
  ↓
Local agent reads bridge → confirms deploy success
```

**GitHub Actions trigger:** `.github/workflows/` — runs on every push to `main`

---

## 7. cpanel — Future Dev Tool

The admin panel at `https://drsscribe.com/cpanel` is a prime candidate for a dedicated developer tool.
Potential additions:
- Live service health dashboard
- One-click migration runner
- Real-time log viewer
- Agent Bridge messages panel (instead of visiting `/dev-tools/`)

When building this: same pattern as dev-tools — FastAPI service, token-gated, proxied by nginx.

---

## 8. Summary — The Collaborative Workflow

```
TASK ASSIGNED
    ↓
1. Read Agent Bridge messages (pending from cloud)
2. Read docs/troubleshooting/ for similar past issues  
3. Read docs/AI_SESSION_LOG.md (last session context)
    ↓
IMPLEMENT
    ↓
4. Run pytest (functional validation)
5. Take screenshot (visual validation)
6. Check docker-compose ps (infra validation)
    ↓
DEPLOY
    ↓
7. git push origin main
8. Cloud agent pulls + restarts service
9. Cloud agent posts health check result to Agent Bridge
10. Local agent reads bridge, confirms ✅
    ↓
CLOSE
    ↓
11. Ask user: "עובד כמצופה?"
12. Document in docs/troubleshooting/ if bug was fixed
13. Write regression test
14. Append to docs/AI_SESSION_LOG.md
```
