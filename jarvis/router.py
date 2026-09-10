"""Intent routing for J.A.R.V.I.S."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Route:
    name: str
    description: str
    handler: Callable[[str], str]
    aliases: tuple[str, ...] = ()


class Router:
    """Compatibility router over the explicit tool registry."""

    def __init__(self) -> None:
        self._routes: dict[str, Route] = {}
        self._aliases: dict[str, str] = {}

    def register(
        self,
        name: str,
        description: str,
        handler: Callable[[str], str],
        aliases: tuple[str, ...] = (),
    ) -> None:
        key = name.strip().lower()
        if not key or key in self._routes or key in self._aliases:
            raise ValueError(f"Route already registered: {name}")
        self._routes[key] = Route(name, description, handler, aliases)
        for alias in aliases:
            alias_key = alias.strip().lower()
            if not alias_key or alias_key in self._routes or alias_key in self._aliases:
                raise ValueError(f"Route alias already registered: {alias}")
            self._aliases[alias_key] = key

    def route(self, command: str) -> str:
        text = command.strip()
        if not text:
            return "I didn't catch a command."

        parts = text.split(maxsplit=1)
        key = parts[0].lower()
        canonical = self._aliases.get(key, key)
        route = self._routes.get(canonical)
        if route is None:
            return "I don't have a tool for that yet."

        argument = parts[1] if len(parts) == 2 else ""
        return route.handler(argument)

    def help_text(self) -> str:
        lines = ["Available tools:"]
        for route in sorted(self._routes.values(), key=lambda item: item.name.lower()):
            aliases = f" (aliases: {', '.join(route.aliases)})" if route.aliases else ""
            lines.append(f"  {route.name:<10} {route.description}{aliases}")
        return "\n".join(lines)
