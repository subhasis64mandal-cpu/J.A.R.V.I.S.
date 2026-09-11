from jarvis.brain import Brain
from jarvis.context import ContextBuilder
from jarvis.control import HomeControl
from jarvis.decision import DecisionEngine
from jarvis.events import EventBus
from jarvis.homebase import HomeBase
from jarvis.memory import MemoryStore
from main import build_router, handle_command


def test_explicit_memory_command_round_trip(tmp_path) -> None:
    homebase = HomeBase.load()
    memory = MemoryStore(tmp_path / "memory.json")
    router = build_router(homebase, memory)
    brain = Brain()
    decision = DecisionEngine(brain, router)
    context = ContextBuilder(memory)
    events = EventBus()
    control = HomeControl(homebase)

    response, running = handle_command(router, brain, decision, context, control, "remember favorite color = blue", events)
    assert running is True
    assert "Remembered" in response
    assert memory.recall("favorite color").value == "blue"
