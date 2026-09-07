"""Command-line entry point for J.A.R.V.I.S."""

from .core import Jarvis


def main() -> None:
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
