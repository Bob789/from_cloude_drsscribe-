---
description: "Use when working on backend Python files: FastAPI routers, services, models, schemas, middleware, utils, Alembic migrations, or tests."
applyTo: "backend/**"
---
# Backend Development Rules

## Structure
- Routers: `app/routers/` — thin, delegate to services
- Services: `app/services/` — business logic
- Models: `app/models/` — SQLAlchemy ORM, must be imported in `app/models/__init__.py` for Alembic
- Schemas: `app/schemas/` — Pydantic request/response
- Middleware: `app/middleware/` — auth, audit, rate limit, metrics

## Database
- Async SQLAlchemy with `AsyncSession`
- Every new model MUST be imported in `app/models/__init__.py` — otherwise Alembic won't detect it
- Migrations: `alembic revision --autogenerate -m "description"` then `alembic upgrade head`
- Always filter queries by `doctor_id` / `created_by` for data isolation

## API Patterns
- All endpoints under `/api/` prefix
- Auth via JWT in `Authorization: Bearer` header
- Use `current_user` dependency for authenticated routes
- Return structured errors via `AppError` / `AppException`

## Testing
- pytest with async support
- Run: `cd backend && pytest tests/ -v`

## Logging
- Use `structlog` — never `print()`
- Never log tokens, passwords, or patient PII

## Common Pitfalls
- Missing model import in `__init__.py` → Alembic migration creates empty upgrade
- `PYTHONPATH=/app` required when running alembic inside Docker
- Redis password must match between `.env` and `docker-compose.yml`
