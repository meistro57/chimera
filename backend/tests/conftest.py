"""
Testing Configuration and Fixtures for Chimera Integration Tests

Provides shared fixtures, mocks, and utilities for comprehensive testing of:
- Database operations
- External API mocking
- WebSocket simulation
- Performance testing
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis

from app.core.database import Base, get_db
from app.core.config import Settings


@pytest.fixture(scope="session")
def test_settings():
    """Complete test settings configuration"""
    return Settings(
        # Database
        database_url="sqlite:///:memory:",
        postgres_host="localhost",
        postgres_port=5432,
        postgres_user="test",
        postgres_password="test",
        postgres_database="chimera_test",

        # Redis
        redis_url="redis://localhost:6379/1",  # Use DB 1 for tests

        # AI Provider API Keys (test keys)
        openai_api_key="sk-test-openai-key-1234567890123456789012345678901234567890",
        anthropic_api_key="sk-ant-test-anthropic-key-1234567890123456789012345678901234567890",
        deepseek_api_key="sk-test-deepseek-key-1234567890123456789012345678901234567890",
        google_ai_api_key="AIzaTestGoogleApiKeyForGemini",
        openrouter_api_key="sk-or-v1-test-openrouter-key-1234567890123456789012345678901234567890",

        # Local AI Endpoints
        lm_studio_url="http://localhost:1234",
        ollama_url="http://localhost:11434",

        # Application Settings
        debug=True,
        secret_key="test-secret-key-for-jwt-tokens",
        cors_origins=["http://localhost:5173", "http://localhost:3000"],
        app_name="Chimera Test",
    )


@pytest.fixture(scope="session")
def test_engine(test_settings):
    """Create test database engine"""
    if "sqlite" in test_settings.database_url:
        # SQLite for fast testing
        engine = create_engine(
            test_settings.database_url,
            connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL for more realistic testing
        engine = create_engine(test_settings.database_url)

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Test session factory"""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session(test_session_factory):
    """Clean database session for each test"""
    session = test_session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
async def redis_client(test_settings):
    """Mock Redis client for testing"""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=1)
    mock_redis.publish = AsyncMock(return_value=None)

    # Mock pipeline operations
    mock_pipeline = Mock()
    mock_pipeline.set = Mock(return_value=mock_pipeline)
    mock_pipeline.expire = Mock(return_value=mock_pipeline)
    mock_pipeline.execute = AsyncMock(return_value=[True, True])
    mock_redis.pipeline = Mock(return_value=mock_pipeline)

    return mock_redis


@pytest.fixture
async def websocket_manager_mock():
    """Mock WebSocket manager for integration tests"""
    ws_manager = AsyncMock()
    ws_manager.broadcast_to_conversation = AsyncMock()
    ws_manager.send_to_user = AsyncMock()
    ws_manager.get_active_connections = AsyncMock(return_value=[])

    # Mock connection manager
    ws_manager.connection_manager = AsyncMock()
    ws_manager.connection_manager.active_connections = {}
    ws_manager.connection_manager.add_connection = AsyncMock()
    ws_manager.connection_manager.remove_connection = AsyncMock()

    return ws_manager


@pytest.fixture
async def conversation_orchestrator_mock(websocket_manager_mock):
    """Mock conversation orchestrator"""
    with patch('app.services.conversation_orchestrator.ConversationOrchestrator') as mock_orch:
        orchestrator = mock_orch.return_value
        orchestrator.start_conversation = AsyncMock(return_value=True)
        orchestrator.stop_conversation = AsyncMock()
        orchestrator.get_participants = AsyncMock(return_value=["philosopher", "comedian"])
        yield orchestrator


# AI Provider Mocks for Integration Testing
@pytest.fixture
def mock_openai_provider():
    """Mock OpenAI provider with streaming response"""
    provider = AsyncMock()
    provider.provider_name = "openai"
    provider.health_check = AsyncMock(return_value=True)

    async def mock_chat_stream(messages, **kwargs):
        """Mock streaming response"""
        responses = ["Hello", " from ", "OpenAI!", " This is a test."]
        for chunk in responses:
            yield chunk
            await asyncio.sleep(0.01)

    provider.chat = mock_chat_stream
    return provider


@pytest.fixture
def mock_claude_provider():
    """Mock Anthropic Claude provider"""
    provider = AsyncMock()
    provider.provider_name = "claude"
    provider.health_check = AsyncMock(return_value=True)

    async def mock_chat_stream(messages, **kwargs):
        responses = ["Greetings,", " I am", " Claude.", " How may I assist?"]
        for chunk in responses:
            yield chunk
            await asyncio.sleep(0.005)

    provider.chat = mock_chat_stream
    return provider


@pytest.fixture
def mock_gemini_provider():
    """Mock Google Gemini provider"""
    provider = AsyncMock()
    provider.provider_name = "gemini"
    provider.health_check = AsyncMock(return_value=True)

    async def mock_chat_stream(messages, **kwargs):
        responses = ["Hi there!", " I'm Gemini,", " your AI assistant."]
        for chunk in responses:
            yield chunk
            await asyncio.sleep(0.008)

    provider.chat = mock_chat_stream
    return provider


