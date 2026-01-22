"""Transcription providers package."""

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

# Import providers to register them
from .groq import GroqProvider
from .openai_provider import OpenAIProvider
from .assemblyai import AssemblyAIProvider
from .deepgram import DeepgramProvider
from .google_cloud import GoogleCloudProvider

__all__ = [
    # Base classes
    "TranscriptionProvider",
    "TranscriptionResult",
    "TranscriptionError",
    "APIKeyError",
    "RateLimitError",
    "ProviderType",
    "ProviderCapabilities",
    # Factory
    "ProviderRegistry",
    # Providers
    "GroqProvider",
    "OpenAIProvider",
    "AssemblyAIProvider",
    "DeepgramProvider",
    "GoogleCloudProvider",
]
