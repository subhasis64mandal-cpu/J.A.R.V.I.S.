"""Command-line entry point for J.A.R.V.I.S."""

import argparse

from .core import Jarvis
from .web import run as run_web


def main() -> None:
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. personal assistant")
    parser.add_argument("--web", action="store_true", help="start the local chat interface")
    args = parser.parse_args()

    if args.web:
        run_web()
        return

    assistant = Jarvis()
    print(f"{assistant.name} online. Type 'exit' to shut down.")
    while True:
        try:
            message = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if message.strip().lower() == "exit":
            break
        print(f"{assistant.name}: {assistant.respond(message)}")


if __name__ == "__main__":
    main()
