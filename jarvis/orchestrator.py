"""Core J.A.R.V.I.S. orchestration pipeline.

Understand -> Think -> Plan -> Act -> Verify -> Respond.
Only registered router commands are executable. State-changing computer and
workflow commands receive a single-use confirmation token first.
"""

from __future__ import annotations

from dataclasses import dataclass
from secrets import token_urlsafe
from time import monotonic

from jarvis.audit import AuditLog
from jarvis.brain import Brain
from jarvis.context import ContextBuilder
from jarvis.control import HomeControl
from jarvis.decision import DecisionEngine
from jarvis.events import EventBus
from jarvis.homebase import HomeBase
from jarvis.router import Router


@dataclass(frozen=True)
class PendingConfirmation:
    token: str
    command: str
    expires_at: float


class Orchestrator:
    """Own the runtime lifecycle and keep execution behind explicit boundaries."""

    CONFIRMATION_TTL_SECONDS = 180.0
    CONTROL_ACTIONS = {"open_app", "open_site", "window"}
    WORKFLOW_ROUTES = {"workflow", "n8n", "automate"}

    def __init__(
        self,
        router: Router,
        brain: Brain,
        decision: DecisionEngine,
        context: ContextBuilder,
        home_control: HomeControl,
        homebase: HomeBase,
        events: EventBus,
        audit: AuditLog | None = None,
    ) -> None:
        self.router = router
        self.brain = brain
        self.decision = decision
        self.context = context
        self.home_control = home_control
        self.homebase = homebase
        self.events = events
        self.audit = audit or AuditLog()
        self._pending: dict[str, PendingConfirmation] = {}
        self.state = "idle"
        self.last_response = ""

    def _set_state(self, state: str, **payload: object) -> None:
        self.state = state
        self.events.publish("assistant.state", state=state, **payload)

    def _needs_confirmation(self, target: str | None, argument: str) -> bool:
        if target in self.WORKFLOW_ROUTES:
            return argument.strip().lower() not in {"", "status", "health"}
        if target != "pc":
            return False
        action = argument.strip().lower().split(maxsplit=1)[0] if argument.strip() else "status"
        if action == "open":
            action = "open_app"
        elif action in {"site", "navigate", "go"}:
            action = "open_site"
        elif action in {"window", "win"}:
            action = "window"
        return action in self.CONTROL_ACTIONS

    def _prune_confirmations(self) -> None:
        now = monotonic()
        self._pending = {token: item for token, item in self._pending.items() if item.expires_at > now}

    def _request_confirmation(self, command: str) -> str:
        self._prune_confirmations()
        token = token_urlsafe(10)
        self._pending[token] = PendingConfirmation(token, command, monotonic() + self.CONFIRMATION_TTL_SECONDS)
        self.events.publish("assistant.confirmation", required=True, token=token, command=command)
        self.audit.record("confirmation.requested", command=command)
        return f"Confirmation required for: {command}\nUse: confirm {token}"

    def _confirm(self, token: str) -> tuple[str, bool]:
        self._prune_confirmations()
        item = self._pending.pop(token.strip(), None)
        if item is None:
            return "That confirmation is missing or expired.", True
        self.events.publish("assistant.confirmation", required=False, token=token)
        return self._execute(item.command, confirmed=True)

    def _execute(self, command: str, confirmed: bool = False) -> tuple[str, bool]:
        normalized = command.strip().lower()
        if normalized in {"exit", "quit", "goodbye", "shutdown jarvis"}:
            self._set_state("idle")
            self.audit.record("session.stop", command=command)
            return "Standing by.", False

        self._set_state("thinking", input=command)
        runtime_context = self.context.build(command, runtime_state="thinking")
        proposal = self.decision.decide(command)
        self.events.publish(
            "assistant.decision",
            action=proposal.action,
            target=proposal.target,
            confidence=proposal.confidence,
            reason=proposal.reason,
            context=runtime_context.as_system_context(),
        )
        self.audit.record(
            "decision.made",
            command=command,
            action=proposal.action,
            target=proposal.target,
            confidence=proposal.confidence,
        )

        if normalized == "help":
            response = self.router.help_text() + "\n\n" + self.home_control.help_text()
        elif proposal.action == "HOME":
            response = self.home_control.execute(proposal.target or "status")
        elif proposal.action == "ROUTE":
            target = proposal.target
            if not confirmed and self._needs_confirmation(target, proposal.argument):
                response = self._request_confirmation(command)
                self._set_state("speaking")
                self.last_response = response
                return response, True
            self._set_state("executing", target=target or "")
            response = self.router.route(self.brain.normalize(command))
            ok = not any(marker in response.lower() for marker in ("failed safely", "denied safely", "unavailable", "does not allow"))
            self.events.publish("assistant.execution", target=target, ok=ok)
            self.audit.record("execution.completed", target=target, ok=ok)
        else:
            self._set_state("executing", target="brain")
            try:
                response = self.brain.generate(command, runtime_context.as_system_context())
                self.audit.record("brain.completed", provider=getattr(self.brain.provider, "name", "unknown"))
            except Exception as exc:
                response = f"I couldn't reach the configured brain provider safely: {exc}"
                self.audit.record("brain.failed", error=str(exc))

        self._set_state("speaking")
        self.events.publish("assistant.response", response=response)
        self.audit.record("response.completed", command=command, response=response)
        self.last_response = response
        return response, True

    def handle(self, command: str, source: str = "text") -> tuple[str, bool]:
        text = command.strip()
        self.audit.record("command.received", command=text, source=source)
        if not text:
            return "I didn't catch a command.", True
        lowered = text.lower()
        if lowered.startswith("confirm ") and len(text.split(maxsplit=1)) == 2:
            return self._confirm(text.split(maxsplit=1)[1])
        if lowered == "pending confirmations":
            self._prune_confirmations()
            return f"Pending confirmations: {len(self._pending)}", True
        return self._execute(text)

    def runtime_info(self) -> dict[str, object]:
        self._prune_confirmations()
        provider = getattr(self.brain.provider, "name", "unknown")
        model = getattr(self.brain.provider, "model", "")
        return {
            "state": self.state,
            "provider": provider,
            "model": model,
            "pending_confirmations": len(self._pending),
            "last_response": self.last_response[:4_000],
        }

    def recent_activity(self, limit: int = 20) -> tuple[dict[str, object], ...]:
        return self.audit.recent(limit)
