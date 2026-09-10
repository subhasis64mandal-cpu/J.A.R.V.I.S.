"""J.A.R.V.I.S. v0.1 — first working local shell."""

from jarvis.router import Router
from jarvis.tools import get_date, get_time, system_status


def build_router() -> Router:
    router = Router()
    router.register("time", "Show the current time", get_time)
    router.register("date", "Show today's date", get_date)
    router.register("status", "Show assistant status", system_status)
    return router


def main() -> None:
    router = build_router()
    print("J.A.R.V.I.S. v0.1 — online")
    print("Type 'help' for commands or 'exit' to quit.")

    while True:
        try:
            command = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nJ.A.R.V.I.S. > Session ended.")
            break

        if command.lower() in {"exit", "quit", "shutdown jarvis"}:
            print("J.A.R.V.I.S. > Standing by.")
            break
        if command.lower() == "help":
            print(router.help_text())
            continue

        print(f"J.A.R.V.I.S. > {router.route(command)}")


if __name__ == "__main__":
    main()
