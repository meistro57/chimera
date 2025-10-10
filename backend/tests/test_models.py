import pytest
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User

def test_conversation_model():
    conv = Conversation(id="test", title="Test Conv")
    assert conv.id == "test"
    assert conv.title == "Test Conv"

def test_message_model():
    msg = Message(
        conversation_id="test",
        persona="philosopher",
        content="Hello"
    )
    assert msg.persona == "philosopher"

def test_user_model():
    user = User(id="test_user", username="Test User", email="test@example.com")
    assert user.username == "Test User"

# Add validation tests for pydantic schemas