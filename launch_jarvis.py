"""One-click local launcher for J.A.R.V.I.S. on Windows."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from ctypes import windll
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AGENT_URL = "http://127.0.0.1:8766/health"
HOME_URL = "http://127.0.0.1:8787/?mode=desktop"
BROWSER_HOME_URL = "http://127.0.0.1:8787/"
EXPECTED_AGENT_VERSION = 6


def _load_local_env() -> None:
    """Load simple KEY=VALUE entries from a local .env without overwriting shell values."""
    path = ROOT / ".env"
    if not path.is_file():
        return
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key.isidentifier() and key not in os.environ:
            os.environ[key] = value


def _read_agent_health() -> dict[str, object] | None:
    try:
        with urllib.request.urlopen(AGENT_URL, timeout=0.5) as response:
            payload = json.loads(response.read(8192).decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _wait_for_agent(timeout: float = 8.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        health = _read_agent_health()
        if health and health.get("ok") and health.get("version") == EXPECTED_AGENT_VERSION:
            return True
        time.sleep(0.25)
    return False


def _terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        process.terminate()


def _find_edge() -> str | None:
    """Find Microsoft Edge without requiring it to be on PATH."""
    candidates = [
        shutil.which("msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def _desktop_geometry() -> tuple[int, int, int, int]:
    """Return a compact companion size and a top-right desktop position."""
    width = max(900, int(windll.user32.GetSystemMetrics(0)))
    height = max(650, int(windll.user32.GetSystemMetrics(1)))
    window_width = min(470, max(400, width - 80))
    window_height = min(820, max(660, height - 80))
    x = max(12, width - window_width - 24)
    y = max(12, (height - window_height) // 2)
    return window_width, window_height, x, y


def _open_home_base() -> bool:
    """Open Home Base as a compact Edge app window, falling back to the default browser."""
    mode = os.getenv("JARVIS_HOME_MODE", "desktop").strip().lower()
    if mode in {"browser", "normal"}:
        try:
            os.startfile(BROWSER_HOME_URL)
            return True
        except OSError:
            return False

    edge = _find_edge()
    if edge:
        width, height, x, y = _desktop_geometry()
        args = [
            edge,
            f"--app={HOME_URL}",
            "--no-first-run",
            "--disable-session-crashed-bubble",
            f"--window-size={width},{height}",
            f"--window-position={x},{y}",
        ]
        try:
            subprocess.Popen(args, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except OSError:
            pass

    try:
        os.startfile(BROWSER_HOME_URL)
        return True
    except OSError:
        return False


def main() -> int:
    if os.name != "nt":
        print("J.A.R.V.I.S. one-click launcher currently targets Windows.")
        return 1

    _load_local_env()
    existing = _read_agent_health()
    agent: subprocess.Popen[str] | None = None
    if existing and existing.get("ok"):
        version = existing.get("version")
        if version != EXPECTED_AGENT_VERSION:
            print(
                f"An older J.A.R.V.I.S. Local Agent is already using port 8766 "
                f"(version {version}; expected {EXPECTED_AGENT_VERSION})."
            )
            print("Stop that old agent, then run Start-JARVIS.bat again.")
            return 1
        print("J.A.R.V.I.S. Local Agent is already running; reusing it.")
    else:
        agent = subprocess.Popen([sys.executable, "-m", "jarvis.agent"], cwd=ROOT)
        if not _wait_for_agent():
            _terminate(agent)
            print("J.A.R.V.I.S. local agent did not become ready with the expected protocol version.")
            return 1

    runtime = subprocess.Popen([sys.executable, "main.py"], cwd=ROOT)
    time.sleep(0.75)

    if not _open_home_base():
        _terminate(runtime)
        if agent is not None:
            _terminate(agent)
        print("Could not open J.A.R.V.I.S. Home Base.")
        return 1

    print("J.A.R.V.I.S. is running with Home Base desktop companion mode.")
    print("Stop this launcher to stop local services when running manually.")
    try:
        return runtime.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        _terminate(runtime)
        if agent is not None:
            _terminate(agent)
        try:
            runtime.wait(timeout=3)
        except subprocess.TimeoutExpired:
            runtime.kill()
        if agent is not None:
            try:
                agent.wait(timeout=3)
            except subprocess.TimeoutExpired:
                agent.kill()
