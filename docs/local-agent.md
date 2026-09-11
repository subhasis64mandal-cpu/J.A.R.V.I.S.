# J.A.R.V.I.S. Local Agent

The local agent is the bridge between the J.A.R.V.I.S. runtime and the user's Windows machine.

## First bootstrap

From a clone of this repository on the Windows PC:

```powershell
python -m jarvis.agent
```

The agent listens only on `127.0.0.1:8766`.

Check it from another local terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8766/health
Invoke-RestMethod http://127.0.0.1:8766/capabilities
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8766/action -ContentType 'application/json' -Body '{"action":"machine"}'
```

Current allowlisted actions are `time`, `date`, `status`, `machine`, and `hostname`.

## Safety boundary

The agent is intentionally loopback-only and read-only in this first release. It does not provide arbitrary shell, arbitrary Python, file writes, browser control, desktop input, or remote network access.

Future control capabilities must be added as explicit actions behind J.A.R.V.I.S. execution policy and confirmation requirements where appropriate.

Do not expose port `8766` to the LAN or internet.
