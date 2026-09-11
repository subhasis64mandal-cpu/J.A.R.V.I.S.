"""Read-only capability adapters that stay bounded and explicit."""

from __future__ import annotations

import os
import platform
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


MAX_FILE_BYTES = 64 * 1024
MAX_WEB_BYTES = 128 * 1024
ALLOWED_SCHEMES = {"http", "https"}


class CapabilityError(RuntimeError):
    """Raised when a bounded capability cannot be completed safely."""


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _safe_workspace_path(argument: str) -> Path:
    relative = argument.strip() or "."
    candidate = (_workspace_root() / relative).resolve()
    root = _workspace_root().resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise CapabilityError("Path is outside the J.A.R.V.I.S. workspace.") from exc
    return candidate


def list_files(argument: str = "") -> str:
    path = _safe_workspace_path(argument)
    if not path.is_dir():
        raise CapabilityError("Requested path is not a directory.")
    entries = sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
    shown = entries[:100]
    lines = [f"{'[DIR] ' if item.is_dir() else '[FILE]'}{item.name}" for item in shown]
    if len(entries) > len(shown):
        lines.append(f"... {len(entries) - len(shown)} more entries omitted")
    return "\n".join(lines) or "Directory is empty."


def read_file(argument: str = "") -> str:
    path = _safe_workspace_path(argument)
    if not path.is_file():
        raise CapabilityError("Requested path is not a file.")
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise CapabilityError(f"File exceeds the {MAX_FILE_BYTES // 1024} KiB read limit.")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise CapabilityError("Only UTF-8 text files are supported.") from exc
    return text


def fetch_web(argument: str = "") -> str:
    url = argument.strip()
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES or not parsed.netloc:
        raise CapabilityError("Only valid HTTP(S) URLs are allowed.")
    if parsed.username or parsed.password:
        raise CapabilityError("Credential-bearing URLs are not allowed.")

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "JARVIS-SafeWeb/0.1", "Accept": "text/plain,text/html;q=0.9,*/*;q=0.1"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            content_type = response.headers.get_content_type()
            if content_type not in {"text/plain", "text/html", "application/json", "application/xml"}:
                raise CapabilityError("Response content type is not an allowed text format.")
            data = response.read(MAX_WEB_BYTES + 1)
    except (urllib.error.URLError, TimeoutError) as exc:
        raise CapabilityError("Web request failed safely.") from exc

    if len(data) > MAX_WEB_BYTES:
        raise CapabilityError("Response exceeded the web read limit.")
    return data.decode("utf-8", errors="replace")


def host_diagnostics(_: str = "") -> str:
    return "\n".join(
        (
            f"OS: {platform.system()} {platform.release()}",
            f"Architecture: {platform.machine()}",
            f"Python: {platform.python_version()}",
            f"CPU count: {os.cpu_count() or 'unknown'}",
        )
    )
