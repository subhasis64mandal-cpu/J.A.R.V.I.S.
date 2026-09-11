"""Intent routing for J.A.R.V.I.S."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from jarvis.homebase import HomeBase


@dataclass(frozen=True)
class Route:
    name: str
    description: str
    handler: Callable[[str], str]
    aliases: tuple[str, ...] = ()
    capability: str | None = None


class Router:
    """Route requests through explicit tools and Home Base policy."""

    def __init__(self, homebase: HomeBase | None = None) -> None:
        self._routes: dict[str, Route] = {}
        self._aliases: dict[str, str] = {}
        self._homebase = homebase

    def register(self, name: str, description: str, handler: Callable[[str], str], aliases: tuple[str, ...] = (), capability: str | None = None) -> None:
        key = name.strip().lower()
        if not key or key in self._routes or key in self._aliases:
            raise ValueError(f"Route already registered: {name}")
        self._routes[key] = Route(name, description, handler, aliases, capability)
        for alias in aliases:
            alias_key = alias.strip().lower()
            if not alias_key or alias_key in self._routes or alias_key in self._aliases:
                raise ValueError(f"Route alias already registered: {alias}")
            self._aliases[alias_key] = key

    def resolve_route_name(self, name: str) -> str:
        """Resolve a tool name or alias without executing it."""
        key = name.strip().lower()
        return self._aliases.get(key, key)

    def route_names(self) -> frozenset[str]:
        """Return canonical route names for decision and inspection layers."""
        return frozenset(self._routes)

    def route(self, command: str) -> str:
        text = command.strip()
        if not text:
            return "I didn't catch a command."
        parts = text.split(maxsplit=1)
        canonical = self.resolve_route_name(parts[0])
        route = self._routes.get(canonical)
        if route is None:
            return "I don't have a tool for that yet."
        if self._homebase is not None and route.capability is not None and not self._homebase.capability_enabled(route.capability):
            return f"The '{route.name}' capability is disabled in Home Base."
        argument = parts[1] if len(parts) == 2 else ""
        return route.handler(argument)

    def help_text(self) -> str:
        lines = ["Available tools:"]
        for route in sorted(self._routes.values(), key=lambda item: item.name.lower()):
            aliases = f" (aliases: {', '.join(route.aliases)})" if route.aliases else ""
            state = ""
            if self._homebase is not None and route.capability is not None and not self._homebase.capability_enabled(route.capability):
                state = " [disabled]"
            lines.append(f"  {route.name:<10} {route.description}{aliases}{state}")
        return "\n".join(lines)
