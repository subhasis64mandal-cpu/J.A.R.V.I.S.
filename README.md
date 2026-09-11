# J.A.R.V.I.S.

Personal modular AI assistant project built toward a personal operating-system-style agent.

## v0.3 architecture

```text
Input (text / voice / Home Base)
        |
        v
      Brain
        |
        v
 Decision Engine
        |
        v
 Context + Memory
        |
        v
  Tool Registry
        |
        v
 Execution Policy
        |
        v
 Approved Capability
        |
        v
    Event Bus
        |
        v
    Home Base UI
```

## Active read-only capabilities

- `time`, `date`, `status`, `system`
- `web <http(s) URL>` — bounded text retrieval
- `files` — workspace listing
- `read <path>` — workspace-scoped file reading
- `remember`, `recall`, `memories`

The Home Base provides a continuously animated interface with runtime state and capability observability.

Computer control, browser automation, paired-device control, and other state-changing actions remain staged until their specific policy and adapter contracts are implemented.

PyAutoGUI, BeautifulSoup, and Selenium are intentionally not installed yet.

## Run

```bash
python main.py
```

Optional voice mode:

```bash
python main.py --voice
```

Tests:

```bash
python -m unittest discover -s tests -v
```

## Safety direction

Tools are explicit capabilities, not arbitrary code execution. Provider/LLM output is a proposal, never executable code. State-changing actions will require explicit registration, risk policy, and confirmation where appropriate.

API keys and passwords stay outside the repository, using environment variables or a proper secrets store for future external services.
