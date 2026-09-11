"""Bounded context assembly for the Brain provider."""

from __future__ import annotations

from dataclasses import dataclass

from jarvis.memory import MemoryStore


@dataclass(frozen=True)
class Context:
    user_text: str
    memories: tuple[str, ...] = ()
    runtime_state: str = "idle"

    def as_system_context(self) -> str:
        lines = [f"Runtime state: {self.runtime_state}"]
        if self.memories:
            lines.append("Relevant remembered facts:")
            lines.extend(f"- {memory}" for memory in self.memories)
        return "\n".join(lines)


class ContextBuilder:
    """Build small bounded context; never dumps the full memory store into prompts."""

    def __init__(self, memory: MemoryStore, max_memories: int = 5) -> None:
        self.memory = memory
        self.max_memories = max(0, max_memories)

    def build(self, user_text: str, runtime_state: str = "idle") -> Context:
        matches = self.memory.search(user_text, limit=self.max_memories)
        memories = tuple(f"{item.key}: {item.value}" for item in matches)
        return Context(user_text=user_text, memories=memories, runtime_state=runtime_state)
