from typing import Callable
from collections import defaultdict

_handlers: dict[str, list[Callable]] = defaultdict(list)


def on(event_name: str, handler: Callable):
    _handlers[event_name].append(handler)


async def emit(event_name: str, data: dict = None):
    for handler in _handlers.get(event_name, []):
        try:
            result = handler(data or {})
            if hasattr(result, "__await__"):
                await result
        except Exception:
            pass


def clear():
    _handlers.clear()
