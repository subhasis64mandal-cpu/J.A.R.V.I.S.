@echo off
setlocal
cd /d "%~dp0"

echo.
echo ============================================
echo        J.A.R.V.I.S. FIRST-TIME SETUP
echo ============================================
echo.

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>&1
  if %ERRORLEVEL%==0 (
    set "PY=python"
  ) else (
    echo Python 3 was not found on this PC.
    echo Install Python 3.10+ and run this installer again.
    pause
    exit /b 1
  )
)

if not exist "%~dp0.venv\Scripts\python.exe" (
  echo Creating J.A.R.V.I.S. virtual environment...
  %PY% -m venv .venv
  if errorlevel 1 goto :fail
)

set "JARVIS_PY=%~dp0.venv\Scripts\python.exe"

echo Installing J.A.R.V.I.S. dependencies...
"%JARVIS_PY%" -m pip install --upgrade pip
if errorlevel 1 goto :fail
"%JARVIS_PY%" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

if not exist "%~dp0.env" (
  copy /y "%~dp0.env.example" "%~dp0.env" >nul
  echo Created local .env from .env.example.
  echo Add your own Gemini key there only if you want cloud AI.
)

echo.
echo Enabling automatic J.A.R.V.I.S. startup at Windows sign-in...
"%JARVIS_PY%" -m jarvis.startup install
if errorlevel 1 goto :fail

echo.
echo ============================================
echo SETUP COMPLETE
echo ============================================
echo.
echo J.A.R.V.I.S. will now start automatically when you sign in to Windows.
echo Home Base opens as a compact desktop companion.
echo You can still double-click Start-JARVIS.bat to launch it manually.
echo To disable automatic startup, run Disable-JARVIS-Startup.bat.
echo Your local memory/state stays in the ignored .jarvis folder.
echo.
pause
exit /b 0

:fail
echo.
echo J.A.R.V.I.S. setup failed. No project files were changed beyond the local .venv/.env setup.
echo.
pause
exit /b 1
