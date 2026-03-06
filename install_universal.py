#!/usr/bin/env python3
"""
AI Terminal RPG - Universal One-Command Installer

This is the ONLY installation script you need.
It works on Windows, macOS, and Linux automatically.

USAGE:
  macOS/Linux:  sudo python3 install_universal.py
  Windows:      python install_universal.py  (run as Administrator)

The installer will:
  ✓ Install all dependencies
  ✓ Configure PATH automatically
  ✓ Create the 'trpg' command
  ✓ Work on any drive (C:, D:, etc.)
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path

# ============================================================================
# AUTO-ELEVATION FOR WINDOWS (Run as Administrator)
# ============================================================================

def is_admin():
    """Check if running as administrator (Windows)."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    """Restart script as administrator (Windows)."""
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
    sys.exit(0)

# ============================================================================
# COLORED OUTPUT
# ============================================================================

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

# ============================================================================
# PLATFORM DETECTION
# ============================================================================

def get_platform():
    """Detect the current platform."""
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'macos'
    else:
        return 'linux'

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

def get_python_paths():
    """Get Python scripts and packages paths."""
    import sysconfig
    return {
        'scripts': sysconfig.get_path('scripts'),
        'purelib': sysconfig.get_path('purelib')
    }

def add_to_path_windows(path):
    """Add path to Windows PATH (user level, no admin needed for user PATH)."""
    try:
        import winreg
        
        # Try user PATH first (no admin required)
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "Environment",
                0,
                winreg.KEY_ALL_ACCESS
            )
            
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                current_path = ""
            
            if path.upper() not in current_path.upper():
                new_path = f"{current_path};{path}" if current_path else path
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                print_success(f"Added to user PATH: {path}")
                
                # Notify Windows of PATH change
                HWND_BROADCAST = 0xFFFF
                WM_SETTINGCHANGE = 0x001A
                import ctypes
                ctypes.windll.user32.SendMessageTimeoutW(
                    HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 0, 5000
                )
            else:
                print_info(f"Already in user PATH: {path}")
            
            winreg.CloseKey(key)
            return True
            
        except PermissionError:
            print_warning("User PATH modification restricted, trying system PATH...")
        
        # Try system PATH (requires admin)
        if not is_admin():
            print_warning("Admin rights required for system PATH")
            return False
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_ALL_ACCESS
            )
            
            try:
                current_path, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_path = ""
            
            if path.upper() not in current_path.upper():
                new_path = f"{current_path};{path}" if current_path else path
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                print_success(f"Added to system PATH: {path}")
            
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            print_error(f"System PATH modification failed: {e}")
            return False
            
    except Exception as e:
        print_error(f"PATH modification failed: {e}")
        return False

def add_to_path_unix(path, shell_rc):
    """Add path to Unix shell configuration."""
    try:
        export_line = f'\nexport PATH="{path}:$PATH"\n'
        
        # Check if already present
        if shell_rc.exists():
            content = shell_rc.read_text()
            if path in content:
                print_info(f"Already in {shell_rc.name}: {path}")
                return True
        
        # Append to shell config
        with open(shell_rc, "a") as f:
            f.write(export_line)
        
        print_success(f"Added to {shell_rc.name}: {path}")
        print_info(f"Restart terminal or run: source {shell_rc}")
        return True
    except Exception as e:
        print_error(f"PATH modification failed: {e}")
        return False

def configure_path(scripts_path):
    """Configure PATH for the current platform."""
    platform = get_platform()
    
    if platform == 'windows':
        return add_to_path_windows(scripts_path)
    else:
        # Unix-like (macOS/Linux)
        home = Path.home()
        
        # Detect shell config
        shell = os.environ.get("SHELL", "")
        
        if "zsh" in shell or (home / ".zshrc").exists():
            shell_rc = home / ".zshrc"
        elif "bash" in shell or (home / ".bashrc").exists():
            shell_rc = home / ".bashrc"
        elif (home / ".profile").exists():
            shell_rc = home / ".profile"
        else:
            shell_rc = home / ".bashrc"
        
        return add_to_path_unix(scripts_path, shell_rc)

# ============================================================================
# INSTALLATION
# ============================================================================

def check_python():
    """Check Python version."""
    if sys.version_info < (3, 8):
        print_error("Python 3.8 or higher is required!")
        print_info(f"Current version: {sys.version.split()[0]}")
        print_info("Download from: https://www.python.org/downloads/")
        sys.exit(1)
    
    print_success(f"Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install required dependencies."""
    print_info("Installing dependencies...")
    
    script_dir = Path(__file__).parent.absolute()
    requirements = script_dir / "requirements.txt"
    
    try:
        if requirements.exists():
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements)],
                capture_output=True,
                text=True,
                check=True
            )
        else:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", 
                 "openai", "python-dotenv", "colorama"],
                capture_output=True,
                text=True,
                check=True
            )
        print_success("Dependencies installed")
    except subprocess.CalledProcessError as e:
        print_error(f"Dependency installation failed: {e.stderr}")
        sys.exit(1)

def install_package():
    """Install the game package."""
    print_info("Installing AI Terminal RPG...")
    
    script_dir = Path(__file__).parent.absolute()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(script_dir)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("AI Terminal RPG installed")
            return True
        else:
            # Fallback: manual copy
            print_warning("pip install failed, trying manual installation...")
            return manual_install(script_dir)
            
    except Exception as e:
        print_warning(f"Installation error: {e}")
        return manual_install(script_dir)

