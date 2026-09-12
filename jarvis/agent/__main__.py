"""Run the J.A.R.V.I.S. local agent with ``python -m jarvis.agent``."""

from __future__ import annotations

from .server import AGENT_ACTIONS, LocalAgentServer


if __name__ == "__main__":
    server = LocalAgentServer()
    print(f"J.A.R.V.I.S. Local Agent listening on http://{server.address[0]}:{server.address[1]}")
    print(f"Allowed actions: {', '.join(sorted(AGENT_ACTIONS))}")
    print("Remote shell: disabled")
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nJ.A.R.V.I.S. Local Agent stopped.")
    finally:
        server.stop()
