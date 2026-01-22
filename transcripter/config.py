"""Configuration management for Transcripter."""

import os
import toml
import keyring
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class GeneralConfig(BaseModel):
    """General application settings."""
    autostart: bool = False
    show_notifications: bool = True
    language: str = "pt"


class AudioConfig(BaseModel):
    """Audio recording settings."""
    sample_rate: int = 16000
    channels: int = 1
    format: str = "wav"
    device_name: str = ""
    max_duration: int = 300


class HotkeysConfig(BaseModel):
    """Hotkey configuration."""
    start_recording: str = "ctrl+alt+r"
    stop_recording: str = "ctrl+alt+r"
    toggle_mode: bool = True


class GroqConfig(BaseModel):
    """Groq API settings."""
    model: str = "whisper-large-v3-turbo"
    temperature: float = 0.0
    response_format: str = "text"
    prompt: str = ""


class ClipboardConfig(BaseModel):
    """Clipboard settings."""
    auto_paste: bool = False
    clear_after: int = 0


class HistoryConfig(BaseModel):
    """Transcription history settings."""
    enabled: bool = True
    max_items: int = 50
    save_to_file: bool = True


class UIConfig(BaseModel):
    """UI settings."""
    theme: str = "system"
    show_recording_indicator: bool = True


class Config(BaseModel):
    """Main configuration model."""
    general: GeneralConfig = Field(default_factory=GeneralConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    hotkeys: HotkeysConfig = Field(default_factory=HotkeysConfig)
    groq: GroqConfig = Field(default_factory=GroqConfig)
    clipboard: ClipboardConfig = Field(default_factory=ClipboardConfig)
    history: HistoryConfig = Field(default_factory=HistoryConfig)
    ui: UIConfig = Field(default_factory=UIConfig)


class ConfigManager:
    """Manages application configuration."""

    APP_NAME = "transcripter"
    KEYRING_SERVICE = "transcripter"
    KEYRING_USERNAME = "groq_api_key"

    def __init__(self):
        """Initialize the configuration manager."""
        self.config_dir = Path.home() / ".config" / self.APP_NAME
        self.config_file = self.config_dir / "config.toml"
        self.history_file = self.config_dir / "history.json"

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

    def _get_default_config_path(self) -> Path:
        """Get the default configuration file path."""
        # Look for default config in the package directory
        package_dir = Path(__file__).parent.parent
        return package_dir / "config" / "default_config.toml"

    def _load_config(self) -> Config:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            # Load existing config
            with open(self.config_file, 'r') as f:
                config_data = toml.load(f)
            return Config(**config_data)
        else:
            # Create default config
            default_config_path = self._get_default_config_path()
            if default_config_path.exists():
                with open(default_config_path, 'r') as f:
                    config_data = toml.load(f)
                config = Config(**config_data)
            else:
                config = Config()

            # Save default config
            self.save_config(config)
            return config

    def save_config(self, config: Optional[Config] = None) -> None:
        """Save configuration to file."""
        if config is None:
            config = self.config
        else:
            self.config = config

        config_dict = config.model_dump()
        with open(self.config_file, 'w') as f:
            toml.dump(config_dict, f)

    def get_api_key(self) -> Optional[str]:
        """Get Groq API key from secure storage."""
        try:
            return keyring.get_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME)
        except Exception as e:
            print(f"Error retrieving API key: {e}")
            return None

    def set_api_key(self, api_key: str) -> None:
        """Store Groq API key in secure storage."""
        try:
            keyring.set_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME, api_key)
        except Exception as e:
            print(f"Error storing API key: {e}")
            raise

    def delete_api_key(self) -> None:
        """Delete Groq API key from secure storage."""
        try:
            keyring.delete_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME)
        except keyring.errors.PasswordDeleteError:
            pass  # Key doesn't exist
        except Exception as e:
            print(f"Error deleting API key: {e}")

    def update_setting(self, section: str, key: str, value: Any) -> None:
        """Update a specific setting."""
        config_dict = self.config.model_dump()
        if section in config_dict and key in config_dict[section]:
            config_dict[section][key] = value
            self.config = Config(**config_dict)
            self.save_config()
        else:
            raise KeyError(f"Invalid setting: {section}.{key}")

    def get_setting(self, section: str, key: str) -> Any:
        """Get a specific setting value."""
        config_dict = self.config.model_dump()
        if section in config_dict and key in config_dict[section]:
            return config_dict[section][key]
        else:
            raise KeyError(f"Invalid setting: {section}.{key}")

    def reset_to_default(self) -> None:
        """Reset configuration to default values."""
        default_config_path = self._get_default_config_path()
        if default_config_path.exists():
            with open(default_config_path, 'r') as f:
                config_data = toml.load(f)
            self.config = Config(**config_data)
        else:
            self.config = Config()

        self.save_config()


# Global configuration instance
config_manager = ConfigManager()
