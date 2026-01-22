"""Main entry point for Transcripter."""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

import os
import sys
import signal
import tempfile
import threading
from pathlib import Path
from typing import Optional

from .config import ConfigManager
from .audio import AudioRecorder
from .transcription import TranscriptionService
from .clipboard import ClipboardManager, ClipboardHistory
from .hotkeys import HotkeyManager
from .tray import TrayIcon, NotificationManager
from .gui.settings import SettingsWindow
from .gui.history import HistoryWindow


class TranscripterApp:
    """Main application class for Transcripter."""

    def __init__(self):
        """Initialize the application."""
        # Core components
        self.config_manager = ConfigManager()
        self.clipboard_manager = ClipboardManager()
        self.clipboard_history = ClipboardHistory(
            max_items=self.config_manager.config.history.max_items
        )
        self.hotkey_manager = HotkeyManager()
        self.notification_manager = NotificationManager()

        # Audio and transcription (initialized later)
        self.audio_recorder: Optional[AudioRecorder] = None
        self.transcription_service: Optional[TranscriptionService] = None

        # GUI
        self.tray_icon = TrayIcon()
        self.settings_window = SettingsWindow(self.config_manager)
        self.history_window = HistoryWindow(
            self.clipboard_history,
            self.clipboard_manager,
            max_items=self.config_manager.config.history.max_items
        )

        # State
        self.is_recording = False
        self.temp_audio_file: Optional[str] = None

        # Setup callbacks
        self._setup_callbacks()

    def _setup_callbacks(self) -> None:
        """Setup callbacks for various components."""
        # Tray icon callbacks
        self.tray_icon.on_start_recording = self.start_recording
        self.tray_icon.on_stop_recording = self.stop_recording
        self.tray_icon.on_settings = self.show_settings
        self.tray_icon.on_history = self.show_history
        self.tray_icon.on_quit = self.quit

        # Settings window callback
        self.settings_window.on_settings_changed = self.on_settings_changed

    def initialize(self) -> bool:
        """
        Initialize all components.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Check for API key
            api_key = self.config_manager.get_api_key()
            if not api_key:
                print("No API key found. Please configure your Groq API key in settings.")
                # Show settings on first run
                GLib.idle_add(self.show_settings)
            else:
                # Initialize transcription service
                self.transcription_service = TranscriptionService(api_key)

            # Initialize audio recorder
            config = self.config_manager.config
            self.audio_recorder = AudioRecorder(
                sample_rate=config.audio.sample_rate,
                channels=config.audio.channels,
                device_name=config.audio.device_name
            )

            # Register hotkeys
            self._register_hotkeys()

            # Create tray icon
            if not self.tray_icon.create():
                print("Warning: Failed to create tray icon")
                return False

            # Start hotkey listener
            self.hotkey_manager.start()

            return True

        except Exception as e:
            print(f"Initialization error: {e}")
            return False

    def _register_hotkeys(self) -> None:
        """Register global hotkeys."""
        config = self.config_manager.config

        if config.hotkeys.toggle_mode:
            # Same key for start and stop
            self.hotkey_manager.register_hotkey(
                config.hotkeys.start_recording,
                self.toggle_recording
            )
        else:
            # Separate keys
            self.hotkey_manager.register_hotkey(
                config.hotkeys.start_recording,
                self.start_recording
            )
            self.hotkey_manager.register_hotkey(
                config.hotkeys.stop_recording,
                self.stop_recording
            )

    def toggle_recording(self) -> None:
        """Toggle recording on/off."""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self) -> None:
        """Start audio recording."""
        if self.is_recording:
            return

        try:
            # Create temp file for audio
            temp_dir = tempfile.gettempdir()
            self.temp_audio_file = os.path.join(
                temp_dir,
                f"transcripter_{os.getpid()}.wav"
            )

            # Start recording
            max_duration = self.config_manager.config.audio.max_duration
            if self.audio_recorder.start_recording(max_duration=max_duration):
                self.is_recording = True
                GLib.idle_add(self.tray_icon.set_recording_state, True)

                if self.config_manager.config.general.show_notifications:
                    self.notification_manager.show_recording_started()

                print("Recording started...")

        except Exception as e:
            print(f"Error starting recording: {e}")
            self._show_error(f"Failed to start recording: {e}")

    def stop_recording(self) -> None:
        """Stop audio recording and process transcription."""
        if not self.is_recording:
            return

        try:
            # Stop recording
            audio_data = self.audio_recorder.stop_recording()
            self.is_recording = False
            GLib.idle_add(self.tray_icon.set_recording_state, False)

            if self.config_manager.config.general.show_notifications:
                self.notification_manager.show_recording_stopped()

            print("Recording stopped. Processing...")

            if audio_data is None or len(audio_data) == 0:
                self._show_error("No audio data recorded")
                return

            # Save audio to temp file
            if not self.audio_recorder.save_to_file(audio_data, self.temp_audio_file):
                self._show_error("Failed to save audio file")
                return

            # Process transcription in background thread
            thread = threading.Thread(target=self._process_transcription)
            thread.daemon = True
            thread.start()

        except Exception as e:
            print(f"Error stopping recording: {e}")
            self._show_error(f"Failed to stop recording: {e}")

    def _process_transcription(self) -> None:
        """Process transcription in background thread."""
        try:
            if not self.transcription_service:
                api_key = self.config_manager.get_api_key()
                if not api_key:
                    GLib.idle_add(
                        self._show_error,
                        "No API key configured. Please set your Groq API key in settings."
                    )
                    return

                self.transcription_service = TranscriptionService(api_key)

            config = self.config_manager.config

            # Update status
            GLib.idle_add(self.tray_icon.set_status, "Transcribing...")

            # Transcribe with retry
            transcription = self.transcription_service.transcribe_file_with_retry(
                file_path=self.temp_audio_file,
                model=config.groq.model,
                language=config.general.language if config.general.language else None,
                temperature=config.groq.temperature,
                response_format=config.groq.response_format,
                max_retries=3
            )

            # Clean up temp file
            if self.temp_audio_file and os.path.exists(self.temp_audio_file):
                os.remove(self.temp_audio_file)

            if transcription:
                # Copy to clipboard
                self.clipboard_manager.copy_text(transcription)

                # Add to history
                if config.history.enabled:
                    import time
                    self.clipboard_history.add_item(transcription, time.time())

                # Show success notification
                if config.general.show_notifications:
                    self.notification_manager.show_transcription_complete(transcription)

                print(f"Transcription complete: {transcription}")

                # Update status
                GLib.idle_add(self.tray_icon.set_status, "Idle")

            else:
                error_msg = self.transcription_service.get_last_error() or "Unknown error"
                GLib.idle_add(self._show_error, f"Transcription failed: {error_msg}")
                GLib.idle_add(self.tray_icon.set_status, "Idle")

        except Exception as e:
            print(f"Transcription error: {e}")
            GLib.idle_add(self._show_error, f"Transcription error: {e}")
            GLib.idle_add(self.tray_icon.set_status, "Idle")

    def _show_error(self, message: str) -> None:
        """Show an error notification."""
        print(f"Error: {message}")
        if self.config_manager.config.general.show_notifications:
            self.notification_manager.show_error(message)

    def show_settings(self) -> None:
        """Show the settings window."""
        self.settings_window.show()

    def show_history(self) -> None:
        """Show the transcription history window."""
        self.history_window.show()

    def on_settings_changed(self) -> None:
        """Handle settings changes."""
        print("Settings changed. Reloading configuration...")

        # Reload audio recorder settings
        config = self.config_manager.config
        if self.audio_recorder:
            if config.audio.device_name:
                self.audio_recorder.set_device(config.audio.device_name)

        # Re-register hotkeys
        self.hotkey_manager.unregister_all()
        self._register_hotkeys()

        # Update clipboard history size
        self.clipboard_history.max_items = config.history.max_items

        # Update history window max items
        self.history_window.max_items = config.history.max_items

        # Reinitialize transcription service if API key changed
        api_key = self.config_manager.get_api_key()
        if api_key:
            self.transcription_service = TranscriptionService(api_key)

    def _setup_signal_handlers(self) -> None:
        """Setup Unix signal handlers for external control."""
        def signal_handler(signum, frame):
            """Handle USR1 signal to toggle recording."""
            if signum == signal.SIGUSR1:
                print("Received USR1 signal - toggling recording")
                GLib.idle_add(self.toggle_recording)

        signal.signal(signal.SIGUSR1, signal_handler)
        print("Signal handlers configured (USR1 = toggle recording)")

    def run(self) -> None:
        """Run the application."""
        if not self.initialize():
            print("Failed to initialize application")
            sys.exit(1)

        # Setup signal handlers for external control
        self._setup_signal_handlers()

        print("Transcripter started successfully!")
        print(f"Hotkey: {self.config_manager.config.hotkeys.start_recording}")
        print("Alternative: Send USR1 signal to toggle recording")
        print(f"  kill -USR1 {os.getpid()}")

        # Run GTK main loop
        try:
            Gtk.main()
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.quit()

    def quit(self) -> None:
        """Quit the application."""
        print("Quitting Transcripter...")

        # Stop recording if active
        if self.is_recording:
            self.audio_recorder.stop_recording()

        # Stop hotkey listener
        self.hotkey_manager.stop()

        # Destroy tray icon
        self.tray_icon.destroy()

        # Clean up temp file
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            os.remove(self.temp_audio_file)

        # Quit GTK
        Gtk.main_quit()


def main():
    """Main entry point."""
    app = TranscripterApp()
    app.run()


if __name__ == "__main__":
    main()
