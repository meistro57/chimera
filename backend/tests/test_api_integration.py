from app.api.auth import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.main import app

"""
API Integration Tests for Chimera REST Endpoints

Tests full HTTP request/response cycles including:
- Conversation CRUD operations
- Conversation lifecycle management
- Error responses and validation
- CORS and authentication endpoints
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock, Mock

from app.core.database import Base, get_database
from app.core.config import Settings


@pytest_asyncio.fixture(scope="session")
def engine():
    """Create in-memory SQLite database for all tests"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest_asyncio.fixture(scope="session")
def SessionLocal(engine):
    """Create session factory"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


@pytest_asyncio.fixture(scope="function")
def db_session(SessionLocal):
    """Clean database session for each test"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest_asyncio.fixture
def test_settings():
    """Settings for testing with mock keys"""
    return Settings(
        database_url="sqlite:///:memory:",
        openai_api_key="test_openai_key",
        anthropic_api_key="test_anthropic_key",
        deepseek_api_key="test_deepseek_key",
        google_ai_api_key="test_google_key",
        lm_studio_url="http://localhost:1234",
        ollama_url="http://localhost:11434",
        cors_origins=["http://localhost:5173"],
        debug=True
    )


@pytest_asyncio.fixture
async def client(db_session):
    """Test client with database override"""
    # Override database dependency as generator
    def override_database():
        yield db_session

    app.dependency_overrides[get_database] = override_database

    # Override user dependency
    def override_user():
        return User(id="test", username="test", email="test@example.com")

    app.dependency_overrides[get_current_user] = override_user

    async with AsyncClient(app=app, base_url="http://testserver") as ac_client:
        yield ac_client

    # Clear overrides
    app.dependency_overrides.clear()


