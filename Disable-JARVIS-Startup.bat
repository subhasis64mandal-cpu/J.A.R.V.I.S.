@echo off
setlocal
cd /d "%~dp0"
set "JARVIS_PY=%~dp0.venv\Scripts\python.exe"
if not exist "%JARVIS_PY%" (
  echo J.A.R.V.I.S. is not installed yet.
  pause
  exit /b 1
)
"%JARVIS_PY%" -m jarvis.startup remove
pause
