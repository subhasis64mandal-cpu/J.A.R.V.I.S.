"""Explicit desktop controls for J.A.R.V.I.S.

Only fixed, benign Windows applications are exposed in this first desktop
control layer. No shell parsing, arbitrary executable paths, or free-form
command strings are accepted.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class DesktopApp:
    name: str
    executable: str
    description: str


APPROVED_APPS: dict[str, DesktopApp] = {
    "notepad": DesktopApp("notepad", "notepad.exe", "Open Windows Notepad"),
    "calculator": DesktopApp("calculator", "calc.exe", "Open Windows Calculator"),
    "paint": DesktopApp("paint", "mspaint.exe", "Open Microsoft Paint"),
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
