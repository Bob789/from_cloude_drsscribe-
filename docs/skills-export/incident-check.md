---
name: incident-check
description: "Automatically triggered before any bug fix. Reads the incident log to avoid repeating past mistakes."
user-invocable: false
---

# Incident Check (Auto-trigger)

Before fixing ANY bug or error, read `/opt/drscribe/.incidents.md` and check:

1. Has this exact issue happened before? → Apply the known fix directly.
2. Is the symptom similar to a past incident? → Check if the root cause is the same pattern.
3. Does the fix involve a pattern from the "Lesson" of any past incident? → Avoid the anti-pattern.

After fixing a NEW bug (one not in the log), append a new entry:
```
## INC-XXX | YYYY-MM | Area | Short description
**Symptom:** What the user saw
**Root cause:** Why it happened (be specific)
**Fix:** What was changed
**Lesson:** What to avoid in the future
```
