"""Bounded J.A.R.V.I.S. -> n8n workflow bridge.

The bridge only calls a workflow endpoint configured by the operator. It never
accepts an arbitrary URL from a user command and only permits HTTPS or local
loopback HTTP endpoints.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

MAX_COMMAND_BYTES = 4_096
MAX_RESPONSE_BYTES = 8_192
DEFAULT_TIMEOUT_SECONDS = 20


class N8nUnavailable(RuntimeError):
    """n8n integration is not configured or reachable."""


@dataclass(frozen=True)
class N8nConfig:
    webhook_url: str
    token: str | None = None
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    @property
    def enabled(self) -> bool:
        return bool(self.webhook_url)


def _validate_endpoint(value: str) -> str:
    url = value.strip()
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.netloc:
        return url
    if parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}:
        return url
    raise N8nUnavailable("n8n endpoint must use HTTPS or loopback HTTP.")


def load_config() -> N8nConfig:
    raw_url = os.getenv("JARVIS_N8N_WEBHOOK_URL", "").strip()
    if not raw_url:
        return N8nConfig("")
    url = _validate_endpoint(raw_url)
    token = os.getenv("JARVIS_N8N_WEBHOOK_TOKEN", "").strip() or None
    try:
        timeout = int(os.getenv("JARVIS_N8N_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))
    except ValueError:
        timeout = DEFAULT_TIMEOUT_SECONDS
    return N8nConfig(url, token, max(3, min(timeout, 60)))


class N8nWorkflowClient:
    """Trigger one operator-configured n8n webhook with bounded input/output."""

    def __init__(self, config: N8nConfig | None = None) -> None:
        self.config = config or load_config()

    def status(self) -> str:
        if not self.config.enabled:
            return "n8n bridge is disabled. Set JARVIS_N8N_WEBHOOK_URL to enable it."
        return "n8n bridge is configured and ready."

    def trigger(self, command: str) -> str:
        if not self.config.enabled:
            raise N8nUnavailable("n8n bridge is disabled.")
        payload = command.strip()
        if not payload:
            return "Use: workflow <task>"
        if len(payload.encode("utf-8")) > MAX_COMMAND_BYTES:
            raise N8nUnavailable("Workflow request is too large.")

        body = json.dumps({"source": "jarvis", "command": payload}, ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "JARVIS-n8n-bridge/1",
        }
        if self.config.token:
            headers["X-JARVIS-N8N-TOKEN"] = self.config.token

        request = Request(self.config.webhook_url, data=body, headers=headers, method="POST")
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                data = response.read(MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            raise N8nUnavailable(f"n8n returned HTTP {exc.code}.") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise N8nUnavailable("n8n could not be reached.") from exc

        if len(data) > MAX_RESPONSE_BYTES:
            raise N8nUnavailable("n8n response is too large.")
        text = data.decode("utf-8", errors="replace").strip()
        if not text:
            return "n8n workflow completed with no response body."
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return text[:2_000]
        if isinstance(parsed, dict):
            for key in ("result", "response", "message", "data"):
                value = parsed.get(key)
                if isinstance(value, str):
                    return value[:2_000]
        return text[:2_000]
