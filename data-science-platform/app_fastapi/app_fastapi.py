# File: app_fastapi/app_fastapi.py
"""
FastAPI application entry point.

This module configures and runs the FastAPI server for the
Data Science Demo Platform backend.
"""

from fastapi import FastAPI
from app_fastapi.routers import models_router, auth_router, admin_router
from app_fastapi.database.connection import get_connection

app = FastAPI(
    title="Data Science Demo Platform",
    description="Backend API for model training, prediction, and user management.",
    version="1.0.0"
)

app.include_router(models_router.router, prefix="/models", tags=["Models"])
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin_router.router, prefix="/auth", tags=["Admin"])


@app.get("/")
def root():
    """Root endpoint — system info."""
    return {
        "name": "Data Science Demo Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check — verifies server + database connectivity."""
    db_ok = False
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        db_ok = True
    except Exception:
        pass

    status = "ok" if db_ok else "degraded"
    return {"status": status, "database": "connected" if db_ok else "unreachable"}