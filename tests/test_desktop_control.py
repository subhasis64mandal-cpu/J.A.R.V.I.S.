from __future__ import annotations

from unittest.mock import Mock, patch

from jarvis.desktop import APPROVED_APPS, list_approved_apps, open_approved_app, search_google


def test_edge_is_allowlisted() -> None:
    assert "edge" in APPROVED_APPS
    assert "notepad" in list_approved_apps()


def test_google_search_rejects_empty_query() -> None:
    try:
        search_google("")
    except ValueError:
        pass
    else:
        raise AssertionError("Empty Google searches must be rejected")


def test_windows_app_launch_uses_fixed_executable() -> None:
    fake_proc = Mock()
    with patch("jarvis.desktop.os.name", "nt"), patch("jarvis.desktop.subprocess.Popen", fake_proc):
        result = open_approved_app("notepad")
    assert result == "Opened notepad."
    fake_proc.assert_called_once_with(["notepad.exe"], close_fds=True)
