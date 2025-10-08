import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from app.services.conversation_orchestrator import ConversationOrchestrator

@pytest.fixture
def mock_websocket_manager():
    return Mock()

@pytest.fixture
def mock_redis_client():
    mock = Mock()
    mock.get.return_value = None
    mock.set = AsyncMock()
    return mock

@pytest.fixture
async def orchestrator(mock_websocket_manager, mock_redis_client):
    with patch('app.services.conversation_orchestrator.redis_client', mock_redis_client):
        with patch('app.services.conversation_orchestrator.settings') as mock_settings:
            # Mock API keys
            mock_settings.openai_api_key = "test_key"
            mock_settings.anthropic_api_key = "test_key"
            mock_settings.deepseek_api_key = "test_key"
            mock_settings.google_ai_api_key = "test_key"
            mock_settings.openrouter_api_key = "test_key"
            mock_settings.lm_studio_url = "http://localhost:1234"
            mock_settings.ollama_url = "http://localhost:11434"

            orch = ConversationOrchestrator(mock_websocket_manager)
            yield orch

@pytest.mark.asyncio
async def test_provider_initialization(orchestrator):
    """Test that providers are initialized correctly based on settings"""
    with patch('app.services.conversation_orchestrator.settings') as mock_settings:
        mock_settings.openai_api_key = "test"
        mock_settings.openrouter_api_key = "test"
        mock_settings.lm_studio_url = "http://localhost:1234"

        providers = orchestrator._initialize_providers()
        assert "openai" in providers
        assert "openrouter" in providers
        assert "lm_studio" in providers

@pytest.mark.asyncio
async def test_start_conversation(orchestrator, mock_websocket_manager):
    """Test starting a conversation"""
    mock_websocket_manager.broadcast_to_conversation = AsyncMock()

    result = await orchestrator.start_conversation("test_conv", ["philosopher", "comedian"])
    assert result is True

@pytest.mark.asyncio
async def test_generate_response(orchestrator):
    """Test response generation with mocked provider"""
    # Mock provider health check and chat
    mock_provider = Mock()
    mock_provider.health_check = AsyncMock(return_value=True)
    async def mock_chat(*args, **kwargs):
        for chunk in ["Hello", " world"]:
            yield chunk

    mock_provider.chat = mock_chat

    orchestrator.providers = {"openai": mock_provider}
    orchestrator.provider_persona_assignment = {"philosopher": ["openai"]}

    # Mock message history
    orchestrator._get_conversation_history = AsyncMock(return_value=[])
    orchestrator.persona_manager.get_system_prompt = Mock(return_value="Test system prompt")
    orchestrator.persona_manager.get_persona_params = Mock(return_value={"temperature": 0.7, "max_tokens": 150})

    response = await orchestrator._generate_response("test_conv", "philosopher")
    assert "Hello world" in response

@pytest.mark.asyncio
async def test_select_provider_for_persona(orchestrator):
    """Test provider selection logic"""
    # Mock healthy provider
    mock_provider = Mock()
    mock_provider.health_check = AsyncMock(return_value=True)

    orchestrator.providers = {"openai": mock_provider}
    orchestrator.provider_persona_assignment = {"philosopher": ["openai"]}

    provider = await orchestrator._select_provider_for_persona("philosopher")
    assert provider is not None

    # Test fallback
    orchestrator.provider_persona_assignment = {"philosopher": ["nonexistent"]}
    provider = await orchestrator._select_provider_for_persona("philosopher")
    assert provider is not None