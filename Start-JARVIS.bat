@echo off
setlocal
cd /d "%~dp0"

set "JARVIS_PY=%~dp0.venv\Scripts\python.exe"
if not exist "%JARVIS_PY%" set "JARVIS_PY=python"

if not exist "%~dp0.venv\Scripts\python.exe" (
  echo.
  echo J.A.R.V.I.S. is not installed in its local environment yet.
  echo Run Install-JARVIS.bat once, then double-click Start-JARVIS.bat.
  echo.
  pause
  exit /b 1
)

"%JARVIS_PY%" launch_jarvis.py
set "EXITCODE=%ERRORLEVEL%"
echo.
if not "%EXITCODE%"=="0" echo J.A.R.V.I.S. stopped with code %EXITCODE%.
pause
exit /b %EXITCODE%
