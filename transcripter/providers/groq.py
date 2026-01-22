"""Groq transcription provider."""

import os
from typing import Optional

from .base import (
    TranscriptionProvider,
    TranscriptionResult,
    TranscriptionError,
    APIKeyError,
    RateLimitError,
    ProviderType,
    ProviderCapabilities,
)
from .factory import ProviderRegistry


@ProviderRegistry.register(ProviderType.GROQ)
class GroqProvider(TranscriptionProvider):
    """Transcription provider using Groq's Whisper API."""

    provider_type = ProviderType.GROQ
    display_name = "Groq"
    capabilities = ProviderCapabilities(
        supports_streaming=False,
        supports_diarization=False,
        supports_timestamps=True,
        supports_language_detection=True,
        max_file_size_mb=25,
        supported_formats=["wav", "mp3", "m4a", "flac", "ogg", "webm", "mp4", "mpeg", "mpga"],
    )

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Groq client."""
        try:
            from groq import Groq
            self._client = Groq(api_key=self._api_key)
        except ImportError:
            raise ImportError("groq package is not installed. Install with: pip install groq")

    def transcribe_file(
        self,
        file_path: str,
        model: Optional[str] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        response_format: str = "text",
        **kwargs
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe an audio file using Groq's Whisper API.

        Args:
            file_path: Path to the audio file
            model: Whisper model to use (default: whisper-large-v3-turbo)
            language: Language code (e.g., "en", "pt") or None for auto-detection
            prompt: Optional prompt to guide the model
            temperature: Sampling temperature (0.0 - 1.0)
            response_format: Response format ("text", "json", "verbose_json")
            **kwargs: Additional parameters (ignored)

        Returns:
            TranscriptionResult or None if transcription failed
        """
        try:
            self._validate_file(file_path)
        except (FileNotFoundError, ValueError) as e:
            self._notify_failed(str(e))
            return None

        model = model or "whisper-large-v3-turbo"

        try:
            self._notify_started()

            with open(file_path, "rb") as audio_file:
                transcription_params = {
                    "file": (os.path.basename(file_path), audio_file),
                    "model": model,
                    "temperature": temperature,
                    "response_format": response_format,
                }

                if language:
                    transcription_params["language"] = language

                if prompt:
                    transcription_params["prompt"] = prompt

                response = self._client.audio.transcriptions.create(**transcription_params)

                # Extract text based on response format
                if response_format == "text":
                    text = response
                else:
                    text = response.text

                result = TranscriptionResult(
                    text=text,
                    provider=self.provider_type,
                    model=model,
                    language=language,
                    raw_response=response if response_format != "text" else None,
                )

                self._notify_completed(result)
                return result

        except Exception as e:
            error_str = str(e).lower()
            error_msg = f"Groq API error: {e}"

            if "invalid api key" in error_str or "authentication" in error_str:
                self._notify_failed(error_msg)
                raise APIKeyError(self.provider_type)
            elif "rate limit" in error_str:
                self._notify_failed(error_msg)
                raise RateLimitError(self.provider_type)
            else:
                self._notify_failed(error_msg)
                raise TranscriptionError(error_msg, self.provider_type)

    def validate_api_key(self) -> bool:
        """
        Validate the API key by making a test request.

        Returns:
            True if API key is valid, False otherwise
        """
        try:
            self._client.models.list()
            return True
        except Exception as e:
            print(f"Groq API key validation failed: {e}")
            return False

    def get_supported_models(self) -> list[dict[str, str]]:
        """
        Get list of supported Whisper models.

        Returns:
            List of dicts with 'id' and 'name' keys
        """
        return [
            {"id": "whisper-large-v3-turbo", "name": "Whisper Large V3 Turbo (Recommended)"},
            {"id": "whisper-large-v3", "name": "Whisper Large V3"},
        ]

    def get_default_model(self) -> str:
        return "whisper-large-v3-turbo"
