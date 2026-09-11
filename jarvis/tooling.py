"""Small introspection helpers for the J.A.R.V.I.S. tool plane."""

from __future__ import annotations

from jarvis.registry import ToolRegistry


def describe_registry(registry: ToolRegistry) -> tuple[dict[str, object], ...]:
    """Return UI-safe metadata without exposing handler implementation details."""
    return tuple(
        {
            "name": tool.name,
            "description": tool.description,
            "aliases": list(tool.aliases),
            "category": tool.category,
            "requires_confirmation": tool.requires_confirmation,
        }
        for tool in registry.list_tools()
    )
