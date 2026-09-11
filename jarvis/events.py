"""Small synchronous event bus shared by the runtime and UI adapters."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from threading import RLock
from typing import Callable


@dataclass(frozen=True)
class JarvisEvent:
    """An observable runtime event."""

    name: str
    payload: dict[str, object]


EventHandler = Callable[[JarvisEvent], None]


class EventBus:
    """In-process pub/sub with explicit subscriptions."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._lock = RLock()

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        with self._lock:
            if handler not in self._handlers[event_name]:
                self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        with self._lock:
            handlers = self._handlers.get(event_name, [])
            if handler in handlers:
                handlers.remove(handler)

    def publish(self, event_name: str, **payload: object) -> JarvisEvent:
        event = JarvisEvent(event_name, payload)
        with self._lock:
            handlers = tuple(self._handlers.get(event_name, ()))
            wildcard = tuple(self._handlers.get("*", ()))
        for handler in (*handlers, *wildcard):
            handler(event)
        return event
