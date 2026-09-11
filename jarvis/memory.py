"""Small local memory layer with explicit, inspectable persistence."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Memory:
    key: str
    value: str
    created_at: str
    source: str = "user"


class MemoryStore:
    """Persist simple facts locally; callers decide what is worth remembering."""

    def __init__(self, path: str | Path = ".jarvis/memory.json") -> None:
        self.path = Path(path)
        self._items: list[Memory] = []
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self._items = []
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self._items = [Memory(**item) for item in raw if isinstance(item, dict)]
        except (OSError, ValueError, TypeError):
            self._items = []

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(item) for item in self._items]
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def remember(self, key: str, value: str, source: str = "user") -> Memory:
        normalized_key = " ".join(key.strip().lower().split())
        if not normalized_key:
            raise ValueError("Memory key cannot be empty")
        item = Memory(normalized_key, value.strip(), datetime.now(timezone.utc).isoformat(), source)
        self._items = [existing for existing in self._items if existing.key != normalized_key]
        self._items.append(item)
        self.save()
        return item

    def recall(self, key: str) -> Memory | None:
        normalized_key = " ".join(key.strip().lower().split())
        for item in reversed(self._items):
            if item.key == normalized_key:
                return item
        return None

    def search(self, query: str, limit: int = 5) -> list[Memory]:
        tokens = set(" ".join(query.lower().split()).split())
        if not tokens:
            return []
        scored = []
        for item in reversed(self._items):
            haystack = set(f"{item.key} {item.value}".lower().split())
            score = len(tokens & haystack)
            if score:
                scored.append((score, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[: max(0, limit)]]

    def all(self) -> tuple[Memory, ...]:
        return tuple(self._items)
