# AI Terminal RPG - PowerShell Installer
# This script installs AI Terminal RPG and configures PATH automatically
# 
# Usage:
#   powershell -ExecutionPolicy Bypass -File install_windows.ps1
#
# Or from PowerShell:
#   .\install_windows.ps1

param(
    [switch]$NoPrompt,
    [switch]$CreateShortcut
)

$ErrorActionPreference = "Stop"

# Colors
function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host $Text.PadLeft(($Text.Length + 30), ' ').PadRight(60, ' ') -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host "✓ $Text" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "✗ $Text" -ForegroundColor Red
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ $Text" -ForegroundColor Cyan
}

# Check if running on Windows
if ($env:OS -ne "Windows_NT") {
    Write-Error-Custom "This installer is for Windows only!"
    Write-Info "On macOS/Linux, use: pip install -e ."
    exit 1
}

Write-Header "AI TERMINAL RPG - WINDOWS INSTALLER"

# Check Python installation
Write-Info "Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python found: $pythonVersion"
} catch {
    try {
        $pythonVersion = python3 --version 2>&1
        Write-Success "Python found: $pythonVersion"
    } catch {
        Write-Error-Custom "Python is not installed or not in PATH!"
        Write-Info "Please install Python 3.8+ from https://www.python.org/downloads/"
        Write-Info "During installation, check 'Add Python to PATH'"
        exit 1
    }
}

# Get Python Scripts path
Write-Info "Getting Python Scripts path..."
$scriptsPath = python -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>&1
Write-Info "Scripts directory: $scriptsPath"

# Add to PATH (User scope - no admin required)
Write-Info "Adding Python Scripts to PATH..."
try {
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    
    if ($currentPath -notlike "*$scriptsPath*") {
        $newPath = "$currentPath;$scriptsPath"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Success "Added to User PATH"
        
        # Also update current session
        $env:PATH += ";$scriptsPath"
    } else {
        Write-Info "Already in PATH"
    }
} catch {
    Write-Error-Custom "Failed to modify PATH: $_"
    Write-Info "You may need to add it manually or run as Administrator"
}

# Install the package
Write-Info "Installing AI Terminal RPG..."
$installDir = Split-Path -Parent $MyInvocation.MyCommand.Path

try {
    & python -m pip install -e $installDir 2>&1 | Out-Null
    Write-Success "Package installed successfully"
} catch {
    Write-Error-Custom "Installation failed: $_"
    exit 1
}

# Verify installation
Write-Info "Verifying installation..."
try {
    $trpgPath = Join-Path $scriptsPath "trpg.exe"
    if (Test-Path $trpgPath) {
        Write-Success "trpg executable found at: $trpgPath"
    } else {
        # Check for .cmd
        $trpgCmd = Join-Path $scriptsPath "trpg.cmd"
        if (Test-Path $trpgCmd) {
            Write-Success "trpg script found at: $trpgCmd"
        } else {
            Write-Info "Executable not found, checking Python module..."
            python -c "import trpg; print('trpg module found at:', trpg.__file__)" 2>&1
        }
    }
} catch {
    Write-Info "Verification skipped"
}

# Create desktop shortcut
if ($CreateShortcut -or (-not $NoPrompt)) {
    Write-Host ""
    if (-not $NoPrompt) {
        $response = Read-Host "Create desktop shortcut? [y/N]"
    } else {
        $response = "y"
    }
    
    if ($response -eq "y" -or $response -eq "Y") {
        try {
            $desktop = [Environment]::GetFolderPath("Desktop")
            $shortcutPath = Join-Path $desktop "AI Terminal RPG.lnk"
            
            $WScriptShell = New-Object -ComObject WScript.Shell
            $shortcut = $WScriptShell.CreateShortcut($shortcutPath)
            $shortcut.TargetPath = "cmd.exe"
            $shortcut.Arguments = "/k trpg"
            $shortcut.WorkingDirectory = $installDir
            $shortcut.IconLocation = "cmd.exe,0"
            $shortcut.Save()
            
            Write-Success "Desktop shortcut created: $shortcutPath"
        } catch {
            Write-Error-Custom "Failed to create shortcut: $_"
        }
    }
}

# Completion message
Write-Header "INSTALLATION COMPLETE!"

Write-Success "AI Terminal RPG has been installed successfully!"
Write-Host ""
Write-Info "To play the game:"
Write-Host "  1. Close this window" -ForegroundColor White
Write-Host "  2. Open a NEW PowerShell or Command Prompt window" -ForegroundColor White
Write-Host "  3. Type: trpg" -ForegroundColor Yellow
Write-Host ""
Write-Info "Or run directly from this directory:"
Write-Host "  python -m trpg" -ForegroundColor Yellow
Write-Host ""
Write-Info "To update the game in the future:"
Write-Host "  trpg update" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan

# Ask to play now
if (-not $NoPrompt) {
    $response = Read-Host "`nDo you want to play now? [Y/n]"
    if ($response -ne "n" -and $response -ne "N") {
        Write-Host ""
        Write-Info "Starting game..."
        Write-Host ""
        python -m trpg
    }
}
