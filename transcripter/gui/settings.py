"""Settings window for Transcripter."""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from typing import Callable, Optional
from ..config import ConfigManager
from ..audio import AudioRecorder
from ..hotkeys import HotkeyValidator


class SettingsWindow:
    """Settings window for configuring the application."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the settings window.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.window: Optional[Gtk.Window] = None
        self.on_settings_changed: Optional[Callable] = None

        # Widgets
        self.api_key_entry: Optional[Gtk.Entry] = None
        self.language_combo: Optional[Gtk.ComboBoxText] = None
        self.model_combo: Optional[Gtk.ComboBoxText] = None
        self.device_combo: Optional[Gtk.ComboBoxText] = None
        self.hotkey_entry: Optional[Gtk.Entry] = None
        self.toggle_mode_check: Optional[Gtk.CheckButton] = None
        self.notifications_check: Optional[Gtk.CheckButton] = None
        self.autostart_check: Optional[Gtk.CheckButton] = None
        self.history_check: Optional[Gtk.CheckButton] = None
        self.max_history_spin: Optional[Gtk.SpinButton] = None

    def show(self) -> None:
        """Show the settings window."""
        if self.window:
            self.window.present()
            return

        self._create_window()
        self._load_settings()
        self.window.show_all()

    def _create_window(self) -> None:
        """Create the settings window and its widgets."""
        self.window = Gtk.Window(title="Transcripter Settings")
        self.window.set_default_size(600, 500)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("delete-event", self._on_close)

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_border_width(10)
        self.window.add(main_box)

        # Create notebook for tabs
        notebook = Gtk.Notebook()
        main_box.pack_start(notebook, True, True, 0)

        # Create tabs
        notebook.append_page(self._create_general_tab(), Gtk.Label(label="General"))
        notebook.append_page(self._create_audio_tab(), Gtk.Label(label="Audio"))
        notebook.append_page(self._create_groq_tab(), Gtk.Label(label="Groq API"))
        notebook.append_page(self._create_hotkeys_tab(), Gtk.Label(label="Hotkeys"))
        notebook.append_page(self._create_history_tab(), Gtk.Label(label="History"))

        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_halign(Gtk.Align.END)
        main_box.pack_start(button_box, False, False, 0)

        # Save button
        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self._on_save_clicked)
        button_box.pack_start(save_button, False, False, 0)

        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self._on_cancel_clicked)
        button_box.pack_start(cancel_button, False, False, 0)

    def _create_general_tab(self) -> Gtk.Box:
        """Create the general settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # Notifications
        self.notifications_check = Gtk.CheckButton(label="Show notifications")
        box.pack_start(self.notifications_check, False, False, 0)

        # Autostart
        self.autostart_check = Gtk.CheckButton(label="Start on system login")
        box.pack_start(self.autostart_check, False, False, 0)

        # Language
        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lang_label = Gtk.Label(label="Transcription language:")
        lang_label.set_xalign(0)
        lang_box.pack_start(lang_label, False, False, 0)

        self.language_combo = Gtk.ComboBoxText()
        self.language_combo.append("auto", "Auto-detect")
        self.language_combo.append("en", "English")
        self.language_combo.append("pt", "Portuguese")
        self.language_combo.append("es", "Spanish")
        self.language_combo.append("fr", "French")
        self.language_combo.append("de", "German")
        self.language_combo.append("it", "Italian")
        self.language_combo.append("ja", "Japanese")
        self.language_combo.append("ko", "Korean")
        self.language_combo.append("zh", "Chinese")
        lang_box.pack_start(self.language_combo, True, True, 0)

        box.pack_start(lang_box, False, False, 0)

        return box

    def _create_audio_tab(self) -> Gtk.Box:
        """Create the audio settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # Audio device selection
        device_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        device_label = Gtk.Label(label="Microphone:")
        device_label.set_xalign(0)
        device_box.pack_start(device_label, False, False, 0)

        self.device_combo = Gtk.ComboBoxText()
        self.device_combo.append("", "System Default")

        # List available audio devices
        try:
            devices = AudioRecorder.list_devices()
            for device in devices:
                self.device_combo.append(device.name, device.name)
        except Exception as e:
            print(f"Error listing audio devices: {e}")

        device_box.pack_start(self.device_combo, True, True, 0)
        box.pack_start(device_box, False, False, 0)

        # Sample rate info (read-only)
        info_label = Gtk.Label()
        info_label.set_markup(
            "<small>Sample rate: 16000 Hz (optimized for speech)\n"
            "Format: Mono WAV</small>"
        )
        info_label.set_xalign(0)
        box.pack_start(info_label, False, False, 0)

        return box

    def _create_groq_tab(self) -> Gtk.Box:
        """Create the Groq API settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # API Key
        api_key_label = Gtk.Label(label="Groq API Key:")
        api_key_label.set_xalign(0)
        box.pack_start(api_key_label, False, False, 0)

        api_key_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.api_key_entry = Gtk.Entry()
        self.api_key_entry.set_placeholder_text("Enter your Groq API key")
        self.api_key_entry.set_visibility(False)  # Hide password
        self.api_key_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        api_key_box.pack_start(self.api_key_entry, True, True, 0)

        show_button = Gtk.Button(label="Show")
        show_button.connect("clicked", self._on_toggle_api_key_visibility)
        api_key_box.pack_start(show_button, False, False, 0)

        box.pack_start(api_key_box, False, False, 0)

        # Info about getting API key
        info_label = Gtk.Label()
        info_label.set_markup(
            '<small>Get your API key at: <a href="https://console.groq.com/">console.groq.com</a></small>'
        )
        info_label.set_xalign(0)
        box.pack_start(info_label, False, False, 0)

        # Separator
        box.pack_start(Gtk.Separator(), False, False, 5)

        # Model selection
        model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        model_label = Gtk.Label(label="Whisper Model:")
        model_label.set_xalign(0)
        model_box.pack_start(model_label, False, False, 0)

        self.model_combo = Gtk.ComboBoxText()
        self.model_combo.append("whisper-large-v3-turbo", "Whisper Large V3 Turbo (Fast)")
        self.model_combo.append("whisper-large-v3", "Whisper Large V3 (Accurate)")
        model_box.pack_start(self.model_combo, True, True, 0)

        box.pack_start(model_box, False, False, 0)

        return box

    def _create_hotkeys_tab(self) -> Gtk.Box:
        """Create the hotkeys settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # Hotkey entry
        hotkey_label = Gtk.Label(label="Recording Hotkey:")
        hotkey_label.set_xalign(0)
        box.pack_start(hotkey_label, False, False, 0)

        self.hotkey_entry = Gtk.Entry()
        self.hotkey_entry.set_placeholder_text("e.g., ctrl+alt+r")
        box.pack_start(self.hotkey_entry, False, False, 0)

        # Toggle mode
        self.toggle_mode_check = Gtk.CheckButton(
            label="Toggle mode (same key starts and stops recording)"
        )
        box.pack_start(self.toggle_mode_check, False, False, 0)

        # Info
        info_label = Gtk.Label()
        info_label.set_markup(
            "<small>Format: modifier+key (e.g., ctrl+alt+r)\n"
            "Valid modifiers: ctrl, alt, shift, super\n"
            "Valid keys: a-z, 0-9, F1-F12, space, etc.</small>"
        )
        info_label.set_xalign(0)
        box.pack_start(info_label, False, False, 0)

        return box

    def _create_history_tab(self) -> Gtk.Box:
        """Create the history settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # Enable history
        self.history_check = Gtk.CheckButton(label="Keep transcription history")
        box.pack_start(self.history_check, False, False, 0)

        # Max history items
        history_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        history_label = Gtk.Label(label="Maximum history items:")
        history_label.set_xalign(0)
        history_box.pack_start(history_label, False, False, 0)

        adjustment = Gtk.Adjustment(value=50, lower=10, upper=500, step_increment=10)
        self.max_history_spin = Gtk.SpinButton()
        self.max_history_spin.set_adjustment(adjustment)
        history_box.pack_start(self.max_history_spin, False, False, 0)

        box.pack_start(history_box, False, False, 0)

        return box

    def _load_settings(self) -> None:
        """Load current settings into the widgets."""
        config = self.config_manager.config

        # General
        self.notifications_check.set_active(config.general.show_notifications)
        self.autostart_check.set_active(config.general.autostart)

        # Set language
        lang = config.general.language if config.general.language else "auto"
        self.language_combo.set_active_id(lang)

        # Audio
        self.device_combo.set_active_id(config.audio.device_name)

        # Groq
        api_key = self.config_manager.get_api_key()
        if api_key:
            self.api_key_entry.set_text(api_key)

        self.model_combo.set_active_id(config.groq.model)

        # Hotkeys
        self.hotkey_entry.set_text(config.hotkeys.start_recording)
        self.toggle_mode_check.set_active(config.hotkeys.toggle_mode)

        # History
        self.history_check.set_active(config.history.enabled)
        self.max_history_spin.set_value(config.history.max_items)

    def _on_save_clicked(self, button) -> None:
        """Handle save button click."""
        try:
            # Validate hotkey
            hotkey = self.hotkey_entry.get_text().strip()
            is_valid, error_msg = HotkeyValidator.validate(hotkey)
            if not is_valid:
                self._show_error_dialog("Invalid Hotkey", error_msg)
                return

            # Save settings
            config = self.config_manager.config

            # General
            config.general.show_notifications = self.notifications_check.get_active()
            config.general.autostart = self.autostart_check.get_active()
            lang = self.language_combo.get_active_id()
            config.general.language = "" if lang == "auto" else lang

            # Audio
            config.audio.device_name = self.device_combo.get_active_id() or ""

            # Groq
            api_key = self.api_key_entry.get_text().strip()
            if api_key:
                self.config_manager.set_api_key(api_key)

            config.groq.model = self.model_combo.get_active_id()

            # Hotkeys
            config.hotkeys.start_recording = HotkeyValidator.normalize(hotkey)
            config.hotkeys.stop_recording = config.hotkeys.start_recording
            config.hotkeys.toggle_mode = self.toggle_mode_check.get_active()

            # History
            config.history.enabled = self.history_check.get_active()
            config.history.max_items = int(self.max_history_spin.get_value())

            # Save to file
            self.config_manager.save_config(config)

            # Notify callback
            if self.on_settings_changed:
                self.on_settings_changed()

            # Close window
            self.window.destroy()
            self.window = None

        except Exception as e:
            self._show_error_dialog("Error Saving Settings", str(e))

    def _on_cancel_clicked(self, button) -> None:
        """Handle cancel button click."""
        self.window.destroy()
        self.window = None

    def _on_close(self, widget, event) -> bool:
        """Handle window close event."""
        self.window = None
        return False

    def _on_toggle_api_key_visibility(self, button) -> None:
        """Toggle API key visibility."""
        if self.api_key_entry.get_visibility():
            self.api_key_entry.set_visibility(False)
            button.set_label("Show")
        else:
            self.api_key_entry.set_visibility(True)
            button.set_label("Hide")

    def _show_error_dialog(self, title: str, message: str) -> None:
        """Show an error dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
