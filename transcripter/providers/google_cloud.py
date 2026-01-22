"""Google Cloud Speech-to-Text transcription provider."""

import os
from typing import Optional

from .base import (
    TranscriptionProvider,
    TranscriptionResult,
    TranscriptionError,
    APIKeyError,
    ProviderType,
    ProviderCapabilities,
)
from .factory import ProviderRegistry


@ProviderRegistry.register(ProviderType.GOOGLE_CLOUD)
class GoogleCloudProvider(TranscriptionProvider):
    """Transcription provider using Google Cloud Speech-to-Text API."""

    provider_type = ProviderType.GOOGLE_CLOUD
    display_name = "Google Cloud"
    capabilities = ProviderCapabilities(
        supports_streaming=True,
        supports_diarization=True,
        supports_timestamps=True,
        supports_language_detection=False,  # Requires specifying language
        max_file_size_mb=480,  # For async recognition
        supported_formats=["wav", "flac", "mp3", "ogg", "webm"],
    )

    def __init__(self, api_key: str):
        """
        Initialize the Google Cloud provider.

        Args:
            api_key: Path to the service account JSON credentials file
        """
        super().__init__(api_key)
        self._credentials_path = api_key
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Google Cloud Speech client."""
        try:
            from google.cloud import speech
            from google.oauth2 import service_account

            # Check if credentials file exists
            if not os.path.exists(self._credentials_path):
                raise FileNotFoundError(
                    f"Google Cloud credentials file not found: {self._credentials_path}"
                )

            credentials = service_account.Credentials.from_service_account_file(
                self._credentials_path
            )
            self._client = speech.SpeechClient(credentials=credentials)
            self._speech = speech
        except ImportError:
            raise ImportError(
                "google-cloud-speech package is not installed. "
                "Install with: pip install google-cloud-speech"
            )

    def _get_audio_encoding(self, file_path: str):
        """Get the audio encoding based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        encoding_map = {
            ".wav": self._speech.RecognitionConfig.AudioEncoding.LINEAR16,
            ".flac": self._speech.RecognitionConfig.AudioEncoding.FLAC,
            ".mp3": self._speech.RecognitionConfig.AudioEncoding.MP3,
            ".ogg": self._speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            ".webm": self._speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        }
        return encoding_map.get(ext, self._speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED)

    def _get_sample_rate(self, file_path: str) -> int:
        """Try to determine the sample rate of the audio file."""
        try:
            import wave
            if file_path.lower().endswith('.wav'):
                with wave.open(file_path, 'rb') as wav_file:
                    return wav_file.getframerate()
        except Exception:
            pass
        # Default sample rate
        return 16000

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
        Transcribe an audio file using Google Cloud Speech-to-Text.

        Args:
            file_path: Path to the audio file
            model: Model to use ("default", "chirp", "chirp_2")
            language: Language code (e.g., "en-US", "pt-BR") - REQUIRED
            prompt: Speech context phrases to improve recognition
            temperature: Not used by Google Cloud
            **kwargs: Additional parameters
                - enable_word_time_offsets: bool - Include word timestamps
                - enable_automatic_punctuation: bool - Add punctuation

        Returns:
            TranscriptionResult or None if transcription failed
        """
        try:
            self._validate_file(file_path)
        except (FileNotFoundError, ValueError) as e:
            self._notify_failed(str(e))
            return None

        # Google Cloud requires language to be specified
        if not language:
            language = "en-US"

        # Convert short language codes to Google format if needed
        if len(language) == 2:
            language_map = {
                "en": "en-US",
                "pt": "pt-BR",
                "es": "es-ES",
                "fr": "fr-FR",
                "de": "de-DE",
                "it": "it-IT",
                "ja": "ja-JP",
                "ko": "ko-KR",
                "zh": "zh-CN",
            }
            language = language_map.get(language, f"{language}-{language.upper()}")

        model = model or "chirp_2"

        try:
            self._notify_started()

            # Read audio file
            with open(file_path, "rb") as audio_file:
                content = audio_file.read()

            audio = self._speech.RecognitionAudio(content=content)

            # Configure recognition
            config_params = {
                "language_code": language,
                "enable_automatic_punctuation": kwargs.get("enable_automatic_punctuation", True),
                "enable_word_time_offsets": kwargs.get("enable_word_time_offsets", True),
            }

            # Set model
            if model == "chirp_2":
                config_params["model"] = "chirp_2"
            elif model == "chirp":
                config_params["model"] = "chirp"
            else:
                config_params["model"] = "latest_long"

            # Set encoding and sample rate for non-Chirp models
            if model not in ["chirp", "chirp_2"]:
                config_params["encoding"] = self._get_audio_encoding(file_path)
                config_params["sample_rate_hertz"] = self._get_sample_rate(file_path)

            # Add speech context if prompt provided
            if prompt:
                speech_context = self._speech.SpeechContext(phrases=prompt.split(","))
                config_params["speech_contexts"] = [speech_context]

            config = self._speech.RecognitionConfig(**config_params)

            # Check file size for sync vs async
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            if file_size_mb > 10:  # Use async for larger files
                operation = self._client.long_running_recognize(config=config, audio=audio)
                response = operation.result(timeout=600)
            else:
                response = self._client.recognize(config=config, audio=audio)

            # Extract results
            if not response.results:
                error_msg = "Google Cloud returned empty results"
                self._notify_failed(error_msg)
                return TranscriptionResult(
                    text="",
                    provider=self.provider_type,
                    model=model,
                    language=language,
                )

            # Combine all transcripts
            texts = []
            words = []
            total_confidence = 0.0
            confidence_count = 0

            for result in response.results:
                if result.alternatives:
                    alt = result.alternatives[0]
                    texts.append(alt.transcript)
                    total_confidence += alt.confidence
                    confidence_count += 1

                    # Extract word timestamps
                    if alt.words:
                        for word_info in alt.words:
                            words.append({
                                "text": word_info.word,
                                "start": word_info.start_time.total_seconds(),
                                "end": word_info.end_time.total_seconds(),
                                "confidence": alt.confidence,
                            })

            text = " ".join(texts)
            avg_confidence = total_confidence / confidence_count if confidence_count > 0 else None

            result = TranscriptionResult(
                text=text,
                provider=self.provider_type,
                model=model,
                language=language,
                confidence=avg_confidence,
                words=words if words else None,
                raw_response=response,
            )

            self._notify_completed(result)
            return result

        except Exception as e:
            error_str = str(e).lower()
            error_msg = f"Google Cloud API error: {e}"

            if "permission denied" in error_str or "invalid" in error_str or "credentials" in error_str:
                self._notify_failed(error_msg)
                raise APIKeyError(self.provider_type)
            else:
                self._notify_failed(error_msg)
                raise TranscriptionError(error_msg, self.provider_type)

    def validate_api_key(self) -> bool:
        """
        Validate the credentials file.

        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            # Check if file exists and is valid JSON
            if not os.path.exists(self._credentials_path):
                return False

            import json
            with open(self._credentials_path, 'r') as f:
                creds = json.load(f)

            # Check for required fields
            required_fields = ["type", "project_id", "private_key", "client_email"]
            return all(field in creds for field in required_fields)
        except Exception as e:
            print(f"Google Cloud credentials validation failed: {e}")
            return False

    def get_supported_models(self) -> list[dict[str, str]]:
        """
        Get list of supported models.

        Returns:
            List of dicts with 'id' and 'name' keys
        """
        return [
            {"id": "chirp_2", "name": "Chirp 2 (Recommended)"},
            {"id": "chirp", "name": "Chirp"},
            {"id": "default", "name": "Default"},
        ]

    def get_default_model(self) -> str:
        return "chirp_2"
