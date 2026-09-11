# J.A.R.V.I.S. Home Base

Home Base is the repository-controlled control plane for J.A.R.V.I.S.

It is intentionally independent of the web, browser automation, PyAutoGUI, Bash, and external AI providers. Those are future capabilities that plug into this core.

## What Home Base owns

- identity and runtime metadata
- enabled capabilities
- safety policy defaults
- persistent configuration
- planned modules
- a stable place for future state and memory adapters
- local runtime observability for the Home Base UI

## Current capability surface

- `system` — read-only host diagnostics
- `files` — workspace-scoped read/list operations
- `web` — bounded HTTP(S) text retrieval

Computer, browser, and device control are still staged behind explicit policies and adapters.

## Design rule

Home Base stores **what J.A.R.V.I.S. is configured to do**, not secrets and not arbitrary executable commands.

Never commit API keys, passwords, access tokens, or private credentials here.

## Layout

```text
homebase/
├── README.md
├── config.json
├── modules.json
├── schema.json
└── tool_catalog.json
```

Future runtime components can read this configuration through dedicated adapters without giving configuration files permission to execute anything by themselves.
