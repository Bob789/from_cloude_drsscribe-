---
name: secure-audit
description: "Security audit for the DoctorScribe medical application. Use before releases, after adding auth-related code, or periodically."
---

# Security Audit — Medical SaaS

This is a medical application handling PHI (Protected Health Information). Security is critical.

## Audit Checklist

### 1. Authentication & Authorization
```bash
# Find endpoints without auth
grep -rn "async def " backend/app/routers/ | grep -v "Depends(get_current_user)\|Depends(require_admin)\|Depends(require_doctor)"
```
Every endpoint (except /health, /ready, /auth/google, /auth/login) MUST have auth.

### 2. Information Leakage
```bash
# Find raw exception forwarding
grep -rn "str(e)\|str(exc)\|traceback\|__traceback__" backend/app/routers/ backend/app/services/
# Find potential data exposure
grep -rn "detail=.*str(" backend/app/
```
Verify: error responses only contain `error_id` + `code` + Hebrew message. Never stack traces, SQL, or file paths.

### 3. SQL Injection
```bash
# Find raw SQL or string formatting in queries
grep -rn "f\".*SELECT\|f\".*INSERT\|f\".*UPDATE\|f\".*DELETE\|\.text(" backend/app/
# Find .filter with string interpolation
grep -rn "\.where(.*f\"" backend/app/
```
All queries must use SQLAlchemy ORM or parameterized queries. Never f-strings in SQL.

### 4. Input Validation
Check all Body() and Query() parameters:
- Do they have type annotations?
- Are string lengths bounded?
- Are numeric ranges validated?
- Are UUIDs validated before DB queries?

### 5. File Upload Security
```bash
grep -rn "UploadFile\|upload\|file" backend/app/routers/
```
Check: file type validation, size limits (nginx: 500MB max), filename sanitization, storage path doesn't allow traversal.

### 6. JWT Token Security
- Tokens expire (check exp claim)
- Refresh tokens are single-use (check blacklist)
- Secret key is strong (not default "changeme")
- Token in header only (not URL query param)

### 7. CORS & Headers
```bash
grep -rn "allow_origins\|CORS\|cors" backend/app/
```
Origins should be explicit (not `*`), credentials allowed only for known origins.

### 8. Rate Limiting
Verify rate limits on sensitive endpoints:
- `/api/auth/*` — 10/min (brute force protection)
- `/api/*` — 100/min (general abuse)
- File uploads — lower limit

### 9. Secrets in Code
```bash
# Check for hardcoded secrets
grep -rn "password\|secret\|api_key\|token" backend/app/ --include="*.py" | grep -v "\.pyc\|test_\|#\|import\|Depends\|Bearer\|get_current"
```
All secrets must come from environment variables, never hardcoded.

### 10. Medical Data (PHI)
- Audio recordings encrypted at rest (AES)
- PII masked before LLM processing
- Audit log tracks all data access
- No patient data in error logs

## Output
Present findings as:
| # | Severity | Finding | File:Line | Remediation |
|---|----------|---------|-----------|-------------|
| 1 | CRITICAL | ... | ... | ... |
