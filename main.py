"""J.A.R.V.I.S. v0.1 — local assistant core with optional voice I/O."""

from __future__ import annotations

import argparse

from jarvis.router import Router
from jarvis.tools import get_date, get_time, system_status
from jarvis.voice import VoiceInterface, VoiceUnavailable


def build_router() -> Router:
    router = Router()
    router.register("time", "Show the current time", get_time)
    router.register("date", "Show today's date", get_date)
    router.register("status", "Show assistant status", system_status)
    return router


def handle_command(router: Router, command: str) -> tuple[str, bool]:
    normalized = command.strip().lower()
    if normalized in {"exit", "quit", "shutdown jarvis"}:
        return "Standing by.", False
    if normalized == "help":
        return router.help_text(), True
    return router.route(command), True


def run_text(router: Router) -> None:
    print("J.A.R.V.I.S. v0.1 — online")
    print("Text mode. Type 'help' for commands or 'exit' to quit.")

    while True:
        try:
            command = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nJ.A.R.V.I.S. > Session ended.")
            return

        response, keep_running = handle_command(router, command)
        print(f"J.A.R.V.I.S. > {response}")
        if not keep_running:
            return


def run_voice(router: Router) -> None:
    voice = VoiceInterface()
    voice.speak("J.A.R.V.I.S. online.")

    while True:
        try:
            command = voice.listen()
        except VoiceUnavailable as exc:
            print(f"Voice error: {exc}")
            return

        if not command:
            continue

        print(f"You > {command}")
        response, keep_running = handle_command(router, command)
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

    router = build_router()

    if args.voice:
        try:
            run_voice(router)
        except VoiceUnavailable as exc:
            print(f"Voice mode unavailable: {exc}")
            print("Falling back to text mode.")
            run_text(router)
    else:
        run_text(router)


if __name__ == "__main__":
    main()
