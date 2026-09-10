"""Repository-controlled Home Base for J.A.R.V.I.S.

Home Base is configuration/state, not an execution engine. It gives the assistant
one stable control plane while keeping future web, browser, computer, and device
adapters separate from the core.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class HomeBaseError(RuntimeError):
    """Raised when Home Base configuration cannot be loaded safely."""


@dataclass(frozen=True)
class HomeBase:
    root: Path
    config: dict[str, Any]

    @classmethod
    def load(cls, root: str | Path | None = None) -> "HomeBase":
        base = Path(root) if root is not None else Path(__file__).resolve().parent.parent / "homebase"
        config_path = base / "config.json"

        if not config_path.is_file():
            raise HomeBaseError(f"Home Base configuration not found: {config_path}")

        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise HomeBaseError(f"Could not load Home Base: {exc}") from exc

        if not isinstance(data, dict):
            raise HomeBaseError("Home Base configuration must be a JSON object.")

        return cls(base, data)

    def assistant_name(self) -> str:
        return str(self.config.get("assistant", {}).get("name", "J.A.R.V.I.S."))

    def capability_enabled(self, capability: str) -> bool:
        capabilities = self.config.get("capabilities", {})
        return bool(capabilities.get(capability, False))

    def requires_confirmation(self) -> bool:
        safety = self.config.get("safety", {})
        return bool(safety.get("require_confirmation_for_control_tools", True))

    def allows_arbitrary_shell(self) -> bool:
        safety = self.config.get("safety", {})
        return bool(safety.get("allow_arbitrary_shell", False))
