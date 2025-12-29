# websockets.py
"""WebSocket API router for conversation events."""

import json
import logging
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..services.websocket_manager import get_websocket_manager

router = APIRouter()

# Global WebSocket manager instance shared across the application
websocket_manager = get_websocket_manager()
logger = logging.getLogger(__name__)

@router.websocket("/conversation/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time conversation updates"""
    await websocket_manager.connect(websocket, conversation_id)

    try:
        # Send initial connection confirmation
        await websocket_manager.send_personal_message(
            {
                "type": "connection",
                "status": "connected",
                "conversation_id": conversation_id,
                "timestamp": time.time(),
            },
            websocket,
        )

        # Send current conversation status
        await websocket_manager.send_conversation_status(conversation_id)

        # Listen for client messages
        while True:
            data = await websocket.receive_text()
            websocket_manager.mark_heartbeat(conversation_id, websocket)

            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, conversation_id, message)
            except json.JSONDecodeError:
                await websocket_manager.send_error(
                    websocket,
                    code="invalid_json",
                    message="Invalid JSON payload; expected JSON text.",
                )

    except WebSocketDisconnect as exc:
        websocket_manager.disconnect(
            websocket, conversation_id, reason="client_disconnect", detail=str(exc)
        )
        await websocket_manager.send_conversation_status(conversation_id)

    except Exception as e:
        logger.exception("WebSocket error", extra={"conversation_id": conversation_id})
        await websocket_manager.send_error(
            websocket,
            code="internal_error",
            message="An internal server error occurred.",
        )
        websocket_manager.disconnect(
            websocket, conversation_id, reason="server_error", detail=str(e)
        )
        await websocket_manager.send_conversation_status(conversation_id)

async def handle_websocket_message(websocket: WebSocket, conversation_id: str, message: dict):
    """Handle incoming WebSocket messages from clients"""
    message_type = message.get("type")

    if message_type == "ping":
        # Respond to ping with pong
        await websocket_manager.send_personal_message(
            {
                "type": "pong",
                "timestamp": time.time(),
            },
            websocket,
        )
        websocket_manager.mark_heartbeat(conversation_id, websocket)

    elif message_type == "user_message":
        # Handle user messages (broadcast to other clients)
        user_message = {
            "type": "message",
            "id": f"user_msg_{time.time()}",
            "conversation_id": conversation_id,
            "sender_type": "user",
            "sender_id": message.get("user_id", "anonymous"),
            "content": message.get("content", ""),
            "timestamp": time.time(),
        }

        await websocket_manager.broadcast_to_conversation(conversation_id, user_message)

    elif message_type == "status_request":
        # Send current conversation status
        await websocket_manager.send_conversation_status(conversation_id)

    elif message_type == "disconnect":
        # Client requested disconnect
        reason = message.get("reason", "client_requested")
        await websocket_manager.send_personal_message(
            {
                "type": "disconnect",
                "reason": reason,
                "timestamp": time.time(),
            },
            websocket,
        )
        await websocket.close(code=1000)
        websocket_manager.disconnect(websocket, conversation_id, reason=reason)
        await websocket_manager.send_conversation_status(conversation_id)

    else:
        # Unknown message type
        await websocket_manager.send_error(
            websocket,
            code="unknown_message",
            message=f"Unknown message type: {message_type}",
        )
