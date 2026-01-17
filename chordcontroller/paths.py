"""
Path utilities for handling config file locations.

This module provides functions to determine the correct paths for configuration
files based on how the application is being run:

1. Running directly with Python (python -m chordcontroller.main): config.json in the current directory
2. Installed as a package (pip install): config.json in user config directory
   - Linux: ~/.config/chordcontroller/
   - Windows: %APPDATA%/chordcontroller/
   - macOS: ~/Library/Application Support/chordcontroller/
"""

import os
import sys
from pathlib import Path

APP_NAME = "chordcontroller"


def is_installed_package() -> bool:
    """
    Check if running as an installed package.
    
    This is determined by checking if the module is being run from a 
    site-packages directory.
    """
    # Check if running from site-packages or similar installed location
    module_path = Path(__file__).resolve()
    
    # Common indicators of an installed package
    site_packages_indicators = ['site-packages', 'dist-packages']
    path_str = str(module_path).lower()
    
    return any(indicator in path_str for indicator in site_packages_indicators)


def get_user_config_dir() -> Path:
    """
    Get the user-specific configuration directory.
    
    Returns:
        Path to the user config directory for this application.
    """
    if sys.platform == 'win32':
        # Windows: Use APPDATA
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    elif sys.platform == 'darwin':
        # macOS: Use Application Support
        base = Path.home() / 'Library' / 'Application Support'
    else:
        # Linux and others: Use XDG_CONFIG_HOME or ~/.config
        base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    
    return base / APP_NAME


def get_config_path() -> Path:
    """
    Get the path to the config.json file based on the execution context.
    
    Returns:
        Path to the config.json file.
    """
    if is_installed_package():
        # Installed package: use user config directory
        return get_user_config_dir() / 'config.json'
    
    # Running directly with Python: use current working directory
    return Path.cwd() / 'config.json'


def ensure_config_dir_exists() -> None:
    """
    Ensure the configuration directory exists (only relevant for installed packages).
    """
    if is_installed_package():
        config_dir = get_user_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)


def get_config_dir() -> Path:
    """
    Get the directory containing the config file.
    
    Returns:
        Path to the directory containing config.json.
    """
    return get_config_path().parent
