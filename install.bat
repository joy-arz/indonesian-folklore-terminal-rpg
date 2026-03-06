@echo off
REM AI Terminal RPG - Windows Installer (Batch Wrapper)
REM This script runs the universal Python installer
REM
REM Usage:
REM   install.bat
REM   (Right-click → Run as Administrator for system-wide install)

echo.
echo ============================================================
echo   AI TERMINAL RPG - WINDOWS INSTALLER
echo ============================================================
echo.

REM Check for Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo During installation, check "Add Python to PATH"
    pause
    exit /b 1
)

echo Using Python:
python --version
echo.

REM Get the directory of this script
set "SCRIPT_DIR=%~dp0"

REM Check if install.py exists
if exist "%SCRIPT_DIR%install.py" (
    echo Running universal installer...
    echo.
    python "%SCRIPT_DIR%install.py" %*
) else (
    echo Error: install.py not found!
    echo Make sure you're running this from the ai_terminal_rpg directory.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Installation script finished.
echo ============================================================
echo.
pause
