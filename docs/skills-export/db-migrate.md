---
name: db-migrate
description: "Safely add/modify database tables or columns in production. Use when adding new models, columns, indexes, or constraints."
---

# Database Migration (Safe Production Changes)

The project uses PostgreSQL 16 + SQLAlchemy async + Alembic.
Database: `drscribe`, User: `drscribe`, Container: `drscribe-postgres`.

## Procedure

### Step 1: Plan the change
Before touching the DB, answer:
- Is this additive (new column/table) or destructive (drop/rename)?
- Does the column need a DEFAULT for existing rows?
- Will existing queries break?
- Does the backend code need to change simultaneously?

### Step 2: Apply DDL via psql (for immediate changes)
```bash
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U drscribe -d drscribe -c "ALTER TABLE ... ;"
```

**Safe patterns:**
```sql
-- Add nullable column (safe, no lock)
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(50);

-- Add column with default (safe in PG 11+)
ALTER TABLE visits ADD COLUMN IF NOT EXISTS priority INT DEFAULT 0 NOT NULL;

-- Add index concurrently (no lock)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visits_date ON visits(visit_date);

-- New table (safe)
CREATE TABLE IF NOT EXISTS ... ;
```

**DANGEROUS patterns — ask user first:**
```sql
-- Column rename (breaks all queries using old name)
ALTER TABLE x RENAME COLUMN old TO new;

-- Drop column (data loss)
ALTER TABLE x DROP COLUMN y;

-- NOT NULL on existing column (fails if NULLs exist)
ALTER TABLE x ALTER COLUMN y SET NOT NULL;
```

### Step 3: Update SQLAlchemy model
Edit the model in `backend/app/models/` to match the DB change.
The model MUST match the actual DB state.

### Step 4: Create Alembic migration (for version tracking)
```bash
docker compose -f docker-compose.prod.yml exec -T backend \
  alembic revision --autogenerate -m "description"
```
Review the generated migration file. Alembic version files are in `backend/alembic/versions/`.

### Step 5: Rebuild backend
The backend must be rebuilt to pick up model changes:
```bash
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml up -d backend celery-worker
```

### Step 6: Verify
```bash
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U drscribe -d drscribe -c "\d tablename"
```

## Rules
- ALWAYS use `IF NOT EXISTS` / `IF EXISTS` — idempotent operations
- ALWAYS add columns as nullable first, add NOT NULL constraint later after backfill
- NEVER drop tables or columns without explicit user approval
- NEVER run ALTER TABLE on large tables without checking row count first
- Keep model file and DB schema in sync — mismatches cause runtime crashes
- Test with a SELECT before and after to verify no regressions
