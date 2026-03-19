---
description: "Use when working with Docker, docker-compose, nginx, deployment, environment variables, or infrastructure configuration."
applyTo: ["docker-compose.yml", "docker-compose.prod.yml", "nginx/**", "frontend/nginx.conf", "frontend/Dockerfile", "backend/Dockerfile", ".env*"]
---
# Infrastructure Rules

## Docker Compose
- Dev: `docker-compose.yml` — builds frontend in debug mode
- Prod: `docker-compose.prod.yml` — release mode, with SSL
- Frontend serves on port 3000 (mapped to container port 80)
- Backend on port 8000

## Nginx (frontend/nginx.conf)
- Proxies `/api/` to `backend:8000`
- Proxies `/ws/` to `backend:8000` (WebSocket)
- SPA fallback: `try_files $uri $uri/ /index.html`
- Security headers:
  - `Cross-Origin-Opener-Policy: same-origin-allow-popups` (required for Google Sign-In)
  - `Referrer-Policy: no-referrer` (prevents Google CDN 429 errors)

## Environment
- `.env` is gitignored — never commit it
- `ENV_MODE=dev` for local development (disables strict password rules)
- `GOOGLE_REDIRECT_URI` must match the port where frontend runs

## Common Pitfalls
- MinIO credentials in docker-compose must match `.env` (`S3_ACCESS_KEY`, `S3_SECRET_KEY`)
- Redis password: set `--requirepass` in docker-compose AND `REDIS_PASSWORD` in `.env`
- After changing `.env`: restart affected containers (`docker-compose up -d`)
- `version:` attribute in docker-compose.yml is obsolete — ignore the warning
