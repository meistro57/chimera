import pytest
from unittest.mock import AsyncMock
from ..app.services.websocket_manager import WebSocketManager

@pytest.fixture
async def ws_manager():
    return WebSocketManager()

@pytest.mark.asyncio
async def test_connect_and_disconnect(ws_manager):
    mock_ws = AsyncMock()
    conversation_id = "test_conv"
    
    await ws_manager.connect(mock_ws, conversation_id)
    assert conversation_id in ws_manager.active_connections
    assert mock_ws in ws_manager.active_connections[conversation_id]
    
    ws_manager.disconnect(mock_ws, conversation_id)
    assert conversation_id not in ws_manager.active_connections

@pytest.mark.asyncio
async def test_broadcast_to_room(ws_manager):
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    conversation_id = "test_conv"
    
    await ws_manager.connect(mock_ws1, conversation_id)
    await ws_manager.connect(mock_ws2, conversation_id)
    
    await ws_manager.broadcast(message={"type": "test"}, conversation_id=conversation_id)
    
    mock_ws1.send_text.assert_called_once()
    mock_ws2.send_text.assert_called_once()