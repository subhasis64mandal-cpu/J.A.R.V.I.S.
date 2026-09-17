"""J.A.R.V.I.S. — local-first personal AI runtime."""

from __future__ import annotations

import argparse

from jarvis.agent.client import LocalAgentClient, LocalAgentUnavailable
from jarvis.audit import AuditLog
from jarvis.brain import Brain
from jarvis.context import ContextBuilder
from jarvis.control import HomeControl
from jarvis.decision import DecisionEngine
from jarvis.devices import Device, DeviceKind, DeviceRegistry
from jarvis.events import EventBus
from jarvis.gateway import HomeBaseGateway
from jarvis.homebase import HomeBase, HomeBaseError
from jarvis.memory import MemoryStore
from jarvis.n8n import N8nUnavailable, N8nWorkflowClient
from jarvis.orchestrator import Orchestrator
from jarvis.providers import provider_from_environment
from jarvis.router import Router
from jarvis.safe_tools import CapabilityError, fetch_web, host_diagnostics, list_files, read_file
from jarvis.tools import get_date, get_time, system_status
from jarvis.voice import VoiceInterface, VoiceUnavailable


def build_router(homebase: HomeBase, memory: MemoryStore, devices: DeviceRegistry | None = None) -> Router:
    router = Router(homebase)
    router.register("time", "Show the current time", get_time, aliases=("clock",))
    router.register("date", "Show today's date", get_date, aliases=("day",))
    router.register("status", "Show assistant status", system_status, aliases=("health",))

    agent = LocalAgentClient()
    n8n = N8nWorkflowClient()
    device_registry = devices or DeviceRegistry()

    def pc(argument: str) -> str:
        parts = argument.strip().split(maxsplit=1)
        action = parts[0].lower() if parts else "status"
        action_argument = parts[1] if len(parts) == 2 else ""
        aliases = {
            "open": "open_app",
            "search": "google_search",
            "site": "open_site",
            "navigate": "open_site",
            "go": "open_site",
            "window": "window",
            "win": "window",
        }
        action = aliases.get(action, action)
        try:
            response = agent.action(action, action_argument)
        except ValueError:
            return "Try: pc status, pc machine, pc apps, pc sites, pc open edge, pc search <query>, pc site youtube, or pc window <app> <action>."
        except LocalAgentUnavailable:
            return "The local J.A.R.V.I.S. agent is offline or unavailable."
        return response.result if response.ok else (response.error or "The local PC action failed safely.")

    router.register("pc", "Query or control approved Windows capabilities through the local agent", pc, aliases=("computer", "localpc"), capability="system")

    def workflow(argument: str) -> str:
        if argument.strip().lower() in {"", "status", "health"}:
            return n8n.status()
        try:
            return n8n.trigger(argument)
        except N8nUnavailable as exc:
            return f"n8n workflow unavailable: {exc}"

    router.register("workflow", "Trigger or inspect the operator-configured n8n workflow", workflow, aliases=("n8n", "automate"), capability="system")

    def files(argument: str) -> str:
        try:
            return list_files(argument)
        except (CapabilityError, OSError) as exc:
            return f"File access denied safely: {exc}"

    def read(argument: str) -> str:
        try:
            return read_file(argument)
        except (CapabilityError, OSError) as exc:
            return f"File read denied safely: {exc}"

    def web(argument: str) -> str:
        try:
            return fetch_web(argument)
        except (CapabilityError, OSError) as exc:
            return f"Web retrieval denied safely: {exc}"

    router.register("files", "List files inside the J.A.R.V.I.S. workspace", files, aliases=("ls",), capability="files")
    router.register("read", "Read a UTF-8 text file inside the J.A.R.V.I.S. workspace", read, aliases=("cat",), capability="files")
    router.register("web", "Fetch bounded text from an HTTP(S) URL", web, aliases=("fetch",), capability="web")
    router.register("diagnostics", "Show read-only host diagnostics", host_diagnostics, aliases=("diag",), capability="system")

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
        return "Memory is empty." if not items else "\n".join(f"- {item.key}: {item.value}" for item in items[-10:])

    router.register("remember", "Store an explicit fact locally", remember, aliases=("memorize",))
    router.register("recall", "Recall one stored fact", recall, aliases=("remembered",))
    router.register("memories", "List recent stored facts", memories, aliases=("memory",))

    def devices_command(_: str) -> str:
        return device_registry.list_text()

    router.register("devices", "Inspect paired device identities and advertised capabilities", devices_command, aliases=("device", "phones"), capability="system")

    def brain_status(_: str) -> str:
        provider = provider_from_environment().name
        return f"Configured brain provider: {provider}."

    router.register("brain", "Inspect the configured AI brain provider", brain_status, aliases=("ai",))
    return router


