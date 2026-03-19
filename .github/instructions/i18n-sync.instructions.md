---
description: "Use when adding, removing, or modifying translation keys. Validates all 8 language files are in sync. Use after adding UI text, before deploy, or when i18n errors appear."
---
# i18n Translation Sync

The project uses easy_localization with 8 language files in `frontend/assets/translations/`.
Languages: he, en, de, es, fr, pt, ko, it.

## When to run this check
- After adding any new `.tr()` call in Flutter code
- After adding/removing a translation key
- Before deploying frontend
- When seeing "Missing translation" errors

## Sync procedure

### 1. Find missing keys
Compare all translation files against Hebrew (the primary language):
```bash
# In the project root, compare keys across all language files
cd frontend/assets/translations
python3 -c "
import json, sys
with open('he.json','r') as f: he = set(json.load(f).keys())
for lang in ['en','de','es','fr','pt','ko','it']:
    with open(f'{lang}.json','r') as f: other = set(json.load(f).keys())
    missing = he - other
    extra = other - he
    if missing: print(f'{lang}.json MISSING: {missing}')
    if extra: print(f'{lang}.json EXTRA: {extra}')
    if not missing and not extra: print(f'{lang}.json ✓ OK')
"
```

### 2. Find unused keys in code
```bash
# Search for .tr() calls and extract keys
grep -rohP "'\K[^']+(?='\.tr\(\))" frontend/lib/ | sort -u > /tmp/used_keys.txt
# Compare with he.json keys  
python3 -c "
import json
with open('frontend/assets/translations/he.json') as f:
    defined = set(json.load(f).keys())
with open('/tmp/used_keys.txt') as f:
    used = set(line.strip() for line in f if line.strip())
unused = defined - used
if unused: print(f'Possibly unused keys: {unused}')
else: print('All keys appear to be used')
"
```

### 3. Add missing keys
When adding a new key:
1. Add to `he.json` first (Hebrew is the source of truth)
2. Add the same key to ALL other 7 files with translated value
3. If you don't have a translation — use the English text as placeholder with a `[TODO]` prefix

### 4. Validate JSON syntax
```bash
for f in frontend/assets/translations/*.json; do
  python3 -c "import json; json.load(open('$f'))" 2>&1 && echo "$f ✓" || echo "$f INVALID JSON"
done
```

## i18n Code Rules
- `import 'package:easy_localization/easy_localization.dart' hide TextDirection;` — ALWAYS hide TextDirection
- `Locale('he')` not `Locale('he', 'IL')` — locale without country code
- `.tr()` breaks `const` — remove const from parent widget
- Nested keys use dot notation: `'settings.profile'.tr()`
- Keys with parameters: `'welcome.message'.tr(args: [userName])`
