"""Module discovery and capability management for J.A.R.V.I.S."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jarvis.homebase import HomeBase, HomeBaseError


@dataclass(frozen=True)
class ModuleSpec:
    """Declarative description of a J.A.R.V.I.S. module."""

    name: str
    description: str
    capability: str
    enabled: bool = False
    entrypoint: str | None = None


class ModuleManager:
    """Load and inspect only explicitly declared Home Base modules.

    The manifest describes modules; it never imports or executes an entrypoint.
    Runtime adapters can later use these declarations when their capabilities are
    enabled and their dependencies are installed.
    """

    def __init__(self, homebase: HomeBase) -> None:
        self.homebase = homebase
        self._modules = self._load_manifest()

    def _load_manifest(self) -> dict[str, ModuleSpec]:
        path = self.homebase.root / "modules.json"
        try:
            data: Any = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise HomeBaseError(f"Could not load Home Base modules: {exc}") from exc

        modules = data.get("modules", {}) if isinstance(data, dict) else {}
        if not isinstance(modules, dict):
            raise HomeBaseError("Home Base modules must be an object.")

        result: dict[str, ModuleSpec] = {}
        for name, value in modules.items():
            if not isinstance(name, str) or not isinstance(value, dict):
                continue
            capability = value.get("capability")
            if not isinstance(capability, str) or not capability:
                continue
            result[name.lower()] = ModuleSpec(
                name=name,
                description=str(value.get("description", "")),
                capability=capability,
                enabled=bool(value.get("enabled", False)),
                entrypoint=value.get("entrypoint") if isinstance(value.get("entrypoint"), str) else None,
            )
        return result

    def get(self, name: str) -> ModuleSpec | None:
        return self._modules.get(name.strip().lower())

    def is_available(self, name: str) -> bool:
        module = self.get(name)
        return bool(
            module
            and module.enabled
            and self.homebase.capability_enabled(module.capability)
        )

    def list_text(self) -> str:
        lines = ["J.A.R.V.I.S. modules:"]
        for module in sorted(self._modules.values(), key=lambda item: item.name.lower()):
            enabled = module.enabled and self.homebase.capability_enabled(module.capability)
            state = "ON" if enabled else "OFF"
            lines.append(f"  {module.name:<12} {state:<3} {module.description}")
        return "\n".join(lines)
