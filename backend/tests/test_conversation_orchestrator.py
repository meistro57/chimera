# backend/tests/test_conversation_orchestrator.py
import asyncio
import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.services import conversation_orchestrator
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

@pytest_asyncio.fixture
async def orchestrator(mock_websocket_manager, mock_redis_client):
    # Create a simple orchestrator without complex patches for now
    orch = ConversationOrchestrator(mock_websocket_manager)
    yield orch

@pytest.mark.asyncio
async def test_provider_initialization(orchestrator):
    """Test that providers are initialized correctly based on settings"""
    with patch('app.services.conversation_orchestrator.settings') as mock_settings:
        mock_settings.openai_api_key = "test"
        mock_settings.anthropic_api_key = None  # Not set
        mock_settings.deepseek_api_key = None
        mock_settings.google_ai_api_key = None
        mock_settings.openrouter_api_key = None
        mock_settings.lm_studio_url = "http://localhost:1234"
        mock_settings.ollama_url = "http://localhost:11434"

        providers = orchestrator._initialize_providers()
        assert "openai" in providers
        assert "lm_studio" in providers
        assert "ollama" in providers
        # Claude should not be present since API key is None
        assert "claude" not in providers

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


def _configure_in_memory_session(monkeypatch):
    """Configure SessionLocal to use an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    monkeypatch.setattr(conversation_orchestrator, "SessionLocal", testing_session_local)
    return engine


def test_fetch_recent_conversation_messages_empty_history(monkeypatch):
    """Ensure helper returns an empty list when no messages exist without raising."""
    engine = _configure_in_memory_session(monkeypatch)
    orchestrator = ConversationOrchestrator(Mock())
    conversation_id = str(uuid.uuid4())

    try:
        messages = orchestrator._fetch_recent_conversation_messages(conversation_id)
        assert messages == []
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_fetch_recent_conversation_messages_invalid_id(monkeypatch):
    """Ensure helper degrades gracefully when given a malformed conversation ID."""
    engine = _configure_in_memory_session(monkeypatch)
    orchestrator = ConversationOrchestrator(Mock())

    try:
        messages = orchestrator._fetch_recent_conversation_messages("not-a-uuid")
        assert messages == []
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
