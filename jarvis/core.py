"""Core assistant logic for J.A.R.V.I.S."""

from dataclasses import dataclass


@dataclass
class Jarvis:
    """Minimal, testable assistant core."""

    name: str = "J.A.R.V.I.S."

    def respond(self, message: str) -> str:
        text = message.strip()
        if not text:
            return "I'm listening."
        if text.lower() in {"hello", "hi", "hey"}:
            return "Good to hear from you. How can I help?"
        return f"I heard you say: {text}"
