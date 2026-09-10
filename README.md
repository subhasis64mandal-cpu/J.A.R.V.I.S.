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
  `-- Device Tools
```

### Safety direction

Tools will be explicit capabilities, not arbitrary code execution. Actions that can change files, applications, devices, or other external state will use allowlists and confirmation gates where appropriate.

PyAutoGUI, BeautifulSoup, and Selenium are planned for the tool layer later; they are deliberately **not installed yet**.

API keys and passwords must stay outside the repository, using environment variables or a proper secrets store when external AI/web services are added.
