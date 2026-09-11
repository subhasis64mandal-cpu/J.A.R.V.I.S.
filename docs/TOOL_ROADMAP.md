# J.A.R.V.I.S. tool roadmap

The tool system is intentionally staged. Every capability must have an explicit registry entry, capability metadata, execution risk, tests, and Home Base observability before it becomes active.

## Available now

- **system** — read-only host diagnostics.
- **files** — read/list inside the J.A.R.V.I.S. workspace only; no writes and no path traversal.
- **web** — bounded HTTP(S) GET for text resources; no arbitrary process execution and no browser scripting.

## Next integrations

1. **browser** — Selenium-backed browser workflows behind explicit allowlists and confirmation for state-changing actions.
2. **computer** — PyAutoGUI-backed desktop control behind target/action allowlists and confirmation gates.
3. **web parsing** — BeautifulSoup parsing for fetched HTML, with bounded input and output sizes.
4. **devices** — paired-device registry plus authenticated transport; each device advertises explicit capabilities.
5. **Android** — phone-first transport adapter after device identity, pairing, and permission contracts are stable.

## Non-negotiable invariants

- No arbitrary shell execution from model output.
- No arbitrary Python execution from model output.
- LLM/provider output is a proposal, never executable code.
- Control/write actions require explicit tool registration and risk policy.
- Home Base is the control plane, not an unrestricted command shell.
- Optional third-party automation packages stay absent until their specific capability is ready.
