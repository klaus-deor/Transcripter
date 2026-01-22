"""History window for Transcripter."""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

from typing import Optional, Callable
from ..clipboard import ClipboardHistory, ClipboardManager, format_timestamp


class HistoryWindow:
    """Window to display transcription history."""

    def __init__(self, clipboard_history: ClipboardHistory, clipboard_manager: ClipboardManager, max_items: int = 50):
        """
        Initialize the history window.

        Args:
            clipboard_history: ClipboardHistory instance with transcription history
            clipboard_manager: ClipboardManager for copying text
            max_items: Maximum number of history items to display
        """
        self.clipboard_history = clipboard_history
        self.clipboard_manager = clipboard_manager
        self.max_items = max_items
        self.window: Optional[Gtk.Window] = None

    def show(self) -> None:
        """Show the history window."""
        if self.window:
            self.window.present()
            self._refresh_history()
            return

        self._create_window()
        self.window.show_all()

    def _create_window(self) -> None:
        """Create the history window and its widgets."""
        self.window = Gtk.Window(title="Transcription History")
        self.window.set_default_size(500, 400)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("delete-event", self._on_close)

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_border_width(10)
        self.window.add(main_box)

        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_label = Gtk.Label()
        header_label.set_markup("<b>Recent Transcriptions</b>")
        header_label.set_xalign(0)
        header_box.pack_start(header_label, True, True, 0)

        # Refresh button
        refresh_button = Gtk.Button(label="Refresh")
        refresh_button.connect("clicked", self._on_refresh_clicked)
        header_box.pack_end(refresh_button, False, False, 0)

        main_box.pack_start(header_box, False, False, 0)

        # Scrolled window for history items
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        main_box.pack_start(scrolled, True, True, 0)

        # Container for history items
        self.history_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scrolled.add(self.history_box)

        # Populate history
        self._refresh_history()

        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_halign(Gtk.Align.END)
        main_box.pack_start(button_box, False, False, 0)

        # Clear history button
        clear_button = Gtk.Button(label="Clear History")
        clear_button.connect("clicked", self._on_clear_clicked)
        button_box.pack_start(clear_button, False, False, 0)

        # Close button
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", self._on_close_clicked)
        button_box.pack_start(close_button, False, False, 0)

    def _refresh_history(self) -> None:
        """Refresh the history display."""
        # Clear existing items
        for child in self.history_box.get_children():
            self.history_box.remove(child)

        # Get recent history (based on configured max_items)
        history = self.clipboard_history.get_recent(self.max_items)

        if not history:
            # Show empty message
            empty_label = Gtk.Label(label="No transcriptions yet.\n\nUse the hotkey to record and transcribe audio.")
            empty_label.set_justify(Gtk.Justification.CENTER)
            empty_label.set_opacity(0.6)
            self.history_box.pack_start(empty_label, True, True, 50)
        else:
            # Show history items (newest first)
            for i, item in enumerate(reversed(history)):
                frame = self._create_history_item(item, len(history) - 1 - i)
                self.history_box.pack_start(frame, False, False, 0)

        self.history_box.show_all()

    def _create_history_item(self, item: dict, index: int) -> Gtk.Frame:
        """
        Create a widget for a history item.

        Args:
            item: History item dict with 'text', 'timestamp', 'length'
            index: Index in history list

        Returns:
            Gtk.Frame containing the history item
        """
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_border_width(10)
        frame.add(box)

        # Header with timestamp
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        timestamp_label = Gtk.Label()
        timestamp_str = format_timestamp(item["timestamp"])
        timestamp_label.set_markup(f"<small><b>{timestamp_str}</b></small>")
        timestamp_label.set_xalign(0)
        header_box.pack_start(timestamp_label, True, True, 0)

        # Character count
        chars_label = Gtk.Label()
        chars_label.set_markup(f"<small>{item['length']} chars</small>")
        chars_label.set_opacity(0.6)
        header_box.pack_end(chars_label, False, False, 0)

        box.pack_start(header_box, False, False, 0)

        # Text content (truncated if too long)
        text = item["text"]
        display_text = text if len(text) <= 200 else text[:200] + "..."

        text_label = Gtk.Label(label=display_text)
        text_label.set_line_wrap(True)
        text_label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        text_label.set_xalign(0)
        text_label.set_selectable(True)
        text_label.set_max_width_chars(60)
        box.pack_start(text_label, False, False, 0)

        # Copy button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_halign(Gtk.Align.END)

        copy_button = Gtk.Button(label="Copy")
        copy_button.connect("clicked", self._on_copy_clicked, text)
        button_box.pack_start(copy_button, False, False, 0)

        box.pack_start(button_box, False, False, 0)

        return frame

    def _on_copy_clicked(self, button, text: str) -> None:
        """Handle copy button click."""
        self.clipboard_manager.copy_text(text)

        # Visual feedback
        original_label = button.get_label()
        button.set_label("Copied!")
        button.set_sensitive(False)

        # Reset after a short delay
        from gi.repository import GLib
        GLib.timeout_add(1000, self._reset_copy_button, button, original_label)

    def _reset_copy_button(self, button, label: str) -> bool:
        """Reset copy button to original state."""
        button.set_label(label)
        button.set_sensitive(True)
        return False  # Don't repeat

    def _on_refresh_clicked(self, button) -> None:
        """Handle refresh button click."""
        self._refresh_history()

    def _on_clear_clicked(self, button) -> None:
        """Handle clear history button click."""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Clear History?"
        )
        dialog.format_secondary_text("This will remove all transcription history. This action cannot be undone.")

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self.clipboard_history.clear_history()
            self._refresh_history()

    def _on_close_clicked(self, button) -> None:
        """Handle close button click."""
        self.window.destroy()
        self.window = None

    def _on_close(self, widget, event) -> bool:
        """Handle window close event."""
        self.window = None
        return False
