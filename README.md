# J.A.R.V.I.S.

Personal modular AI assistant project.

## v0.2

J.A.R.V.I.S. now has the first real architecture layer between the user and executable tools:

- deterministic natural-language brain boundary
- explicit tool/route registry
- aliases for common commands
- safe refusal for unknown tools
- time/date/status tools
- optional voice input/output
- standard-library unit tests
- no API keys or passwords committed to the repository
- no computer-control or browser-automation packages installed yet

The current brain is intentionally local and deterministic. It is **not** the final AI model. It gives us a stable interface so a real model provider can be plugged in later without rewriting the tool layer.

## Run

```bash
python main.py
```

Try commands such as:

```text
What time is it?
Tell me the date
Are you online?
What can you do?
help
exit
```

Run the tests without third-party test packages:

```bash
python -m unittest discover -s tests -v
```

Optional voice mode remains available when the voice dependencies are installed:

```bash
python main.py --voice
```

## n8n workflow bridge

J.A.R.V.I.S. can optionally hand a task to **one operator-configured n8n Webhook workflow**. The integration is disabled unless `JARVIS_N8N_WEBHOOK_URL` is set.

Set the following environment variables locally (never commit the real values):

```text
JARVIS_N8N_WEBHOOK_URL=https://your-n8n-host/webhook/jarvis
JARVIS_N8N_WEBHOOK_TOKEN=optional-shared-secret
JARVIS_N8N_TIMEOUT_SECONDS=20
```

Then use:

```text
workflow <task>
n8n <task>
automate <task>
```

JARVIS sends a bounded JSON body containing the source and task text. The bridge does **not** accept arbitrary URLs from commands; endpoints must be HTTPS or loopback HTTP. Responses are size-limited before being returned to the assistant.

A practical first n8n workflow is a read-oriented automation that accepts the incoming `command` field, performs a bounded sequence of API or data steps, and returns a small JSON object such as `{"result":"..."}`. n8n Webhook nodes support production URLs and can be configured with authentication such as Header auth. See the n8n webhook documentation for the workflow-side configuration.

## Architecture

```text
User
  |
  v
Voice / Text Interface
  |
  v
AI Brain (currently deterministic; LLM comes later)
  |
  v
Tool Router / Registry
  |
  +-- Computer Tools
  +-- Web Tools
  +-- File Tools
  +-- System Tools
  +-- Memory Tools
  +-- n8n Workflow Bridge ----> n8n Webhook --> workflow nodes/integrations
  `-- Device Tools
```

### Safety direction

Tools will be explicit capabilities, not arbitrary code execution. Actions that can change files, applications, devices, or other external state will use allowlists and confirmation gates where appropriate.

The n8n bridge follows the same local-first principle: no arbitrary command execution, no user-supplied destination URLs, bounded request/response sizes, and secrets kept outside the repository.

PyAutoGUI, BeautifulSoup, and Selenium are planned for the tool layer later; they are deliberately **not installed yet**.

API keys and passwords must stay outside the repository, using environment variables or a proper secrets store when external AI/web services are added.
