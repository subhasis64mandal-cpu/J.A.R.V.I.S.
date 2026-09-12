"""One-click local launcher for J.A.R.V.I.S. on Windows."""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AGENT_URL = "http://127.0.0.1:8766/health"
HOME_URL = "http://127.0.0.1:8787/"


def _wait_for_agent(timeout: float = 8.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(AGENT_URL, timeout=0.5) as response:
                return response.status == 200
        except (OSError, urllib.error.URLError):
            time.sleep(0.25)
    return False


def _terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        process.terminate()


def main() -> int:
    if os.name != "nt":
        print("J.A.R.V.I.S. one-click launcher currently targets Windows.")
        return 1

    agent = subprocess.Popen([sys.executable, "-m", "jarvis.agent"], cwd=ROOT)
    if not _wait_for_agent():
        _terminate(agent)
        print("J.A.R.V.I.S. local agent did not become ready.")
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
