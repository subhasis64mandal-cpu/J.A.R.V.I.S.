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

Current allowlisted actions include system inspection plus approved desktop/browser-launch actions:

- `time`
- `date`
- `status`
- `machine`
- `hostname`
- `apps`
- `open_app` for Notepad, Calculator, Paint, or Microsoft Edge
- `google_search`, which opens the query in Microsoft Edge on Google

From the J.A.R.V.I.S. text interface, examples are:

```text
pc apps
pc open edge
pc search latest science news
```

## Safety boundary

The agent is intentionally loopback-only. Desktop control is allowlisted and uses fixed application targets. Google search builds a Google HTTPS search URL from the supplied search text; it does not accept arbitrary executable paths or shell commands.

The agent does not provide arbitrary shell execution, arbitrary Python execution, file writes, free-form executable paths, or LAN/internet exposure. Rich browser automation and mouse/keyboard control remain separate future capabilities.

Do not expose port `8766` to the LAN or internet.
