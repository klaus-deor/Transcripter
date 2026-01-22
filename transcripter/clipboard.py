"""Clipboard management module."""

import pyperclip
import time
import threading
from typing import Optional, Callable


class ClipboardManager:
    """Manages clipboard operations."""

    def __init__(self):
        """Initialize the clipboard manager."""
        self.last_copied_text: Optional[str] = None
        self.clear_timer: Optional[threading.Timer] = None

        # Callbacks
        self.on_copied: Optional[Callable[[str], None]] = None
        self.on_cleared: Optional[Callable] = None

    def copy_text(self, text: str) -> bool:
        """
        Copy text to clipboard.

        Args:
            text: Text to copy

        Returns:
            True if successful, False otherwise
        """
        try:
            pyperclip.copy(text)
            self.last_copied_text = text

            if self.on_copied:
                self.on_copied(text)

            return True

        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            return False

    def paste_text(self) -> Optional[str]:
        """
        Get text from clipboard.

        Returns:
            Text from clipboard or None if error
        """
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Error pasting from clipboard: {e}")
            return None

    def clear_clipboard(self) -> bool:
        """
        Clear the clipboard.

        Returns:
            True if successful, False otherwise
        """
        try:
            pyperclip.copy("")

            if self.on_cleared:
                self.on_cleared()

            return True

        except Exception as e:
            print(f"Error clearing clipboard: {e}")
            return False

    def copy_with_auto_clear(self, text: str, clear_after_seconds: int) -> bool:
        """
        Copy text to clipboard and automatically clear after specified time.

        Args:
            text: Text to copy
            clear_after_seconds: Seconds to wait before clearing

        Returns:
            True if successful, False otherwise
        """
        # Cancel any existing timer
        if self.clear_timer:
            self.clear_timer.cancel()

        # Copy text
        success = self.copy_text(text)

        if success and clear_after_seconds > 0:
            # Schedule automatic clear
            self.clear_timer = threading.Timer(
                clear_after_seconds,
                self.clear_clipboard
            )
            self.clear_timer.daemon = True
            self.clear_timer.start()

        return success

    def cancel_auto_clear(self) -> None:
        """Cancel any pending auto-clear timer."""
        if self.clear_timer:
            self.clear_timer.cancel()
            self.clear_timer = None

    def get_last_copied(self) -> Optional[str]:
        """
        Get the last text copied by this manager.

        Returns:
            Last copied text or None
        """
        return self.last_copied_text

    @staticmethod
    def is_clipboard_available() -> bool:
        """
        Check if clipboard functionality is available.

        Returns:
            True if clipboard is available, False otherwise
        """
        try:
            pyperclip.paste()
            return True
        except pyperclip.PyperclipException:
            return False
        except Exception:
            return False


class ClipboardHistory:
    """Manages history of clipboard items."""

    def __init__(self, max_items: int = 50):
        """
        Initialize clipboard history.

        Args:
            max_items: Maximum number of items to keep in history
        """
        self.history: list[dict] = []
        self.max_items = max_items

    def add_item(self, text: str, timestamp: Optional[float] = None) -> None:
        """
        Add an item to the history.

        Args:
            text: Text to add
            timestamp: Unix timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()

        item = {
            "text": text,
            "timestamp": timestamp,
            "length": len(text)
        }

        # Add to history
        self.history.append(item)

        # Trim history if needed
        if len(self.history) > self.max_items:
            self.history.pop(0)

    def get_history(self) -> list[dict]:
        """
        Get the full history.

        Returns:
            List of history items
        """
        return self.history.copy()

    def get_recent(self, count: int = 10) -> list[dict]:
        """
        Get recent items from history.

        Args:
            count: Number of recent items to return

        Returns:
            List of recent history items
        """
        return self.history[-count:]

    def clear_history(self) -> None:
        """Clear all history."""
        self.history.clear()

    def remove_item(self, index: int) -> bool:
        """
        Remove an item from history by index.

        Args:
            index: Index of item to remove

        Returns:
            True if removed, False if index invalid
        """
        if 0 <= index < len(self.history):
            self.history.pop(index)
            return True
        return False

    def search_history(self, query: str) -> list[dict]:
        """
        Search history for items containing the query.

        Args:
            query: Search query

        Returns:
            List of matching history items
        """
        query_lower = query.lower()
        return [
            item for item in self.history
            if query_lower in item["text"].lower()
        ]

    def get_item(self, index: int) -> Optional[dict]:
        """
        Get a specific item from history.

        Args:
            index: Index of item

        Returns:
            History item or None if index invalid
        """
        if 0 <= index < len(self.history):
            return self.history[index]
        return None

    def size(self) -> int:
        """
        Get the current size of history.

        Returns:
            Number of items in history
        """
        return len(self.history)


def format_timestamp(timestamp: float) -> str:
    """
    Format a Unix timestamp to human-readable string.

    Args:
        timestamp: Unix timestamp

    Returns:
        Formatted time string
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
