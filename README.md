# J.A.R.V.I.S.

Personal local-first AI assistant and operating layer.

## Ready-to-use Windows build

The current build is designed around one simple Windows flow:

1. Double-click `Install-JARVIS.bat` once.
2. Add a Gemini API key to `.env` only if you want cloud AI.
3. Restart Windows, or double-click `Start-JARVIS.bat` once to try it immediately.
4. Home Base opens automatically as a compact J.A.R.V.I.S. desktop companion.

After the first setup, Windows starts J.A.R.V.I.S. automatically when you sign in. The startup launcher runs through the project's local `.venv` with no console window.

To disable automatic startup, run `Disable-JARVIS-Startup.bat`. To enable it again, run `Enable-JARVIS-Startup.bat`.

Set `JARVIS_HOME_MODE=browser` in `.env` when you prefer the normal full browser presentation. The default is the compact desktop companion mode.

## What is included

- J.A.R.V.I.S. Understand -> Think -> Plan -> Act -> Verify -> Respond orchestration
- Home Base UI with live runtime state, command input, activity stream, and system status
- Compact desktop-companion presentation for the Windows launcher
- Automatic Windows sign-in startup with no terminal window
- Optional Gemini brain with a deterministic local fallback
- Persistent local memory
- Explicit tool/route registry and aliases
- Allowlisted Windows app and window control through the local loopback agent
- Allowlisted Edge/Google search and approved-site navigation
- Bounded web/file capabilities
- Optional n8n workflow bridge through one operator-configured Webhook endpoint
- Persistent device identity/capability metadata without storing credentials
- Local audit logging with common secret-field redaction
- Loopback-only local services and bounded request/response sizes
- Confirmation gates for state-changing computer and workflow actions
- Stale Local Agent protocol detection so an old process cannot silently satisfy the launcher
- Security headers and JSON-only command input on the Home Base gateway

The project deliberately does **not** enable arbitrary shell commands, arbitrary Python execution, unrestricted browser automation, unrestricted keyboard/mouse control, or arbitrary destination URLs.

PyAutoGUI, BeautifulSoup, and Selenium remain uninstalled until bounded adapters are deliberately designed.

## Commands

Examples:

```text
help
status
time
date
brain
remember favorite color = sea green
recall favorite color
memories
files
read README.md
diagnostics
devices
pc apps
pc sites
pc open edge
pc search weather
pc site github
pc window edge focus
workflow status
workflow <task>
exit
```

State-changing commands such as opening applications, controlling windows, navigating to approved sites, and triggering workflows require a one-time confirmation. J.A.R.V.I.S. reports the confirmation command in the response and expires unused confirmations automatically.

## Gemini

Gemini is optional. Keep the default `JARVIS_BRAIN_PROVIDER=deterministic` for a fully local fallback, or set:

```text
JARVIS_BRAIN_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
JARVIS_GEMINI_MODEL=gemini-3.8-flash
```

Never commit `.env` or real API keys to Git.

## n8n workflow bridge

J.A.R.V.I.S. can optionally hand a task to **one operator-configured n8n Webhook workflow**. The bridge stays disabled when `JARVIS_N8N_WEBHOOK_URL` is blank.

```text
JARVIS_N8N_WEBHOOK_URL=https://your-n8n-host/webhook/jarvis
JARVIS_N8N_WEBHOOK_TOKEN=optional-shared-secret
JARVIS_N8N_TIMEOUT_SECONDS=20
```

The endpoint must be HTTPS or loopback HTTP. Requests and responses are bounded, and the command itself cannot supply a destination URL.

## Tests

Run the standard-library test suite with:

```bash
python -m unittest discover -s tests -v
```

Voice mode is optional and depends on the installed speech/audio stack:

```bash
python main.py --voice
```

## Architecture

```text
Windows sign-in / manual launch
             |
             v
      Desktop Companion
             |
             v
Voice / Text / Home Base
             |
             v
J.A.R.V.I.S. Orchestrator
             |
     +-------+-------+
     |               |
 Brain / Memory   Policy / Confirmation
     |               |
     +-------+-------+
             |
        Tool Router
             |
   +---------+---------+---------+---------+
   |         |         |         |         |
Computer  Browser     Web      Devices  Cybersecurity
   |         |         |         |         |
   +---------+---------+---------+---------+
             |
       Verification
             |
           Audit
             |
          Response
```

The architecture treats model output and external web/workflow data as untrusted input. Tools are explicit capabilities behind policy checks rather than a general-purpose code execution surface.

## Security direction

J.A.R.V.I.S. is intended to grow into a serious cybersecurity assistant for systems and labs the operator owns or is authorized to test. The repository's `SECURITY.md` maps the current baseline to relevant secure-coding and AI-security issue classes.

It is intentionally not a credential-stealing, covert-monitoring, unrestricted intrusion, or arbitrary-code-execution framework.