def manual_install(script_dir):
    """Manual installation by copying files."""
    import sysconfig
    purelib = Path(sysconfig.get_path('purelib'))
    scripts = Path(sysconfig.get_path('scripts'))
    
    trpg_source = script_dir / "trpg"
    trpg_dest = purelib / "trpg"
    
    try:
        # Copy package
        if trpg_dest.exists():
            shutil.rmtree(trpg_dest)
        shutil.copytree(trpg_source, trpg_dest)
        print_success(f"Package copied to: {trpg_dest}")
        
        # Create entry point
        create_entry_point(scripts)
        return True
        
    except Exception as e:
        print_error(f"Manual installation failed: {e}")
        return False

def create_entry_point(scripts_dir):
    """Create the 'trpg' command entry point."""
    platform = get_platform()
    
    if platform == 'windows':
        # Windows .cmd file
        cmd_file = scripts_dir / "trpg.cmd"
        with open(cmd_file, "w") as f:
            f.write("@echo off\n")
            f.write("title AI Terminal RPG\n")
            f.write(f'"{sys.executable}" -m trpg %*\n')
            f.write("pause\n")
        print_success(f"Created: {cmd_file}")
        
        # Also create .bat
        bat_file = scripts_dir / "trpg.bat"
        with open(bat_file, "w") as f:
            f.write("@echo off\n")
            f.write(f'"{sys.executable}" -m trpg %*\n')
        print_success(f"Created: {bat_file}")
        
    else:
        # Unix shell script
        sh_file = scripts_dir / "trpg"
        with open(sh_file, "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f'"{sys.executable}" -m trpg "$@"\n')
        os.chmod(sh_file, 0o755)
        print_success(f"Created: {sh_file}")

def create_shortcut():
    """Create desktop shortcut (optional)."""
    platform = get_platform()
    
    try:
        if platform == 'windows':
            desktop = Path.home() / "Desktop"
            if not desktop.exists():
                desktop = Path.home() / "OneDrive" / "Desktop"
            
            if desktop.exists():
                shortcut = desktop / "AI Terminal RPG.bat"
                with open(shortcut, "w") as f:
                    f.write("@echo off\n")
                    f.write("title AI Terminal RPG\n")
                    f.write('trpg\n')
                    f.write("pause\n")
                print_success(f"Desktop shortcut: {shortcut}")
                
        else:
            desktop = Path.home() / "Desktop"
            if not desktop.exists():
                desktop = Path.home() / "Bureau"
            
            if desktop.exists():
                shortcut = desktop / "AI Terminal RPG.sh"
                with open(shortcut, "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write("trpg\n")
                os.chmod(shortcut, 0o755)
                print_success(f"Desktop shortcut: {shortcut}")
                
    except Exception as e:
        print_warning(f"Shortcut creation failed: {e}")

def verify_installation():
    """Verify the installation works."""
    print_info("Verifying installation...")
    
    try:
        import trpg
        print_success(f"trpg module: {trpg.__file__}")
        print_success(f"Version: {getattr(trpg, '__version__', 'unknown')}")
        return True
    except ImportError as e:
        print_error(f"Verification failed: {e}")
        return False

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main installation function."""
    print_header("AI TERMINAL RPG - UNIVERSAL INSTALLER")
    
    platform = get_platform()
    print_info(f"Platform: {platform}")
    print_info(f"Python: {sys.version.split()[0]}")
    print_info(f"Installer: {Path(__file__).absolute()}")
    print()
    
    # Windows admin check
    if platform == 'windows' and not is_admin():
        print_warning("Windows requires Administrator privileges for full installation")
        print_info("Restarting as Administrator...")
        run_as_admin()
    
    # Check Python
    check_python()
    
    # Get paths
    paths = get_python_paths()
    print_info(f"Scripts: {paths['scripts']}")
    print_info(f"Packages: {paths['purelib']}")
    print()
    
    # Configure PATH first
    print_header("STEP 1/4: Configuring PATH")
    configure_path(paths['scripts'])
    print()
    
    # Install dependencies
    print_header("STEP 2/4: Installing Dependencies")
    install_dependencies()
    print()
    
    # Install package
    print_header("STEP 3/4: Installing Game")
    install_package()
    print()
    
    # Create shortcut
    print_header("STEP 4/4: Creating Shortcuts")
    create_shortcut()
    print()
    
    # Verify
    print_header("VERIFICATION")
    if verify_installation():
        print()
        print_header("INSTALLATION COMPLETE!")
        print()
        print_success("AI Terminal RPG is ready to play!")
        print()
        print_info("To play:")
        if platform == 'windows':
            print("  1. Close this window")
            print("  2. Open a NEW Command Prompt")
            print("  3. Type: trpg")
        else:
            print(f"  1. Run: source ~/.bashrc  (or restart terminal)")
            print("  2. Type: trpg")
        print()
        print_info("Or play now:")
        print(f"  {sys.executable} -m trpg")
        print()
        print("=" * 70)
        print()
        
        # Ask to play now
        try:
            response = input("Play now? [Y/n]: ").strip().lower()
            if response not in ["n", "no"]:
                print("\nStarting game...\n")
                from trpg.game import main
                main()
        except KeyboardInterrupt:
            print("\n\nRun 'trpg' to play anytime!")
        except Exception as e:
            print(f"\nError starting game: {e}")
            print(f"\nRun manually: {sys.executable} -m trpg")
    else:
        print()
        print_error("Installation may have issues")
        print_info(f"Try running manually: {sys.executable} -m trpg")

if __name__ == "__main__":
    main()
