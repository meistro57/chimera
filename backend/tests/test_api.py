import pytest
from fastapi.testclient import TestClient
from ..app.api.conversations import router

client = TestClient(router)

def test_create_conversation():
    response = client.post("/conversations", json={"title": "Test Conv", "topic": "Test"})
    assert response.status_code == 200
    assert "id" in response.json()

def test_get_conversation_messages():
    response = client.get("/conversations/test/message")
    assert response.status_code == 200
    # Mock DB, so returns [] initially

def test_start_conversation_no_data():
    response = client.post("/conversations/test/start")
    assert response.status_code == 422  # Unprocessable due to missing body

def test_providers_endpoint():
    response = client.get("/providers")
    assert response.status_code == 200

# Add auth tests when implemented