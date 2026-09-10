"""Natural-language intent layer for J.A.R.V.I.S.

This is deliberately dependency-free. It is the first version of the brain
boundary; a real LLM provider can later implement the same intent contract.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Intent:
    """A normalized request for the deterministic tool layer."""

    command: str
    argument: str = ""


class Brain:
    """Turn common natural-language requests into safe canonical commands."""

    _INTENTS: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("time", ("what time is it", "tell me the time", "current time", "time")),
        ("date", ("what is the date", "what's the date", "tell me the date", "today's date", "date")),
        ("status", ("are you online", "are you online?", "system status", "your status", "status")),
        ("help", ("what can you do", "what can you do?", "show commands", "show tools", "help")),
    )

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
