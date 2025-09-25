from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from ..services.websocket_manager import get_websocket_manager

router = APIRouter()

# Global WebSocket manager instance shared across the application
websocket_manager = get_websocket_manager()

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
                "timestamp": __import__('time').time()
            },
            websocket
        )

        # Send current conversation status
        await websocket_manager.send_conversation_status(conversation_id)

        # Listen for client messages
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, conversation_id, message)
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Invalid JSON format"
                    },
                    websocket
                )

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, conversation_id)
        await websocket_manager.send_conversation_status(conversation_id)

    except Exception as e:
        print(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket, conversation_id)

async def handle_websocket_message(websocket: WebSocket, conversation_id: str, message: dict):
    """Handle incoming WebSocket messages from clients"""
    message_type = message.get("type")

    if message_type == "ping":
        # Respond to ping with pong
        await websocket_manager.send_personal_message(
            {
                "type": "pong",
                "timestamp": __import__('time').time()
            },
            websocket
        )

    elif message_type == "user_message":
        # Handle user messages (broadcast to other clients)
        user_message = {
            "type": "message",
            "id": f"user_msg_{__import__('time').time()}",
            "conversation_id": conversation_id,
            "sender_type": "user",
            "sender_id": message.get("user_id", "anonymous"),
            "content": message.get("content", ""),
            "timestamp": __import__('time').time()
        }

        await websocket_manager.broadcast_to_conversation(conversation_id, user_message)

    elif message_type == "status_request":
        # Send current conversation status
        await websocket_manager.send_conversation_status(conversation_id)

    else:
        # Unknown message type
        await websocket_manager.send_personal_message(
            {
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            },
            websocket
        )