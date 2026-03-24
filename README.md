# Doctor Scribe

Medical visit documentation platform. Records physician-patient conversations, transcribes audio to text, generates structured clinical summaries, and organizes patient records — all from the browser.

Built for clinics that need fast, accurate documentation without paper or manual typing.

---

## What It Does

- **Record** — browser-based audio capture (MediaRecorder API), chunked upload, stored encrypted in S3
- **Transcribe** — automatic speech-to-text via OpenAI Whisper, multi-language support
- **Summarize** — LLM-generated structured summaries (complaint, findings, diagnosis, treatment plan)
- **Tag** — automatic medical entity extraction (ICD-10 codes, medications, procedures)
- **Search** — full-text search across summaries and transcriptions (Meilisearch), encrypted patient lookup
- **Export** — PDF generation for clinical records (ReportLab)
- **Multi-language UI** — 8 languages: Hebrew, English, German, Spanish, French, Portuguese, Korean, Italian

---

## Architecture

```
Browser → Nginx (TLS) → FastAPI → PostgreSQL
                ↓              ↓
           Flutter Web    Celery Workers → Whisper / GPT-4.1
                              ↓
                         Redis (queue)
                              ↓
                         MinIO (audio storage)
                         Meilisearch (search index)
```

Single-server deployment. All services containerized with Docker Compose.

---

## Tech Stack

### Backend — Python 3.11+
| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI + Uvicorn (async) |
| ORM | SQLAlchemy 2.0 (async, asyncpg) |
| Migrations | Alembic |
| Task Queue | Celery + Redis |
| Auth | Google OAuth → JWT (python-jose) |
| Speech-to-Text | OpenAI Whisper API |
| LLM | GPT-4.1 (summaries), Claude (fallback) |
| Search Engine | Meilisearch |
| Object Storage | MinIO (S3-compatible, boto3) |
| Encryption | AES-256-GCM (cryptography lib) |
| PDF Generation | ReportLab |
| Logging | structlog (JSON) |
| Error Tracking | Sentry |
| Metrics | Prometheus client |
| Rate Limiting | SlowAPI |
| Testing | pytest + pytest-asyncio |
| Linting | Ruff, mypy |

### Frontend — Flutter Web (Dart 3)
| Component | Technology |
|-----------|-----------|
| State Management | Riverpod |
| HTTP Client | Dio |
| Routing | go_router |
| Auth | google_sign_in |
| Internationalization | easy_localization (8 languages) |
| WebSocket | web_socket_channel |
| Design System | Material 3, Google Fonts |

### Landing Page — Next.js 15
| Component | Technology |
|-----------|-----------|
| Framework | Next.js 15 + React 18 |
| Styling | Tailwind CSS |
| Language | TypeScript |

### Infrastructure
| Component | Technology |
|-----------|-----------|
| Containers | Docker Compose (9 services) |
| Reverse Proxy | Nginx + Let's Encrypt (TLS 1.3) |
| Database | PostgreSQL 16 |
| Cache / Queue | Redis 7 |
| Object Storage | MinIO |
| Search | Meilisearch v1.10 |
| Monitoring | Prometheus + Grafana |
| CI/CD | GitHub Actions |

---

## Services (Docker Compose)

| Service | Port | Purpose |
|---------|------|---------|
| `nginx` | 80, 443 | Reverse proxy, SSL termination, rate limiting |
| `backend` | 8000 | FastAPI REST API |
| `celery-worker` | — | Async processing (STT, summaries, tagging) |
| `frontend` | 3000 | Flutter Web app |
| `parent-website` | 3001 | Next.js marketing site |
| `postgres` | 5432 | Primary database |
| `redis` | 6379 | Task queue + cache |
| `minio` | 9000/9001 | Encrypted audio storage |
| `meilisearch` | 7700 | Full-text search index |

---

## Data Model

17 tables. Key entities:

```
users ─── visits ─── recordings ─── transcriptions
  │          │                            │
  │          └── summaries ── tags        │
  │                                       │
  └── patients ── appointments      audit_log
```

All patient PII encrypted at field level (AES-256-GCM). Audio files encrypted with per-file DEK (envelope encryption). ID numbers stored with HMAC-SHA256 hash for O(1) lookup.

---

## Security

- **Encryption at rest** — AES-256-GCM for all PII fields, envelope encryption for audio
- **Encryption in transit** — TLS 1.3 (Let's Encrypt)
- **Authentication** — Google OAuth 2.0 → JWT tokens
- **Authorization** — RBAC (doctor / admin / receptionist)
- **PII masking** — patient data stripped before sending to LLM
- **Audit trail** — every mutation logged (user, action, entity, IP, timestamp)
- **Rate limiting** — 100 req/min API, 10 req/min auth endpoints
- **Security headers** — HSTS, X-Frame-Options DENY, X-Content-Type-Options nosniff, CSP

---

## Quick Start

```bash
# Clone
git clone https://github.com/Bob789/-from_pc_drsscribe.git
cd Doctor-Scribe

# Configure
cp .env.example .env
# Edit .env with your credentials (DB, Redis, MinIO, OpenAI, Google OAuth)

# Run
docker-compose up -d

# Migrate database
docker-compose exec backend bash -c "cd /app && PYTHONPATH=/app python -m alembic upgrade head"
```

App: `http://localhost:3000` | API: `http://localhost:8000/docs` | MinIO Console: `http://localhost:9001`

---

## Project Structure

```
├── backend/           Python FastAPI server
│   ├── app/
│   │   ├── models/    SQLAlchemy ORM (17 models)
│   │   ├── routers/   API endpoints
│   │   ├── services/  Business logic (18 services)
│   │   ├── schemas/   Pydantic validation
│   │   ├── middleware/ Auth, audit, rate limit, CSP
│   │   └── utils/     Encryption, validators, helpers
│   ├── alembic/       Database migrations
│   └── tests/         pytest suite
├── frontend/          Flutter Web client
│   └── lib/
│       ├── screens/   15 screens
│       ├── providers/ Riverpod state
│       ├── services/  API client, auth
│       ├── widgets/   Reusable components
│       └── models/    Data classes
├── parent-website/    Next.js landing page
├── nginx/             Reverse proxy config
├── monitoring/        Prometheus + Grafana
└── docker-compose.yml
```

---

## Processing Pipeline

```
1. Doctor records visit in browser
2. Audio chunks upload to MinIO (encrypted)
3. Celery worker → Whisper API → transcription saved to DB
4. Celery worker → PII masked → GPT-4.1 → summary + tags saved to DB
5. WebSocket notifies frontend → UI updates
```

---

## License

Proprietary. All rights reserved.