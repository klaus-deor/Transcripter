"""Transcripter - Audio transcription tool for Linux."""

__version__ = "1.0.0"
__author__ = "Klaus Deor & Claude Code"
__description__ = "Audio transcription tool using Groq API"
__url__ = "https://github.com/klaus-deor/Transcripter"

from .config import ConfigManager
from .audio import AudioRecorder
from .transcription import TranscriptionService
from .clipboard import ClipboardManager
from .hotkeys import HotkeyManager
from .tray import TrayIcon, NotificationManager

__all__ = [
    'ConfigManager',
    'AudioRecorder',
    'TranscriptionService',
    'ClipboardManager',
    'HotkeyManager',
    'TrayIcon',
    'NotificationManager',
]
