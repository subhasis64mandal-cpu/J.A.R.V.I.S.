"""J.A.R.V.I.S. — Home Base + deterministic brain + explicit tool routing."""

from __future__ import annotations

import argparse

from jarvis.brain import Brain
from jarvis.control import HomeControl
from jarvis.homebase import HomeBase, HomeBaseError
from jarvis.router import Router
from jarvis.tools import get_date, get_time, system_status
from jarvis.voice import VoiceInterface, VoiceUnavailable


def build_router(homebase: HomeBase) -> Router:
    router = Router(homebase)
    router.register("time", "Show the current time", get_time, aliases=("clock",))
    router.register("date", "Show today's date", get_date, aliases=("day",))
    router.register("status", "Show assistant status", system_status, aliases=("health",))
    return router


def handle_command(
    router: Router,
    brain: Brain,
    home_control: HomeControl,
    command: str,
) -> tuple[str, bool]:
    normalized = command.strip().lower()
    if normalized in {"exit", "quit", "goodbye", "shutdown jarvis"}:
        return "Standing by.", False
    if normalized == "help":
        return router.help_text() + "\n\n" + home_control.help_text(), True

    # Home Base is a separate control plane. Only commands declared in
    # homebase/commands.json reach it; arbitrary shell commands are never passed through.
    if normalized == "home" or normalized.startswith("home "):
        home_command = normalized.removeprefix("home").strip()
        return home_control.execute(home_command), True

    understood = brain.understand(command)
    if understood is not None:
        if understood.command == "help":
            return router.help_text() + "\n\n" + home_control.help_text(), True
        command = brain.normalize(command)

    return router.route(command), True


def run_text(router: Router, brain: Brain, home_control: HomeControl, homebase: HomeBase) -> None:
    print(f"{homebase.assistant_name()} — online")
    print("Home Base: loaded | Text mode. Try 'home status', 'home modules', 'help', or 'exit'.")

    while True:
        try:
            command = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nJ.A.R.V.I.S. > Session ended.")
            return

        response, keep_running = handle_command(router, brain, home_control, command)
        print(f"J.A.R.V.I.S. > {response}")
        if not keep_running:
            return


def run_voice(router: Router, brain: Brain, home_control: HomeControl, homebase: HomeBase) -> None:
    voice = VoiceInterface()
    voice.speak(f"{homebase.assistant_name()} online. Home Base loaded.")

    while True:
        try:
            command = voice.listen()
        except VoiceUnavailable as exc:
            print(f"Voice error: {exc}")
            return

        if not command:
            continue

        print(f"You > {command}")
        response, keep_running = handle_command(router, brain, home_control, command)
        print(f"J.A.R.V.I.S. > {response}")
        voice.speak(response)
        if not keep_running:
            return


def main() -> None:
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. local assistant")
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Use the optional microphone + speech output interface",
    )
    args = parser.parse_args()

    try:
        homebase = HomeBase.load()
        home_control = HomeControl(homebase)
    except HomeBaseError as exc:
        print(f"Home Base error: {exc}")
        return

    router = build_router(homebase)
    brain = Brain()

    if args.voice:
        try:
            run_voice(router, brain, home_control, homebase)
        except VoiceUnavailable as exc:
            print(f"Voice mode unavailable: {exc}")
            print("Falling back to text mode.")
            run_text(router, brain, home_control, homebase)
    else:
        run_text(router, brain, home_control, homebase)


if __name__ == "__main__":
    main()
