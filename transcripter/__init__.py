"""Transcripter - Cross-platform audio transcription tool."""

__version__ = "1.0.0"
__author__ = "Klaus Deor & Claude Code"
__description__ = "Cross-platform audio transcription tool using Groq API"
__url__ = "https://github.com/klaus-deor/Transcripter"

from .config import ConfigManager
from .audio import AudioRecorder
from .transcription import TranscriptionService
from .clipboard import ClipboardManager
from .hotkeys import HotkeyManager
from .platform_utils import get_platform, is_linux, is_macos, is_windows

# Platform-specific imports
try:
    from .tray import TrayIcon, NotificationManager
except ImportError:
    TrayIcon = None
    NotificationManager = None

try:
    from .tray_cross import CrossPlatformTray, CrossPlatformNotificationManager
except ImportError:
    CrossPlatformTray = None
    CrossPlatformNotificationManager = None

__all__ = [
    'ConfigManager',
    'AudioRecorder',
    'TranscriptionService',
    'ClipboardManager',
    'HotkeyManager',
    'TrayIcon',
    'NotificationManager',
    'CrossPlatformTray',
    'CrossPlatformNotificationManager',
    'get_platform',
    'is_linux',
    'is_macos',
    'is_windows',
]
