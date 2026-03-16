from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import structlog
from app.config import settings
from app.routers import auth, patients, visits, visits_manual, recordings, transcriptions, summaries, search, tags, websocket, dashboard, admin, reports, health, patient_files, custom_fields, question_templates, appointments, messages
from app.middleware.rate_limit import setup_rate_limiting
from app.middleware.audit import AuditMiddleware
from app.middleware.metrics import setup_metrics
from app.utils.logging import setup_logging
from app.exceptions import AppError
from app.middleware.error_handler import app_error_handler, global_exception_handler

setup_logging("DEBUG" if settings.is_dev else "INFO")
logger = structlog.get_logger()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.is_dev else None,
    redoc_url="/redoc" if settings.is_dev else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(AuditMiddleware)

@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        f"frame-ancestors 'self' {settings.PARENT_WEBSITE_URL};"
    )
    if "X-Frame-Options" in response.headers:
        del response.headers["X-Frame-Options"]
    return response
setup_rate_limiting(app)
setup_metrics(app)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, global_exception_handler)

if settings.SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    sentry_sdk.init(dsn=settings.SENTRY_DSN, integrations=[FastApiIntegration()], traces_sample_rate=0.1)

@app.on_event("startup")
async def startup_event():
    from app.services.storage_service import ensure_bucket
    from app.services import redis_service
    try:
        await ensure_bucket()
    except Exception as exc:
        logger.error("startup_storage_unavailable", error=str(exc))

    try:
        await redis_service.get_redis()
    except Exception as exc:
        logger.error("startup_redis_unavailable", error=str(exc))


@app.on_event("shutdown")
async def shutdown_event():
    from app.services import redis_service
    await redis_service.close_redis()

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(visits.router, prefix="/api")
app.include_router(visits_manual.router, prefix="/api")
app.include_router(recordings.router, prefix="/api")
app.include_router(transcriptions.router, prefix="/api")
app.include_router(summaries.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(tags.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(patient_files.router, prefix="/api")
app.include_router(custom_fields.router, prefix="/api")
app.include_router(question_templates.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(websocket.router, prefix="/api")
