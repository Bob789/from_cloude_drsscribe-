---
name: add-feature
description: "Add a new feature to the product following the project's architecture. Use when adding new functionality, endpoints, screens, or capabilities."
---

# Add Feature — Professional Checklist

Add new functionality following the project's architecture patterns.

## Architecture awareness

### Backend (FastAPI + SQLAlchemy async)
- **Models** → `backend/app/models/` (SQLAlchemy mapped_column, UUID PKs)
- **Routers** → `backend/app/routers/` (APIRouter, Depends for auth/db)
- **Services** → `backend/app/services/` (business logic, never in routers)
- **Register router** → `backend/app/main.py` (import + include_router)
- **Auth patterns**: `get_current_user` for any user, `require_admin` for admin only
- **DB session**: always `db: AsyncSession = Depends(get_db)`
- **Error handling**: raise `AppError` subclasses with ERR-XXXX codes

### Frontend (Flutter + Riverpod)
- **Screens** → `frontend/lib/screens/`
- **Widgets** → `frontend/lib/widgets/`
- **Providers** → `frontend/lib/providers/` (Riverpod for state)
- **API calls** → `ApiClient().dio` with relative paths (`/endpoint`)
- **Routing** → `go_router` in the router config
- **i18n** → translation keys in `frontend/assets/translations/*.json`
- **Theme** → use `AppColors` and `MedScribeThemeExtension`

### Parent Website (Next.js)
- **Pages** → `parent-website/app/*/page.tsx` (App Router)
- **Components** → `parent-website/components/`
- **API calls** → fetch from `${API}/endpoint` with Bearer token
- **Styling** → inline styles matching existing dark theme

## Step-by-step process

### 1. Plan the data model
- What new tables/columns are needed?
- What are the relationships to existing models?
- Apply db-migrate skill for safe schema changes

### 2. Backend first
- Create model → create router → register in main.py
- Follow existing patterns: async/await, proper error codes, pagination
- Protect endpoints: every endpoint needs auth (`get_current_user` or `require_admin`)
- Never return internal details in error responses

### 3. Frontend second
- Build the UI using existing theme and widgets
- Handle loading states, error states, empty states
- Use Hebrew text for user-facing strings
- Test both compact and expanded sidebar modes

### 4. Integration checklist
Before deploying any new feature, verify:
- [ ] New endpoint has proper auth (not public by default)
- [ ] Error responses use ERR-XXXX codes
- [ ] No sensitive data in API responses (passwords, tokens, internal IDs)
- [ ] Nullable columns have proper defaults
- [ ] Frontend handles API errors gracefully (shows message, doesn't crash)
- [ ] Hebrew text reads correctly (RTL layout)
- [ ] Works in both mobile and desktop viewport

### 5. Deploy
Use the deploy skill to build and push the affected services.

## Anti-patterns to avoid
- Don't add global state when local state suffices
- Don't create a new service for a single function — put it in an existing relevant service
- Don't duplicate API calls — check if an existing endpoint already returns what you need
- Don't hardcode URLs — use environment variables and config
- Don't add optional dependencies without checking bundle size impact
