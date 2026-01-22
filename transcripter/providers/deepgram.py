"""Deepgram transcription provider."""

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


@ProviderRegistry.register(ProviderType.DEEPGRAM)
class DeepgramProvider(TranscriptionProvider):
    """Transcription provider using Deepgram's API."""

    provider_type = ProviderType.DEEPGRAM
    display_name = "Deepgram"
    capabilities = ProviderCapabilities(
        supports_streaming=True,
        supports_diarization=True,
        supports_timestamps=True,
        supports_language_detection=True,
        max_file_size_mb=2000,  # Deepgram supports large files
        supported_formats=["wav", "mp3", "m4a", "flac", "ogg", "webm", "mp4", "mpeg", "mpga", "aac"],
    )

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Deepgram client."""
        try:
            from deepgram import DeepgramClient
            self._client = DeepgramClient(self._api_key)
        except ImportError:
            raise ImportError("deepgram-sdk package is not installed. Install with: pip install deepgram-sdk")

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
        Transcribe an audio file using Deepgram's API.

        Args:
            file_path: Path to the audio file
            model: Model to use ("nova-2", "whisper-large", etc.)
            language: Language code (e.g., "en", "pt") or None for auto-detection
            prompt: Not used by Deepgram
            temperature: Not used by Deepgram
            **kwargs: Additional parameters
                - diarize: bool - Enable speaker diarization
                - punctuate: bool - Add punctuation (default True)
                - smart_format: bool - Enable smart formatting (default True)

        Returns:
            TranscriptionResult or None if transcription failed
        """
        try:
            self._validate_file(file_path)
        except (FileNotFoundError, ValueError) as e:
            self._notify_failed(str(e))
            return None

        model = model or "nova-2"

        try:
            self._notify_started()

            from deepgram import FileSource, PrerecordedOptions

            # Read audio file
            with open(file_path, "rb") as audio_file:
                buffer_data = audio_file.read()

            payload: FileSource = {
                "buffer": buffer_data,
            }

            # Configure options
            options_dict = {
                "model": model,
                "punctuate": kwargs.get("punctuate", True),
                "smart_format": kwargs.get("smart_format", True),
            }

            if language:
                options_dict["language"] = language
            else:
                options_dict["detect_language"] = True

            if kwargs.get("diarize"):
                options_dict["diarize"] = True

            options = PrerecordedOptions(**options_dict)

            # Transcribe
            response = self._client.listen.rest.v("1").transcribe_file(payload, options)

            # Extract results
            results = response.results
            if not results or not results.channels:
                error_msg = "Deepgram returned empty results"
                self._notify_failed(error_msg)
                raise TranscriptionError(error_msg, self.provider_type)

            channel = results.channels[0]
            if not channel.alternatives:
                error_msg = "Deepgram returned no alternatives"
                self._notify_failed(error_msg)
                raise TranscriptionError(error_msg, self.provider_type)

            alternative = channel.alternatives[0]
            text = alternative.transcript

            # Extract word-level timestamps if available
            words = None
            if alternative.words:
                words = [
                    {
                        "text": w.word,
                        "start": w.start,
                        "end": w.end,
                        "confidence": w.confidence,
                    }
                    for w in alternative.words
                ]

            # Get detected language
            detected_language = None
            if hasattr(channel, 'detected_language'):
                detected_language = channel.detected_language
            elif language:
                detected_language = language

            result = TranscriptionResult(
                text=text,
                provider=self.provider_type,
                model=model,
                language=detected_language,
                duration_seconds=results.metadata.duration if results.metadata else None,
                confidence=alternative.confidence,
                words=words,
                raw_response=response,
            )

            self._notify_completed(result)
            return result

        except Exception as e:
            error_str = str(e).lower()
            error_msg = f"Deepgram API error: {e}"

            if "invalid api key" in error_str or "authentication" in error_str or "401" in error_str or "unauthorized" in error_str:
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
            # Try to get project info as validation
            self._client.manage.v("1").get_projects()
            return True
        except Exception as e:
            print(f"Deepgram API key validation failed: {e}")
            return False

    def get_supported_models(self) -> list[dict[str, str]]:
        """
        Get list of supported models.

        Returns:
            List of dicts with 'id' and 'name' keys
        """
        return [
            {"id": "nova-2", "name": "Nova-2 (Recommended)"},
            {"id": "nova", "name": "Nova"},
            {"id": "whisper-large", "name": "Whisper Large"},
            {"id": "whisper-medium", "name": "Whisper Medium"},
            {"id": "whisper-small", "name": "Whisper Small"},
            {"id": "whisper-base", "name": "Whisper Base"},
            {"id": "whisper-tiny", "name": "Whisper Tiny"},
        ]

    def get_default_model(self) -> str:
        return "nova-2"
