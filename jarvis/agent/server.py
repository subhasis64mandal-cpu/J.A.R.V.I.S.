"""Loopback-only local agent for approved J.A.R.V.I.S. actions.

This agent is deliberately boring: it exposes a tiny HTTP API, binds only to
127.0.0.1, validates JSON input, and executes only explicitly registered,
low-risk actions. It is a bridge to the user's machine, not a remote shell.
"""

from __future__ import annotations

import json
import platform
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from jarvis.tools import get_date, get_time, system_status


MAX_BODY_BYTES = 8_192


def _safe_status(_: str) -> str:
    return system_status("")


def _machine(_: str) -> str:
    return f"{platform.system()} {platform.release()} ({platform.machine()})"


def _hostname(_: str) -> str:
    return socket.gethostname()


AGENT_ACTIONS = {
    "time": get_time,
    "date": get_date,
    "status": _safe_status,
    "machine": _machine,
    "hostname": _hostname,
}


def handle_action(action: str, argument: str = "") -> dict[str, Any]:
    normalized = action.strip().lower()
    handler = AGENT_ACTIONS.get(normalized)
    if handler is None:
        return {
            "ok": False,
            "error": "Action is not allowlisted.",
            "allowed_actions": sorted(AGENT_ACTIONS),
        }
    try:
        return {"ok": True, "action": normalized, "result": handler(argument)}
    except Exception:
        return {"ok": False, "action": normalized, "error": "Action failed safely."}


class _Handler(BaseHTTPRequestHandler):
    server_version = "JARVISLocalAgent/0.1"

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(200, {"ok": True, "service": "jarvis-local-agent", "version": 1})
            return
        if self.path == "/capabilities":
            self._send_json(200, {"ok": True, "actions": sorted(AGENT_ACTIONS), "arbitrary_commands": False})
            return
        self._send_json(404, {"ok": False, "error": "Not found."})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/action":
            self._send_json(404, {"ok": False, "error": "Not found."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY_BYTES:
            self._send_json(413, {"ok": False, "error": "Request body rejected."})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"ok": False, "error": "Invalid JSON."})
            return
        if not isinstance(payload, dict) or not isinstance(payload.get("action"), str):
            self._send_json(400, {"ok": False, "error": "Expected JSON object with string 'action'."})
            return
        argument = payload.get("argument", "")
        if not isinstance(argument, str) or len(argument) > 1_024:
            self._send_json(400, {"ok": False, "error": "Invalid argument."})
            return
        result = handle_action(payload["action"], argument)
        self._send_json(200 if result["ok"] else 403, result)

    def log_message(self, _: str, *args: object) -> None:
        return


class LocalAgentServer:
    """Start a local-only J.A.R.V.I.S. agent server."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8766) -> None:
        if host not in {"127.0.0.1", "localhost"}:
            raise ValueError("LocalAgentServer must bind to loopback.")
        self.address = (host, port)
        self._server = ThreadingHTTPServer(self.address, _Handler)
        self._server.daemon_threads = True

    def start(self) -> None:
        self._server.serve_forever(poll_interval=0.2)

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()
