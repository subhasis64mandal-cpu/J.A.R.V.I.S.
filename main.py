"""J.A.R.V.I.S. — orchestrated Home Base, brain, memory, decisions and tools."""

from __future__ import annotations

import argparse

from jarvis.brain import Brain
from jarvis.context import ContextBuilder
from jarvis.control import HomeControl
from jarvis.decision import DecisionEngine
from jarvis.events import EventBus
from jarvis.gateway import HomeBaseGateway
from jarvis.homebase import HomeBase, HomeBaseError
from jarvis.memory import MemoryStore
from jarvis.router import Router
from jarvis.tools import get_date, get_time, system_status
from jarvis.voice import VoiceInterface, VoiceUnavailable


def build_router(homebase: HomeBase, memory: MemoryStore) -> Router:
    router = Router(homebase)
    router.register("time", "Show the current time", get_time, aliases=("clock",))
    router.register("date", "Show today's date", get_date, aliases=("day",))
    router.register("status", "Show assistant status", system_status, aliases=("health",))

    def remember(argument: str) -> str:
        if "=" not in argument:
            return "Use: remember key = value"
        key, value = argument.split("=", 1)
        item = memory.remember(key, value)
        return f"Remembered '{item.key}'."

    def recall(argument: str) -> str:
        item = memory.recall(argument)
        return f"{item.key}: {item.value}" if item else "I don't have that in memory."

    def memories(_: str) -> str:
        items = memory.all()
        if not items:
            return "Memory is empty."
        return "\n".join(f"- {item.key}: {item.value}" for item in items[-10:])

    router.register("remember", "Store an explicit fact locally", remember, aliases=("memorize",))
    router.register("recall", "Recall one stored fact", recall, aliases=("remembered",))
    router.register("memories", "List recent stored facts", memories, aliases=("memory",))
    return router


def handle_command(router: Router, brain: Brain, decision: DecisionEngine, context: ContextBuilder, home_control: HomeControl, command: str, events: EventBus) -> tuple[str, bool]:
    normalized = command.strip().lower()
    events.publish("assistant.state", state="thinking", input=command)
    runtime_context = context.build(command, runtime_state="thinking")
    proposal = decision.decide(command)
    events.publish("assistant.decision", action=proposal.action, target=proposal.target, confidence=proposal.confidence, reason=proposal.reason, context=runtime_context.as_system_context())

    if normalized in {"exit", "quit", "goodbye", "shutdown jarvis"}:
        events.publish("assistant.state", state="idle")
        return "Standing by.", False
    if normalized == "help":
        response = router.help_text() + "\n\n" + home_control.help_text()
        events.publish("assistant.state", state="speaking")
        return response, True
    if normalized == "home" or normalized.startswith("home "):
        home_command = normalized.removeprefix("home").strip()
        response = home_control.execute(home_command)
        events.publish("assistant.state", state="speaking")
        return response, True

    if proposal.action == "HOME":
        response = home_control.execute(proposal.target or "status")
    else:
        command = brain.normalize(command)
        response = router.route(command)
    events.publish("assistant.state", state="speaking")
    return response, True


def run_text(router: Router, brain: Brain, decision: DecisionEngine, context: ContextBuilder, home_control: HomeControl, homebase: HomeBase, events: EventBus) -> None:
    print(f"{homebase.assistant_name()} — online")
    print("Home Base: loaded | Text mode. Try 'remember name = JARVIS', 'recall name', 'home status', or 'help'.")
    events.publish("assistant.state", state="idle")
    while True:
        try:
            command = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            events.publish("assistant.state", state="idle")
            print("\nJ.A.R.V.I.S. > Session ended.")
            return
        response, keep_running = handle_command(router, brain, decision, context, home_control, command, events)
        print(f"J.A.R.V.I.S. > {response}")
        if not keep_running:
            return
        events.publish("assistant.state", state="idle")


def run_voice(router: Router, brain: Brain, decision: DecisionEngine, context: ContextBuilder, home_control: HomeControl, homebase: HomeBase, events: EventBus) -> None:
    voice = VoiceInterface()
    voice.speak(f"{homebase.assistant_name()} online. Home Base loaded.")
    events.publish("assistant.state", state="idle")
    while True:
        try:
            events.publish("assistant.state", state="listening")
            command = voice.listen()
        except VoiceUnavailable as exc:
            print(f"Voice error: {exc}")
            return
        if not command:
            continue
        print(f"You > {command}")
        response, keep_running = handle_command(router, brain, decision, context, home_control, command, events)
        print(f"J.A.R.V.I.S. > {response}")
        events.publish("assistant.state", state="speaking")
        voice.speak(response)
        if not keep_running:
            return
        events.publish("assistant.state", state="idle")


def main() -> None:
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. local assistant")
    parser.add_argument("--voice", action="store_true", help="Use the optional microphone + speech output interface")
    args = parser.parse_args()
    try:
        homebase = HomeBase.load()
        home_control = HomeControl(homebase)
    except HomeBaseError as exc:
        print(f"Home Base error: {exc}")
        return

    memory = MemoryStore()
    router = build_router(homebase, memory)
    brain = Brain()
    decision = DecisionEngine(brain, router)
    context = ContextBuilder(memory)
    events = EventBus()
    gateway = HomeBaseGateway(events, lambda command: handle_command(router, brain, decision, context, home_control, command, events)[0])
    gateway.start()
    print(f"Home Base UI bridge: {gateway.address}")

    try:
        if args.voice:
            try:
                run_voice(router, brain, decision, context, home_control, homebase, events)
            except VoiceUnavailable as exc:
                print(f"Voice mode unavailable: {exc}")
                print("Falling back to text mode.")
                run_text(router, brain, decision, context, home_control, homebase, events)
        else:
            run_text(router, brain, decision, context, home_control, homebase, events)
    finally:
        gateway.stop()


if __name__ == "__main__":
    main()
