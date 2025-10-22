# backend/app/providers/__init__.py
"""Provider exports and registry initialisation."""

from .base import AIProvider, ChatMessage
from .claude_provider import ClaudeProvider
from .deepseek_provider import DeepSeekProvider
from .demo_provider import DemoProvider
from .gemini_provider import GeminiProvider
from .lm_studio_provider import LMStudioProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider
from .openrouter_provider import OpenRouterProvider
from .registry import (
    MissingAPIKeyError,
    ProviderInitializationError,
    ProviderRegistration,
    ProviderRegistry,
    provider_registry,
)

__all__ = [
    "AIProvider",
    "ChatMessage",
    "ClaudeProvider",
    "DeepSeekProvider",
    "DemoProvider",
    "GeminiProvider",
    "LMStudioProvider",
    "MissingAPIKeyError",
    "OllamaProvider",
    "OpenAIProvider",
    "OpenRouterProvider",
    "ProviderInitializationError",
    "ProviderRegistration",
    "ProviderRegistry",
    "provider_registry",
]
