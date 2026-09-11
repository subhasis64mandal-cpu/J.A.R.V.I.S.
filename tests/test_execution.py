from jarvis.execution import ExecutionPolicy
from jarvis.registry import ToolRegistry, ToolSpec


def test_safe_tool_executes_without_confirmation() -> None:
    registry = ToolRegistry()
    registry.register(ToolSpec("status", "status", lambda _: "ok"))
    policy = ExecutionPolicy(registry)

    result = policy.execute("status")

    assert result.ok is True
    assert result.message == "ok"


def test_confirmation_is_single_use() -> None:
    registry = ToolRegistry()
    registry.register(ToolSpec("control", "control", lambda _: "done", requires_confirmation=True))
    policy = ExecutionPolicy(registry)

    prepared = policy.prepare("control")
    assert prepared.requires_confirmation is True
    assert prepared.confirmation_token

    first = policy.execute("control", confirmation_token=prepared.confirmation_token)
    second = policy.execute("control", confirmation_token=prepared.confirmation_token)

    assert first.ok is True
    assert second.ok is False
    assert second.requires_confirmation is True
