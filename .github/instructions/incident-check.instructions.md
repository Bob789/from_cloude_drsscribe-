---
description: "Automatically triggered before any bug fix. Reads the incident log to avoid repeating past mistakes."
---

# Incident Check (Auto-trigger)

Before fixing ANY bug or error, read `docs/troubleshooting.md` and check:

1. Has this exact issue happened before? → Apply the known fix directly.
2. Is the symptom similar to a past incident? → Check the **Detection Method** section — it tells you exactly what to grep for.
3. Does the fix involve a pattern from a past incident? → Avoid the anti-pattern.

After fixing a NEW bug (one not in the log):

### Step 1: Document in `docs/troubleshooting.md`
```
## INC-XXX | YYYY-MM | Area | Short description
**Symptom:** What the user saw
**Root Cause:** Why it happened (be specific)
**Detection Method:** How to detect if this bug recurs — specific patterns, grep commands, symptoms
**Fix:** What was changed
**Files Changed:** list of modified files
**Regression Test:** test function name + file path
```

### Step 2: Write regression tests (MANDATORY)
- Create test(s) in `backend/tests/` that reproduce the exact bug scenario
- Test must fail if the bug is reintroduced
- Test must pass with the current fix
- Use mocks/fixtures to avoid external dependencies (DB, Docker, APIs)

### Step 3: Update `docs/troubleshooting.md` lessons-learned section in `lessons-learned.instructions.md` if the bug reveals a new pattern
