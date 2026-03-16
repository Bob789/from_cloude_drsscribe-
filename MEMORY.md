# DoctorScribe AI — Production Server Guidelines

## Project
- Production server: `/opt/drscribe` (Google Cloud VM: 34.140.74.189)
- Domains: `drsscribe.com` (parent website), `app.drsscribe.com` (Flutter app)
- Incident log: `/opt/drscribe/.incidents.md` — READ BEFORE FIXING ANY BUG

## Work Style
- All permissions pre-approved — files, builds, deploys, DB changes
- Take reasonable decisions autonomously — don't ask for approval on every step
- Only pause for REAL risk: data loss, breaking production, security issues
- Report final result, not every intermediate step

## Skills Available
- `/deploy` — Build and deploy services
- `/db-migrate` — Safe database schema changes
- `/check-prod` — Full production health check
- `/safe-fix` — Fix bugs without creating new ones (reads incident log)
- `/add-feature` — Add features following project architecture
- `/secure-audit` — Security audit for medical SaaS
- `/perf-check` — Performance diagnostics
- `/backup-restore` — Database backup and restore

## Key Commands
- Build: `docker compose -f docker-compose.prod.yml build <service>`
- Deploy: `docker compose -f docker-compose.prod.yml up -d <service>`
- Logs: `docker compose -f docker-compose.prod.yml logs <service> --tail=20`
- DB: `docker compose -f docker-compose.prod.yml exec -T postgres psql -U drscribe -d drscribe`
- Redis: `docker compose -f docker-compose.prod.yml exec -T redis redis-cli`

## Error Handling
- All errors use ERR-XXXX codes (see `backend/app/error_codes.py`)
- Client sees: `{error_id, code, message}` — never internals
- Server logs: full details with error_id for correlation

## Critical Rules
- NEVER use `--no-build` after code changes
- NEVER restart postgres/redis without explicit request
- ALWAYS use `IF NOT EXISTS` for DB schema changes
- ALWAYS read `.incidents.md` before fixing bugs
- ALWAYS check for the same anti-pattern across the codebase after fixing a bug
