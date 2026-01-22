"""Settings window for Transcripter."""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from typing import Callable, Optional
from ..config import ConfigManager
from ..audio import AudioRecorder
from ..hotkeys import HotkeyValidator
from ..providers import ProviderType, ProviderRegistry


# Provider display names and info URLs
PROVIDER_INFO = {
    ProviderType.GROQ: {
        "name": "Groq",
        "url": "https://console.groq.com/",
        "key_label": "API Key",
        "key_placeholder": "Enter your Groq API key",
    },
    ProviderType.OPENAI: {
        "name": "OpenAI",
        "url": "https://platform.openai.com/api-keys",
        "key_label": "API Key",
        "key_placeholder": "Enter your OpenAI API key",
    },
    ProviderType.GOOGLE_CLOUD: {
        "name": "Google Cloud",
        "url": "https://console.cloud.google.com/",
        "key_label": "Credentials File Path",
        "key_placeholder": "Path to service account JSON file",
    },
    ProviderType.ASSEMBLYAI: {
        "name": "AssemblyAI",
        "url": "https://www.assemblyai.com/app/account",
        "key_label": "API Key",
        "key_placeholder": "Enter your AssemblyAI API key",
    },
    ProviderType.DEEPGRAM: {
        "name": "Deepgram",
        "url": "https://console.deepgram.com/",
        "key_label": "API Key",
        "key_placeholder": "Enter your Deepgram API key",
    },
}


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

        # General widgets
        self.language_combo: Optional[Gtk.ComboBoxText] = None
        self.notifications_check: Optional[Gtk.CheckButton] = None
        self.autostart_check: Optional[Gtk.CheckButton] = None

        # Audio widgets
        self.device_combo: Optional[Gtk.ComboBoxText] = None

        # Transcription widgets
        self.provider_combo: Optional[Gtk.ComboBoxText] = None
        self.api_key_entry: Optional[Gtk.Entry] = None
        self.api_key_label: Optional[Gtk.Label] = None
        self.api_key_info_label: Optional[Gtk.Label] = None
        self.model_combo: Optional[Gtk.ComboBoxText] = None
        self.fallback_combo: Optional[Gtk.ComboBoxText] = None
        self.provider_settings_box: Optional[Gtk.Box] = None

        # Hotkey widgets
        self.hotkey_entry: Optional[Gtk.Entry] = None
        self.toggle_mode_check: Optional[Gtk.CheckButton] = None

        # History widgets
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
        self.window.set_default_size(650, 550)
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
        notebook.append_page(self._create_transcription_tab(), Gtk.Label(label="Transcription"))
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

    def _create_transcription_tab(self) -> Gtk.Box:
        """Create the transcription settings tab with provider selection."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # Provider selection
        provider_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        provider_label = Gtk.Label(label="Transcription Provider:")
        provider_label.set_xalign(0)
        provider_box.pack_start(provider_label, False, False, 0)

        self.provider_combo = Gtk.ComboBoxText()
        for provider_type in ProviderType:
            info = PROVIDER_INFO.get(provider_type, {})
            name = info.get("name", provider_type.value)
            installed = ProviderRegistry.is_provider_available(provider_type)
            label = f"{name}" if installed else f"{name} (SDK not installed)"
            self.provider_combo.append(provider_type.value, label)

        self.provider_combo.connect("changed", self._on_provider_changed)
        provider_box.pack_start(self.provider_combo, True, True, 0)

        box.pack_start(provider_box, False, False, 0)

        # Separator
        box.pack_start(Gtk.Separator(), False, False, 5)

        # Provider-specific settings container
        self.provider_settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.pack_start(self.provider_settings_box, False, False, 0)

        # API Key / Credentials
        self.api_key_label = Gtk.Label(label="API Key:")
        self.api_key_label.set_xalign(0)
        self.provider_settings_box.pack_start(self.api_key_label, False, False, 0)

        api_key_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.api_key_entry = Gtk.Entry()
        self.api_key_entry.set_placeholder_text("Enter your API key")
        self.api_key_entry.set_visibility(False)
        self.api_key_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        api_key_box.pack_start(self.api_key_entry, True, True, 0)

        show_button = Gtk.Button(label="Show")
        show_button.connect("clicked", self._on_toggle_api_key_visibility)
        api_key_box.pack_start(show_button, False, False, 0)

        self.provider_settings_box.pack_start(api_key_box, False, False, 0)

        # Info about getting API key
        self.api_key_info_label = Gtk.Label()
        self.api_key_info_label.set_markup(
            '<small>Get your API key at: <a href="https://console.groq.com/">console.groq.com</a></small>'
        )
        self.api_key_info_label.set_xalign(0)
        self.provider_settings_box.pack_start(self.api_key_info_label, False, False, 0)

        # Separator
        self.provider_settings_box.pack_start(Gtk.Separator(), False, False, 5)

        # Model selection
        model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        model_label = Gtk.Label(label="Model:")
        model_label.set_xalign(0)
        model_box.pack_start(model_label, False, False, 0)

        self.model_combo = Gtk.ComboBoxText()
        model_box.pack_start(self.model_combo, True, True, 0)

        self.provider_settings_box.pack_start(model_box, False, False, 0)

        # Separator
        box.pack_start(Gtk.Separator(), False, False, 5)

        # Fallback provider selection
        fallback_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        fallback_label = Gtk.Label(label="Fallback Provider:")
        fallback_label.set_xalign(0)
        fallback_box.pack_start(fallback_label, False, False, 0)

        self.fallback_combo = Gtk.ComboBoxText()
        self.fallback_combo.append("", "None (Disabled)")
        for provider_type in ProviderType:
            info = PROVIDER_INFO.get(provider_type, {})
            name = info.get("name", provider_type.value)
            self.fallback_combo.append(provider_type.value, name)

        fallback_box.pack_start(self.fallback_combo, True, True, 0)
        box.pack_start(fallback_box, False, False, 0)

        fallback_info = Gtk.Label()
        fallback_info.set_markup(
            "<small>Fallback provider is used when the primary provider fails.</small>"
        )
        fallback_info.set_xalign(0)
        box.pack_start(fallback_info, False, False, 0)

        return box

    def _on_provider_changed(self, combo) -> None:
        """Handle provider selection change."""
        provider_id = combo.get_active_id()
        if not provider_id:
            return

        try:
            provider_type = ProviderType(provider_id)
        except ValueError:
            return

        info = PROVIDER_INFO.get(provider_type, {})

        # Update API key label
        key_label = info.get("key_label", "API Key")
        self.api_key_label.set_text(f"{key_label}:")

        # Update placeholder
        placeholder = info.get("key_placeholder", "Enter your API key")
        self.api_key_entry.set_placeholder_text(placeholder)

        # Update info URL
        url = info.get("url", "")
        name = info.get("name", provider_type.value)
        self.api_key_info_label.set_markup(
            f'<small>Get your credentials at: <a href="{url}">{url}</a></small>'
        )

        # Load API key for this provider
        api_key = self.config_manager.get_api_key(provider_type)
        self.api_key_entry.set_text(api_key if api_key else "")

        # Update model combo
        self._update_model_combo(provider_type)

    def _update_model_combo(self, provider_type: ProviderType) -> None:
        """Update the model combo based on provider."""
        self.model_combo.remove_all()

        # Get models for this provider
        try:
            # Create a temporary provider to get models
            if ProviderRegistry.is_provider_available(provider_type):
                provider_class = ProviderRegistry.get_provider_class(provider_type)
                if provider_class:
                    # Get models from class (without needing API key)
                    models = self._get_provider_models(provider_type)
                    for model in models:
                        self.model_combo.append(model["id"], model["name"])

                    # Set active model from config
                    provider_config = self.config_manager.get_provider_config(provider_type)
                    if hasattr(provider_config, 'model'):
                        self.model_combo.set_active_id(provider_config.model)
                    elif self.model_combo.get_model().iter_n_children(None) > 0:
                        self.model_combo.set_active(0)
            else:
                self.model_combo.append("", "SDK not installed")
                self.model_combo.set_active(0)

        except Exception as e:
            print(f"Error updating model combo: {e}")
            self.model_combo.append("", "Error loading models")
            self.model_combo.set_active(0)

    def _get_provider_models(self, provider_type: ProviderType) -> list[dict]:
        """Get models for a provider without requiring API key."""
        models = {
            ProviderType.GROQ: [
                {"id": "whisper-large-v3-turbo", "name": "Whisper Large V3 Turbo (Recommended)"},
                {"id": "whisper-large-v3", "name": "Whisper Large V3"},
            ],
            ProviderType.OPENAI: [
                {"id": "whisper-1", "name": "Whisper-1"},
            ],
            ProviderType.GOOGLE_CLOUD: [
                {"id": "chirp_2", "name": "Chirp 2 (Recommended)"},
                {"id": "chirp", "name": "Chirp"},
                {"id": "default", "name": "Default"},
            ],
            ProviderType.ASSEMBLYAI: [
                {"id": "best", "name": "Best (Highest accuracy)"},
                {"id": "nano", "name": "Nano (Faster, lower cost)"},
            ],
            ProviderType.DEEPGRAM: [
                {"id": "nova-2", "name": "Nova-2 (Recommended)"},
                {"id": "nova", "name": "Nova"},
                {"id": "whisper-large", "name": "Whisper Large"},
                {"id": "whisper-medium", "name": "Whisper Medium"},
                {"id": "whisper-small", "name": "Whisper Small"},
            ],
        }
        return models.get(provider_type, [])

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

        # Transcription provider
        active_provider = config.transcription.active_provider
        self.provider_combo.set_active_id(active_provider)

        # Trigger provider change to load provider-specific settings
        self._on_provider_changed(self.provider_combo)

        # Fallback provider
        fallback = config.transcription.fallback_provider
        self.fallback_combo.set_active_id(fallback if fallback else "")

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

            # Transcription provider
            provider_id = self.provider_combo.get_active_id()
            if provider_id:
                config.transcription.active_provider = provider_id

                # Save API key for this provider
                api_key = self.api_key_entry.get_text().strip()
                if api_key:
                    try:
                        provider_type = ProviderType(provider_id)
                        self.config_manager.set_api_key(api_key, provider_type)
                    except ValueError:
                        pass

                # Save model
                model_id = self.model_combo.get_active_id()
                if model_id:
                    try:
                        provider_type = ProviderType(provider_id)
                        self.config_manager.update_provider_config(provider_type, model=model_id)
                    except ValueError:
                        pass

            # Fallback provider
            fallback_id = self.fallback_combo.get_active_id()
            config.transcription.fallback_provider = fallback_id if fallback_id else ""

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
