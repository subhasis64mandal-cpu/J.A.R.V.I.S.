"""One-click local launcher for J.A.R.V.I.S. on Windows.

Starts the loopback local agent, starts the J.A.R.V.I.S. runtime, and opens
Home Base in the default browser. It never enables arbitrary shell/Python
execution and shuts down child processes cleanly on exit.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AGENT_URL = "http://127.0.0.1:8766/health"
HOME_URL = "http://127.0.0.1:8787/"


def _python() -> str:
    return sys.executable


def _wait_for_agent(timeout: float = 8.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(AGENT_URL, timeout=0.5) as response:
                return response.status == 200
        except (OSError, urllib.error.URLError):
            time.sleep(0.25)
    return False


def main() -> int:
    if os.name != "nt":
        print("J.A.R.V.I.S. one-click launcher currently targets Windows.")
        return 1

    agent = subprocess.Popen([_python(), "-m", "jarvis.agent"], cwd=ROOT)
    if not _wait_for_agent():
        agent.terminate()
        print("J.A.R.V.I.S. local agent did not become ready.")
        return 1

    runtime = subprocess.Popen([_python(), "main.py"], cwd=ROOT)
    time.sleep(1.0)

    try:
        os.startfile(HOME_URL)
    except OSError as exc:
        runtime.terminate()
        agent.terminate()
        print(f"Could not open Home Base: {exc}")
        return 1

    print("J.A.R.V.I.S. is running. Close this launcher window to stop local services.")
    try:
        return runtime.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        if runtime.poll() is None:
            runtime.terminate()
        if agent.poll() is None:
            agent.terminate()
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
