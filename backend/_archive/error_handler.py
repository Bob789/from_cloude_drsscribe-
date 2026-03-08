import asyncio
import structlog
from typing import Callable, TypeVar

logger = structlog.get_logger()
T = TypeVar("T")

_dead_letter_queue: list[dict] = []


async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    *args,
    **kwargs,
) -> T:
    for attempt in range(max_retries + 1):
        try:
            result = func(*args, **kwargs)
            if hasattr(result, "__await__"):
                return await result
            return result
        except Exception as e:
            if attempt == max_retries:
                logger.error("max_retries_exceeded", func=func.__name__, error=str(e))
                _dead_letter_queue.append({
                    "func": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "error": str(e),
                    "attempts": max_retries + 1,
                })
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning("retrying", func=func.__name__, attempt=attempt + 1, delay=delay, error=str(e))
            await asyncio.sleep(delay)


def get_dead_letter_queue() -> list[dict]:
    return list(_dead_letter_queue)


def clear_dead_letter_queue():
    _dead_letter_queue.clear()
