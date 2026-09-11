from __future__ import annotations

import pytest

from jarvis.agent.client import LocalAgentClient


def test_client_requires_exact_loopback_endpoint() -> None:
    with pytest.raises(ValueError):
        LocalAgentClient("http://0.0.0.0:8766")


def test_client_rejects_unknown_actions_before_network_call() -> None:
    client = LocalAgentClient()
    with pytest.raises(ValueError):
        client.action("shell", "whoami")


def test_client_rejects_oversized_arguments() -> None:
    client = LocalAgentClient()
    with pytest.raises(ValueError):
        client.action("status", "x" * 1025)
