import pytest
from ..app.models.conversation import Conversation
from ..app.models.message import Message
from ..app.models.user import User

def test_conversation_model():
    conv = Conversation(id="test", title="Test", topic="Topic")
    assert conv.id == "test"
    assert conv.topic == "Topic"

def test_message_model():
    msg = Message(
        conversation_id="test",
        persona_name="philosopher",
        content="Hello"
    )
    assert msg.persona_name == "philosopher"

def test_user_model():
    user = User(id="test_user", name="Test User")
    assert user.name == "Test User"

# Add validation tests for pydantic schemas