---
name: deploy
description: "Build and deploy specific services to production. Use when the user says deploy, build, push, or after code changes that need to go live."
---

# Deploy to Production

Deploy one or more services to production on the DoctorScribe server.

## Services Map

| Service | Build command | Container |
|---------|--------------|-----------|
| backend | `docker compose -f docker-compose.prod.yml build backend` | drscribe-backend |
| frontend | `docker compose -f docker-compose.prod.yml build frontend` | drscribe-frontend |
| parent-website | `docker compose -f docker-compose.prod.yml build parent-website` | drscribe-parent |
| celery | `docker compose -f docker-compose.prod.yml build celery-worker` | drscribe-celery |

## Deploy Procedure

Follow this EXACT order. Do not skip steps.

### 1. Determine what changed
- If backend Python files changed → build `backend` + restart `celery-worker`
- If Flutter files changed → build `frontend`
- If Next.js files changed → build `parent-website`
- If docker-compose.prod.yml changed → rebuild all affected
- If nginx.conf changed → restart `nginx`

### 2. Build
```bash
docker compose -f docker-compose.prod.yml build <service> 2>&1 | tail -5
```
Wait for "Built" confirmation. If build fails, FIX THE ERROR before proceeding.

### 3. Deploy
```bash
docker compose -f docker-compose.prod.yml up -d <service> 2>&1
```

### 4. Verify
```bash
# Check container is running
docker compose -f docker-compose.prod.yml ps <service>

# Check logs for startup errors
docker compose -f docker-compose.prod.yml logs <service> --tail=5

# For backend: verify health endpoint
curl -s http://localhost:8000/api/health | head -1
```

### 5. Smoke test
- Backend: verify the changed endpoint works
- Frontend: confirm the Flutter app loads
- Parent-website: confirm drsscribe.com loads

## Rules
- NEVER use `--no-build` after code changes — the old image won't have new files
- NEVER restart postgres or redis unless explicitly asked — data loss risk
- If backend changed, also restart celery-worker (it shares the same code)
- Always check logs AFTER restart — a running container doesn't mean healthy
- If deployment fails, report the error and suggest rollback
