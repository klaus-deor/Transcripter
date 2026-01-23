# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Transcripter."""

import sys
from pathlib import Path

block_cipher = None

# Project paths
spec_dir = Path(SPECPATH)
project_root = spec_dir.parent.parent
transcripter_dir = project_root / 'transcripter'
config_dir = project_root / 'config'
assets_dir = spec_dir.parent / 'assets'

# Determine platform-specific settings
is_windows = sys.platform == 'win32'
is_macos = sys.platform == 'darwin'
is_linux = sys.platform.startswith('linux')

# Data files to include
datas = [
    (str(config_dir / 'default_config.toml'), 'config'),
    (str(assets_dir / 'transcripter.png'), 'gui/icons'),
    (str(assets_dir / 'recording.png'), 'gui/icons'),
]

# Hidden imports for all platforms
hiddenimports = [
    # Core dependencies
    'toml',
    'keyring',
    'keyring.backends',
    'pydantic',

    # Pystray backends
    'pystray',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',

    # Audio recording
    'sounddevice',
    'soundfile',
    'numpy',

    # HTTP clients
    'httpx',
    'httpcore',
    'h11',
    'certifi',

    # Clipboard
    'pyperclip',

    # Transcripter core modules
    'transcripter',
    'transcripter.config',
    'transcripter.audio',
    'transcripter.clipboard',
    'transcripter.hotkeys',
    'transcripter.transcription',
    'transcripter.tray',
    'transcripter.tray_cross',
    'transcripter.platform_utils',
    'transcripter.main',
    'transcripter.main_cross',

    # GTK GUI (Linux)
    'transcripter.gui',
    'transcripter.gui.settings',
    'transcripter.gui.history',

    # Providers
    'transcripter.providers',
    'transcripter.providers.base',
    'transcripter.providers.factory',
    'transcripter.providers.groq',
    'transcripter.providers.openai_provider',
    'transcripter.providers.assemblyai',
    'transcripter.providers.deepgram',
    'transcripter.providers.google_cloud',

    # GUI modules
    'transcripter.gui_cross',
    'transcripter.gui_cross.settings',
    'transcripter.gui_cross.history',

    # Tkinter (needed for GUI)
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
]

# Platform-specific hidden imports
if is_windows:
    hiddenimports.extend([
        'pystray._win32',
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
        'keyring.backends.Windows',
        'win32api',
        'win32con',
        'win32gui',
        'win10toast',
    ])
elif is_macos:
    hiddenimports.extend([
        'pystray._darwin',
        'pynput.keyboard._darwin',
        'pynput.mouse._darwin',
        'keyring.backends.macOS',
        'AppKit',
        'Foundation',
    ])
else:  # Linux
    hiddenimports.extend([
        'pystray._gtk',
        'pystray._appindicator',
        'pynput.keyboard._xorg',
        'pynput.mouse._xorg',
        'keyring.backends.SecretService',
        # GTK/GI modules for native Linux tray
        'gi',
        'gi.repository',
        'gi.repository.Gtk',
        'gi.repository.GLib',
        'gi.repository.GObject',
        'gi.repository.Gdk',
        'gi.repository.GdkPixbuf',
        'gi.repository.Pango',
        'gi.repository.AppIndicator3',
        'gi.repository.Notify',
    ])

# Exclude unnecessary modules
excludes = [
    'matplotlib',
    'pandas',
    'test',
    'tests',
    'unittest',
    'doctest',
]

a = Analysis(
    [str(transcripter_dir / '__main__.py')],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[str(spec_dir / 'hooks')],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Platform-specific executable settings
exe_kwargs = {
    'name': 'Transcripter',
    'debug': False,
    'bootloader_ignore_signals': False,
    'strip': False,
    'upx': False,  # UPX can cause issues with some libraries
    'console': False,  # GUI application, no console window
    'disable_windowed_traceback': False,
    'argv_emulation': False,
    'target_arch': None,
    'codesign_identity': None,
    'entitlements_file': None,
}

if is_windows:
    exe_kwargs['icon'] = str(spec_dir.parent / 'windows' / 'transcripter.ico')
elif is_macos:
    icns_path = spec_dir.parent / 'macos' / 'transcripter.icns'
    if icns_path.exists():
        exe_kwargs['icon'] = str(icns_path)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    **exe_kwargs,
)

# macOS app bundle
if is_macos:
    app = BUNDLE(
        exe,
        name='Transcripter.app',
        icon=str(spec_dir.parent / 'macos' / 'transcripter.icns') if (spec_dir.parent / 'macos' / 'transcripter.icns').exists() else None,
        bundle_identifier='com.klausdeor.transcripter',
        version='1.0.0',
        info_plist={
            'CFBundleName': 'Transcripter',
            'CFBundleDisplayName': 'Transcripter',
            'CFBundleGetInfoString': 'Audio transcription tool',
            'CFBundleIdentifier': 'com.klausdeor.transcripter',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSMicrophoneUsageDescription': 'Transcripter needs microphone access for audio recording.',
            'NSAppleEventsUsageDescription': 'Transcripter needs accessibility for global hotkeys.',
            'LSUIElement': True,  # Hide from dock (menu bar app)
            'LSMinimumSystemVersion': '10.13',
            'NSHighResolutionCapable': True,
        },
    )
