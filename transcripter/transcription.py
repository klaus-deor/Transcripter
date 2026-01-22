"""Transcription module using Groq API."""

import os
import time
from pathlib import Path
from typing import Optional, Callable
from groq import Groq, GroqError


class TranscriptionService:
    """Handles audio transcription using Groq Whisper API."""

    def __init__(self, api_key: str):
        """
        Initialize the transcription service.

        Args:
            api_key: Groq API key

        Raises:
            ValueError: If API key is empty or None
        """
        if not api_key:
            raise ValueError("API key is required")

        self.client = Groq(api_key=api_key)
        self.last_transcription: Optional[str] = None
        self.last_error: Optional[str] = None

        # Callbacks
        self.on_transcription_started: Optional[Callable] = None
        self.on_transcription_completed: Optional[Callable[[str], None]] = None
        self.on_transcription_failed: Optional[Callable[[str], None]] = None

    def transcribe_file(
        self,
        file_path: str,
        model: str = "whisper-large-v3-turbo",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        response_format: str = "text"
    ) -> Optional[str]:
        """
        Transcribe an audio file.

        Args:
            file_path: Path to the audio file
            model: Whisper model to use (default: whisper-large-v3-turbo)
            language: Language code (e.g., "en", "pt") or None for auto-detection
            prompt: Optional prompt to guide the model
            temperature: Sampling temperature (0.0 - 1.0)
            response_format: Response format ("text", "json", "verbose_json")

        Returns:
            Transcribed text or None if transcription failed
        """
        if not os.path.exists(file_path):
            error_msg = f"Audio file not found: {file_path}"
            print(error_msg)
            self.last_error = error_msg
            if self.on_transcription_failed:
                self.on_transcription_failed(error_msg)
            return None

        try:
            if self.on_transcription_started:
                self.on_transcription_started()

            # Open and read the audio file
            with open(file_path, "rb") as audio_file:
                # Prepare transcription parameters
                transcription_params = {
                    "file": (os.path.basename(file_path), audio_file),
                    "model": model,
                    "temperature": temperature,
                    "response_format": response_format
                }

                # Add optional parameters
                if language:
                    transcription_params["language"] = language

                if prompt:
                    transcription_params["prompt"] = prompt

                # Call Groq API
                transcription = self.client.audio.transcriptions.create(**transcription_params)

                # Extract text based on response format
                if response_format == "text":
                    transcribed_text = transcription
                else:
                    transcribed_text = transcription.text

                self.last_transcription = transcribed_text
                self.last_error = None

                if self.on_transcription_completed:
                    self.on_transcription_completed(transcribed_text)

                return transcribed_text

        except GroqError as e:
            error_msg = f"Groq API error: {str(e)}"
            print(error_msg)
            self.last_error = error_msg
            if self.on_transcription_failed:
                self.on_transcription_failed(error_msg)
            return None

        except Exception as e:
            error_msg = f"Transcription error: {str(e)}"
            print(error_msg)
            self.last_error = error_msg
            if self.on_transcription_failed:
                self.on_transcription_failed(error_msg)
            return None

    def transcribe_file_with_retry(
        self,
        file_path: str,
        model: str = "whisper-large-v3-turbo",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        response_format: str = "text",
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Optional[str]:
        """
        Transcribe an audio file with retry logic.

        Args:
            file_path: Path to the audio file
            model: Whisper model to use
            language: Language code or None for auto-detection
            prompt: Optional prompt to guide the model
            temperature: Sampling temperature
            response_format: Response format
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

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
                    response_format=response_format
                )

                if result:
                    return result

                # If result is None but no exception, don't retry
                if self.last_error and "rate limit" in self.last_error.lower():
                    # Rate limited, wait and retry
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                else:
                    # Other error, don't retry
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
        Get list of supported Whisper models.

        Returns:
            List of model names
        """
        return [
            "whisper-large-v3",
            "whisper-large-v3-turbo",
        ]

    def validate_api_key(self) -> bool:
        """
        Validate the API key by making a test request.

        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # Try to list models as a simple validation
            self.client.models.list()
            return True
        except GroqError as e:
            print(f"API key validation failed: {e}")
            return False
        except Exception as e:
            print(f"API key validation error: {e}")
            return False

    def estimate_cost(self, audio_duration_seconds: float) -> float:
        """
        Estimate transcription cost in USD.

        Note: This is an estimate based on Groq's pricing.
        Actual costs may vary.

        Args:
            audio_duration_seconds: Duration of audio in seconds

        Returns:
            Estimated cost in USD
        """
        # Groq Whisper pricing (as of 2024)
        # This is just an estimate - check Groq's current pricing
        cost_per_minute = 0.0001  # Example: $0.0001 per minute

        duration_minutes = audio_duration_seconds / 60.0
        return duration_minutes * cost_per_minute

    def get_last_transcription(self) -> Optional[str]:
        """
        Get the last successful transcription.

        Returns:
            Last transcribed text or None
        """
        return self.last_transcription

    def get_last_error(self) -> Optional[str]:
        """
        Get the last error message.

        Returns:
            Last error message or None
        """
        return self.last_error


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
