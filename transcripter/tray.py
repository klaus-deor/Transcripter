"""System tray icon and menu management."""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, AppIndicator3, GLib
from typing import Callable, Optional
import os
from pathlib import Path


class TrayIcon:
    """Manages the system tray icon and menu."""

    def __init__(self, app_name: str = "Transcripter"):
        """
        Initialize the tray icon.

        Args:
            app_name: Name of the application
        """
        self.app_name = app_name
        self.indicator: Optional[AppIndicator3.Indicator] = None
        self.menu: Optional[Gtk.Menu] = None

        # Callbacks
        self.on_start_recording: Optional[Callable] = None
        self.on_stop_recording: Optional[Callable] = None
        self.on_settings: Optional[Callable] = None
        self.on_history: Optional[Callable] = None
        self.on_about: Optional[Callable] = None
        self.on_quit: Optional[Callable] = None

        # State
        self.is_recording = False

        # Menu items (stored for dynamic updates)
        self.record_menu_item: Optional[Gtk.MenuItem] = None
        self.status_menu_item: Optional[Gtk.MenuItem] = None

    def _get_icon_path(self, icon_name: str) -> str:
        """
        Get the full path to an icon.

        Args:
            icon_name: Name of the icon file

        Returns:
            Full path to the icon, or fallback to system icon
        """
        # Try to find icon in package directory
        package_dir = Path(__file__).parent
        icon_path = package_dir / "gui" / "icons" / icon_name

        if icon_path.exists():
            return str(icon_path)

        # Fallback to system icons
        icon_theme_map = {
            "idle.png": "audio-input-microphone",
            "recording.png": "media-record",
            "transcripter.png": "audio-input-microphone"
        }

        return icon_theme_map.get(icon_name, "audio-input-microphone")

    def create(self) -> bool:
        """
        Create and display the tray icon.

        Returns:
            True if created successfully, False otherwise
        """
        try:
            # Create indicator
            self.indicator = AppIndicator3.Indicator.new(
                self.app_name.lower(),
                self._get_icon_path("transcripter.png"),
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )

            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_title(self.app_name)

            # Create menu
            self.menu = Gtk.Menu()

            # Status item (non-clickable)
            self.status_menu_item = Gtk.MenuItem(label="Status: Idle")
            self.status_menu_item.set_sensitive(False)
            self.menu.append(self.status_menu_item)

            # Separator
            self.menu.append(Gtk.SeparatorMenuItem())

            # Start/Stop Recording
            self.record_menu_item = Gtk.MenuItem(label="Start Recording")
            self.record_menu_item.connect("activate", self._on_record_clicked)
            self.menu.append(self.record_menu_item)

            # Separator
            self.menu.append(Gtk.SeparatorMenuItem())

            # History
            history_item = Gtk.MenuItem(label="History")
            history_item.connect("activate", self._on_history_clicked)
            self.menu.append(history_item)

            # Settings
            settings_item = Gtk.MenuItem(label="Settings")
            settings_item.connect("activate", self._on_settings_clicked)
            self.menu.append(settings_item)

            # About
            about_item = Gtk.MenuItem(label="About")
            about_item.connect("activate", self._on_about_clicked)
            self.menu.append(about_item)

            # Separator
            self.menu.append(Gtk.SeparatorMenuItem())

            # Quit
            quit_item = Gtk.MenuItem(label="Quit")
            quit_item.connect("activate", self._on_quit_clicked)
            self.menu.append(quit_item)

            # Show all menu items
            self.menu.show_all()

            # Set the menu
            self.indicator.set_menu(self.menu)

            return True

        except Exception as e:
            print(f"Error creating tray icon: {e}")
            return False

    def _on_record_clicked(self, widget):
        """Handle record button click."""
        if self.is_recording:
            if self.on_stop_recording:
                self.on_stop_recording()
        else:
            if self.on_start_recording:
                self.on_start_recording()

    def _on_settings_clicked(self, widget):
        """Handle settings button click."""
        if self.on_settings:
            self.on_settings()

    def _on_history_clicked(self, widget):
        """Handle history button click."""
        if self.on_history:
            self.on_history()

    def _on_about_clicked(self, widget):
        """Handle about button click."""
        if self.on_about:
            self.on_about()
        else:
            # Show default about dialog
            self._show_about_dialog()

    def _on_quit_clicked(self, widget):
        """Handle quit button click."""
        if self.on_quit:
            self.on_quit()
        else:
            Gtk.main_quit()

    def set_recording_state(self, is_recording: bool) -> None:
        """
        Update the tray icon to reflect recording state.

        Args:
            is_recording: Whether recording is active
        """
        self.is_recording = is_recording

        if self.indicator:
            if is_recording:
                self.indicator.set_icon(self._get_icon_path("recording.png"))
                if self.record_menu_item:
                    self.record_menu_item.set_label("Stop Recording")
                if self.status_menu_item:
                    self.status_menu_item.set_label("Status: Recording")
            else:
                self.indicator.set_icon(self._get_icon_path("idle.png"))
                if self.record_menu_item:
                    self.record_menu_item.set_label("Start Recording")
                if self.status_menu_item:
                    self.status_menu_item.set_label("Status: Idle")

    def set_status(self, status: str) -> None:
        """
        Set the status text in the menu.

        Args:
            status: Status text to display
        """
        if self.status_menu_item:
            GLib.idle_add(self.status_menu_item.set_label, f"Status: {status}")

    def show_notification(self, title: str, message: str, icon: str = "dialog-information") -> None:
        """
        Show a desktop notification.

        Args:
            title: Notification title
            message: Notification message
            icon: Icon name (optional)
        """
        try:
            from gi.repository import Notify
            Notify.init(self.app_name)

            notification = Notify.Notification.new(title, message, icon)
            notification.show()

        except Exception as e:
            print(f"Error showing notification: {e}")

    def _show_about_dialog(self) -> None:
        """Show the about dialog."""
        dialog = Gtk.AboutDialog()
        dialog.set_program_name(self.app_name)
        dialog.set_version("1.0.0")
        dialog.set_comments(
            "Ferramenta de transcrição de áudio para Linux.\n"
            "Converte fala em texto usando a API Groq Whisper.\n\n"
            "Grave áudio com um atalho de teclado e tenha o texto\n"
            "automaticamente copiado para a área de transferência."
        )
        dialog.set_website("https://github.com/klaus-deor/Transcripter")
        dialog.set_website_label("GitHub - klaus-deor/Transcripter")
        dialog.set_license_type(Gtk.License.MIT_X11)
        dialog.set_copyright("Copyright © 2024 Klaus Deor")
        dialog.set_authors([
            "Klaus Deor <github.com/klaus-deor>",
            "Claude Code (Anthropic AI Assistant)"
        ])
        dialog.set_documenters(["Klaus Deor"])
        dialog.set_translator_credits("Klaus Deor")

        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()

    def update_menu(self) -> None:
        """Force update the menu display."""
        if self.menu:
            self.menu.show_all()

    def destroy(self) -> None:
        """Clean up and remove the tray icon."""
        if self.indicator:
            self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
            self.indicator = None

        if self.menu:
            self.menu = None


