from jarvis.registry import ToolRegistry, ToolSpec
from jarvis.tooling import describe_registry


def test_describe_registry_hides_handler_details() -> None:
    registry = ToolRegistry()
    registry.register(ToolSpec("demo", "Demo tool", lambda _: "ok", aliases=("d",), category="test"))
    metadata = describe_registry(registry)
    assert metadata[0]["name"] == "demo"
    assert metadata[0]["aliases"] == ["d"]
    assert "handler" not in metadata[0]
