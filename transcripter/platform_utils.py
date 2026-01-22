"""Platform detection and utility functions."""

import sys
import os


def get_platform() -> str:
    """
    Get the current platform.

    Returns:
        'linux', 'darwin' (macOS), or 'windows'
    """
    if sys.platform.startswith('linux'):
        return 'linux'
    elif sys.platform == 'darwin':
        return 'darwin'
    elif sys.platform in ('win32', 'cygwin'):
        return 'windows'
    else:
        return sys.platform


def is_linux() -> bool:
    """Check if running on Linux."""
    return get_platform() == 'linux'


def is_macos() -> bool:
    """Check if running on macOS."""
    return get_platform() == 'darwin'


def is_windows() -> bool:
    """Check if running on Windows."""
    return get_platform() == 'windows'


def get_config_dir() -> str:
    """
    Get the appropriate configuration directory for the platform.

    Returns:
        Path to the configuration directory
    """
    from pathlib import Path

    if is_windows():
        # Use AppData on Windows
        appdata = os.environ.get('APPDATA')
        if appdata:
            return str(Path(appdata) / 'Transcripter')
        return str(Path.home() / 'AppData' / 'Roaming' / 'Transcripter')
    elif is_macos():
        # Use Application Support on macOS
        return str(Path.home() / 'Library' / 'Application Support' / 'Transcripter')
    else:
        # Use .config on Linux
        return str(Path.home() / '.config' / 'transcripter')


def get_temp_dir() -> str:
    """
    Get the appropriate temporary directory for the platform.

    Returns:
        Path to the temporary directory
    """
    import tempfile
    return tempfile.gettempdir()


def get_autostart_path() -> str:
    """
    Get the path for autostart configuration.

    Returns:
        Path to the autostart configuration location
    """
    from pathlib import Path

    if is_windows():
        # Startup folder on Windows
        appdata = os.environ.get('APPDATA', '')
        return str(Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup')
    elif is_macos():
        # LaunchAgents on macOS
        return str(Path.home() / 'Library' / 'LaunchAgents')
    else:
        # Autostart on Linux
        return str(Path.home() / '.config' / 'autostart')


def supports_gtk() -> bool:
    """
    Check if GTK is available on the current platform.

    Returns:
        True if GTK is available
    """
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
        return True
    except (ImportError, ValueError):
        return False


def supports_appindicator() -> bool:
    """
    Check if AppIndicator is available (Linux only).

    Returns:
        True if AppIndicator is available
    """
    if not is_linux():
        return False

    try:
        import gi
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3
        return True
    except (ImportError, ValueError):
        return False


def get_notification_backend() -> str:
    """
    Get the appropriate notification backend for the platform.

    Returns:
        'notify' (Linux), 'osascript' (macOS), or 'toast' (Windows)
    """
    if is_linux():
        return 'notify'
    elif is_macos():
        return 'osascript'
    elif is_windows():
        return 'toast'
    return 'none'
