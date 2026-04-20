"""
Dev-Tools admin router.

Allows admins to start/stop/check the `medscribe-dev-tools` container from the
cpanel UI without needing terminal access. Uses the Docker SDK against the
mounted /var/run/docker.sock.

This router is **disabled in production** (settings.is_dev must be True).
"""
from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.middleware.permissions import require_admin
from app.models.user import User

logger = structlog.get_logger()

router = APIRouter(prefix="/admin/dev-tools", tags=["admin", "dev-tools"])

CONTAINER_NAME = "medscribe-dev-tools"
IMAGE_NAME = "doctor-scribe-dev-tools"
NETWORK_NAME = "medscribe-network"
HOST_PORT = 8090
CONTAINER_PORT = 8090


def _get_docker_client():
    """Lazy import so the backend still boots if the docker package is missing."""
    try:
        import docker  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Docker SDK not installed in backend image",
        ) from exc

    try:
        return docker.from_env()
    except Exception as exc:
        logger.error("dev_tools_docker_unavailable", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Docker socket not reachable",
        ) from exc


def _ensure_dev_only() -> None:
    if not settings.is_dev:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dev-tools control is only available in dev environment",
        )


def _container_state(client) -> dict[str, Any]:
    try:
        c = client.containers.get(CONTAINER_NAME)
    except Exception:
        return {"exists": False, "running": False, "status": "absent"}

    return {
        "exists": True,
        "running": c.status == "running",
        "status": c.status,
        "id": c.short_id,
    }


@router.get("/status")
async def status_endpoint(
    _: User = Depends(require_admin),
) -> dict[str, Any]:
    _ensure_dev_only()
    client = _get_docker_client()
    state = _container_state(client)
    state["image"] = IMAGE_NAME
    state["host_port"] = HOST_PORT
    return state


@router.post("/start")
async def start_endpoint(
    current_user: User = Depends(require_admin),
) -> dict[str, Any]:
    _ensure_dev_only()
    client = _get_docker_client()

    # Already running?
    state = _container_state(client)
    if state["running"]:
        return {"action": "noop", "state": state}

    # If exists but stopped — just start it
    if state["exists"]:
        c = client.containers.get(CONTAINER_NAME)
        c.start()
        logger.info("dev_tools_started", user=current_user.email, action="start_existing")
        return {"action": "started", "state": _container_state(client)}

    # Otherwise create + run from existing image
    try:
        client.images.get(IMAGE_NAME)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=(
                f"Image '{IMAGE_NAME}' not found. Build it first: "
                f"docker-compose --profile dev-tools build dev-tools"
            ),
        ) from exc

    import os
    dev_token = os.getenv("DEV_TOOLS_TOKEN", "dev-token-change-me")

    c = client.containers.run(
        image=IMAGE_NAME,
        name=CONTAINER_NAME,
        detach=True,
        ports={f"{CONTAINER_PORT}/tcp": HOST_PORT},
        environment={"DEV_TOOLS_TOKEN": dev_token},
        network=NETWORK_NAME,
        restart_policy={"Name": "unless-stopped"},
    )
    logger.info("dev_tools_started", user=current_user.email, action="created", id=c.short_id)
    return {"action": "created", "state": _container_state(client)}


@router.post("/stop")
async def stop_endpoint(
    current_user: User = Depends(require_admin),
) -> dict[str, Any]:
    _ensure_dev_only()
    client = _get_docker_client()
    state = _container_state(client)
    if not state["exists"] or not state["running"]:
        return {"action": "noop", "state": state}

    c = client.containers.get(CONTAINER_NAME)
    c.stop(timeout=10)
    logger.info("dev_tools_stopped", user=current_user.email)
    return {"action": "stopped", "state": _container_state(client)}
