"""Transcription service facade for multi-provider support."""

import time
from typing import Optional, Callable

from .providers import (
    TranscriptionProvider,
    TranscriptionResult,
    TranscriptionError,
    APIKeyError,
    RateLimitError,
    ProviderType,
    ProviderRegistry,
)


class TranscriptionService:
    """
    Facade for transcription providers.

    This class provides a unified interface for transcription operations,
    supporting multiple providers with automatic fallback.
    """

    def __init__(
        self,
        api_key: str,
        provider_type: Optional[ProviderType] = None,
        fallback_api_key: Optional[str] = None,
        fallback_provider_type: Optional[ProviderType] = None,
    ):
        """
        Initialize the transcription service.

        Args:
            api_key: API key for the primary provider
            provider_type: Primary provider type (default: GROQ for backward compatibility)
            fallback_api_key: API key for the fallback provider
            fallback_provider_type: Fallback provider type

        Raises:
            ValueError: If API key is empty or provider is not available
        """
        if not api_key:
            raise ValueError("API key is required")

        self.provider_type = provider_type or ProviderType.GROQ
        self.fallback_provider_type = fallback_provider_type

        # Initialize primary provider
        self._provider = ProviderRegistry.create_provider(self.provider_type, api_key)

        # Initialize fallback provider if configured
        self._fallback_provider: Optional[TranscriptionProvider] = None
        if fallback_api_key and fallback_provider_type:
            try:
                self._fallback_provider = ProviderRegistry.create_provider(
                    fallback_provider_type, fallback_api_key
                )
            except Exception as e:
                print(f"Failed to initialize fallback provider: {e}")

        # State
        self.last_transcription: Optional[str] = None
        self.last_result: Optional[TranscriptionResult] = None
        self.last_error: Optional[str] = None

        # Callbacks
        self.on_transcription_started: Optional[Callable] = None
        self.on_transcription_completed: Optional[Callable[[str], None]] = None
        self.on_transcription_failed: Optional[Callable[[str], None]] = None

    def _setup_provider_callbacks(self, provider: TranscriptionProvider) -> None:
        """Set up callbacks on a provider."""
        provider.on_transcription_started = self.on_transcription_started

        def on_completed(result: TranscriptionResult):
            self.last_result = result
            self.last_transcription = result.text
            self.last_error = None
            if self.on_transcription_completed:
                self.on_transcription_completed(result.text)

        provider.on_transcription_completed = on_completed
        provider.on_transcription_failed = self.on_transcription_failed

    def transcribe_file(
        self,
        file_path: str,
        model: Optional[str] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        response_format: str = "text",
        **kwargs
    ) -> Optional[str]:
        """
        Transcribe an audio file.

        Args:
            file_path: Path to the audio file
            model: Model to use (provider-specific)
            language: Language code (e.g., "en", "pt") or None for auto-detection
            prompt: Optional prompt to guide the model
            temperature: Sampling temperature (0.0 - 1.0)
            response_format: Response format (provider-specific)
            **kwargs: Additional provider-specific parameters

        Returns:
            Transcribed text or None if transcription failed
        """
        self._setup_provider_callbacks(self._provider)

        try:
            result = self._provider.transcribe_file(
                file_path=file_path,
                model=model,
                language=language,
                prompt=prompt,
                temperature=temperature,
                response_format=response_format,
                **kwargs
            )

            if result:
                return result.text

        except (TranscriptionError, APIKeyError, RateLimitError) as e:
            self.last_error = str(e)
            print(f"Primary provider failed: {e}")

            # Try fallback provider
            if self._fallback_provider and e.recoverable:
                print(f"Attempting fallback provider: {self.fallback_provider_type.value}")
                return self._try_fallback(
                    file_path=file_path,
                    language=language,
                    prompt=prompt,
                    temperature=temperature,
                    **kwargs
                )

            if self.on_transcription_failed:
                self.on_transcription_failed(str(e))

        except Exception as e:
            self.last_error = str(e)
            print(f"Transcription error: {e}")

            if self.on_transcription_failed:
                self.on_transcription_failed(str(e))

        return None

    def _try_fallback(
        self,
        file_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        **kwargs
    ) -> Optional[str]:
        """Try transcription with the fallback provider."""
        if not self._fallback_provider:
            return None

        self._setup_provider_callbacks(self._fallback_provider)

        try:
            result = self._fallback_provider.transcribe_file(
                file_path=file_path,
                language=language,
                prompt=prompt,
                temperature=temperature,
                **kwargs
            )

            if result:
                return result.text

        except Exception as e:
            self.last_error = str(e)
            print(f"Fallback provider also failed: {e}")

            if self.on_transcription_failed:
                self.on_transcription_failed(str(e))

        return None

    def transcribe_file_with_retry(
        self,
        file_path: str,
        model: Optional[str] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        response_format: str = "text",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ) -> Optional[str]:
        """
        Transcribe an audio file with retry logic.

        Args:
            file_path: Path to the audio file
            model: Model to use (provider-specific)
            language: Language code or None for auto-detection
            prompt: Optional prompt to guide the model
            temperature: Sampling temperature
            response_format: Response format
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            **kwargs: Additional provider-specific parameters

        Returns:
            Transcribed text or None if all retries failed
        """
        for attempt in range(max_retries):
            try:
                result = self.transcribe_file(
                    file_path=file_path,
                    model=model,
                    language=language,
                    prompt=prompt,
                    temperature=temperature,
                    response_format=response_format,
                    **kwargs
                )

                if result:
                    return result

                # Check if we should retry
                if self.last_error and "rate limit" in self.last_error.lower():
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                else:
                    # Non-retryable error
                    break

            except Exception as e:
                print(f"Retry attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    break

        return None

    def get_supported_models(self) -> list[str]:
        """
        Get list of supported models for the active provider.

        Returns:
            List of model names
        """
        models = self._provider.get_supported_models()
        return [m["id"] for m in models]

    def get_supported_models_with_names(self) -> list[dict[str, str]]:
        """
        Get list of supported models with display names.

        Returns:
            List of dicts with 'id' and 'name' keys
        """
        return self._provider.get_supported_models()

    def validate_api_key(self) -> bool:
        """
        Validate the API key for the active provider.

        Returns:
            True if API key is valid, False otherwise
        """
        return self._provider.validate_api_key()

    def get_provider_name(self) -> str:
        """
        Get the display name of the active provider.

        Returns:
            Provider display name
        """
        return self._provider.display_name

    def get_provider_type(self) -> ProviderType:
        """
        Get the type of the active provider.

        Returns:
            Provider type enum value
        """
        return self.provider_type

    def get_capabilities(self):
        """
        Get the capabilities of the active provider.

        Returns:
            ProviderCapabilities instance
        """
        return self._provider.capabilities

    def estimate_cost(self, audio_duration_seconds: float) -> float:
        """
        Estimate transcription cost in USD.

        Note: This is a rough estimate. Actual costs vary by provider.

        Args:
            audio_duration_seconds: Duration of audio in seconds

        Returns:
            Estimated cost in USD
        """
        # Provider-specific pricing (rough estimates)
        cost_per_minute = {
            ProviderType.GROQ: 0.0001,
            ProviderType.OPENAI: 0.006,
            ProviderType.GOOGLE_CLOUD: 0.016,
            ProviderType.ASSEMBLYAI: 0.0025,
            ProviderType.DEEPGRAM: 0.0043,
        }

        rate = cost_per_minute.get(self.provider_type, 0.01)
        duration_minutes = audio_duration_seconds / 60.0
        return duration_minutes * rate

    def get_last_transcription(self) -> Optional[str]:
        """Get the last successful transcription text."""
        return self.last_transcription

    def get_last_result(self) -> Optional[TranscriptionResult]:
        """Get the last successful transcription result with full details."""
        return self.last_result

    def get_last_error(self) -> Optional[str]:
        """Get the last error message."""
        return self.last_error

    @staticmethod
    def get_available_providers() -> list[ProviderType]:
        """Get list of all registered providers."""
        return ProviderRegistry.get_available_providers()

    @staticmethod
    def get_installed_providers() -> list[ProviderType]:
        """Get list of providers with installed SDKs."""
        return ProviderRegistry.get_installed_providers()

    @staticmethod
    def is_provider_available(provider_type: ProviderType) -> bool:
        """Check if a provider SDK is installed."""
        return ProviderRegistry.is_provider_available(provider_type)


class TranscriptionCache:
    """Simple cache for transcription results."""

    def __init__(self, max_size: int = 50):
        """
        Initialize the transcription cache.

        Args:
            max_size: Maximum number of items to cache
        """
        self.cache: dict[str, str] = {}
        self.max_size = max_size
        self.access_order: list[str] = []

    def get(self, key: str) -> Optional[str]:
        """
        Get a cached transcription.

        Args:
            key: Cache key (e.g., file hash)

        Returns:
            Cached transcription or None
        """
        if key in self.cache:
            # Update access order
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def put(self, key: str, value: str) -> None:
        """
        Cache a transcription.

        Args:
            key: Cache key
            value: Transcription text
        """
        if key in self.cache:
            # Update existing entry
            self.cache[key] = value
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            # Add new entry
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                lru_key = self.access_order.pop(0)
                del self.cache[lru_key]

            self.cache[key] = value
            self.access_order.append(key)

    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self.access_order.clear()

    def size(self) -> int:
        """Get the current cache size."""
        return len(self.cache)
