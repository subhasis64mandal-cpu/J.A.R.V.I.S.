from __future__ import annotations

from unittest.mock import patch

from jarvis.agent.server import LocalAgentServer, handle_action
from jarvis.desktop import open_approved_app


def test_allowed_actions_are_read_only_and_allowlisted() -> None:
    result = handle_action("machine")
    assert result["ok"] is True
    assert result["action"] == "machine"
    denied = handle_action("shell", "whoami")
    assert denied["ok"] is False
    assert "shell" not in denied["allowed_actions"]


def test_agent_rejects_non_loopback_binding() -> None:
    try:
        LocalAgentServer(host="0.0.0.0")
    except ValueError:
        pass
    else:
        raise AssertionError("Local agent must refuse non-loopback binding")


def test_open_app_uses_only_fixed_executable() -> None:
    with patch("jarvis.desktop.subprocess.Popen") as popen, patch("jarvis.desktop.os.name", "nt"):
        assert open_approved_app("notepad") == "Opened notepad."
        popen.assert_called_once_with(["notepad.exe"], close_fds=True)


def test_open_app_rejects_arbitrary_path() -> None:
    with patch("jarvis.desktop.os.name", "nt"):
        try:
            open_approved_app("C:/Windows/System32/cmd.exe")
        except ValueError:
            pass
        else:
            raise AssertionError("Arbitrary executable paths must be rejected")
