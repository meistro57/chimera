import pytest
from app.services.conversation_orchestrator import ConversationOrchestrator
from app.services.persona_manager import PersonaManager
from app.services.turn_manager import TurnManager
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_websocket_manager():
    return AsyncMock()


@pytest.fixture
def orchestrator(mock_websocket_manager):
    persona_manager = PersonaManager()
    turn_manager = TurnManager()
    return ConversationOrchestrator(
        websocket_manager=mock_websocket_manager,
        persona_manager=persona_manager,
        turn_manager=turn_manager
    )


@pytest.mark.asyncio
async def test_start_conversation(orchestrator, mock_websocket_manager):
    # Mock providers
    mock_provider = AsyncMock()
    mock_provider.health_check.return_value = True
    orchestrator.providers = {'openai': mock_provider}

    success = await orchestrator.start_conversation(
        'test_conv', ['philosopher', 'comedian']
    )
    assert success == True
    mock_websocket_manager.initialize.assert_called_once()


@pytest.mark.asyncio
async def test_get_conversation_history(orchestrator):
    # Assuming some setup with mocks for database
    messages = await orchestrator.get_conversation_history('test_conv')
    assert isinstance(messages, list)