@echo off
cd /d "%~dp0"
py main.py
if errorlevel 1 (
    echo.
    echo Python was not found in PATH. Try: python main.py
    pause
)
