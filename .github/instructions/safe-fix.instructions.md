---
description: "Fix a bug without creating new bugs. Use when fixing errors, crashes, or unexpected behavior. Enforces a professional fix process."
---

# Safe Bug Fix Protocol

Fix bugs professionally — never fix one thing and break another.

## Before writing any code:

### 0. Check incident log FIRST
Read `/opt/drscribe/.incidents.md` — check if this bug or a similar pattern has occurred before. If yes, apply the known fix and skip to step 4.

### 1. Reproduce and understand
- Read the relevant code completely (not just the error line)
- Understand the data flow: where does the input come from? Where does the output go?
- Check: is this the only place this pattern exists? (search for similar code)
- Identify: who calls this code? What depends on it?

### 2. Root cause analysis
Answer these before fixing:
- **What** is the actual bug? (not the symptom)
- **Why** does it happen? (root cause, not surface)
- **When** was it introduced? (git blame if needed)
- **Where** else might the same pattern exist?

### 3. Impact assessment
- List every file/function that will be affected
- Check: will this change break any existing behavior?
- Check: are there other callers of the changed function?
- Check: does this affect the database schema?
- Check: does this affect the API contract (request/response shape)?

## Writing the fix:

### 4. Minimal change principle
- Change ONLY what needs to change to fix the bug
- Do NOT refactor surrounding code in the same change
- Do NOT add features alongside the fix
- Do NOT "improve" code you didn't need to touch

### 5. Defensive coding
- Add a check for the specific edge case that caused the bug
- Use `.first()` instead of `.scalar_one_or_none()` when duplicates are possible
- Use `try/except` only when you handle the specific exception meaningfully
- Never catch bare `except:` — always catch specific exceptions
- Log the error server-side with context (user_id, entity_id, action)
- Return a safe error code to the client (ERR-XXXX), never internal details

### 6. Verify the fix
After making the change:
- Re-read the modified code in context (not just the diff)
- Trace the data flow through the fixed code manually
- Ask: "What happens if this input is None? Empty? Duplicate? Very large?"
- Check that error responses use error codes from `backend/app/error_codes.py`

## After the fix:

### 7. Check for the same pattern elsewhere
```
# Search for the same dangerous pattern in the entire codebase
grep -rn "the_dangerous_pattern" backend/app/
```
If found elsewhere, fix those too.

### 8. Log the incident
If this is a NEW bug (not in the incident log), append it to `docs/troubleshooting.md` with this format:
```
## INC-XXX | YYYY-MM | Area | Short description
**Symptom:** What the user saw
**Root Cause:** Why it happened (be specific — this is what helps detect recurrence)
**Detection Method:** How to detect if this bug recurs (specific patterns to grep for, symptoms to watch)
**Fix:** What was changed (files + description)
**Files Changed:** list of files
**Regression Test:** test name + file path
```

### 9. Write regression tests
**MANDATORY** — every bug fix MUST include at least one test that:
- Reproduces the exact scenario that caused the bug
- Verifies the fix works (positive case)
- Verifies the old broken behavior doesn't return
- Place tests in `backend/tests/` with descriptive names
- Tests should be runnable without Docker (use mocks/fixtures)

### 10. Deploy safely
- Build and restart only the affected service
- Check logs immediately after deploy
- Verify the specific endpoint/feature that was broken now works
- Run the new regression tests to confirm they pass
