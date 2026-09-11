# J.A.R.V.I.S. architecture

## Control flow

1. Input arrives from text, voice, or Home Base.
2. `Brain` normalizes deterministic intents and exposes the provider boundary.
3. `ContextBuilder` selects a bounded set of relevant memories and runtime state.
4. `DecisionEngine` proposes an explicit action; it does not execute code.
5. `Router` resolves only registered capabilities.
6. `ExecutionPolicy` is the future gate for state-changing tools and confirmations.
7. `EventBus` publishes state/decision telemetry to Home Base.

## Capability tiers

### Tier 1 — read-only

System diagnostics, scoped workspace reads, and bounded HTTP(S) retrieval.

### Tier 2 — controlled automation

Browser and desktop automation. These require explicit target/action boundaries, cancellation, and confirmation for state-changing operations.

### Tier 3 — device orchestration

Only paired devices with explicit identities and advertised capabilities may be addressed.

## Design rule

The model is never the authority to execute arbitrary code. It may propose an action, but the deterministic control plane decides whether that action exists, is enabled, is safe for the current policy, and may execute.