class TestConversationsAPI:
    """Test conversation CRUD endpoints"""

    @pytest.mark.asyncio
    async def test_create_conversation_success(self, client, db_session):
        """Test successful conversation creation"""
        conv_data = {
            "title": "Test Conversation",
            "ai_participants": ["philosopher", "comedian", "scientist"],
            "conversation_mode": "sequential",
            "is_public": False
        }

        response = await client.post("/api/conversations", json=conv_data)
        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert data["title"] == conv_data["title"]
        assert len(data["ai_participants"]) == 3
        assert "philosopher" in data["ai_participants"]

        # Verify in database
        conversation = db_session.query(Conversation).filter(Conversation.id == data["id"]).first()
        assert conversation is not None
        assert conversation.title == conv_data["title"]

    @pytest.mark.asyncio
    async def test_create_conversation_validation_error(self, client):
        """Test conversation creation with invalid data"""
        invalid_data = {
            "title": "",  # Empty title should fail
            "ai_participants": [],
            "conversation_mode": "invalid_mode"
        }

        response = await client.post("/api/conversations", json=invalid_data)
        assert response.status_code == 422  # Validation error

        errors = response.json()
        assert "detail" in errors

    @pytest.mark.asyncio
    async def test_get_conversation_list(self, client):
        """Test listing conversations"""
        # Create multiple conversations
        for i in range(3):
            conv_data = {
                "title": f"Conversation {i}",
                "ai_participants": ["philosopher"]
            }
            await client.post("/api/conversations", json=conv_data)

        response = await client.get("/api/conversations")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

        # Verify structure
        for conv in data:
            assert "id" in conv
            assert "title" in conv
            assert "ai_participants" in conv

    @pytest.mark.asyncio
    async def test_get_single_conversation(self, client):
        """Test getting a specific conversation"""
        # Create conversation
        create_response = await client.post("/api/conversations", json={
            "title": "Get Test",
            "ai_participants": ["philosopher", "comedian"]
        })
        conversation_id = create_response.json()["id"]

        # Retrieve it
        response = await client.get(f"/api/conversations/{conversation_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == conversation_id
        assert data["title"] == "Get Test"
        assert len(data["ai_participants"]) == 2

    @pytest.mark.asyncio
    async def test_get_nonexistent_conversation(self, client):
        """Test accessing non-existent conversation"""
        response = await client.get("/api/conversations/fake-uuid-here")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_start_conversation_endpoint(self, client):
        """Test starting a conversation via API"""
        # Create conversation
        create_response = await client.post("/api/conversations", json={
            "title": "Start Test",
            "ai_participants": ["philosopher", "comedian"]
        })
        conversation_id = create_response.json()["id"]

        # Mock the orchestrator
        with patch('app.api.conversations.orchestrator') as mock_orch:
            mock_orch.start_conversation = AsyncMock(return_value=True)

            # Start conversation
            response = await client.post(
                f"/api/conversations/{conversation_id}/start",
                json={"participants": ["philosopher", "comedian"]}
            )
            assert response.status_code == 200

            # Verify orchestrator was called
            mock_orch.start_conversation.assert_called_once_with(
                conversation_id, ["philosopher", "comedian"]
            )

    @pytest.mark.asyncio
    async def test_stop_conversation_endpoint(self, client):
        """Test stopping a conversation via API"""
        # Create conversation
        create_response = await client.post("/api/conversations", json={
            "title": "Stop Test",
            "ai_participants": ["philosopher"]
        })
        conversation_id = create_response.json()["id"]

        # Mock the orchestrator
        with patch('app.api.conversations.orchestrator') as mock_orch:
            mock_orch.stop_conversation = AsyncMock()

            # Stop conversation
            response = await client.post(f"/api/conversations/{conversation_id}/stop")
            assert response.status_code == 200

            # Verify orchestrator was called
            mock_orch.stop_conversation.assert_called_once_with(conversation_id)


class TestPersonasAPI:
    """Test persona management endpoints"""

    @pytest.mark.asyncio
    async def test_get_personas_list(self, client):
        """Test listing available personas"""
        response = await client.get("/api/personas")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

        # Should have at least the three main personas
        personas = data
        assert len(personas) >= 3

        # Check for required personas
        persona_names = list(personas.keys())
        assert "philosopher" in persona_names
        assert "comedian" in persona_names
        assert "scientist" in persona_names

        # Check persona structure
        philosopher = personas["philosopher"]
        required_fields = ["name", "display_name", "provider"]
        for field in required_fields:
            assert field in philosopher


class TestCorsAndSecurity:
    """Test CORS and security-related functionality"""

    @pytest.mark.asyncio
    async def test_cors_headers(self, client, test_settings):
        """Test CORS headers are properly set"""
        response = await client.options("/api/conversations")
        assert "Access-Control-Allow-Origin" in response.headers

        response = await client.get("/api/conversations")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = await client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_malformed_json_request(self, client):
        """Test handling of malformed JSON"""
        response = await client.post(
            "/api/conversations",
            content="{invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400  # Bad request

    @pytest.mark.asyncio
    async def test_missing_required_field(self, client):
        """Test validation when required fields are missing"""
        response = await client.post("/api/conversations", json={
            "title": "Test"  # Missing ai_participants
        })
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_conversation_with_large_participants(self, client):
        """Test handling large participant lists"""
        conv_data = {
            "title": "Large Conversation Test",
            "ai_participants": ["philosopher", "comedian", "scientist"] * 20  # 60 participants
        }

        response = await client.post("/api/conversations", json=conv_data)
        assert response.status_code == 200

        data = response.json()
        assert len(data["ai_participants"]) == 60


# Performance and load testing utilities
class TestConversationPerformance:
    """Performance tests for conversation operations"""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_conversations(self, client):
        """Test creating multiple conversations simultaneously"""
        import asyncio

        async def create_conversation(i):
            conv_data = {
                "title": f"Concurrent Test {i}",
                "ai_participants": ["philosopher"]
            }
            return await client.post("/api/conversations", json=conv_data)

        # Create 10 conversations concurrently
        tasks = [create_conversation(i) for i in range(10)]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 200

        # Verify all conversations exist
        list_response = await client.get("/api/conversations")
        conversations = list_response.json()
        assert len(conversations) >= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])
