@echo off
setlocal
cd /d "%~dp0"
echo.
echo ================================================
echo  SENTINEL - Phishing URL and QR Code Detector
echo  Premium Dark Security SaaS Dashboard
echo ================================================
echo.
where py >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python launcher 'py' was not found.
  echo Install Python 3.10-3.12 from python.org and enable the launcher.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 goto failed
)
echo [2/4] Installing dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo [3/4] Training classifiers using the included SYNTHETIC DEMO dataset...
".venv\Scripts\python.exe" train_model.py
if errorlevel 1 goto failed
echo [4/4] Starting the local Flask app...
echo Open http://127.0.0.1:5000 in your browser. Press Ctrl+C to stop.
".venv\Scripts\python.exe" app.py
goto end
:failed
echo.
echo Setup failed. Read the error above, check your Python installation and internet connection, then retry.
pause
exit /b 1
:end
endlocal
