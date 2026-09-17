"""Install or remove the J.A.R.V.I.S. Windows sign-in launcher."""

from __future__ import annotations

import os
import sys
from pathlib import Path

STARTUP_NAME = "J.A.R.V.I.S. Home Base.vbs"
ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "launch_jarvis.py"


def _startup_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("Windows APPDATA is not available.")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _pythonw() -> Path:
    candidate = Path(sys.executable).with_name("pythonw.exe")
    if candidate.is_file():
        return candidate
    raise RuntimeError("pythonw.exe was not found in the J.A.R.V.I.S. Python environment.")


def _script_content(pythonw: Path) -> str:
    python_path = str(pythonw).replace('"', '""')
    launcher_path = str(LAUNCHER).replace('"', '""')
    root_path = str(ROOT).replace('"', '""')
    return (
        'Set shell = CreateObject("WScript.Shell")\n'
        f'shell.CurrentDirectory = "{root_path}"\n'
        f'shell.Run Chr(34) & "{python_path}" & Chr(34) & " " & Chr(34) & "{launcher_path}" & Chr(34), 0, False\n'
    )


def install() -> Path:
    startup = _startup_dir()
    startup.mkdir(parents=True, exist_ok=True)
    path = startup / STARTUP_NAME
    path.write_text(_script_content(_pythonw()), encoding="utf-8")
    return path


def remove() -> bool:
    path = _startup_dir() / STARTUP_NAME
    try:
        path.unlink()
    except FileNotFoundError:
        return False
    return True


def main() -> int:
    if os.name != "nt":
        print("J.A.R.V.I.S. automatic startup currently targets Windows.")
        return 1

    action = sys.argv[1].lower() if len(sys.argv) > 1 else "install"
    try:
        if action in {"install", "enable"}:
            path = install()
            print(f"J.A.R.V.I.S. will start automatically at sign-in: {path}")
            return 0
        if action in {"remove", "disable", "uninstall"}:
            removed = remove()
            print("Automatic J.A.R.V.I.S. startup removed." if removed else "Automatic startup was already disabled.")
            return 0
    except (OSError, RuntimeError) as exc:
        print(f"Could not change automatic startup safely: {exc}")
        return 1

    print("Use: python -m jarvis.startup install|remove")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
