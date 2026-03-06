#!/bin/bash
# AI Terminal RPG - Universal Installer (Shell Wrapper)
# This script downloads and runs the universal Python installer
# Works on macOS, Linux, and Unix-like systems
#
# Usage:
#   ./install.sh
#   sudo ./install.sh  (if permission errors occur)

set -e

echo ""
echo "============================================================"
echo "  AI TERMINAL RPG - INSTALLER"
echo "============================================================"
echo ""

# Detect platform
UNAME=$(uname -s)
case "$UNAME" in
    Darwin*)    PLATFORM="macOS";;
    Linux*)     PLATFORM="Linux";;
    *)          PLATFORM="Unknown";;
esac

echo "Detected platform: $PLATFORM"
echo ""

# Check for Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python is not installed!"
    echo ""
    echo "Please install Python 3.8+ first:"
    echo "  macOS:  brew install python"
    echo "  Ubuntu: sudo apt install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo ""
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "Error: Python 3.8 or higher is required!"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if install.py exists
if [ -f "$SCRIPT_DIR/install.py" ]; then
    echo "Running universal installer..."
    echo ""
    $PYTHON_CMD "$SCRIPT_DIR/install.py" "$@"
else
    echo "Error: install.py not found!"
    echo "Make sure you're running this from the ai_terminal_rpg directory."
    exit 1
fi

echo ""
echo "============================================================"
echo "  Installation script finished."
echo "============================================================"
