from __future__ import annotations

from jarvis.agent.server import LocalAgentServer, handle_action


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
