"""Loopback-only Home Base gateway for the local UI."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock, Thread
from typing import Callable

from jarvis.capabilities import CapabilityCatalog
from jarvis.events import EventBus, JarvisEvent


class HomeBaseGateway:
    """Expose a tiny local SSE/HTTP bridge without arbitrary command execution."""

    def __init__(self, events: EventBus, command_handler: Callable[[str], str], host: str = "127.0.0.1", port: int = 8787) -> None:
        self.events = events
        self.command_handler = command_handler
        self.host = host
        self.port = port
        self._clients: list[object] = []
        self._lock = Lock()
        self._server: ThreadingHTTPServer | None = None
        self._thread: Thread | None = None
        self._state = "idle"
        self._catalog = CapabilityCatalog.load()
        events.subscribe("assistant.state", self._on_event)
        events.subscribe("assistant.decision", self._on_event)

    @property
    def address(self) -> str:
        return f"http://{self.host}:{self.port}"

    def _on_event(self, event: JarvisEvent) -> None:
        if event.name == "assistant.state":
            state = str(event.payload.get("state", "idle"))
            self._state = state
            self._broadcast({"event": event.name, "state": state})
            return
        if event.name == "assistant.decision":
            # Do not stream prompt/context contents to the UI transport.
            self._broadcast({
                "event": event.name,
                "action": event.payload.get("action"),
                "target": event.payload.get("target"),
                "confidence": event.payload.get("confidence"),
                "reason": event.payload.get("reason"),
            })

    def _broadcast(self, payload: dict[str, object]) -> None:
        message = f"data: {json.dumps(payload)}\n\n".encode()
        with self._lock:
            clients = list(self._clients)
        stale = []
        for client in clients:
            try:
                client.wfile.write(message)
                client.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                stale.append(client)
        if stale:
            with self._lock:
                self._clients = [client for client in self._clients if client not in stale]

    def start(self) -> None:
        gateway = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                return

            def _json(self, status: int, payload: dict[str, object]) -> None:
                body = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:  # noqa: N802
                if self.path == "/state":
                    self._json(HTTPStatus.OK, {"state": gateway._state})
                    return
                if self.path == "/capabilities":
                    self._json(HTTPStatus.OK, gateway._catalog.as_dict())
                    return
                if self.path == "/health":
                    available = sum(item.status == "available" for item in gateway._catalog.capabilities)
                    self._json(HTTPStatus.OK, {
                        "status": "online",
                        "state": gateway._state,
                        "capabilities": len(gateway._catalog.capabilities),
                        "available_capabilities": available,
                        "policy": gateway._catalog.policy,
                    })
                    return
                if self.path != "/events":
                    self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                    return
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                with gateway._lock:
                    gateway._clients.append(self)
                try:
                    self.wfile.write(f"data: {json.dumps({'event': 'assistant.state', 'state': gateway._state})}\n\n".encode())
                    self.wfile.flush()
                    while True:
                        if self.rfile.read(1) == b"":
                            break
                except (BrokenPipeError, ConnectionResetError, OSError):
                    pass
                finally:
                    with gateway._lock:
                        if self in gateway._clients:
                            gateway._clients.remove(self)

            def do_POST(self) -> None:  # noqa: N802
                if self.path != "/command":
                    self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                    return
                try:
                    size = min(int(self.headers.get("Content-Length", "0")), 4096)
                    payload = json.loads(self.rfile.read(size) or b"{}")
                    command = str(payload.get("command", "")).strip().lower()
                except (ValueError, json.JSONDecodeError):
                    self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid request"})
                    return
                if command not in {"activate", "status", "help"}:
                    self._json(HTTPStatus.FORBIDDEN, {"error": "command is not exposed by Home Base"})
                    return
                if command == "activate":
                    gateway.events.publish("assistant.state", state="listening", source="homebase.ui")
                    self._json(HTTPStatus.OK, {"ok": True, "state": "listening"})
                    return
                self._json(HTTPStatus.OK, {"ok": True, "response": gateway.command_handler(command)})

        self._server = ThreadingHTTPServer((self.host, self.port), Handler)
        self._thread = Thread(target=self._server.serve_forever, name="jarvis-homebase-gateway", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
