"""Small local JSONL audit trail for runtime decisions and results."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SECRET_KEY = re.compile(r"(token|secret|password|api[_-]?key)", re.IGNORECASE)


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: "[redacted]" if _SECRET_KEY.search(str(key)) else _sanitize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value]
    if isinstance(value, str):
        return value[:4_000]
    return value


class AuditLog:
    """Append-only local runtime log; secrets are redacted before persistence."""

    def __init__(self, path: str | Path = ".jarvis/audit.jsonl") -> None:
        self.path = Path(path)

    def record(self, event: str, **payload: Any) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "payload": _sanitize(payload),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def recent(self, limit: int = 25) -> tuple[dict[str, Any], ...]:
        if limit <= 0 or not self.path.exists():
            return ()
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()[-limit:]
        except OSError:
            return ()
        records: list[dict[str, Any]] = []
        for line in lines:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                records.append(value)
        return tuple(records)
