"""Read-only local workspace inspection for J.A.R.V.I.S."""

from __future__ import annotations

from pathlib import Path

MAX_BYTES = 128_000


def _workspace() -> Path:
    return Path.cwd().resolve()


def _safe_path(raw: str) -> Path | None:
    candidate = (_workspace() / raw).resolve()
    try:
        candidate.relative_to(_workspace())
    except ValueError:
        return None
    return candidate


def file_read(argument: str) -> str:
    path = _safe_path(argument.strip())
    if path is None:
        return "File access is restricted to the J.A.R.V.I.S. workspace."
    if not path.is_file():
        return "File not found."
    try:
        payload = path.read_bytes()
    except OSError as exc:
        return f"File read failed: {exc}."
    if len(payload) > MAX_BYTES:
        return f"File exceeds the {MAX_BYTES} byte safety limit."
    return payload.decode("utf-8", errors="replace") or "File is empty."


def file_list(argument: str = "") -> str:
    base = _workspace() if not argument.strip() else _safe_path(argument)
    if base is None:
        return "Directory access is restricted to the J.A.R.V.I.S. workspace."
    if not base.is_dir():
        return "Directory not found."
    try:
        entries = sorted(base.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))[:100]
    except OSError as exc:
        return f"Directory listing failed: {exc}."
    if not entries:
        return "Directory is empty."
    return "\n".join(f"{'DIR ' if item.is_dir() else 'FILE'} {item.relative_to(_workspace())}" for item in entries)
