"""Bounded read-only web retrieval for J.A.R.V.I.S.

This tool intentionally supports only HTTP(S) GET requests, redirects, and a
small byte/time budget. It does not execute page scripts or arbitrary URLs
through a shell/browser process.
"""

from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


MAX_BYTES = 256_000
TIMEOUT_SECONDS = 8


def web_get(argument: str) -> str:
    """Fetch a small text resource from an explicit HTTP(S) URL."""
    url = argument.strip()
    if not (url.startswith("https://") or url.startswith("http://")):
        return "Use: web <http(s) URL>"
    request = Request(url, headers={"User-Agent": "JARVIS/0.1"}, method="GET")
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            content_type = response.headers.get_content_type()
            if content_type not in {"text/plain", "text/html", "application/json", "application/xml"}:
                return f"Web tool declined non-text content: {content_type}."
            payload = response.read(MAX_BYTES + 1)
    except HTTPError as exc:
        return f"Web request failed: HTTP {exc.code}."
    except (URLError, TimeoutError, OSError) as exc:
        return f"Web request failed: {exc.reason if hasattr(exc, 'reason') else exc}."
    if len(payload) > MAX_BYTES:
        return f"Web response exceeded the {MAX_BYTES} byte safety limit."
    text = payload.decode("utf-8", errors="replace").strip()
    return text or "Web response was empty."
