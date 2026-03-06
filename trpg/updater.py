"""
Auto-updater module for AI Terminal RPG.

This module handles:
- Checking GitHub for new versions
- Downloading and installing updates
- Backup before update
- Rollback on failure
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
import hashlib
from typing import Optional, Tuple
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError

# GitHub repository info
GITHUB_OWNER = "joy-arz"
GITHUB_REPO = "ai-terminal-rpg"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"

# Current version
CURRENT_VERSION = "2.0.0"


def get_current_version() -> str:
    """Get the current installed version."""
    try:
        from trpg import __version__
        return __version__
    except ImportError:
        return CURRENT_VERSION


def get_latest_version() -> Optional[str]:
    """
    Fetch the latest version from GitHub.
    
    Tries releases API first, then falls back to tags.
    
    Returns:
        Latest version string or None if fetch failed
    """
    try:
        # Try releases first
        releases_url = f"{GITHUB_API_URL}/releases/latest"
        with urlopen(releases_url, timeout=10) as response:
            data = json.loads(response.read().decode())
            tag = data.get("tag_name", "")
            if tag:
                return tag.lstrip("v")
    except Exception:
        pass
    
    try:
        # Fallback to tags
        tags_url = f"{GITHUB_API_URL}/tags"
        with urlopen(tags_url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data and len(data) > 0:
                tag = data[0].get("name", "")
                return tag.lstrip("v")
    except Exception as e:
        # Silent fail - will be reported by caller
        pass
    
    return None


def check_for_update(silent: bool = True) -> Tuple[bool, str, str]:
    """
    Check if a new version is available.

    Args:
        silent: If True, suppress error messages

    Returns:
        Tuple of (update_available, current_version, latest_version)
    """
    current = get_current_version()
    latest = get_latest_version()

    if not latest:
        if not silent:
            print("  Could not check for updates (no network or repo not found)")
        return False, current, "Unknown"

    # Compare versions
    def parse_version(v: str) -> tuple:
        try:
            return tuple(map(int, v.split(".")))
        except ValueError:
            return (0, 0, 0)

    current_tuple = parse_version(current)
    latest_tuple = parse_version(latest)

    return latest_tuple > current_tuple, current, latest


def get_download_url() -> Optional[str]:
    """Get the download URL for the latest release."""
    try:
        releases_url = f"{GITHUB_API_URL}/releases/latest"
        with urlopen(releases_url, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            # Look for source tarball
            tarball_url = data.get("tarball_url")
            if tarball_url:
                return tarball_url
            
            # Fallback to archive URL
            tag = data.get("tag_name", "main")
            return f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/archive/{tag}.tar.gz"
    except Exception:
        return None


def backup_current_installation() -> Optional[str]:
    """
    Create a backup of the current installation.
    
    Returns:
        Path to backup directory or None if failed
    """
    try:
        # Find package location
        import trpg
        package_dir = os.path.dirname(trpg.__file__)
        parent_dir = os.path.dirname(package_dir)
        
        # Create backup
        backup_name = f"trpg_backup_{get_current_version()}"
        backup_path = os.path.join(parent_dir, backup_name)
        
        if os.path.exists(backup_path):
            # Add timestamp to avoid conflicts
            import time
            backup_name = f"trpg_backup_{get_current_version()}_{int(time.time())}"
            backup_path = os.path.join(parent_dir, backup_name)
        
        shutil.copytree(package_dir, backup_path)
        print(f"  ✓ Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"  ✗ Failed to create backup: {e}")
        return None


def download_update() -> Optional[str]:
    """
    Download the latest version.
    
    Returns:
        Path to downloaded file or None if failed
    """
    download_url = get_download_url()
    if not download_url:
        print("  ✗ Could not get download URL")
        return None
    
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="trpg_update_")
        download_path = os.path.join(temp_dir, "update.tar.gz")
        
        print(f"  Downloading update from GitHub...")
        print(f"  URL: {download_url}")
        
        # Download with progress
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded / total_size) * 100)
                print(f"\r  Progress: {percent:.1f}%", end="", flush=True)
        
        urlretrieve(download_url, download_path, reporthook=report_progress)
        print()  # Newline after progress
        
        return temp_dir
    except Exception as e:
        print(f"  ✗ Download failed: {e}")
        return None


def install_update(download_dir: str) -> bool:
    """
    Install the downloaded update.
    
    Args:
        download_dir: Directory containing downloaded files
        
    Returns:
        True if installation successful
    """
    try:
        import tarfile
        
        # Extract tarball
        tarball_path = os.path.join(download_dir, "update.tar.gz")
        
        print("  Extracting update...")
        with tarfile.open(tarball_path, "r:gz") as tar:
            tar.extractall(download_dir)
        
        # Find extracted directory (usually has format owner-repo-hash)
        extracted_dirs = [d for d in os.listdir(download_dir) 
                        if os.path.isdir(os.path.join(download_dir, d)) 
                        and d != "__pycache__"]
        
        if not extracted_dirs:
            print("  ✗ No extracted files found")
            return False
        
        source_dir = os.path.join(download_dir, extracted_dirs[0])
        
        # Find trpg package in extracted files
        trpg_source = os.path.join(source_dir, "trpg")
        if not os.path.exists(trpg_source):
            # Try to find it recursively
            for root, dirs, files in os.walk(source_dir):
                if "trpg" in dirs:
                    trpg_source = os.path.join(root, "trpg")
                    break
        
        if not os.path.exists(trpg_source):
            print("  ✗ Could not find trpg package in update")
            return False
        
        # Find installation directory
        import trpg
        package_dir = os.path.dirname(trpg.__file__)
        install_dir = os.path.dirname(package_dir)
        
        print(f"  Installing to: {install_dir}")
        
        # Copy new files
        for item in os.listdir(trpg_source):
            source_path = os.path.join(trpg_source, item)
            dest_path = os.path.join(package_dir, item)
            
            if os.path.isdir(source_path):
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
            else:
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.copy2(source_path, dest_path)
        
        # Also update pyproject.toml if present
        pyproject_source = os.path.join(source_dir, "pyproject.toml")
        if os.path.exists(pyproject_source):
            shutil.copy2(pyproject_source, os.path.join(install_dir, "pyproject.toml"))
        
        print("  ✓ Update installed successfully!")
        return True
        
    except Exception as e:
        print(f"  ✗ Installation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def rollback(backup_path: str) -> bool:
    """
    Rollback to previous version from backup.
    
    Args:
        backup_path: Path to backup directory
        
    Returns:
        True if rollback successful
    """
    try:
        import trpg
        package_dir = os.path.dirname(trpg.__file__)
        parent_dir = os.path.dirname(package_dir)
        
        # Remove current (broken) installation
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
        
        # Restore backup
        shutil.copytree(backup_path, package_dir)
        print(f"  ✓ Rolled back to previous version")
        return True
    except Exception as e:
        print(f"  ✗ Rollback failed: {e}")
        return False


def cleanup(download_dir: str) -> None:
    """Clean up temporary files."""
    try:
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
    except Exception:
        pass


def update_interactive() -> bool:
    """
    Run the update process interactively.
    
    Returns:
        True if update was successful
    """
    print("\n" + "=" * 60)
    print("  AI TERMINAL RPG - AUTO-UPDATER")
    print("=" * 60 + "\n")
    
    # Check for update
    print("  Checking for updates...")
    available, current, latest = check_for_update()
    
    print(f"  Current version: {current}")
    print(f"  Latest version:  {latest}")
    
    if not available:
        print("\n  ✓ You're already running the latest version!")
        return False
    
    print(f"\n  ⚡ Update available: v{current} → v{latest}")
    print()
    
    # Confirm update
    response = input("  Do you want to update now? [Y/n]: ").strip().lower()
    if response in ["n", "no"]:
        print("  Update cancelled.")
        return False
    
    # Create backup
    print("\n  Creating backup...")
    backup_path = backup_current_installation()
    
    # Download update
    print("\n  Downloading update...")
    download_dir = download_update()
    
    if not download_dir:
        print("  ✗ Update download failed")
        return False
    
    # Install update
    print("\n  Installing update...")
    success = install_update(download_dir)
    
    # Cleanup
    cleanup(download_dir)
    
    if success:
        print("\n" + "=" * 60)
        print(f"  ✓ UPDATE COMPLETE! Now running v{latest}")
        print("=" * 60)
        print("\n  Please restart the game to use the new version.")
        return True
    else:
        # Attempt rollback
        if backup_path:
            print("\n  Attempting rollback...")
            rollback(backup_path)
        print("\n  ✗ Update failed. Please try manual installation.")
        return False


def update_auto() -> bool:
    """
    Run the update process automatically (non-interactive).
    
    Returns:
        True if update was successful
    """
    available, current, latest = check_for_update()
    
    if not available:
        return False
    
    print(f"  Updating from v{current} to v{latest}...")
    
    backup_path = backup_current_installation()
    download_dir = download_update()
    
    if not download_dir:
        return False
    
    success = install_update(download_dir)
    cleanup(download_dir)
    
    if not success and backup_path:
        rollback(backup_path)
    
    return success


def main():
    """Main entry point for updater."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "check":
            available, current, latest = check_for_update()
            if available:
                print(f"Update available: v{current} → v{latest}")
                sys.exit(0)
            else:
                print(f"Already up to date (v{current})")
                sys.exit(0)
        
        elif command == "auto":
            success = update_auto()
            sys.exit(0 if success else 1)
    
    # Default: interactive mode
    success = update_interactive()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
