"""Explicit desktop and browser-launch controls for J.A.R.V.I.S.

Only fixed, benign Windows applications and a fixed Google search endpoint are
exposed. No shell parsing, arbitrary executable paths, or arbitrary URLs are
accepted by these helpers.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from urllib.parse import quote_plus


@dataclass(frozen=True)
class DesktopApp:
    name: str
    executable: str
    description: str


APPROVED_APPS: dict[str, DesktopApp] = {
    "notepad": DesktopApp("notepad", "notepad.exe", "Open Windows Notepad"),
    "calculator": DesktopApp("calculator", "calc.exe", "Open Windows Calculator"),
    "paint": DesktopApp("paint", "mspaint.exe", "Open Microsoft Paint"),
    "edge": DesktopApp("edge", "msedge.exe", "Open Microsoft Edge"),
}


def list_approved_apps(_: str = "") -> str:
    return ", ".join(sorted(APPROVED_APPS))


def open_approved_app(name: str) -> str:
    key = name.strip().lower()
    app = APPROVED_APPS.get(key)
    if app is None:
        raise ValueError(f"App is not allowlisted: {name}")
    if os.name != "nt":
        raise RuntimeError("Approved desktop app launching currently requires Windows.")
    subprocess.Popen([app.executable], close_fds=True)
    return f"Opened {app.name}."


def search_google(query: str) -> str:
    cleaned = query.strip()
    if not cleaned:
        raise ValueError("Google search query cannot be empty.")
    if os.name != "nt":
        raise RuntimeError("Google search launching currently requires Windows.")
    url = f"https://www.google.com/search?q={quote_plus(cleaned)}"
    subprocess.Popen(["msedge.exe", url], close_fds=True)
    return f"Searching Google for: {cleaned}"
