"""Loopback-only Home Base gateway for the local UI."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock, Thread
from typing import Callable

from jarvis.capabilities import CapabilityCatalog
from jarvis.events import EventBus, JarvisEvent


MAX_COMMAND_BYTES = 1_024
UI_ROOT = Path(__file__).resolve().parent.parent / "homebase" / "ui"
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


class HomeBaseGateway:
    """Expose a local UI/API bridge without arbitrary command execution."""

    def __init__(
        self,
        events: EventBus,
        command_handler: Callable[[str], str],
        host: str = "127.0.0.1",
        port: int = 8787,
        runtime_info: Callable[[], dict[str, object]] | None = None,
        activity_info: Callable[[int], tuple[dict[str, object], ...]] | None = None,
        device_info: Callable[[], str] | None = None,
    ) -> None:
        if host not in {"127.0.0.1", "localhost"}:
            raise ValueError("HomeBaseGateway must bind to loopback.")
        self.events = events
        self.command_handler = command_handler
        self.host = host
        self.port = port
        self._runtime_info = runtime_info or (lambda: {"state": self._state})
        self._activity_info = activity_info or (lambda _limit: ())
        self._device_info = device_info or (lambda: "No device registry connected.")
        self._clients: list[object] = []
        self._lock = Lock()
        self._server: ThreadingHTTPServer | None = None
        self._thread: Thread | None = None
        self._state = "idle"
        self._catalog = CapabilityCatalog.load()
        events.subscribe("assistant.state", self._on_event)
        events.subscribe("assistant.decision", self._on_event)
        events.subscribe("assistant.confirmation", self._on_event)
        events.subscribe("assistant.execution", self._on_event)
        events.subscribe("assistant.response", self._on_event)

    @property
    def address(self) -> str:
        return f"http://{self.host}:{self.port}"

    def _on_event(self, event: JarvisEvent) -> None:
        if event.name == "assistant.state":
            state = str(event.payload.get("state", "idle"))
            self._state = state
            self._broadcast({"event": event.name, "state": state})
            return
        payload = {"event": event.name}
        payload.update({key: value for key, value in event.payload.items() if key not in {"context", "token"}})
        self._broadcast(payload)

    def _broadcast(self, payload: dict[str, object]) -> None:
        message = f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode()
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

            def _headers(self) -> None:
                for name, value in SECURITY_HEADERS.items():
                    self.send_header(name, value)

            def _json(self, status: int, payload: object) -> None:
                body = json.dumps(payload, ensure_ascii=False).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self._headers()
                self.end_headers()
                self.wfile.write(body)

            def _file(self, path: Path, content_type: str) -> None:
                try:
                    body = path.read_bytes()
                except OSError:
                    self._json(404, {"error": "ui asset not found"})
                    return
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self._headers()
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:  # noqa: N802
                if self.path in {"/", "/index.html"}:
                    self._file(UI_ROOT / "index.html", "text/html; charset=utf-8")
                    return
                if self.path == "/state":
                    self._json(200, {"state": gateway._state})
                    return
                if self.path == "/runtime":
                    self._json(200, gateway._runtime_info())
                    return
                if self.path == "/activity":
                    self._json(200, list(gateway._activity_info(25)))
                    return
                if self.path == "/devices":
                    self._json(200, {"text": gateway._device_info()})
                    return
                if self.path == "/capabilities":
                    self._json(200, gateway._catalog.as_dict())
                    return
                if self.path == "/health":
                    available = sum(item.status == "available" for item in gateway._catalog.capabilities)
                    self._json(200, {"status": "online", "state": gateway._state, "capabilities": len(gateway._catalog.capabilities), "available_capabilities": available, "policy": gateway._catalog.policy})
                    return
                if self.path != "/events":
                    self._json(404, {"error": "not found"})
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self._headers()
                self.end_headers()
                with gateway._lock:
                    gateway._clients.append(self)
                try:
                    self.wfile.write(f"data: {json.dumps({'event': 'assistant.state', 'state': gateway._state})}\n\n".encode())
                    self.wfile.flush()
                    while self.rfile.read(1) != b"":
                        pass
                except (BrokenPipeError, ConnectionResetError, OSError):
                    pass
                finally:
                    with gateway._lock:
                        if self in gateway._clients:
                            gateway._clients.remove(self)

            def do_POST(self) -> None:  # noqa: N802
                if self.path != "/command":
                    self._json(404, {"error": "not found"})
                    return
                try:
                    raw_size = int(self.headers.get("Content-Length", "0"))
                    if raw_size <= 0 or raw_size > MAX_COMMAND_BYTES:
                        raise ValueError
                    content_type = self.headers.get("Content-Type", "")
                    if not content_type.lower().startswith("application/json"):
                        raise ValueError
                    payload = json.loads(self.rfile.read(raw_size))
                    command = payload.get("command", "")
                except (ValueError, json.JSONDecodeError):
                    self._json(400, {"error": "invalid request"})
                    return
                if not isinstance(command, str) or not command.strip():
                    self._json(400, {"error": "command is required"})
                    return
                response = gateway.command_handler(command.strip())
                self._json(200, {"ok": True, "response": response, "state": gateway._state})

        self._server = ThreadingHTTPServer((self.host, self.port), Handler)
        self._thread = Thread(target=self._server.serve_forever, name="jarvis-homebase-gateway", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
