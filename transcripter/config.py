"""Configuration management for Transcripter."""

import os
import toml
import keyring
from pathlib import Path
from typing import Optional, Any
from pydantic import BaseModel, Field

from .providers.base import ProviderType


class GeneralConfig(BaseModel):
    """General application settings."""
    autostart: bool = False
    show_notifications: bool = True
    language: str = ""  # Transcription language (empty = auto-detect)
    ui_language: str = ""  # UI language (empty = auto-detect from system)


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


# Provider-specific configuration models
class GroqProviderConfig(BaseModel):
    """Groq provider settings."""
    model: str = "whisper-large-v3-turbo"
    temperature: float = 0.0
    response_format: str = "text"
    prompt: str = ""


class OpenAIProviderConfig(BaseModel):
    """OpenAI provider settings."""
    model: str = "whisper-1"
    temperature: float = 0.0
    response_format: str = "text"
    prompt: str = ""


class GoogleCloudProviderConfig(BaseModel):
    """Google Cloud provider settings."""
    model: str = "chirp_2"
    enable_automatic_punctuation: bool = True
    enable_word_time_offsets: bool = True


class AssemblyAIProviderConfig(BaseModel):
    """AssemblyAI provider settings."""
    model: str = "best"
    speaker_labels: bool = False


class DeepgramProviderConfig(BaseModel):
    """Deepgram provider settings."""
    model: str = "nova-2"
    punctuate: bool = True
    smart_format: bool = True
    diarize: bool = False


class TranscriptionConfig(BaseModel):
    """Transcription settings with multi-provider support."""
    active_provider: str = "groq"
    fallback_provider: str = ""

    # Provider-specific settings
    groq: GroqProviderConfig = Field(default_factory=GroqProviderConfig)
    openai: OpenAIProviderConfig = Field(default_factory=OpenAIProviderConfig)
    google_cloud: GoogleCloudProviderConfig = Field(default_factory=GoogleCloudProviderConfig)
    assemblyai: AssemblyAIProviderConfig = Field(default_factory=AssemblyAIProviderConfig)
    deepgram: DeepgramProviderConfig = Field(default_factory=DeepgramProviderConfig)


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
    transcription: TranscriptionConfig = Field(default_factory=TranscriptionConfig)
    clipboard: ClipboardConfig = Field(default_factory=ClipboardConfig)
    history: HistoryConfig = Field(default_factory=HistoryConfig)
    ui: UIConfig = Field(default_factory=UIConfig)

    # Legacy support - deprecated, use transcription.groq instead
    groq: Optional[GroqProviderConfig] = None


