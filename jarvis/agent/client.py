"""Client for the loopback-only J.A.R.V.I.S. Local Agent."""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class AgentResponse:
    ok: bool
    action: str = ""
    result: str = ""
    error: str = ""


class LocalAgentUnavailable(RuntimeError):
    """Raised when the local agent cannot be reached safely."""


class LocalAgentClient:
    """Call only the J.A.R.V.I.S. Local Agent on loopback."""

    def __init__(self, base_url: str = "http://127.0.0.1:8766", timeout: float = 1.5) -> None:
        if base_url.rstrip("/") != "http://127.0.0.1:8766":
            raise ValueError("LocalAgentClient must target the J.A.R.V.I.S. loopback endpoint.")
        if timeout <= 0 or timeout > 10:
            raise ValueError("Timeout must be between 0 and 10 seconds.")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> bool:
        payload = self._get("/health")
        return bool(payload.get("ok"))

    def capabilities(self) -> tuple[str, ...]:
        payload = self._get("/capabilities")
        actions = payload.get("actions", [])
        if not isinstance(actions, list) or not all(isinstance(item, str) for item in actions):
            raise LocalAgentUnavailable("Agent returned an invalid capability list.")
        return tuple(actions)

    def action(self, action: str, argument: str = "") -> AgentResponse:
        normalized = action.strip().lower()
        allowed = {
            "time",
            "date",
            "status",
            "machine",
            "hostname",
            "apps",
            "open_app",
        }
        if normalized not in allowed:
            raise ValueError("LocalAgentClient action is not allowlisted.")
        if len(argument) > 1024:
            raise ValueError("Agent argument is too long.")
        payload = self._post("/action", {"action": normalized, "argument": argument})
        return AgentResponse(
            ok=bool(payload.get("ok")),
            action=str(payload.get("action", normalized)),
            result=str(payload.get("result", "")),
            error=str(payload.get("error", "")),
        )

    def _get(self, path: str) -> dict[str, object]:
        request = Request(f"{self.base_url}{path}", method="GET")
        return self._request(request)

    def _post(self, path: str, body: dict[str, object]) -> dict[str, object]:
        encoded = json.dumps(body).encode("utf-8")
        request = Request(
            f"{self.base_url}{path}",
            data=encoded,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return self._request(request)

    def _request(self, request: Request) -> dict[str, object]:
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read(8192)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise LocalAgentUnavailable("Local J.A.R.V.I.S. agent is unavailable.") from exc
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LocalAgentUnavailable("Local agent returned invalid JSON.") from exc
        if not isinstance(payload, dict):
            raise LocalAgentUnavailable("Local agent returned an invalid response.")
        return payload
