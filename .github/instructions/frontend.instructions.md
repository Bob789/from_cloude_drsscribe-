---
description: "Use when working on frontend Flutter/Dart files: screens, widgets, providers, services, models, utils, or translations."
applyTo: "frontend/**"
---
# Frontend Development Rules

## Structure
- Screens: `lib/screens/` — full page views
- Widgets: `lib/widgets/` — reusable UI components
- Providers: `lib/providers/` — Riverpod state management
- Services: `lib/services/` — API client, auth, upload
- Models: `lib/models/` — data classes
- Utils: `lib/utils/` — theme, router, constants

## State Management
- Riverpod (flutter_riverpod) — no setState for async data
- Pattern: Screen → Provider → ApiService → Backend API

## API Client
- Dio with interceptors for auth token injection and refresh
- Base URL: `/api` (proxied by Nginx to backend:8000)

## i18n — CRITICAL RULES
- Every `import 'package:easy_localization/easy_localization.dart'` MUST add `hide TextDirection` (conflicts with intl)
- Locale without country code: `Locale('he')` not `Locale('he', 'IL')`
- `.tr()` breaks `const` — remove `const` from parent widget, use `static final` instead of `static const`
- 8 translation files: `assets/translations/{he,en,de,es,fr,pt,ko,it}.json`
- RTL/LTR: determined in main.dart by `context.locale.languageCode == 'he'`

## Google Auth
- Uses `google_sign_in` package
- GSI logger suppressed in `web/index.html` to prevent token leakage
- Profile images: do NOT add `headers` to `Image.network` — causes CORS errors. Referrer-Policy is set in nginx.conf

## Image Loading
- Never use `headers` parameter in `Image.network` for external URLs (Google CDN) — triggers XHR/CORS instead of `<img>` tag
- Always provide `errorBuilder` fallback for network images

## Building
- `docker-compose build frontend` — uses Dockerfile multi-stage (Flutter build → Nginx serve)
- Changes to `web/index.html` or `nginx.conf` require full rebuild (not hot reload)
