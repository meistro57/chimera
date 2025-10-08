# AI Provider Integration Guide

## 🎭 Supported AI Providers

Chimera supports 7 major AI providers, allowing you to mix and match different AI models in your conversations. Each provider has different strengths and pricing models.

### 🧠 **OpenAI** (GPT-4, GPT-3.5-turbo)
**Best for:** Balanced performance, creativity, and speed
- **Setup:** Get API key at [platform.openai.com](https://platform.openai.com/api-keys)
- **Models:** GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Pricing:** Moderate (~$0.002/1k tokens)
- **Env Var:** `OPENAI_API_KEY`

### 🤖 **Anthropic Claude** (Opus, Sonnet, Haiku)
**Best for:** Safety, analysis, and long-form responses
- **Setup:** Get API key at [console.anthropic.com](https://console.anthropic.com/)
- **Models:** Claude-3-opus, claude-3-sonnet, claude-3-haiku
- **Pricing:** Moderate (~$0.015-0.025/1k tokens)
- **Env Var:** `ANTHROPIC_API_KEY`

### 🧬 **DeepSeek** (Advanced Reasoning)
**Best for:** Cost-effective advanced reasoning and coding
- **Setup:** Get API key at [platform.deepseek.com](https://platform.deepseek.com/)
- **Models:** DeepSeek-coder, DeepSeek-chat
- **Pricing:** Low (~$0.0005-0.001/1k tokens)
- **Env Var:** `DEEPSEEK_API_KEY`

### 🌐 **Google Gemini** (Latest Gemini Models)
**Best for:** Multimodal capabilities and Google's latest tech
- **Setup:** Get API key at [makersuite.google.com](https://makersuite.google.com/app/apikey)
- **Models:** Gemini-1.5-flash, Gemini-1.5-pro
- **Pricing:** Low (~$0.0003-0.001/1k tokens)
- **Env Var:** `GOOGLE_API_KEY`

### 🔗 **OpenRouter** (Dozens of Models)
**Best for:** Maximum model variety through unified API
- **Setup:** Get API key at [openrouter.ai](https://openrouter.ai/)
- **Models:** Access to Claude, GPT, Gemini, and many more
- **Pricing:** Varies by model (adds ~10% fee)
- **Env Var:** `OPENROUTER_API_KEY`

### 💻 **LM Studio** (Local Models)
**Best for:** Privacy and zero-cost local AI
- **Setup:** Download from [lmstudio.ai](https://lmstudio.ai/), start local server
- **Models:** Any GGUF model you download
- **Pricing:** Free (your hardware)
- **Env Var:** `LM_STUDIO_BASE_URL` (default: http://localhost:1234)

### 🦙 **Ollama** (Open-Source Local Models)
**Best for:** Free open-source models on your machine
- **Setup:** Install from [ollama.ai](https://ollama.ai/), run `ollama serve`
- **Models:** Llama, Mistral, Phi, and more (run `ollama pull <model>`)
- **Pricing:** Free (MIT/Apache licensed)
- **Env Var:** `OLLAMA_BASE_URL` (default: http://localhost:11434)

---

Guide for integrating new AI services into Chimera's multi-AI conversational system.

## 🏗️ Provider Architecture Overview

Chimera uses a modular provider architecture that allows easy integration of any AI service. Each provider implements a common interface while handling service-specific authentication, rate limiting, and response formatting.

### Provider Interface

All AI providers must implement the `AIProvider` abstract base class:

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List, Any

class AIProvider(ABC):
    """Abstract base class for all AI providers"""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> AsyncIterator[str]:
        """Send chat messages and return streaming response"""
        pass

    @abstractmethod
    async def get_models(self) -> List[str]:
        """Get list of available models for this provider"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is available and responsive"""
        pass
```

## 🚀 Creating a New Provider

### Step 1: Basic Provider Structure

Create a new file in `backend/app/providers/` for your provider:

```python
# backend/app/providers/your_provider.py

import asyncio
import httpx
from typing import AsyncIterator, Dict, List, Any
from .base import AIProvider

class YourProvider(AIProvider):
    """Integration for Your AI Service"""

    def __init__(self, api_key: str, base_url: str = None, **config):
        super().__init__("your_provider", config)
        self.api_key = api_key
        self.base_url = base_url or "https://api.your-ai-service.com"

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=httpx.Timeout(30.0)
        )

        # Provider-specific configuration
        self.supported_models = ["your-model-1", "your-model-2"]
        self.default_model = "your-model-1"
```

### Step 2: Implement Required Methods

#### Chat Method (Core Functionality)

```python
async def chat(
    self,
    messages: List[Dict[str, str]],
    stream: bool = False,
    **kwargs
) -> AsyncIterator[str]:
    """Send chat messages and return streaming response"""

    # Extract generation parameters
    model = kwargs.get('model', self.default_model)
    temperature = kwargs.get('temperature', 0.7)
    max_tokens = kwargs.get('max_tokens', 150)

    # Validate model
    if model not in self.supported_models:
        raise ValueError(f"Model {model} not supported")

    # Prepare request
    payload = {
        "model": model,
        "messages": self._format_messages(messages),
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }

    try:
        if stream:
            async for chunk in self._stream_response(payload):
                yield chunk
        else:
            response = await self._single_response(payload)
            yield response

    except Exception as e:
        raise ProviderError(f"API error: {e}")

def _format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Convert standard message format to provider-specific format"""

    formatted_messages = []
    for msg in messages:
        # Standard format: {"role": "user|assistant|system", "content": "..."}
        # Adapt to your provider's expected format
        formatted_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    return formatted_messages

async def _stream_response(self, payload: Dict) -> AsyncIterator[str]:
    """Handle streaming response from API"""

    async with self.client.stream("POST", "/chat/completions", json=payload) as response:
        if response.status_code != 200:
            raise ProviderError(f"API error: {response.status_code}")

        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data_str = line[6:]  # Remove "data: " prefix

                if data_str == "[DONE]":
                    break

                try:
                    data = json.loads(data_str)
                    content = self._extract_content_from_chunk(data)
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue

async def _single_response(self, payload: Dict) -> str:
    """Handle non-streaming response from API"""

    response = await self.client.post("/chat/completions", json=payload)

    if response.status_code != 200:
        raise ProviderError(f"API error: {response.status_code}")

    data = response.json()
    return self._extract_content_from_response(data)
```

#### Model Discovery

```python
async def get_models(self) -> List[str]:
    """Get available models from the provider"""

    try:
        response = await self.client.get("/models")

        if response.status_code != 200:
            return self.supported_models  # Fallback to static list

        data = response.json()

        # Extract model names from provider-specific response format
        models = []
        for model in data.get("models", []):
            if self._is_chat_model(model):
                models.append(model["id"])

        return models

    except Exception:
        return self.supported_models  # Fallback to static list

def _is_chat_model(self, model: Dict) -> bool:
    """Filter to only chat-capable models"""

    return (
        "chat" in model.get("id", "").lower() or
        "instruct" in model.get("id", "").lower()
    )
```

#### Health Check

```python
async def health_check(self) -> bool:
    """Check if the provider is healthy and responsive"""

    try:
        # Try a minimal health check request
        response = await self.client.get("/health", timeout=5.0)

        if response.status_code == 200:
            return True

        # Fallback: try a minimal chat request
        test_response = await self.client.post("/chat/completions", json={
            "model": self.default_model,
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 1
        })

        return test_response.status_code == 200

    except Exception:
        return False
```

### Step 3: Configuration Integration

Add your provider to the main configuration:

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    # Existing provider settings...

    # Your provider settings
    YOUR_PROVIDER_API_KEY: Optional[str] = None
    YOUR_PROVIDER_BASE_URL: Optional[str] = None
    YOUR_PROVIDER_DEFAULT_MODEL: str = "your-model-1"

# backend/app/providers/__init__.py

from .your_provider import YourProvider

async def initialize_providers(settings: Settings) -> Dict[str, AIProvider]:
    """Initialize all configured AI providers"""

    providers = {}

    # Your provider
    if settings.YOUR_PROVIDER_API_KEY:
        providers["your_provider"] = YourProvider(
            api_key=settings.YOUR_PROVIDER_API_KEY,
            base_url=settings.YOUR_PROVIDER_BASE_URL,
            default_model=settings.YOUR_PROVIDER_DEFAULT_MODEL
        )

    return providers
```

### Step 4: Environment Configuration

Update your `.env` file:

```bash
# Your AI Provider
YOUR_PROVIDER_API_KEY=your_api_key_here
YOUR_PROVIDER_BASE_URL=https://api.your-service.com  # Optional
YOUR_PROVIDER_DEFAULT_MODEL=your-model-1
```

### Step 5: Testing Your Provider

Create tests for your provider:

```python
# tests/providers/test_your_provider.py

import pytest
from unittest.mock import AsyncMock, patch
from app.providers.your_provider import YourProvider

class TestYourProvider:

    @pytest.fixture
    def provider(self):
        return YourProvider(
            api_key="test-key",
            base_url="https://api.test.com"
        )

    @pytest.mark.asyncio
    async def test_chat_single_response(self, provider):
        """Test single response generation"""

        with patch.object(provider.client, 'post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Test response"}}]
            }
            mock_post.return_value = mock_response

            messages = [{"role": "user", "content": "Hello"}]

            responses = []
            async for response in provider.chat(messages, stream=False):
                responses.append(response)

            assert len(responses) == 1
            assert responses[0] == "Test response"

    @pytest.mark.asyncio
    async def test_health_check_success(self, provider):
        """Test successful health check"""

        with patch.object(provider.client, 'get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            is_healthy = await provider.health_check()
            assert is_healthy is True

    @pytest.mark.asyncio
    async def test_get_models(self, provider):
        """Test model discovery"""

        with patch.object(provider.client, 'get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"id": "your-chat-model-1"},
                    {"id": "your-chat-model-2"}
                ]
            }
            mock_get.return_value = mock_response

            models = await provider.get_models()
            expected_models = ["your-chat-model-1", "your-chat-model-2"]
            assert set(models) == set(expected_models)
```

## 🔧 Advanced Integration Features

### Error Handling and Resilience

```python
class ProviderError(Exception):
    """Base exception for provider errors"""
    pass

class RateLimitExceededError(ProviderError):
    """Rate limit exceeded"""
    pass

# Enhanced error handling in your provider
async def _handle_api_error(self, response: httpx.Response) -> None:
    """Handle API error responses"""

    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "60")
        raise RateLimitExceededError(f"Rate limit exceeded. Retry after {retry_after}s")
    elif response.status_code == 401:
        raise ProviderError("Authentication failed. Check API key.")
    elif response.status_code >= 500:
        raise ProviderError(f"Provider server error: {response.status_code}")
    else:
        raise ProviderError(f"Unknown API error: {response.status_code}")
```

### Custom Authentication

For providers with non-standard authentication:

```python
class CustomAuthProvider(AIProvider):
    def __init__(self, client_id: str, client_secret: str, **config):
        super().__init__("custom_auth_provider", config)
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None

    async def _ensure_valid_token(self):
        """Ensure we have a valid access token"""

        if (not self.access_token or
            datetime.utcnow() >= self.token_expires_at):
            await self._refresh_token()

    async def _refresh_token(self):
        """Get new access token"""

        response = await self.client.post("/oauth/token", json={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        })

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        else:
            raise ProviderError("Token refresh failed")
```

## 📋 Provider Integration Checklist

Before submitting your provider integration:

### ✅ Core Implementation
- [ ] Implements all required abstract methods
- [ ] Handles both streaming and non-streaming responses
- [ ] Proper error handling with specific exception types
- [ ] Health check implementation
- [ ] Model discovery working

### ✅ Configuration
- [ ] Environment variables documented
- [ ] Default values provided
- [ ] Configuration validation

### ✅ Testing
- [ ] Unit tests for all methods
- [ ] Error condition testing
- [ ] Integration tests with mock API
- [ ] Performance tests

### ✅ Documentation
- [ ] Provider-specific setup instructions
- [ ] API key acquisition guide
- [ ] Supported models documented
- [ ] Troubleshooting guide

### ✅ Security
- [ ] API keys handled securely
- [ ] No sensitive data in logs
- [ ] Input validation and sanitization

## 🐛 Troubleshooting Guide

### Common Issues

#### Authentication Failures
```python
async def debug_auth(self):
    try:
        response = await self.client.get("/user")
        print(f"Auth status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Auth error: {e}")
```

#### Rate Limiting Problems
```python
def _log_rate_limit_info(self, response: httpx.Response):
    headers_to_check = [
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset"
    ]

    for header in headers_to_check:
        if header in response.headers:
            logger.info(f"{header}: {response.headers[header]}")
```

### Performance Optimization

#### Connection Pooling
```python
# Optimize HTTP client configuration
self.client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100,
        keepalive_expiry=30.0
    ),
    timeout=httpx.Timeout(connect=5.0, read=30.0)
)
```

## 🚀 Example Provider Templates

### Local Model Provider (Ollama-style)

```python
class LocalModelProvider(AIProvider):
    """Provider for local model inference servers"""

    def __init__(self, base_url: str = "http://localhost:11434", **config):
        super().__init__("local_models", config)
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=60.0)

    async def chat(self, messages: List[Dict], **kwargs):
        """Chat with local model server"""

        payload = {
            "model": kwargs.get("model", "llama2"),
            "messages": messages,
            "stream": kwargs.get("stream", False),
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 150)
            }
        }

        if kwargs.get("stream", False):
            async for chunk in self._stream_ollama_response(payload):
                yield chunk
        else:
            response = await self.client.post("/api/chat", json=payload)
            data = response.json()
            yield data["message"]["content"]
```

This comprehensive guide should help you integrate any AI service into Chimera. Follow the established patterns, implement proper error handling, and thoroughly test your provider integration.