@pytest.fixture
def mock_all_providers(mock_openai_provider, mock_claude_provider, mock_gemini_provider):
    """All provider mocks configured"""
    return {
        "openai": mock_openai_provider,
        "claude": mock_claude_provider,
        "gemini": mock_gemini_provider
    }


# Sample Data Fixtures
@pytest.fixture
def sample_conversation_data():
    """Sample conversation creation data"""
    return {
        "title": "Integration Test Conversation",
        "ai_participants": ["philosopher", "comedian", "scientist"],
        "conversation_mode": "sequential",
        "is_public": False
    }


@pytest.fixture
def sample_message_data():
    """Sample message data"""
    return {
        "conversation_id": "test-conv-123",
        "sender_type": "ai",
        "sender_id": "philosopher",
        "persona": "philosopher",
        "content": "The unexamined life is not worth living. - Socrates",
        "metadata": {
            "persona_name": "The Philosopher",
            "avatar_color": "#8B4513",
            "model": "gpt-4"
        }
    }


@pytest.fixture
def sample_persona_configs():
    """Sample persona configurations"""
    return {
        "philosopher": {
            "name": "philosopher",
            "display_name": "The Philosopher",
            "system_prompt": "You are a contemplative philosopher...",
            "temperature": 0.7,
            "response_style": "contemplative",
            "avg_response_length": 150
        },
        "comedian": {
            "name": "comedian",
            "display_name": "The Comedian",
            "system_prompt": "You are a witty comedian...",
            "temperature": 0.9,
            "response_style": "humorous",
            "avg_response_length": 80
        },
        "scientist": {
            "name": "scientist",
            "display_name": "The Scientist",
            "system_prompt": "You are an analytical scientist...",
            "temperature": 0.3,
            "response_style": "analytical",
            "avg_response_length": 120
        }
    }


# Test Utilities
class TestUtils:
    """Utility functions for integration tests"""

    @staticmethod
    async def create_test_conversation(client, **overrides):
        """Helper to create a test conversation"""
        data = {
            "title": "Test Conversation",
            "ai_participants": ["philosopher", "comedian"],
            "conversation_mode": "sequential"
        }
        data.update(overrides)

        response = await client.post("/api/conversations", json=data)
        assert response.status_code == 200
        return response.json()

    @staticmethod
    async def wait_for_websocket_message(websocket_mock, timeout=5):
        """Wait for WebSocket message to be sent"""
        import asyncio
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < timeout:
            if websocket_mock.send_json.called:
                return websocket_mock.send_json.call_args[0][0]
            await asyncio.sleep(0.1)

        raise TimeoutError("WebSocket message not sent within timeout")

    @staticmethod
    def assert_conversation_in_list(conversations, conversation_id):
        """Assert a conversation exists in a list"""
        conv_ids = [c["id"] for c in conversations]
        assert conversation_id in conv_ids, f"Conversation {conversation_id} not found in {conv_ids}"

    @staticmethod
    def assert_websocket_message_sent(manager_mock, conversation_id, message_type=None):
        """Assert WebSocket message was broadcast"""
        assert manager_mock.broadcast_to_conversation.called

        call_args_list = manager_mock.broadcast_to_conversation.call_args_list
        for call_args in call_args_list:
            call_conv_id = call_args[0][0]
            call_message = call_args[0][1]

            if call_conv_id == conversation_id:
                if message_type:
                    assert call_message["type"] == message_type
                return call_message

        raise AssertionError(f"No message sent to conversation {conversation_id}")


# Performance Testing Utilities
class PerformanceTestUtils:
    """Utilities for performance testing"""

    @staticmethod
    async def measure_execution_time(coro, iterations=1):
        """Measure async function execution time"""
        import time
        start_time = time.time()

        for _ in range(iterations):
            await coro

        total_time = time.time() - start_time
        avg_time = total_time / iterations
        return {"total": total_time, "average": avg_time, "iterations": iterations}

    @staticmethod
    async def simulate_concurrent_users(client, user_count, action_coro):
        """Simulate concurrent users performing an action"""
        import asyncio

        async def user_action(user_id):
            return await action_coro(user_id)

        tasks = [user_action(i) for i in range(user_count)]
        start_time = asyncio.get_event_loop().time()

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time

        # Count successes and failures
        successes = sum(1 for r in results if not isinstance(r, Exception))
        failures = len(results) - successes

        return {
            "duration": duration,
            "total_users": user_count,
            "successes": successes,
            "failures": failures,
            "success_rate": successes / user_count if user_count > 0 else 0
        }

    @staticmethod
    async def load_test_memory_usage(func, iterations=100):
        """Monitor memory usage during load testing"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        for _ in range(iterations):
            await func()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        return {
            "initial_mb": initial_memory,
            "final_mb": final_memory,
            "difference_mb": final_memory - initial_memory,
            "iterations": iterations
        }


# Global test configuration
def pytest_configure(config):
    """Configure pytest for integration tests"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection for better integration test handling"""
    for item in items:
        # Auto-mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add asyncio marker to async tests
        if "async def test_" in str(item.function):
            item.add_marker(pytest.mark.asyncio)</content>
<parameter name="file_path">backend/tests/conftest.py