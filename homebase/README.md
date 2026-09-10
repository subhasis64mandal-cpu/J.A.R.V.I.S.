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

## Design rule

Home Base stores **what J.A.R.V.I.S. is configured to do**, not secrets and not arbitrary executable commands.

Never commit API keys, passwords, access tokens, or private credentials here.

## Layout

```text
homebase/
├── README.md
├── config.json
└── schema.json
```

Future runtime components can read this configuration through a dedicated adapter without giving the configuration file permission to execute anything by itself.
