"""Read-only local system telemetry."""

from __future__ import annotations

import os
import platform
import shutil


def system_info(_: str = "") -> str:
    total, used, free = shutil.disk_usage(os.getcwd())
    return (
        f"OS: {platform.system()} {platform.release()}\n"
        f"Machine: {platform.machine()}\n"
        f"Python: {platform.python_version()}\n"
        f"Workspace disk: {used // (1024**3)} GB used / {total // (1024**3)} GB total"
    )
