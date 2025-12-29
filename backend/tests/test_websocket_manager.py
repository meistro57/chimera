# test_websocket_manager.py
"""Tests for WebSocketManager core behaviors."""

import asyncio
from unittest.mock import AsyncMock

import pytest

from app.services.websocket_manager import WebSocketManager

@pytest.fixture
def ws_manager():
    return WebSocketManager()

@pytest.mark.asyncio
async def test_connect_and_disconnect(ws_manager):
    mock_ws = AsyncMock()
    conversation_id = "test_conv"

    await ws_manager.connect(mock_ws, conversation_id)
    assert conversation_id in ws_manager.active_connections
    assert mock_ws in ws_manager.active_connections[conversation_id]

    ws_manager.disconnect(mock_ws, conversation_id, reason="test")
    assert conversation_id not in ws_manager.active_connections


@pytest.mark.asyncio
async def test_broadcast_to_room(ws_manager):
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    conversation_id = "test_conv"

    await ws_manager.connect(mock_ws1, conversation_id)
    await ws_manager.connect(mock_ws2, conversation_id)

    message = {"type": "test", "content": "Hello"}
    await ws_manager.broadcast_to_conversation(conversation_id, message)

    assert mock_ws1.send_text.await_count == 1
    assert mock_ws2.send_text.await_count == 1


@pytest.mark.asyncio
async def test_stale_connection_cleanup(ws_manager):
    conversation_id = "stale_conv"
    mock_ws = AsyncMock()
    await ws_manager.connect(mock_ws, conversation_id)

    # simulate stale by rewinding timestamp
    ws_manager.active_connections[conversation_id][mock_ws] -= (
        ws_manager.connection_timeout + 1
    )

    await ws_manager.remove_stale_connections()

    assert conversation_id not in ws_manager.active_connections
    assert mock_ws.close.await_count == 1
