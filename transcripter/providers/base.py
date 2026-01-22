"""Base classes for transcription providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Any
import os


class ProviderType(str, Enum):
    """Supported transcription providers."""
    GROQ = "groq"
    OPENAI = "openai"
    GOOGLE_CLOUD = "google_cloud"
    ASSEMBLYAI = "assemblyai"
    DEEPGRAM = "deepgram"


@dataclass
class ProviderCapabilities:
    """Describes the capabilities of a transcription provider."""
    supports_streaming: bool = False
    supports_diarization: bool = False
    supports_timestamps: bool = False
    supports_language_detection: bool = True
    max_file_size_mb: int = 25
    supported_formats: list[str] = field(default_factory=lambda: ["wav", "mp3", "m4a", "flac", "ogg", "webm"])
    requires_file_upload: bool = False


@dataclass
class TranscriptionResult:
    """Result of a transcription operation."""
    text: str
    provider: ProviderType
    model: str
    language: Optional[str] = None
    duration_seconds: Optional[float] = None
    confidence: Optional[float] = None
    words: Optional[list[dict]] = None
    segments: Optional[list[dict]] = None
    raw_response: Optional[Any] = None


class TranscriptionError(Exception):
    """Base exception for transcription errors."""
    def __init__(self, message: str, provider: ProviderType, recoverable: bool = True):
        self.message = message
        self.provider = provider
        self.recoverable = recoverable
        super().__init__(message)


class APIKeyError(TranscriptionError):
    """Raised when API key is invalid or missing."""
    def __init__(self, provider: ProviderType):
        super().__init__(f"Invalid or missing API key for {provider.value}", provider, recoverable=False)


class RateLimitError(TranscriptionError):
    """Raised when rate limit is exceeded."""
    def __init__(self, provider: ProviderType, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        message = f"Rate limit exceeded for {provider.value}"
        if retry_after:
            message += f" (retry after {retry_after}s)"
        super().__init__(message, provider, recoverable=True)


class TranscriptionProvider(ABC):
    """Abstract base class for transcription providers."""

    # Class-level attributes to be overridden by subclasses
    provider_type: ProviderType
    display_name: str
    capabilities: ProviderCapabilities

    def __init__(self, api_key: str):
        """
        Initialize the provider with an API key.

        Args:
            api_key: The API key for authentication

        Raises:
            ValueError: If API key is empty or None
        """
        if not api_key:
            raise ValueError(f"API key is required for {self.display_name}")
        self._api_key = api_key
        self._client: Any = None

        # Callbacks
        self.on_transcription_started: Optional[Callable] = None
        self.on_transcription_completed: Optional[Callable[[TranscriptionResult], None]] = None
        self.on_transcription_failed: Optional[Callable[[str], None]] = None

    @abstractmethod
    def _initialize_client(self) -> None:
        """Initialize the provider's API client."""
        pass

    @abstractmethod
    def transcribe_file(
        self,
        file_path: str,
        model: Optional[str] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        **kwargs
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe an audio file.

        Args:
            file_path: Path to the audio file
            model: Model to use (provider-specific)
            language: Language code (e.g., "en", "pt") or None for auto-detection
            prompt: Optional prompt to guide the model
            temperature: Sampling temperature (0.0 - 1.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            TranscriptionResult or None if transcription failed
        """
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        Validate the API key by making a test request.

        Returns:
            True if API key is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_supported_models(self) -> list[dict[str, str]]:
        """
        Get list of supported models.

        Returns:
            List of dicts with 'id' and 'name' keys
        """
        pass

    def get_default_model(self) -> str:
        """
        Get the default model for this provider.

        Returns:
            Default model ID
        """
        models = self.get_supported_models()
        return models[0]["id"] if models else ""

    def _validate_file(self, file_path: str) -> bool:
        """
        Validate that the file exists and is a supported format.

        Args:
            file_path: Path to the audio file

        Returns:
            True if file is valid

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower().lstrip(".")
        if ext not in self.capabilities.supported_formats:
            raise ValueError(
                f"Unsupported audio format: {ext}. "
                f"Supported formats: {', '.join(self.capabilities.supported_formats)}"
            )

        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.capabilities.max_file_size_mb:
            raise ValueError(
                f"File size ({file_size_mb:.1f}MB) exceeds maximum "
                f"({self.capabilities.max_file_size_mb}MB) for {self.display_name}"
            )

        return True

    def _notify_started(self) -> None:
        """Notify that transcription has started."""
        if self.on_transcription_started:
            self.on_transcription_started()

    def _notify_completed(self, result: TranscriptionResult) -> None:
        """Notify that transcription has completed."""
        if self.on_transcription_completed:
            self.on_transcription_completed(result)

    def _notify_failed(self, error: str) -> None:
        """Notify that transcription has failed."""
        if self.on_transcription_failed:
            self.on_transcription_failed(error)
