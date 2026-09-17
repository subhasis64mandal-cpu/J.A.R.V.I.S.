"""One-click local launcher for J.A.R.V.I.S. on Windows."""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AGENT_URL = "http://127.0.0.1:8766/health"
HOME_URL = "http://127.0.0.1:8787/"
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


def main() -> int:
    if os.name != "nt":
        print("J.A.R.V.I.S. one-click launcher currently targets Windows.")
        return 1

    _load_local_env()
    existing = _read_agent_health()
    if existing and existing.get("ok") and existing.get("version") != EXPECTED_AGENT_VERSION:
        print(
            f"An older J.A.R.V.I.S. Local Agent is already using port 8766 "
            f"(version {existing.get('version')}; expected {EXPECTED_AGENT_VERSION})."
        )
        print("Stop that old agent, then run Start-JARVIS.bat again.")
        return 1

    agent = subprocess.Popen([sys.executable, "-m", "jarvis.agent"], cwd=ROOT)
    if not _wait_for_agent():
        _terminate(agent)
        print("J.A.R.V.I.S. local agent did not become ready with the expected protocol version.")
        return 1

    runtime = subprocess.Popen([sys.executable, "main.py"], cwd=ROOT)
    time.sleep(0.75)

    try:
        os.startfile(HOME_URL)
    except OSError as exc:
        _terminate(runtime)
        _terminate(agent)
        print(f"Could not open Home Base: {exc}")
        return 1

    print("J.A.R.V.I.S. is running. Stop this launcher to stop local services.")
    try:
        return runtime.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        _terminate(runtime)
        _terminate(agent)
        try:
            runtime.wait(timeout=3)
        except subprocess.TimeoutExpired:
            runtime.kill()
        try:
            agent.wait(timeout=3)
        except subprocess.TimeoutExpired:
            agent.kill()


if __name__ == "__main__":
    raise SystemExit(main())
