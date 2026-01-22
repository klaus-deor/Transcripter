"""Cross-platform Settings window using tkinter."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from ..config import ConfigManager
from ..audio import AudioRecorder
from ..hotkeys import HotkeyValidator


class SettingsWindow:
    """Cross-platform settings window using tkinter."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the settings window.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.window: Optional[tk.Toplevel] = None
        self.on_settings_changed: Optional[Callable] = None

        # Variables for widgets
        self.api_key_var: Optional[tk.StringVar] = None
        self.language_var: Optional[tk.StringVar] = None
        self.model_var: Optional[tk.StringVar] = None
        self.device_var: Optional[tk.StringVar] = None
        self.hotkey_var: Optional[tk.StringVar] = None
        self.toggle_mode_var: Optional[tk.BooleanVar] = None
        self.notifications_var: Optional[tk.BooleanVar] = None
        self.autostart_var: Optional[tk.BooleanVar] = None
        self.history_var: Optional[tk.BooleanVar] = None
        self.max_history_var: Optional[tk.IntVar] = None

    def show(self) -> None:
        """Show the settings window."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return

        self._create_window()
        self._load_settings()

    def _create_window(self) -> None:
        """Create the settings window and its widgets."""
        self.window = tk.Toplevel()
        self.window.title("Transcripter Settings")
        self.window.geometry("550x450")
        self.window.resizable(True, True)

        # Center the window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')

        # Initialize variables
        self.api_key_var = tk.StringVar()
        self.language_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.device_var = tk.StringVar()
        self.hotkey_var = tk.StringVar()
        self.toggle_mode_var = tk.BooleanVar()
        self.notifications_var = tk.BooleanVar()
        self.autostart_var = tk.BooleanVar()
        self.history_var = tk.BooleanVar()
        self.max_history_var = tk.IntVar(value=50)

        # Create notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        notebook.add(self._create_general_tab(), text="General")
        notebook.add(self._create_audio_tab(), text="Audio")
        notebook.add(self._create_groq_tab(), text="Groq API")
        notebook.add(self._create_hotkeys_tab(), text="Hotkeys")
        notebook.add(self._create_history_tab(), text="History")

        # Button frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Save", command=self._on_save).pack(side='right', padx=5)

    def _create_general_tab(self) -> ttk.Frame:
        """Create the general settings tab."""
        frame = ttk.Frame()
        frame.columnconfigure(1, weight=1)

        row = 0

        # Notifications
        ttk.Checkbutton(
            frame, text="Show notifications",
            variable=self.notifications_var
        ).grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        row += 1

        # Autostart
        ttk.Checkbutton(
            frame, text="Start on system login",
            variable=self.autostart_var
        ).grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        row += 1

        # Language
        ttk.Label(frame, text="Transcription language:").grid(
            row=row, column=0, sticky='w', padx=10, pady=5
        )

        languages = [
            ("Auto-detect", "auto"),
            ("English", "en"),
            ("Portuguese", "pt"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("German", "de"),
            ("Italian", "it"),
            ("Japanese", "ja"),
            ("Korean", "ko"),
            ("Chinese", "zh"),
        ]

        language_combo = ttk.Combobox(
            frame, textvariable=self.language_var,
            values=[lang[0] for lang in languages],
            state='readonly'
        )
        language_combo.grid(row=row, column=1, sticky='ew', padx=10, pady=5)
        self._language_map = {lang[0]: lang[1] for lang in languages}
        self._language_map_reverse = {lang[1]: lang[0] for lang in languages}

        return frame

    def _create_audio_tab(self) -> ttk.Frame:
        """Create the audio settings tab."""
        frame = ttk.Frame()
        frame.columnconfigure(1, weight=1)

        row = 0

        # Device selection
        ttk.Label(frame, text="Microphone:").grid(
            row=row, column=0, sticky='w', padx=10, pady=5
        )

        devices = ["System Default"]
        try:
            audio_devices = AudioRecorder.list_devices()
            devices.extend([d.name for d in audio_devices])
        except Exception as e:
            print(f"Error listing audio devices: {e}")

        device_combo = ttk.Combobox(
            frame, textvariable=self.device_var,
            values=devices,
            state='readonly'
        )
        device_combo.grid(row=row, column=1, sticky='ew', padx=10, pady=5)
        row += 1

        # Info label
        info_text = "Sample rate: 16000 Hz (optimized for speech)\nFormat: Mono WAV"
        ttk.Label(frame, text=info_text, foreground='gray').grid(
            row=row, column=0, columnspan=2, sticky='w', padx=10, pady=5
        )

        return frame

    def _create_groq_tab(self) -> ttk.Frame:
        """Create the Groq API settings tab."""
        frame = ttk.Frame()
        frame.columnconfigure(1, weight=1)

        row = 0

        # API Key
        ttk.Label(frame, text="Groq API Key:").grid(
            row=row, column=0, sticky='w', padx=10, pady=5
        )
        row += 1

        api_frame = ttk.Frame(frame)
        api_frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        api_frame.columnconfigure(0, weight=1)

        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show='*')
        self.api_key_entry.grid(row=0, column=0, sticky='ew')

        self.show_key_btn = ttk.Button(api_frame, text="Show", command=self._toggle_api_key_visibility)
        self.show_key_btn.grid(row=0, column=1, padx=(5, 0))
        row += 1

        # Info about getting API key
        ttk.Label(
            frame,
            text="Get your API key at: console.groq.com",
            foreground='blue',
            cursor='hand2'
        ).grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        row += 1

        # Separator
        ttk.Separator(frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky='ew', padx=10, pady=10
        )
        row += 1

        # Model selection
        ttk.Label(frame, text="Whisper Model:").grid(
            row=row, column=0, sticky='w', padx=10, pady=5
        )

        models = [
            ("Whisper Large V3 Turbo (Fast)", "whisper-large-v3-turbo"),
            ("Whisper Large V3 (Accurate)", "whisper-large-v3"),
        ]

        model_combo = ttk.Combobox(
            frame, textvariable=self.model_var,
            values=[m[0] for m in models],
            state='readonly'
        )
        model_combo.grid(row=row, column=1, sticky='ew', padx=10, pady=5)
        self._model_map = {m[0]: m[1] for m in models}
        self._model_map_reverse = {m[1]: m[0] for m in models}

        return frame

    def _create_hotkeys_tab(self) -> ttk.Frame:
        """Create the hotkeys settings tab."""
        frame = ttk.Frame()
        frame.columnconfigure(1, weight=1)

        row = 0

        # Hotkey entry
        ttk.Label(frame, text="Recording Hotkey:").grid(
            row=row, column=0, sticky='w', padx=10, pady=5
        )

        ttk.Entry(frame, textvariable=self.hotkey_var).grid(
            row=row, column=1, sticky='ew', padx=10, pady=5
        )
        row += 1

        # Toggle mode
        ttk.Checkbutton(
            frame,
            text="Toggle mode (same key starts and stops recording)",
            variable=self.toggle_mode_var
        ).grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        row += 1

        # Info
        info_text = (
            "Format: modifier+key (e.g., ctrl+alt+r)\n"
            "Valid modifiers: ctrl, alt, shift, super/cmd\n"
            "Valid keys: a-z, 0-9, F1-F12, space, etc."
        )
        ttk.Label(frame, text=info_text, foreground='gray').grid(
            row=row, column=0, columnspan=2, sticky='w', padx=10, pady=5
        )

        return frame

    def _create_history_tab(self) -> ttk.Frame:
        """Create the history settings tab."""
        frame = ttk.Frame()
        frame.columnconfigure(1, weight=1)

        row = 0

        # Enable history
        ttk.Checkbutton(
            frame,
            text="Keep transcription history",
            variable=self.history_var
        ).grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        row += 1

        # Max history items
        ttk.Label(frame, text="Maximum history items:").grid(
            row=row, column=0, sticky='w', padx=10, pady=5
        )

        spinbox = ttk.Spinbox(
            frame, from_=10, to=500, increment=10,
            textvariable=self.max_history_var, width=10
        )
        spinbox.grid(row=row, column=1, sticky='w', padx=10, pady=5)

        return frame

    def _load_settings(self) -> None:
        """Load current settings into the widgets."""
        config = self.config_manager.config

        # General
        self.notifications_var.set(config.general.show_notifications)
        self.autostart_var.set(config.general.autostart)

        lang = config.general.language if config.general.language else "auto"
        lang_display = self._language_map_reverse.get(lang, "Auto-detect")
        self.language_var.set(lang_display)

        # Audio
        device = config.audio.device_name if config.audio.device_name else "System Default"
        self.device_var.set(device)

        # Groq
        api_key = self.config_manager.get_api_key()
        if api_key:
            self.api_key_var.set(api_key)

        model_display = self._model_map_reverse.get(config.groq.model, "Whisper Large V3 Turbo (Fast)")
        self.model_var.set(model_display)

        # Hotkeys
        self.hotkey_var.set(config.hotkeys.start_recording)
        self.toggle_mode_var.set(config.hotkeys.toggle_mode)

        # History
        self.history_var.set(config.history.enabled)
        self.max_history_var.set(config.history.max_items)

    def _toggle_api_key_visibility(self) -> None:
        """Toggle API key visibility."""
        if self.api_key_entry.cget('show') == '*':
            self.api_key_entry.config(show='')
            self.show_key_btn.config(text='Hide')
        else:
            self.api_key_entry.config(show='*')
            self.show_key_btn.config(text='Show')

    def _on_save(self) -> None:
        """Handle save button click."""
        try:
            # Validate hotkey
            hotkey = self.hotkey_var.get().strip()
            is_valid, error_msg = HotkeyValidator.validate(hotkey)
            if not is_valid:
                messagebox.showerror("Invalid Hotkey", error_msg)
                return

            # Save settings
            config = self.config_manager.config

            # General
            config.general.show_notifications = self.notifications_var.get()
            config.general.autostart = self.autostart_var.get()
            lang_display = self.language_var.get()
            lang = self._language_map.get(lang_display, "auto")
            config.general.language = "" if lang == "auto" else lang

            # Audio
            device = self.device_var.get()
            config.audio.device_name = "" if device == "System Default" else device

            # Groq
            api_key = self.api_key_var.get().strip()
            if api_key:
                self.config_manager.set_api_key(api_key)

            model_display = self.model_var.get()
            config.groq.model = self._model_map.get(model_display, "whisper-large-v3-turbo")

            # Hotkeys
            config.hotkeys.start_recording = HotkeyValidator.normalize(hotkey)
            config.hotkeys.stop_recording = config.hotkeys.start_recording
            config.hotkeys.toggle_mode = self.toggle_mode_var.get()

            # History
            config.history.enabled = self.history_var.get()
            config.history.max_items = self.max_history_var.get()

            # Save to file
            self.config_manager.save_config(config)

            # Notify callback
            if self.on_settings_changed:
                self.on_settings_changed()

            # Close window
            self.window.destroy()
            self.window = None

        except Exception as e:
            messagebox.showerror("Error Saving Settings", str(e))

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.window.destroy()
        self.window = None
