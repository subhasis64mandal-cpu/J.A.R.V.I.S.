"""Safe command control plane backed by the repository Home Base."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from jarvis.homebase import HomeBase, HomeBaseError


@dataclass(frozen=True)
class HomeCommand:
    name: str
    action: str
    description: str
    enabled: bool = True


class HomeControl:
    """Expose only declarative, allowlisted Home Base commands."""

    def __init__(self, homebase: HomeBase) -> None:
        self.homebase = homebase
        self._commands = self._load_commands()

    def _load_commands(self) -> dict[str, HomeCommand]:
        path = self.homebase.root / "commands.json"
        try:
            data: Any = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise HomeBaseError(f"Could not load Home Base commands: {exc}") from exc

        commands = data.get("commands", {}) if isinstance(data, dict) else {}
        if not isinstance(commands, dict):
            raise HomeBaseError("Home Base commands must be an object.")

        result: dict[str, HomeCommand] = {}
        for name, value in commands.items():
            if not isinstance(name, str) or not isinstance(value, dict):
                continue
            action = value.get("action")
            if not isinstance(action, str) or not action:
                continue
            result[name.lower()] = HomeCommand(
                name=name,
                action=action,
                description=str(value.get("description", "")),
                enabled=bool(value.get("enabled", True)),
            )
        return result

    def execute(self, command: str) -> str:
        key = command.strip().lower()
        if not key:
            return self.help_text()

        spec = self._commands.get(key)
        if spec is None:
            return "Home Base does not allow that command."
        if not spec.enabled:
            return f"Home Base command '{spec.name}' is disabled."

        if spec.action == "report_status":
            return self._status()
        if spec.action == "report_capabilities":
            return self._capabilities()

        return "Home Base rejected an unknown action."

    def _status(self) -> str:
        name = self.homebase.assistant_name()
        mode = self.homebase.config.get("assistant", {}).get("mode", "unknown")
        return f"{name} Home Base: online. Mode: {mode}. Control plane: active."

    def _capabilities(self) -> str:
        capabilities = self.homebase.config.get("capabilities", {})
        if not isinstance(capabilities, dict):
            return "No capabilities are configured."
        lines = ["Configured capabilities:"]
        for name, enabled in capabilities.items():
            state = "ON" if bool(enabled) else "OFF"
            lines.append(f"  {name}: {state}")
        return "\n".join(lines)

    def help_text(self) -> str:
        lines = ["Home Base commands:"]
        for command in sorted(self._commands.values(), key=lambda item: item.name.lower()):
            state = "" if command.enabled else " [disabled]"
            lines.append(f"  {command.name:<14} {command.description}{state}")
        return "\n".join(lines)
