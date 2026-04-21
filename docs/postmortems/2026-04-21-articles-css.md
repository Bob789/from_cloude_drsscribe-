# Postmortem: articles page broken on production
**Date:** 2026-04-21  
**Severity:** High — visible UX regression on drsscribe.com/articles  
**Status:** Fixed

---

## What happened

`drsscribe.com/articles` showed broken tab buttons and incorrect responsive layout.  
`localhost:3001/articles` looked correct.

---

## Root causes

### Bug 1 — `.tabs` vs `.tab` selector split

Button styles were applied to the **container div** instead of **individual buttons**:

```css
/* ❌ Was: styling the wrapper, not the buttons */
.tabs {
  display: flex;
  border: none;       /* has no effect on a div */
  padding: 8px 14px;  /* pads the wrapper, not buttons */
  cursor: pointer;
}

/* ✅ Fixed: split into container + item */
.tabs { display: flex; gap: 4px; }
.tab  { border: none; padding: 8px 14px; cursor: pointer; }
```

**Effect:** Tab buttons had default browser styling (grey box with border).

---

### Bug 2 — Missing closing brace in `@media (max-width: 1200px)`

A `}` was missing after the `.card` block, nesting a selector inside a property list
and leaving a declaration orphaned outside any rule:

```css
/* ❌ Was: */
@media (max-width: 1200px) {
  .card {
    padding: 16px;
  .hero {               /* selector treated as property — ignored */
    padding-bottom: 42px;
  }
  }
}
    padding-top: 26px;  /* orphaned — outside every block */

/* ✅ Fixed: */
@media (max-width: 1200px) {
  .card  { padding: 16px; }
  .hero  { padding-bottom: 42px; }
  .page-bg { padding-top: 26px; }
}
```

**Effect:** On screens ≤ 1200px `.page-bg` lost top padding, `.hero` lost bottom padding.

---

## Why localhost looked fine

Browsers silently discard orphaned declarations and malformed nested selectors.  
The gap between environments was that production had an older build where the CSS
damage compounded with the tab styling bug.

---

## Fix

| File | Change |
|------|--------|
| `app/articles/article-theme.css` | Split `.tabs`→`.tab`, close brace, move orphaned `padding-top` |

---

## Prevention

Three layers added:

### 1. `npm run validate-css` (manual)
```bash
cd parent-website && npm run validate-css
```

### 2. `prebuild` hook (automatic)
`package.json` runs `validate-css` before every `npm run build` / Docker build.  
A broken CSS file **blocks the build** before it reaches the server.

### 3. Pre-commit git hook (automatic)
`.githooks/pre-commit` runs validation whenever a `.css` file is staged.  
Activate once per clone:
```bash
git config core.hooksPath .githooks
```

---

## What the validator catches

| Check | Catches |
|-------|---------|
| PostCSS parse | Hard syntax errors |
| Brace-depth line scan | Orphaned declarations outside any selector |
| Selector-pair convention | `.tabs` exists but `.tab` base styles missing |