class NotificationManager:
    """Manages desktop notifications."""

    def __init__(self, app_name: str = "Transcripter"):
        """
        Initialize the notification manager.

        Args:
            app_name: Application name
        """
        self.app_name = app_name
        self.initialized = False

        try:
            from gi.repository import Notify
            Notify.init(app_name)
            self.initialized = True
        except Exception as e:
            print(f"Failed to initialize notifications: {e}")

    def show(
        self,
        title: str,
        message: str,
        icon: str = "dialog-information",
        urgency: str = "normal"
    ) -> bool:
        """
        Show a notification.

        Args:
            title: Notification title
            message: Notification message
            icon: Icon name
            urgency: Urgency level ("low", "normal", "critical")

        Returns:
            True if shown successfully, False otherwise
        """
        if not self.initialized:
            print(f"Notification: {title} - {message}")
            return False

        try:
            from gi.repository import Notify

            notification = Notify.Notification.new(title, message, icon)

            # Set urgency
            urgency_map = {
                "low": Notify.Urgency.LOW,
                "normal": Notify.Urgency.NORMAL,
                "critical": Notify.Urgency.CRITICAL
            }
            notification.set_urgency(urgency_map.get(urgency, Notify.Urgency.NORMAL))

            notification.show()
            return True

        except Exception as e:
            print(f"Error showing notification: {e}")
            return False

    def show_recording_started(self) -> None:
        """Show notification for recording started."""
        self.show(
            "Recording Started",
            "Audio recording in progress...",
            "media-record",
            "normal"
        )

    def show_recording_stopped(self) -> None:
        """Show notification for recording stopped."""
        self.show(
            "Recording Stopped",
            "Processing audio...",
            "media-playback-stop",
            "normal"
        )

    def show_transcription_complete(self, text_preview: str = "") -> None:
        """Show notification for transcription complete."""
        message = "Text copied to clipboard"
        if text_preview:
            preview = text_preview[:50] + "..." if len(text_preview) > 50 else text_preview
            message = f"{message}\n\n{preview}"

        self.show(
            "Transcription Complete",
            message,
            "dialog-information",
            "normal"
        )

    def show_error(self, error_message: str) -> None:
        """Show error notification."""
        self.show(
            "Transcription Error",
            error_message,
            "dialog-error",
            "critical"
        )
