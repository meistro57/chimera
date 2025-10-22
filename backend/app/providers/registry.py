# backend/app/providers/registry.py
"""Provider registry and factory utilities for AI providers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Optional, Type

from ..core.config import Settings
from .base import AIProvider

logger = logging.getLogger(__name__)


class ProviderInitializationError(RuntimeError):
    """Raised when a provider cannot be initialised."""


class MissingAPIKeyError(ProviderInitializationError):
    """Raised when a provider that requires an API key is missing configuration."""


@dataclass(frozen=True)
class ProviderRegistration:
    """Metadata describing how to construct an :class:`AIProvider`."""

    name: str
    provider_cls: Type[AIProvider]
    default_model: Optional[str] = None
    requires_api_key: bool = False
    settings_api_key_attribute: Optional[str] = None
    settings_kwargs_factory: Optional[Callable[[Settings], Dict[str, Any]]] = None
    description: Optional[str] = None

    def build_kwargs(
        self,
        settings: Settings,
        override_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build keyword arguments for the provider constructor."""

        kwargs: Dict[str, Any] = {}

        if self.settings_kwargs_factory:
            try:
                generated_kwargs = self.settings_kwargs_factory(settings)
                if generated_kwargs:
                    for key, value in generated_kwargs.items():
                        if value is not None:
                            kwargs.setdefault(key, value)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning(
                    "Provider %s settings factory failed: %s",
                    self.name,
                    exc,
                )

        if self.default_model and "model" not in (override_kwargs or {}):
            kwargs.setdefault("model", self.default_model)

        if self.settings_api_key_attribute:
            api_key = getattr(settings, self.settings_api_key_attribute, None)
            if api_key:
                kwargs.setdefault("api_key", api_key)

        if override_kwargs:
            for key, value in override_kwargs.items():
                if value is not None:
                    kwargs[key] = value

        if self.requires_api_key and not kwargs.get("api_key"):
            raise MissingAPIKeyError(
                f"Provider '{self.name}' requires an API key but none was provided."
            )

        return kwargs

    def create_provider(
        self,
        settings: Settings,
        override_kwargs: Optional[Dict[str, Any]] = None,
    ) -> AIProvider:
        """Instantiate the provider using the supplied settings."""

        kwargs = self.build_kwargs(settings, override_kwargs)
        return self.provider_cls(**kwargs)


class ProviderRegistry:
    """Registry that keeps track of available AI provider implementations."""

    def __init__(self) -> None:
        self._registrations: Dict[str, ProviderRegistration] = {}

    def register(
        self,
        name: str,
        provider_cls: Type[AIProvider],
        *,
        default_model: Optional[str] = None,
        requires_api_key: bool = False,
        settings_api_key_attribute: Optional[str] = None,
        settings_kwargs_factory: Optional[Callable[[Settings], Dict[str, Any]]] = None,
        description: Optional[str] = None,
    ) -> None:
        """Register a provider class under a short name."""

        if name in self._registrations:
            raise ValueError(f"Provider '{name}' is already registered.")

        registration = ProviderRegistration(
            name=name,
            provider_cls=provider_cls,
            default_model=default_model,
            requires_api_key=requires_api_key,
            settings_api_key_attribute=settings_api_key_attribute,
            settings_kwargs_factory=settings_kwargs_factory,
            description=description,
        )
        self._registrations[name] = registration

    def unregister(self, name: str) -> None:
        """Remove a previously registered provider."""

        self._registrations.pop(name, None)

    def list_registered(self) -> Iterable[str]:
        """Return the names of all registered providers."""

        return tuple(self._registrations.keys())

    def get_registration(self, name: str) -> ProviderRegistration:
        """Return metadata for a provider."""

        try:
            return self._registrations[name]
        except KeyError as exc:
            raise KeyError(f"Provider '{name}' is not registered.") from exc

    def create_provider(
        self,
        name: str,
        settings: Settings,
        override_kwargs: Optional[Dict[str, Any]] = None,
    ) -> AIProvider:
        """Create a provider instance by name."""

        registration = self.get_registration(name)
        overrides = dict(override_kwargs or {})
        enabled = overrides.pop("enabled", True)
        if not enabled:
            raise ProviderInitializationError(
                f"Provider '{name}' has been disabled via configuration."
            )

        return registration.create_provider(settings, overrides)

    def create_configured_providers(
        self,
        settings: Settings,
        overrides: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, AIProvider]:
        """Create provider instances for all registered providers."""

        configured: Dict[str, AIProvider] = {}
        overrides = overrides or {}

        for name, registration in self._registrations.items():
            override_kwargs = overrides.get(name)
            try:
                provider = registration.create_provider(settings, override_kwargs)
            except MissingAPIKeyError:
                logger.info(
                    "Skipping provider '%s' because no API key is configured.",
                    name,
                )
                continue
            except ProviderInitializationError as exc:
                logger.info("Skipping provider '%s': %s", name, exc)
                continue
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception(
                    "Failed to initialise provider '%s': %s",
                    name,
                    exc,
                )
                continue

            configured[name] = provider

        return configured


provider_registry = ProviderRegistry()


def _register_default_providers() -> None:
    """Register the built-in provider implementations."""

    from .claude_provider import ClaudeProvider
    from .deepseek_provider import DeepSeekProvider
    from .demo_provider import DemoProvider
    from .gemini_provider import GeminiProvider
    from .lm_studio_provider import LMStudioProvider
    from .ollama_provider import OllamaProvider
    from .openai_provider import OpenAIProvider
    from .openrouter_provider import OpenRouterProvider

    provider_registry.register(
        "openai",
        OpenAIProvider,
        default_model="gpt-3.5-turbo",
        requires_api_key=True,
        settings_api_key_attribute="openai_api_key",
        description="OpenAI Chat Completions API",
    )
    provider_registry.register(
        "claude",
        ClaudeProvider,
        default_model="claude-3-haiku-20240307",
        requires_api_key=True,
        settings_api_key_attribute="anthropic_api_key",
        description="Anthropic Claude API",
    )
    provider_registry.register(
        "deepseek",
        DeepSeekProvider,
        default_model="deepseek-chat",
        requires_api_key=True,
        settings_api_key_attribute="deepseek_api_key",
        description="DeepSeek conversational models",
    )
    provider_registry.register(
        "gemini",
        GeminiProvider,
        default_model="gemini-pro",
        requires_api_key=True,
        settings_api_key_attribute="google_ai_api_key",
        description="Google Gemini models",
    )
    provider_registry.register(
        "openrouter",
        OpenRouterProvider,
        default_model="openai/gpt-3.5-turbo",
        requires_api_key=True,
        settings_api_key_attribute="openrouter_api_key",
        description="OpenRouter model hub",
    )
    provider_registry.register(
        "lm_studio",
        LMStudioProvider,
        settings_kwargs_factory=lambda cfg: {"base_url": cfg.lm_studio_url},
        description="Local LM Studio bridge",
    )
    provider_registry.register(
        "ollama",
        OllamaProvider,
        settings_kwargs_factory=lambda cfg: {"base_url": cfg.ollama_url},
        description="Local Ollama runtime",
    )
    provider_registry.register(
        "demo",
        DemoProvider,
        description="Deterministic demo provider for development",
    )


_register_default_providers()

__all__ = [
    "provider_registry",
    "ProviderRegistry",
    "ProviderRegistration",
    "ProviderInitializationError",
    "MissingAPIKeyError",
]
