"""Intent routing for J.A.R.V.I.S.

The router deliberately stays deterministic: the AI layer can later choose tools,
while this layer remains responsible for dispatching known commands safely.
"""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Route:
    name: str
    description: str
    handler: Callable[[str], str]


class Router:
    def __init__(self) -> None:
        self._routes: dict[str, Route] = {}

    def register(self, name: str, description: str, handler: Callable[[str], str]) -> None:
        self._routes[name.lower()] = Route(name, description, handler)

    def route(self, command: str) -> str:
        text = command.strip()
        if not text:
            return "I didn't catch a command."

        lowered = text.lower()
        for route in self._routes.values():
            if lowered == route.name.lower() or lowered.startswith(route.name.lower() + " "):
                argument = text[len(route.name):].strip()
                return route.handler(argument)

        return "I don't have a tool for that yet."

    def help_text(self) -> str:
        lines = ["Available commands:"]
        for route in sorted(self._routes.values(), key=lambda item: item.name):
            lines.append(f"  {route.name:<10} {route.description}")
        return "\n".join(lines)
