"""Global hotkey management module."""

import threading
from typing import Callable, Optional, Dict
from pynput import keyboard


class HotkeyManager:
    """Manages global keyboard hotkeys."""

    def __init__(self):
        """Initialize the hotkey manager."""
        self.listener: Optional[keyboard.Listener] = None
        self.hotkeys: Dict[str, Callable] = {}
        self.pressed_keys = set()
        self.is_running = False

    def _normalize_key(self, key_str: str) -> set:
        """
        Normalize a hotkey string to a set of keys.

        Args:
            key_str: Hotkey string (e.g., "ctrl+alt+r")

        Returns:
            Set of normalized key names
        """
        parts = key_str.lower().split('+')
        normalized = set()

        for part in parts:
            part = part.strip()

            # Map common key names
            key_map = {
                'ctrl': keyboard.Key.ctrl_l,
                'control': keyboard.Key.ctrl_l,
                'alt': keyboard.Key.alt_l,
                'shift': keyboard.Key.shift_l,
                'super': keyboard.Key.cmd,
                'win': keyboard.Key.cmd,
                'cmd': keyboard.Key.cmd,
            }

            if part in key_map:
                normalized.add(key_map[part])
            else:
                # Regular character key
                try:
                    normalized.add(keyboard.KeyCode.from_char(part))
                except:
                    # Try as a special key
                    try:
                        normalized.add(getattr(keyboard.Key, part))
                    except:
                        print(f"Warning: Unknown key '{part}'")

        return normalized

    def _key_to_string(self, key) -> str:
        """
        Convert a key object to string representation.

        Args:
            key: Key object

        Returns:
            String representation of the key
        """
        if isinstance(key, keyboard.KeyCode):
            return key.char if key.char else str(key)
        elif isinstance(key, keyboard.Key):
            return key.name
        else:
            return str(key)

    def _on_press(self, key):
        """
        Handle key press events.

        Args:
            key: The key that was pressed
        """
        try:
            self.pressed_keys.add(key)
            self._check_hotkeys()
        except Exception as e:
            print(f"Error in key press handler: {e}")

    def _on_release(self, key):
        """
        Handle key release events.

        Args:
            key: The key that was released
        """
        try:
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)
        except Exception as e:
            print(f"Error in key release handler: {e}")

    def _check_hotkeys(self):
        """Check if any registered hotkeys match the currently pressed keys."""
        for hotkey_str, callback in self.hotkeys.items():
            expected_keys = self._normalize_key(hotkey_str)

            # Check if all expected keys are pressed
            # We need to handle both left and right modifiers
            pressed_key_strings = {self._key_to_string(k) for k in self.pressed_keys}
            expected_key_strings = {self._key_to_string(k) for k in expected_keys}

            # For modifier keys, check if any variant (left/right) is pressed
            modifier_match = True
            regular_match = True

            for expected_key in expected_keys:
                if isinstance(expected_key, keyboard.Key):
                    # Check for modifier keys with left/right variants
                    key_name = expected_key.name
                    if not any(
                        k.name == key_name or
                        k.name == f"{key_name}_l" or
                        k.name == f"{key_name}_r"
                        for k in self.pressed_keys
                        if isinstance(k, keyboard.Key)
                    ):
                        modifier_match = False
                        break
                else:
                    # Regular character key - exact match
                    if expected_key not in self.pressed_keys:
                        regular_match = False
                        break

            if modifier_match and regular_match and len(self.pressed_keys) == len(expected_keys):
                # Hotkey matched - trigger callback
                try:
                    callback()
                except Exception as e:
                    print(f"Error executing hotkey callback: {e}")

    def register_hotkey(self, hotkey: str, callback: Callable) -> bool:
        """
        Register a global hotkey.

        Args:
            hotkey: Hotkey string (e.g., "ctrl+alt+r")
            callback: Function to call when hotkey is pressed

        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Validate the hotkey format
            normalized = self._normalize_key(hotkey)
            if not normalized:
                print(f"Invalid hotkey format: {hotkey}")
                return False

            self.hotkeys[hotkey] = callback
            print(f"Registered hotkey: {hotkey}")
            return True

        except Exception as e:
            print(f"Error registering hotkey: {e}")
            return False

    def unregister_hotkey(self, hotkey: str) -> bool:
        """
        Unregister a global hotkey.

        Args:
            hotkey: Hotkey string to unregister

        Returns:
            True if unregistration successful, False otherwise
        """
        if hotkey in self.hotkeys:
            del self.hotkeys[hotkey]
            print(f"Unregistered hotkey: {hotkey}")
            return True
        else:
            print(f"Hotkey not found: {hotkey}")
            return False

    def unregister_all(self) -> None:
        """Unregister all hotkeys."""
        self.hotkeys.clear()
        print("All hotkeys unregistered")

    def start(self) -> bool:
        """
        Start listening for hotkeys.

        Returns:
            True if started successfully, False otherwise
        """
        if self.is_running:
            print("Hotkey listener already running")
            return False

        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            self.is_running = True
            print("Hotkey listener started")
            return True

        except Exception as e:
            print(f"Error starting hotkey listener: {e}")
            return False

    def stop(self) -> None:
        """Stop listening for hotkeys."""
        if self.listener:
            self.listener.stop()
            self.listener = None
            self.is_running = False
            self.pressed_keys.clear()
            print("Hotkey listener stopped")

    def is_hotkey_pressed(self, hotkey: str) -> bool:
        """
        Check if a specific hotkey is currently pressed.

        Args:
            hotkey: Hotkey string to check

        Returns:
            True if hotkey is pressed, False otherwise
        """
        expected_keys = self._normalize_key(hotkey)
        return expected_keys.issubset(self.pressed_keys)


class HotkeyValidator:
    """Validates and normalizes hotkey strings."""

    VALID_MODIFIERS = ['ctrl', 'control', 'alt', 'shift', 'super', 'win', 'cmd']
    VALID_SPECIAL_KEYS = [
        'space', 'enter', 'tab', 'backspace', 'delete', 'esc', 'escape',
        'up', 'down', 'left', 'right',
        'home', 'end', 'page_up', 'page_down',
        'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
    ]

    @staticmethod
    def validate(hotkey: str) -> tuple[bool, str]:
        """
        Validate a hotkey string.

        Args:
            hotkey: Hotkey string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not hotkey or not isinstance(hotkey, str):
            return False, "Hotkey must be a non-empty string"

        parts = [p.strip().lower() for p in hotkey.split('+')]

        if len(parts) < 1:
            return False, "Hotkey must contain at least one key"

        # Check for valid modifiers and keys
        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)

            if part in HotkeyValidator.VALID_MODIFIERS:
                if is_last:
                    return False, "Hotkey must end with a regular key, not a modifier"
                continue

            if part in HotkeyValidator.VALID_SPECIAL_KEYS:
                continue

            # Check if it's a single character
            if len(part) == 1 and part.isalnum():
                continue

            return False, f"Invalid key: '{part}'"

        return True, ""

    @staticmethod
    def normalize(hotkey: str) -> str:
        """
        Normalize a hotkey string to a consistent format.

        Args:
            hotkey: Hotkey string to normalize

        Returns:
            Normalized hotkey string
        """
        parts = [p.strip().lower() for p in hotkey.split('+')]
        return '+'.join(parts)

    @staticmethod
    def format_for_display(hotkey: str) -> str:
        """
        Format a hotkey string for display to users.

        Args:
            hotkey: Hotkey string

        Returns:
            Formatted hotkey string
        """
        parts = [p.strip().capitalize() for p in hotkey.split('+')]
        return ' + '.join(parts)
