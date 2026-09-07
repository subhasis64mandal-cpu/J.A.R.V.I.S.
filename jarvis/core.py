"""Core assistant logic for J.A.R.V.I.S."""

from dataclasses import dataclass, field

from .memory import Memory
from .permissions import PermissionManager


@dataclass
class Jarvis:
    """Assistant core with explicit memory and tool permissions."""

    name: str = "J.A.R.V.I.S."
    memory: Memory = field(default_factory=Memory)
    permissions: PermissionManager = field(default_factory=PermissionManager)

    def __post_init__(self) -> None:
        self.memory.load()

    def respond(self, message: str) -> str:
        text = message.strip()
        lower = text.lower()

        if not text:
            return "I'm listening."
        if lower in {"hello", "hi", "hey"}:
            return "Good to hear from you. How can I help?"
        if lower == "memory":
            items = self.memory.all()
            if not items:
                return "My memory is empty."
            return "\n".join(f"- {key}: {value}" for key, value in items.items())
        if lower.startswith("remember "):
            payload = text[9:].strip()
            if "=" not in payload:
                return "Use: remember key = value"
            key, value = payload.split("=", 1)
            if not key.strip() or not value.strip():
                return "Both the memory key and value are required."
            self.memory.remember(key, value)
            return f"Remembered: {key.strip()}"
        if lower.startswith("forget "):
            key = text[7:].strip()
            return (
                f"Forgot: {key}"
                if self.memory.forget(key)
                else f"I don't have a memory named '{key}'."
            )
        if lower.startswith("allow "):
            tool = text[6:].strip()
            if not tool:
                return "Tell me which tool to allow."
            self.permissions.grant(tool)
            return f"Permission granted for: {tool}"
        if lower.startswith("deny "):
            tool = text[5:].strip()
            if not tool:
                return "Tell me which tool to deny."
            self.permissions.revoke(tool)
            return f"Permission denied for: {tool}"

        return f"I heard you say: {text}"
