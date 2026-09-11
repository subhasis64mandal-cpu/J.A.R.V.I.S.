"""Provider-neutral decision layer between Brain and executable tools."""

from __future__ import annotations

from dataclasses import dataclass

from jarvis.brain import Brain
from jarvis.router import Router


@dataclass(frozen=True)
class Decision:
    """A proposed action. Decisions are descriptions, not execution."""

    action: str
    target: str | None = None
    argument: str = ""
    confidence: float = 0.0
    reason: str = ""


class DecisionEngine:
    """Turn user text into an explicit, auditable execution proposal."""

    def __init__(self, brain: Brain, router: Router) -> None:
        self.brain = brain
        self.router = router

    def decide(self, text: str) -> Decision:
        cleaned = " ".join(text.strip().lower().split())
        if not cleaned:
            return Decision("RESPOND", reason="empty input")

        if cleaned == "home" or cleaned.startswith("home "):
            return Decision("HOME", target=cleaned.removeprefix("home").strip() or "status", confidence=1.0, reason="explicit Home Base command")

        intent = self.brain.understand(cleaned)
        if intent is not None:
            return Decision("ROUTE", target=intent.command, argument=intent.argument, confidence=1.0, reason="deterministic brain intent match")

        first, *rest = cleaned.split(maxsplit=1)
        routes = self.router.route_names()
        canonical = self.router.resolve_route_name(first)
        if canonical in routes:
            return Decision("ROUTE", target=canonical, argument=rest[0] if rest else "", confidence=0.98, reason="explicit tool name")

        return Decision("RESPOND", confidence=0.0, reason="no safe executable route matched")
