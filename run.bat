@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment missing. Run setup_and_run.bat first.
  pause
  exit /b 1
)
if not exist "model\url_classifier.joblib" (
  echo Model missing. Training the synthetic demo model first...
  ".venv\Scripts\python.exe" train_model.py
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" app.py
goto end
:failed
echo Training failed. Review the terminal output.
pause
:end
endlocal
