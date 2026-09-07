# J.A.R.V.I.S.

A modular personal AI assistant built from the ground up.

## Current status

J.A.R.V.I.S. currently has a small, testable Python core and an interactive command-line interface.

## Run locally

```bash
python -m jarvis
```

Type `exit` to shut down.

## Architecture roadmap

- `jarvis/core.py` — assistant orchestration and response layer
- `jarvis/memory.py` — persistent memory
- `jarvis/tools/` — safe tool integrations
- `jarvis/integrations/notion.py` — Notion integration
- `jarvis/voice/` — speech input/output
- `tests/` — automated tests

The project is intentionally starting with a clean foundation so integrations can be added without turning the codebase into one giant script.
