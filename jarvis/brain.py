"""Natural-language intent and provider boundary for J.A.R.V.I.S."""

from __future__ import annotations

from dataclasses import dataclass

from jarvis.providers import AIProvider, BrainRequest, DeterministicProvider


@dataclass(frozen=True)
class Intent:
    """A normalized request for the deterministic tool layer."""

    command: str
    argument: str = ""


class Brain:
    """Safe intent layer with an injectable AI provider."""

    _INTENTS: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("time", ("what time is it", "tell me the time", "current time", "time")),
        ("date", ("what is the date", "what's the date", "tell me the date", "today's date", "date")),
        ("status", ("are you online", "are you online?", "system status", "your status", "status")),
        ("help", ("what can you do", "what can you do?", "show commands", "show tools", "help")),
    )

    def __init__(self, provider: AIProvider | None = None) -> None:
        self.provider = provider or DeterministicProvider()

    def understand(self, text: str) -> Intent | None:
        cleaned = " ".join(text.strip().lower().split())
        if not cleaned:
            return None
        for command, phrases in self._INTENTS:
            if cleaned in phrases:
                return Intent(command)
        return None

    def normalize(self, text: str) -> str:
        """Return a canonical command when understood, otherwise original text."""
        intent = self.understand(text)
        if intent is None:
            return text.strip()
        return intent.command if not intent.argument else f"{intent.command} {intent.argument}"

    def generate(self, text: str, system_context: str = "") -> str:
        """Generate through the configured provider without coupling the runtime to it."""
        response = self.provider.generate(BrainRequest(text=text, system_context=system_context))
        return response.text
