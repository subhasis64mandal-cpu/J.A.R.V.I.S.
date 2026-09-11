# J.A.R.V.I.S. Architecture

## North-star model

J.A.R.V.I.S. is a local-first personal agent operating above individual tools and devices.

```text
Input / Voice / UI
        |
      Brain
        |
   Decision Engine
        |
 Context + Memory
        |
 Tool Registry + Execution Policy
        |
  +-----+--------+---------+--------+
  |     |        |         |        |
 Web Browser Computer     Files   Devices
  |     |        |         |        |
  +-----+--------+---------+--------+
        |
      Events
        |
    Home Base UI
```

## Boundaries

- Brain interprets intent; it does not directly execute operating-system actions.
- Decision Engine proposes an explicit action and reason.
- Tool Registry is the allowlist of executable capabilities.
- Execution Policy applies risk and confirmation rules.
- Home Base owns configuration, module status, UI transport, and policy visibility.
- Device Registry stores device identity and capability metadata, never credentials.
- EventBus is the shared runtime signal path for UI state and observability.

## Future tool rollout

`system` is currently the only operational capability in the catalog. Computer, web, browser, files, and devices are staged as explicit capabilities and can be implemented one at a time.

PyAutoGUI, BeautifulSoup, and Selenium remain intentionally uninstalled until their corresponding tool boundaries are implemented and tested.

## Safety invariants

1. No arbitrary shell command execution through the assistant.
2. No arbitrary Python execution through user prompts.
3. High-risk tools can require explicit confirmation.
4. Confirmations are single-use.
5. Local UI gateway defaults to loopback.
6. Context sent to providers is bounded rather than the full memory store.
