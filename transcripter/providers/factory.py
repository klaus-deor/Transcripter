"""Provider factory and registry for transcription providers."""

from typing import Type, Optional
from .base import TranscriptionProvider, ProviderType


class ProviderRegistry:
    """Registry and factory for transcription providers."""

    _providers: dict[ProviderType, Type[TranscriptionProvider]] = {}

    @classmethod
    def register(cls, provider_type: ProviderType):
        """
        Decorator to register a provider class.

        Args:
            provider_type: The type of provider to register

        Returns:
            Decorator function
        """
        def decorator(provider_class: Type[TranscriptionProvider]):
            cls._providers[provider_type] = provider_class
            return provider_class
        return decorator

    @classmethod
    def get_provider_class(cls, provider_type: ProviderType) -> Optional[Type[TranscriptionProvider]]:
        """
        Get the provider class for a given type.

        Args:
            provider_type: The type of provider

        Returns:
            Provider class or None if not found
        """
        return cls._providers.get(provider_type)

    @classmethod
    def create_provider(
        cls,
        provider_type: ProviderType,
        api_key: str
    ) -> TranscriptionProvider:
        """
        Create a provider instance.

        Args:
            provider_type: The type of provider to create
            api_key: API key for the provider

        Returns:
            Provider instance

        Raises:
            ValueError: If provider type is not registered
        """
        provider_class = cls._providers.get(provider_type)
        if not provider_class:
            available = [p.value for p in cls._providers.keys()]
            raise ValueError(
                f"Provider '{provider_type.value}' is not registered. "
                f"Available providers: {', '.join(available)}"
            )
        return provider_class(api_key)

    @classmethod
    def get_available_providers(cls) -> list[ProviderType]:
        """
        Get list of all registered providers.

        Returns:
            List of available provider types
        """
        return list(cls._providers.keys())

    @classmethod
    def is_provider_available(cls, provider_type: ProviderType) -> bool:
        """
        Check if a provider is available (SDK installed).

        Args:
            provider_type: The type of provider to check

        Returns:
            True if provider SDK is installed
        """
        try:
            if provider_type == ProviderType.GROQ:
                import groq  # noqa: F401
                return True
            elif provider_type == ProviderType.OPENAI:
                import openai  # noqa: F401
                return True
            elif provider_type == ProviderType.GOOGLE_CLOUD:
                import google.cloud.speech  # noqa: F401
                return True
            elif provider_type == ProviderType.ASSEMBLYAI:
                import assemblyai  # noqa: F401
                return True
            elif provider_type == ProviderType.DEEPGRAM:
                import deepgram  # noqa: F401
                return True
        except ImportError:
            return False
        return False

    @classmethod
    def get_installed_providers(cls) -> list[ProviderType]:
        """
        Get list of providers with installed SDKs.

        Returns:
            List of provider types with available SDKs
        """
        return [p for p in cls._providers.keys() if cls.is_provider_available(p)]

    @classmethod
    def get_provider_info(cls, provider_type: ProviderType) -> dict:
        """
        Get information about a provider.

        Args:
            provider_type: The type of provider

        Returns:
            Dict with provider information
        """
        provider_class = cls._providers.get(provider_type)
        if not provider_class:
            return {}

        return {
            "type": provider_type.value,
            "display_name": provider_class.display_name,
            "capabilities": provider_class.capabilities,
            "models": provider_class("dummy").get_supported_models() if cls.is_provider_available(provider_type) else [],
            "installed": cls.is_provider_available(provider_type)
        }
