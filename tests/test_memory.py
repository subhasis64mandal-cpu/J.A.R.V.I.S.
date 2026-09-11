from jarvis.context import ContextBuilder
from jarvis.memory import MemoryStore


def test_memory_round_trip(tmp_path) -> None:
    store = MemoryStore(tmp_path / "memory.json")
    store.remember("preferred name", "JARVIS")
    assert store.recall("preferred name").value == "JARVIS"


def test_context_is_bounded(tmp_path) -> None:
    store = MemoryStore(tmp_path / "memory.json")
    for index in range(6):
        store.remember(f"fact {index}", "shared context")
    context = ContextBuilder(store, max_memories=2).build("shared context", runtime_state="thinking")
    assert len(context.memories) == 2
    assert context.runtime_state == "thinking"
