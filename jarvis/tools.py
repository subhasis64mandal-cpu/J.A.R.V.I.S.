"""Safe built-in tools for the first J.A.R.V.I.S. version."""

from datetime import datetime

from jarvis.filetools import file_list, file_read
from jarvis.systemtools import system_info
from jarvis.webtools import web_get


def get_time(_: str = "") -> str:
    return datetime.now().strftime("It is %I:%M %p.")


def get_date(_: str = "") -> str:
    return datetime.now().strftime("Today is %A, %d %B %Y.")


def system_status(_: str = "") -> str:
    return "Core status: online. Tool router: online. Home Base: online. Read-only capabilities: web, files, system."


__all__ = [
    "file_list",
    "file_read",
    "get_date",
    "get_time",
    "system_info",
    "system_status",
    "web_get",
]