def handle_command(
    router: Router,
    brain: Brain,
    decision: DecisionEngine,
    context: ContextBuilder,
    home_control: HomeControl,
    command: str,
    events: EventBus,
    orchestrator: Orchestrator | None = None,
) -> tuple[str, bool]:
    runtime = orchestrator or Orchestrator(router, brain, decision, context, home_control, HomeBase.load(), events)
    return runtime.handle(command, source="text")


def run_text(
    router: Router,
    brain: Brain,
    decision: DecisionEngine,
    context: ContextBuilder,
    home_control: HomeControl,
    homebase: HomeBase,
    events: EventBus,
    orchestrator: Orchestrator | None = None,
) -> None:
    runtime = orchestrator or Orchestrator(router, brain, decision, context, home_control, homebase, events)
    print(f"{homebase.assistant_name()} — online")
    print("Home Base: loaded | Try 'pc apps', 'pc window edge focus', 'workflow status', 'devices', or 'help'.")
    events.publish("assistant.state", state="idle")
    while True:
        try:
            command = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            events.publish("assistant.state", state="idle")
            print("\nJ.A.R.V.I.S. > Session ended.")
            return
        response, keep_running = runtime.handle(command, source="text")
        print(f"J.A.R.V.I.S. > {response}")
        if not keep_running:
            return
        events.publish("assistant.state", state="idle")


def run_voice(
    router: Router,
    brain: Brain,
    decision: DecisionEngine,
    context: ContextBuilder,
    home_control: HomeControl,
    homebase: HomeBase,
    events: EventBus,
    orchestrator: Orchestrator | None = None,
) -> None:
    runtime = orchestrator or Orchestrator(router, brain, decision, context, home_control, homebase, events)
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
        response, keep_running = runtime.handle(command, source="voice")
        print(f"J.A.R.V.I.S. > {response}")
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
    devices = DeviceRegistry()
    local_id = "desktop-local"
    if devices.get(local_id) is None:
        try:
            devices.register(Device(local_id, "This PC", DeviceKind.DESKTOP, True, ("system", "approved-desktop")))
        except ValueError:
            pass
    else:
        try:
            devices.set_online(local_id, True)
        except ValueError:
            pass

    router = build_router(homebase, memory, devices)
    brain = Brain(provider=provider_from_environment())
    decision = DecisionEngine(brain, router)
    context = ContextBuilder(memory)
    events = EventBus()
    audit = AuditLog()
    orchestrator = Orchestrator(router, brain, decision, context, home_control, homebase, events, audit)

    gateway = HomeBaseGateway(
        events,
        lambda command: orchestrator.handle(command, source="homebase.ui")[0],
        runtime_info=orchestrator.runtime_info,
        activity_info=orchestrator.recent_activity,
        device_info=devices.list_text,
    )
    gateway.start()
    print(f"Home Base UI bridge: {gateway.address}")
    try:
        if args.voice:
            try:
                run_voice(router, brain, decision, context, home_control, homebase, events, orchestrator)
            except VoiceUnavailable as exc:
                print(f"Voice mode unavailable: {exc}")
                print("Falling back to text mode.")
                run_text(router, brain, decision, context, home_control, homebase, events, orchestrator)
        else:
            run_text(router, brain, decision, context, home_control, homebase, events, orchestrator)
    finally:
        try:
            devices.set_online(local_id, False)
        except ValueError:
            pass
        gateway.stop()


if __name__ == "__main__":
    main()
