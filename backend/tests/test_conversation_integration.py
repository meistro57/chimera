"""
Integration Tests for Chimera Conversation System

These tests cover end-to-end scenarios including:
- Full conversation lifecycle
- WebSocket real-time communication
- Database persistence
- AI provider fallback logic
- Error handling and recovery
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import uuid
from httpx import AsyncClient
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, get_db
from app.core.config import Settings
from app.services.conversation_orchestrator import ConversationOrchestrator
from app.services.websocket_manager import WebSocketManager


# Test database fixtures
@pytest.fixture(scope="session")
def engine():
    """Create in-memory SQLite database for tests"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def SessionLocal(engine):
    """Create session factory for tests"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


@pytest.fixture(scope="function")
def db_session(SessionLocal):
    """Provide a clean database session for each test"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_settings():
    """Test settings with mock API keys"""
    return Settings(
        database_url="sqlite:///:memory:",
        redis_url="redis://localhost:6379",
        openai_api_key="test_openai_key",
        anthropic_api_key="test_anthropic_key",
        deepseek_api_key="test_deepseek_key",
        google_ai_api_key="test_google_key",
        lm_studio_url="http://localhost:1234",
        ollama_url="http://localhost:11434",
        debug=True
    )


@pytest.fixture
async def client(db_session):
    """HTTP client for API testing"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Override database dependency
        app.dependency_overrides[get_db] = lambda: db_session
        yield client
        app.dependency_overrides.clear()


@pytest.fixture
async def websocket_manager():
    """Mock WebSocket manager for integration tests"""
    ws_manager = Mock()
    ws_manager.broadcast_to_conversation = AsyncMock()
    ws_manager.connection_manager = Mock()
    ws_manager.connection_manager.active_connections = []
    return ws_manager


class TestConversationIntegration:
    """Integration tests for full conversation lifecycles"""

    @pytest.mark.asyncio
    async def test_full_conversation_lifecycle(self, client, db_session, websocket_manager):
        """Test complete flow: create conversation → start → generate messages → complete"""
        # Create conversation
        conv_data = {
            "title": "Integration Test Conversation",
            "ai_participants": ["philosopher", "comedian"],
            "conversation_mode": "sequential"
        }

        response = await client.post("/api/conversations", json=conv_data)
        assert response.status_code == 200
        conv_result = response.json()
        conversation_id = conv_result["id"]

        # Verify conversation created in database
        from app.models.conversation import Conversation
        conversation = db_session.query(Conversation).filter(Conversation.id == conversation_id).first()
        assert conversation is not None
        assert conversation.title == conv_data["title"]
        assert "philosopher" in conversation.ai_participants
        assert "comedian" in conversation.ai_participants

        # Start conversation
        start_response = await client.post(f"/api/conversations/{conversation_id}/start", json={
            "participants": ["philosopher", "comedian"]
        })
        assert start_response.status_code == 200

        # Mock orchestrator with controlled behavior
        with patch('app.services.conversation_orchestrator.ConversationOrchestrator') as mock_orch_cls:
            mock_orch = Mock()
            mock_orch.start_conversation = AsyncMock(return_value=True)
            mock_orch_cls.return_value = mock_orch

            # Start conversation through API
            start_response = await client.post(f"/api/conversations/{conversation_id}/start", json={
                "participants": ["philosopher", "comedian"]
            })
            assert start_response.status_code == 200

            # Verify orchestrator was called correctly
            mock_orch.start_conversation.assert_called_once_with(conversation_id, ["philosopher", "comedian"])

    @pytest.mark.asyncio
    async def test_ai_provider_fallback_integration(self, client, websocket_manager, test_settings):
        """Test AI provider fallback when primary providers fail"""
        # Create orchestrator with mocked providers
        orch = ConversationOrchestrator(websocket_manager)

        # Mock provider health checks - primary fail, fallback succeeds
        mock_primary = Mock()
        mock_primary.health_check = AsyncMock(return_value=False)  # OpenAI fails
        mock_fallback = Mock()
        mock_fallback.health_check = AsyncMock(return_value=True)   # Claude works

        orch.providers = {
            "openai": mock_primary,
            "claude": mock_fallback,
            "deepseek": mock_fallback
        }
        orch.provider_persona_assignment = {
            "philosopher": ["openai", "claude", "deepseek"]  # OpenAI first, but fails
        }

        # Select provider for philosopher
        provider = await orch._select_provider_for_persona("philosopher")

        # Should fallback to Claude (second in list)
        assert provider == mock_fallback
        mock_primary.health_check.assert_called_once()
        mock_fallback.health_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_message_broadcasting(self, client, db_session, websocket_manager):
        """Test WebSocket message broadcasting during conversations"""
        # Create and start conversation
        conv_response = await client.post("/api/conversations", json={
            "title": "WebSocket Test",
            "ai_participants": ["philosopher", "comedian"]
        })
        conversation_id = conv_response.json()["id"]

        # Start conversation
        await client.post(f"/api/conversations/{conversation_id}/start", json={
            "participants": ["philosopher", "comedian"]
        })

        # Mock message broadcasting
        websocket_manager.broadcast_to_conversation.side_effect = None

        # Trigger message generation (mocked)
        with patch('app.services.conversation_orchestrator.ConversationOrchestrator') as mock_orch_cls:
            mock_orch = Mock()
            mock_orch._generate_response = AsyncMock(return_value="Hello from AI!")
            mock_orch._get_conversation_history = AsyncMock(return_value=[])
            mock_orch.persona_manager.get_system_prompt = Mock(return_value="Test prompt")
            mock_orch.persona_manager.get_persona_params = Mock(return_value={"temperature": 0.7})
            mock_orch.providers = {"openai": Mock()}
            mock_orch._select_provider_for_persona = AsyncMock(return_value=Mock())
            mock_orch_cls.return_value = mock_orch

            # Save message to database
            orch = ConversationOrchestrator(websocket_manager)
            await orch._generate_response(conversation_id, "philosopher")

            # Verify WebSocket broadcasting was triggered
            websocket_manager.broadcast_to_conversation.assert_called()

    @pytest.mark.asyncio
    async def test_database_persistence_integration(self, client, db_session):
        """Test that conversation data persists correctly across requests"""
        # Create conversation
        conv_data = {
            "title": "Persistence Test",
            "ai_participants": ["philosopher", "scientist", "comedian"]
        }

        response = await client.post("/api/conversations", json=conv_data)
        conversation_id = response.json()["id"]

        # Get conversation back
        get_response = await client.get(f"/api/conversations/{conversation_id}")
        assert get_response.status_code == 200
        retrieved = get_response.json()

        # Verify data persisted
        assert retrieved["id"] == conversation_id
        assert retrieved["title"] == conv_data["title"]
        assert len(retrieved["ai_participants"]) == 3
        assert retrieved["conversation_mode"] == "sequential"

        # Get all conversations
        list_response = await client.get("/api/conversations")
        assert list_response.status_code == 200
        conversations = list_response.json()["conversations"]
        assert len(conversations) >= 1
        assert any(c["id"] == conversation_id for c in conversations)

    @pytest.mark.asyncio
    async def test_conversation_with_turn_management(self, websocket_manager):
        """Test that turn management works in conversation flow"""
        from app.services.turn_manager import TurnManager

        orch = ConversationOrchestrator(websocket_manager)

        # Mock Redis operations
        with patch('redis.Redis') as mock_redis:
            mock_redis_instance = Mock()
            mock_redis.return_value = mock_redis_instance
            mock_redis_instance.set = AsyncMock()
            mock_redis_instance.get = AsyncMock()

            # Start conversation
            conversation_id = "test_conv_turns"
            participants = ["philosopher", "comedian", "scientist"]

            await orch.turn_manager.start_conversation(conversation_id, participants)

            # Get next speakers - should cycle through participants
            first_speaker = await orch.turn_manager.get_next_speaker(conversation_id)
            second_speaker = await orch.turn_manager.get_next_speaker(conversation_id)

            # Verify different speakers selected
            assert first_speaker is not None
            assert second_speaker is not None
            assert first_speaker != second_speaker

            # Verify all are participants
            assert first_speaker in participants
            assert second_speaker in participants

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, client, websocket_manager):
        """Test error handling and graceful degradation"""
        # Test malformed conversation creation
        bad_response = await client.post("/api/conversations", json={
            "invalid_field": "should_fail_validation"
        })
        # Should return validation error
        assert bad_response.status_code == 422

        # Test non-existent conversation access
        nonexistent_response = await client.get("/api/conversations/fake-uuid")
        assert nonexistent_response.status_code == 404

        # Test orchestrator with all providers failing
        orch = ConversationOrchestrator(websocket_manager)

        # Mock all providers as failing
        mock_bad_provider = Mock()
        mock_bad_provider.health_check = AsyncMock(return_value=False)

        orch.providers = {
            "openai": mock_bad_provider,
            "claude": mock_bad_provider,
            "deepseek": mock_bad_provider
        }

        # Should handle gracefully
        provider = await orch._select_provider_for_persona("philosopher")
        assert provider is None  # No healthy providers


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality"""

    @pytest.mark.asyncio
    async def test_websocket_connection_and_messaging(self):
        """Test WebSocket connection and message flow"""
        from app.api.websockets import websocket_manager_for_test

        # This would typically use a WebSocket test client
        # For now, test the manager directly
        ws_manager = WebSocketManager()

        # Mock WebSocket connection
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()

        # Simulate client connecting
        conversation_id = "test_conv_ws"
        ws_manager.active_connections[conversation_id] = [mock_ws]

        # Broadcast message
        test_message = {"type": "test", "content": "Hello WebSocket!"}
        await ws_manager.broadcast_to_conversation(conversation_id, test_message)

        # Verify message sent
        mock_ws.send_json.assert_called_once_with(test_message)

    @pytest.mark.asyncio
    async def test_typing_indicators_and_realtime_updates(self, websocket_manager):
        """Test real-time typing indicators"""
        orch = ConversationOrchestrator(websocket_manager)

        # Test typing indicator broadcast
        await orch._show_typing_indicator("test_conv", "philosopher")

        # Verify typing message sent
        expected_message = {
            "type": "typing",
            "persona": "philosopher",
            "persona_name": orch.persona_manager.get_persona("philosopher")["display_name"],
            "content": f"{orch.persona_manager.get_persona('philosopher')['display_name']} is typing...",
            "timestamp": pytest.approx(float(asyncio.get_event_loop().time()), abs=1.0)
        }

        websocket_manager.broadcast_to_conversation.assert_called_once()
        call_args = websocket_manager.broadcast_to_conversation.call_args[0]
        assert call_args[0] == "test_conv"


# Run integration tests with specific markers
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])</content>
<parameter name="file_path">backend/tests/test_conversation_integration.py