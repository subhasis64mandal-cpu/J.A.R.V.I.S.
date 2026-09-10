"""Tool registry for J.A.R.V.I.S.

The registry is the stable boundary between the AI brain and executable tools.
Tools stay explicit and inspectable instead of being arbitrary Python actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


ToolHandler = Callable[[str], str]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    handler: ToolHandler
    aliases: tuple[str, ...] = ()
    requires_confirmation: bool = False
    category: str = "general"


class ToolRegistry:
    """Register and resolve the tools J.A.R.V.I.S. is allowed to call."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}
        self._aliases: dict[str, str] = {}

    def register(self, spec: ToolSpec) -> None:
        key = spec.name.strip().lower()
        if not key:
            raise ValueError("Tool name cannot be empty.")
        if key in self._tools or key in self._aliases:
            raise ValueError(f"Tool already registered: {spec.name}")
        self._tools[key] = spec
        for alias in spec.aliases:
            alias_key = alias.strip().lower()
            if not alias_key or alias_key in self._tools or alias_key in self._aliases:
                raise ValueError(f"Tool alias already registered: {alias}")
            self._aliases[alias_key] = key

    def get(self, name: str) -> ToolSpec | None:
        key = name.strip().lower()
        canonical = self._aliases.get(key, key)
        return self._tools.get(canonical)

    def execute(self, name: str, argument: str = "") -> str:
        tool = self.get(name)
        if tool is None:
            return "I don't have a tool for that yet."
        if tool.requires_confirmation:
            return f"The '{tool.name}' tool requires confirmation before it can run."
        return tool.handler(argument)

    def list_tools(self) -> tuple[ToolSpec, ...]:
        return tuple(sorted(self._tools.values(), key=lambda item: item.name.lower()))

    def help_text(self) -> str:
        lines = ["Available tools:"]
        for tool in self.list_tools():
            aliases = f" (aliases: {', '.join(tool.aliases)})" if tool.aliases else ""
            lines.append(f"  {tool.name:<10} {tool.description}{aliases}")
        return "\n".join(lines)
