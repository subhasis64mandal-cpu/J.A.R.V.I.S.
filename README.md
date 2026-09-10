# J.A.R.V.I.S.

Personal modular AI assistant project.

## v0.1

The first foundation is intentionally small and safe:

- deterministic command router
- tool registration system
- time/date/status tools
- clean package structure
- executable local entry point
- no API keys committed to the repository
- no computer-control or browser-automation packages installed yet

## Run

```bash
python main.py
```

Then try:

```text
time
date
status
help
exit
```

## Architecture direction

```text
User
  -> Voice/Text Interface
  -> AI Brain
  -> Tool Router
  -> Tools
       |-- Computer
       |-- Web
       |-- Files
       |-- System
       |-- Memory
       `-- Devices
```

PyAutoGUI, BeautifulSoup, and Selenium are planned for the tool layer later; they are deliberately **not installed yet**.
