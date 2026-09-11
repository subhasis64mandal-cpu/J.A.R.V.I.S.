"""Execution policy boundary for future J.A.R.V.I.S. tools.

The executor does not discover or execute arbitrary code. A tool must be
registered explicitly, and higher-risk actions can require an explicit,
single-use confirmation token supplied by the caller/UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from secrets import token_urlsafe

from jarvis.registry import ToolRegistry


class Risk(StrEnum):
    READ = "read"
    WRITE = "write"
    CONTROL = "control"


@dataclass(frozen=True)
class ExecutionResult:
    ok: bool
    message: str
    requires_confirmation: bool = False
    confirmation_token: str | None = None


class ExecutionPolicy:
    """Gate execution by explicit risk metadata and one-time confirmations."""

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry
        self._pending: dict[str, str] = {}

    def prepare(self, name: str) -> ExecutionResult:
        tool = self.registry.get(name)
        if tool is None:
            return ExecutionResult(False, "Tool is not registered.")
        if not tool.requires_confirmation:
            return ExecutionResult(True, "Execution is permitted.")
        token = token_urlsafe(18)
        self._pending[token] = name.strip().lower()
        return ExecutionResult(
            False,
            f"The '{tool.name}' tool requires confirmation.",
            requires_confirmation=True,
            confirmation_token=token,
        )

    def execute(self, name: str, argument: str = "", confirmation_token: str | None = None) -> ExecutionResult:
        tool = self.registry.get(name)
        if tool is None:
            return ExecutionResult(False, "Tool is not registered.")
        if tool.requires_confirmation:
            expected = confirmation_token and self._pending.pop(confirmation_token, None)
            if expected != name.strip().lower():
                return ExecutionResult(False, f"The '{tool.name}' tool requires confirmation.", True)
        return ExecutionResult(True, self.registry.execute(name, argument))
