"""Explicit permission model for J.A.R.V.I.S. tools."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class PermissionManager:
    """Tracks which named tools JARVIS may use.

    Permissions default to denied. A future UI can expose these controls to
    the user without changing the assistant core.
    """

    allowed: Dict[str, bool] = field(default_factory=dict)

    def grant(self, tool: str) -> None:
        self.allowed[tool.strip()] = True

    def revoke(self, tool: str) -> None:
        self.allowed[tool.strip()] = False

    def is_allowed(self, tool: str) -> bool:
        return self.allowed.get(tool.strip(), False)
