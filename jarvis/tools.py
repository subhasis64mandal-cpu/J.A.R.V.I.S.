"""Small, safe built-in tools for the first J.A.R.V.I.S. version."""

from datetime import datetime


def get_time(_: str = "") -> str:
    return datetime.now().strftime("It is %I:%M %p.")


def get_date(_: str = "") -> str:
    return datetime.now().strftime("Today is %A, %d %B %Y.")


def system_status(_: str = "") -> str:
    return "Core status: online. Tool router: online. External tools: not configured yet."