class ConfigManager:
    """Manages application configuration."""

    APP_NAME = "transcripter"
    KEYRING_SERVICE = "transcripter"

    # Provider-specific keyring usernames
    KEYRING_USERNAMES = {
        ProviderType.GROQ: "groq_api_key",
        ProviderType.OPENAI: "openai_api_key",
        ProviderType.GOOGLE_CLOUD: "google_cloud_credentials_path",
        ProviderType.ASSEMBLYAI: "assemblyai_api_key",
        ProviderType.DEEPGRAM: "deepgram_api_key",
    }

    # Legacy support
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
        import sys
        if getattr(sys, 'frozen', False):
            # Running as compiled executable (PyInstaller)
            base_path = Path(sys._MEIPASS)
        else:
            # Running from source
            base_path = Path(__file__).parent.parent
        return base_path / "config" / "default_config.toml"

    def _migrate_legacy_config(self, config_data: dict) -> dict:
        """Migrate old config format to new format with transcription section."""
        # If old 'groq' section exists but no 'transcription' section
        if 'groq' in config_data and 'transcription' not in config_data:
            groq_config = config_data.pop('groq')
            config_data['transcription'] = {
                'active_provider': 'groq',
                'fallback_provider': '',
                'groq': groq_config,
            }
        return config_data

    def _load_config(self) -> Config:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            # Load existing config
            with open(self.config_file, 'r') as f:
                config_data = toml.load(f)

            # Migrate legacy config if needed
            config_data = self._migrate_legacy_config(config_data)

            return Config(**config_data)
        else:
            # Create default config
            default_config_path = self._get_default_config_path()
            if default_config_path.exists():
                with open(default_config_path, 'r') as f:
                    config_data = toml.load(f)
                config_data = self._migrate_legacy_config(config_data)
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

        config_dict = config.model_dump(exclude_none=True)

        # Remove legacy groq section from saved config
        config_dict.pop('groq', None)

        with open(self.config_file, 'w') as f:
            toml.dump(config_dict, f)

    def get_api_key(self, provider: Optional[ProviderType] = None) -> Optional[str]:
        """
        Get API key for a provider from secure storage.

        Args:
            provider: The provider type. If None, uses the active provider.

        Returns:
            The API key or None if not found.
        """
        if provider is None:
            provider = self.get_active_provider()

        keyring_username = self.KEYRING_USERNAMES.get(provider, self.KEYRING_USERNAME)

        try:
            return keyring.get_password(self.KEYRING_SERVICE, keyring_username)
        except Exception as e:
            print(f"Error retrieving API key for {provider.value}: {e}")
            return None

    def set_api_key(self, api_key: str, provider: Optional[ProviderType] = None) -> None:
        """
        Store API key for a provider in secure storage.

        Args:
            api_key: The API key to store.
            provider: The provider type. If None, uses the active provider.
        """
        if provider is None:
            provider = self.get_active_provider()

        keyring_username = self.KEYRING_USERNAMES.get(provider, self.KEYRING_USERNAME)

        try:
            keyring.set_password(self.KEYRING_SERVICE, keyring_username, api_key)
        except Exception as e:
            print(f"Error storing API key for {provider.value}: {e}")
            raise

    def delete_api_key(self, provider: Optional[ProviderType] = None) -> None:
        """
        Delete API key for a provider from secure storage.

        Args:
            provider: The provider type. If None, uses the active provider.
        """
        if provider is None:
            provider = self.get_active_provider()

        keyring_username = self.KEYRING_USERNAMES.get(provider, self.KEYRING_USERNAME)

        try:
            keyring.delete_password(self.KEYRING_SERVICE, keyring_username)
        except keyring.errors.PasswordDeleteError:
            pass  # Key doesn't exist
        except Exception as e:
            print(f"Error deleting API key for {provider.value}: {e}")

    def has_api_key(self, provider: Optional[ProviderType] = None) -> bool:
        """
        Check if an API key exists for a provider.

        Args:
            provider: The provider type. If None, uses the active provider.

        Returns:
            True if the API key exists.
        """
        return self.get_api_key(provider) is not None

    def get_active_provider(self) -> ProviderType:
        """Get the currently active transcription provider."""
        provider_name = self.config.transcription.active_provider
        try:
            return ProviderType(provider_name)
        except ValueError:
            # Default to Groq if invalid
            return ProviderType.GROQ

    def set_active_provider(self, provider: ProviderType) -> None:
        """Set the active transcription provider."""
        self.config.transcription.active_provider = provider.value
        self.save_config()

    def get_fallback_provider(self) -> Optional[ProviderType]:
        """Get the fallback transcription provider."""
        provider_name = self.config.transcription.fallback_provider
        if not provider_name:
            return None
        try:
            return ProviderType(provider_name)
        except ValueError:
            return None

    def set_fallback_provider(self, provider: Optional[ProviderType]) -> None:
        """Set the fallback transcription provider."""
        self.config.transcription.fallback_provider = provider.value if provider else ""
        self.save_config()

    def get_provider_config(self, provider: Optional[ProviderType] = None) -> BaseModel:
        """
        Get the configuration for a specific provider.

        Args:
            provider: The provider type. If None, uses the active provider.

        Returns:
            The provider-specific configuration model.
        """
        if provider is None:
            provider = self.get_active_provider()

        provider_configs = {
            ProviderType.GROQ: self.config.transcription.groq,
            ProviderType.OPENAI: self.config.transcription.openai,
            ProviderType.GOOGLE_CLOUD: self.config.transcription.google_cloud,
            ProviderType.ASSEMBLYAI: self.config.transcription.assemblyai,
            ProviderType.DEEPGRAM: self.config.transcription.deepgram,
        }

        return provider_configs.get(provider, self.config.transcription.groq)

    def update_provider_config(self, provider: ProviderType, **kwargs) -> None:
        """
        Update configuration for a specific provider.

        Args:
            provider: The provider type.
            **kwargs: Configuration values to update.
        """
        provider_config = self.get_provider_config(provider)

        for key, value in kwargs.items():
            if hasattr(provider_config, key):
                setattr(provider_config, key, value)

        self.save_config()

    def update_setting(self, section: str, key: str, value: Any) -> None:
        """Update a specific setting."""
        config_dict = self.config.model_dump()

        # Handle nested sections like transcription.groq.model
        parts = section.split('.')
        current = config_dict

        for part in parts[:-1] if len(parts) > 1 else []:
            if part in current:
                current = current[part]
            else:
                raise KeyError(f"Invalid section: {section}")

        final_section = parts[-1] if len(parts) > 1 else section

        if final_section in current and key in current[final_section]:
            current[final_section][key] = value
            self.config = Config(**config_dict)
            self.save_config()
        else:
            raise KeyError(f"Invalid setting: {section}.{key}")

    def get_setting(self, section: str, key: str) -> Any:
        """Get a specific setting value."""
        config_dict = self.config.model_dump()

        # Handle nested sections
        parts = section.split('.')
        current = config_dict

        for part in parts:
            if part in current:
                current = current[part]
            else:
                raise KeyError(f"Invalid section: {section}")

        if key in current:
            return current[key]
        else:
            raise KeyError(f"Invalid setting: {section}.{key}")

    def reset_to_default(self) -> None:
        """Reset configuration to default values."""
        default_config_path = self._get_default_config_path()
        if default_config_path.exists():
            with open(default_config_path, 'r') as f:
                config_data = toml.load(f)
            config_data = self._migrate_legacy_config(config_data)
            self.config = Config(**config_data)
        else:
            self.config = Config()

        self.save_config()


# Global configuration instance
config_manager = ConfigManager()
