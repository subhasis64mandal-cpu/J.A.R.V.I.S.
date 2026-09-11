"""Repository-owned capability catalog loader."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Capability:
    capability_id: str
    description: str
    status: str
    risk: str
    dependencies: tuple[str, ...] = ()


class CapabilityCatalog:
    """Load declarative capability metadata without importing optional tools."""

    def __init__(self, capabilities: tuple[Capability, ...], policy: dict[str, object]) -> None:
        self.capabilities = capabilities
        self.policy = dict(policy)

    @classmethod
    def load(cls, path: Path | None = None) -> "CapabilityCatalog":
        source = path or Path(__file__).resolve().parents[1] / "homebase" / "tool_catalog.json"
        payload = json.loads(source.read_text(encoding="utf-8"))
        capabilities = tuple(
            Capability(
                capability_id=str(item["id"]),
                description=str(item["description"]),
                status=str(item["status"]),
                risk=str(item["risk"]),
                dependencies=tuple(str(dep) for dep in item.get("dependencies", [])),
            )
            for item in payload.get("capabilities", [])
        )
        return cls(capabilities, dict(payload.get("policy", {})))

    def as_dict(self) -> dict[str, object]:
        return {
            "capabilities": [
                {
                    "id": item.capability_id,
                    "description": item.description,
                    "status": item.status,
                    "risk": item.risk,
                    "dependencies": list(item.dependencies),
                }
                for item in self.capabilities
            ],
            "policy": self.policy,
        }
