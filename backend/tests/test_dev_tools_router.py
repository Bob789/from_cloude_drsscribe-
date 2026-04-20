"""Regression tests for the dev-tools admin router (503 fix)."""
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status


def test_get_docker_client_raises_503_when_socket_unavailable():
    """If Docker socket is unreachable, _get_docker_client must raise 503."""
    from app.routers.dev_tools import _get_docker_client

    with patch("docker.from_env", side_effect=Exception("socket not found")):
        with pytest.raises(HTTPException) as exc_info:
            _get_docker_client()
    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Docker socket not reachable" in exc_info.value.detail


def test_container_state_absent(monkeypatch):
    """_container_state returns absent dict when container doesn't exist."""
    from app.routers.dev_tools import _container_state

    client = MagicMock()
    client.containers.get.side_effect = Exception("not found")
    result = _container_state(client)
    assert result == {"exists": False, "running": False, "status": "absent"}


def test_container_state_running(monkeypatch):
    """_container_state returns running=True when container is running."""
    from app.routers.dev_tools import _container_state

    container = MagicMock()
    container.status = "running"
    container.short_id = "abc123"

    client = MagicMock()
    client.containers.get.return_value = container

    result = _container_state(client)
    assert result["running"] is True
    assert result["exists"] is True
    assert result["id"] == "abc123"
