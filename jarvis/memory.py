"""Local, explicit memory for J.A.R.V.I.S.

Memory is intentionally small and transparent: JARVIS only stores facts when
its caller explicitly asks it to remember them.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict


@dataclass
class Memory:
    """Simple JSON-backed memory store."""

    path: Path = field(default_factory=lambda: Path.home() / ".jarvis" / "memory.json")
    data: Dict[str, str] = field(default_factory=dict)

    def load(self) -> None:
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def remember(self, key: str, value: str) -> None:
        self.data[key.strip()] = value.strip()
        self.save()

    def recall(self, key: str) -> str | None:
        return self.data.get(key.strip())

    def forget(self, key: str) -> bool:
        key = key.strip()
        if key not in self.data:
            return False
        del self.data[key]
        self.save()
        return True

    def all(self) -> Dict[str, str]:
        return dict(self.data)
