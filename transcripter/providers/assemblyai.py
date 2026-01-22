"""AssemblyAI transcription provider."""

import time
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


@ProviderRegistry.register(ProviderType.ASSEMBLYAI)
class AssemblyAIProvider(TranscriptionProvider):
    """Transcription provider using AssemblyAI's API."""

    provider_type = ProviderType.ASSEMBLYAI
    display_name = "AssemblyAI"
    capabilities = ProviderCapabilities(
        supports_streaming=True,
        supports_diarization=True,
        supports_timestamps=True,
        supports_language_detection=True,
        max_file_size_mb=2200,  # AssemblyAI supports large files
        supported_formats=["wav", "mp3", "m4a", "flac", "ogg", "webm", "mp4", "mpeg", "mpga", "aac"],
        requires_file_upload=True,
    )

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the AssemblyAI client."""
        try:
            import assemblyai as aai
            aai.settings.api_key = self._api_key
            self._aai = aai
        except ImportError:
            raise ImportError("assemblyai package is not installed. Install with: pip install assemblyai")

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
        Transcribe an audio file using AssemblyAI's API.

        Args:
            file_path: Path to the audio file
            model: Model tier to use ("best" or "nano")
            language: Language code (e.g., "en", "pt") or None for auto-detection
            prompt: Not used by AssemblyAI
            temperature: Not used by AssemblyAI
            **kwargs: Additional parameters
                - speaker_labels: bool - Enable speaker diarization
                - word_boost: list[str] - Words to boost recognition

        Returns:
            TranscriptionResult or None if transcription failed
        """
        try:
            self._validate_file(file_path)
        except (FileNotFoundError, ValueError) as e:
            self._notify_failed(str(e))
            return None

        model = model or "best"

        try:
            self._notify_started()

            # Configure transcription
            config_params = {}

            # Set speech model
            if model == "nano":
                config_params["speech_model"] = self._aai.SpeechModel.nano
            else:
                config_params["speech_model"] = self._aai.SpeechModel.best

            # Set language
            if language:
                # AssemblyAI uses language codes like "en", "pt", "es"
                config_params["language_code"] = language
            else:
                config_params["language_detection"] = True

            # Additional options from kwargs
            if kwargs.get("speaker_labels"):
                config_params["speaker_labels"] = True

            if kwargs.get("word_boost"):
                config_params["word_boost"] = kwargs["word_boost"]

            config = self._aai.TranscriptionConfig(**config_params)
            transcriber = self._aai.Transcriber(config=config)

            # Transcribe (this handles upload and polling automatically)
            transcript = transcriber.transcribe(file_path)

            if transcript.status == self._aai.TranscriptStatus.error:
                error_msg = f"AssemblyAI error: {transcript.error}"
                self._notify_failed(error_msg)
                raise TranscriptionError(error_msg, self.provider_type)

            # Build result
            words = None
            if transcript.words:
                words = [
                    {
                        "text": w.text,
                        "start": w.start / 1000.0,  # Convert ms to seconds
                        "end": w.end / 1000.0,
                        "confidence": w.confidence,
                    }
                    for w in transcript.words
                ]

            result = TranscriptionResult(
                text=transcript.text,
                provider=self.provider_type,
                model=model,
                language=transcript.language_code,
                duration_seconds=transcript.audio_duration,
                confidence=transcript.confidence,
                words=words,
                raw_response=transcript,
            )

            self._notify_completed(result)
            return result

        except Exception as e:
            error_str = str(e).lower()
            error_msg = f"AssemblyAI API error: {e}"

            if "invalid api key" in error_str or "authentication" in error_str or "401" in error_str:
                self._notify_failed(error_msg)
                raise APIKeyError(self.provider_type)
            elif "rate limit" in error_str or "429" in error_str:
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
            # Try to get account info as validation
            import requests
            response = requests.get(
                "https://api.assemblyai.com/v2/account",
                headers={"authorization": self._api_key}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"AssemblyAI API key validation failed: {e}")
            return False

    def get_supported_models(self) -> list[dict[str, str]]:
        """
        Get list of supported models.

        Returns:
            List of dicts with 'id' and 'name' keys
        """
        return [
            {"id": "best", "name": "Best (Highest accuracy)"},
            {"id": "nano", "name": "Nano (Faster, lower cost)"},
        ]

    def get_default_model(self) -> str:
        return "best"
