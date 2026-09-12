"""Explicit desktop and browser-launch controls for J.A.R.V.I.S.

Only fixed, benign Windows applications, allowlisted website endpoints, and a
small set of window-management actions are exposed. No shell parsing,
arbitrary executable paths, arbitrary URLs, or free-form input injection.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus


@dataclass(frozen=True)
class DesktopApp:
    name: str
    executable: str
    description: str


@dataclass(frozen=True)
class ApprovedSite:
    name: str
    url: str
    description: str


APPROVED_APPS: dict[str, DesktopApp] = {
    "notepad": DesktopApp("notepad", "notepad.exe", "Open Windows Notepad"),
    "calculator": DesktopApp("calculator", "calc.exe", "Open Windows Calculator"),
    "paint": DesktopApp("paint", "mspaint.exe", "Open Microsoft Paint"),
    "edge": DesktopApp("edge", "msedge.exe", "Open Microsoft Edge"),
}

APPROVED_SITES: dict[str, ApprovedSite] = {
    "google": ApprovedSite("google", "https://www.google.com/", "Open Google"),
    "youtube": ApprovedSite("youtube", "https://www.youtube.com/", "Open YouTube"),
    "github": ApprovedSite("github", "https://github.com/", "Open GitHub"),
    "wikipedia": ApprovedSite("wikipedia", "https://www.wikipedia.org/", "Open Wikipedia"),
}

WINDOW_ACTIONS = {"focus", "minimize", "maximize", "restore"}


def list_approved_apps(_: str = "") -> str:
    return ", ".join(sorted(APPROVED_APPS))


def list_approved_sites(_: str = "") -> str:
    return ", ".join(sorted(APPROVED_SITES))


def _edge_candidates() -> tuple[Path, ...]:
    candidates: list[Path] = []
    for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        root = os.environ.get(variable)
        if root:
            candidates.append(Path(root) / "Microsoft" / "Edge" / "Application" / "msedge.exe")
    return tuple(candidates)


def _edge_executable() -> str:
    for candidate in _edge_candidates():
        if candidate.is_file():
            return str(candidate)
    return "msedge.exe"


def open_approved_app(name: str) -> str:
    key = name.strip().lower()
    app = APPROVED_APPS.get(key)
    if app is None:
        raise ValueError(f"App is not allowlisted: {name}")
    if os.name != "nt":
        raise RuntimeError("Approved desktop app launching currently requires Windows.")
    executable = _edge_executable() if key == "edge" else app.executable
    subprocess.Popen([executable], close_fds=True)
    return f"Opened {app.name}."


def open_approved_site(name: str) -> str:
    key = name.strip().lower()
    site = APPROVED_SITES.get(key)
    if site is None:
        raise ValueError(f"Site is not allowlisted: {name}")
    if os.name != "nt":
        raise RuntimeError("Approved browser navigation currently requires Windows.")
    subprocess.Popen([_edge_executable(), site.url], close_fds=True)
    return f"Opened {site.name}."


def search_google(query: str) -> str:
    cleaned = query.strip()
    if not cleaned:
        raise ValueError("Google search query cannot be empty.")
    if os.name != "nt":
        raise RuntimeError("Google search launching currently requires Windows.")
    url = f"https://www.google.com/search?q={quote_plus(cleaned)}"
    subprocess.Popen([_edge_executable(), url], close_fds=True)
    return f"Searching Google for: {cleaned}"


def _window_for_app(app_name: str) -> int:
    if os.name != "nt":
        raise RuntimeError("Window control currently requires Windows.")
    user32 = ctypes.windll.user32
    handles: list[int] = []

    @wintypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def callback(hwnd: int, _: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if not length:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        title = buffer.value.lower()
        keywords = {"notepad": ("notepad",), "calculator": ("calculator",), "paint": ("paint",), "edge": ("edge",)}[app_name]
        if any(keyword in title for keyword in keywords):
            handles.append(hwnd)
            return False
        return True

    user32.EnumWindows(callback, 0)
    if not handles:
        raise ValueError(f"No visible window found for approved app: {app_name}")
    return handles[0]


def manage_approved_window(argument: str) -> str:
    parts = argument.strip().lower().split(maxsplit=1)
    if len(parts) != 2 or parts[0] not in APPROVED_APPS or parts[1] not in WINDOW_ACTIONS:
        raise ValueError("Use: pc window <app> <focus|minimize|maximize|restore>")
    app_name, action = parts
    hwnd = _window_for_app(app_name)
    user32 = ctypes.windll.user32
    commands = {"minimize": 6, "maximize": 3, "restore": 9}
    if action == "focus":
        user32.ShowWindow(hwnd, 9)
        user32.SetForegroundWindow(hwnd)
    else:
        user32.ShowWindow(hwnd, commands[action])
    return f"{action.title()}d {app_name}."
