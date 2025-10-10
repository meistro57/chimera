from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_database
from sqlalchemy.orm import Session
from unittest.mock import MagicMock

# Mock the database dependency for tests
def mock_get_database():
    mock_session = MagicMock(spec=Session)
    return mock_session

app.dependency_overrides[get_database] = mock_get_database

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Chimera AI Conversation System!", "version": "1.0.0"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_conversation():
    response = client.post("/api/conversations", json={"title": "Test Conv"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Conv"

def test_get_conversation_messages():
    response = client.get("/api/conversations/test/messages")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_start_conversation_no_data():
    response = client.post("/api/conversations/demo-conversation/start")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "started"

def test_providers_endpoint():
    response = client.get("/api/providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_personas_endpoint():
    response = client.get("/api/personas")
    assert response.status_code == 200
    data = response.json()
    assert "philosopher" in data
    assert isinstance(data["philosopher"], dict)

def test_cache_stats():
    response = client.get("/api/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert "cache_stats" in data

def test_public_conversation():
    response = client.get("/api/public/conversations/demo")
    assert response.status_code == 404  # No demo token, should fail

# Clean up overrides
app.dependency_overrides = {}
