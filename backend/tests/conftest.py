"""Pytest configuration for backend tests."""
import asyncio
import pytest

# Make asyncio tests work properly
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    """Single event loop for the entire test session.
    Prevents 'Event loop is closed' errors from anyio/Redis/httpx cleanup.
    Safe with NullPool DB engines (no loop-bound connection pools).
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio test"
    )
