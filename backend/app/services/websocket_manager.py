import json
from typing import Dict, List, Optional, Set
from fastapi import WebSocket
from ..core.redis_client import redis_client

class WebSocketManager:
    def __init__(self):
        # Store active connections per conversation
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        """Connect a websocket to a conversation"""
        await websocket.accept()

        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = set()

        self.active_connections[conversation_id].add(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        """Disconnect a websocket from a conversation"""
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].discard(websocket)

            # Clean up empty conversation rooms
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific websocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending personal message: {e}")

    async def broadcast_to_conversation(self, conversation_id: str, message: dict):
        """Broadcast a message to all clients in a conversation"""
        if conversation_id not in self.active_connections:
            return

        # Create a copy of the set to avoid modification during iteration
        connections = self.active_connections[conversation_id].copy()

        disconnected_connections = []

        for connection in connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected_connections.append(connection)

        # Clean up disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection, conversation_id)

        # Also publish to Redis for scaling across multiple instances
        await self._publish_to_redis(conversation_id, message)

    async def _publish_to_redis(self, conversation_id: str, message: dict):
        """Publish message to Redis for cross-instance communication"""
        try:
            await redis_client.publish(
                f"conversation:{conversation_id}",
                json.dumps(message)
            )
        except Exception as e:
            print(f"Error publishing to Redis: {e}")

    async def get_conversation_clients_count(self, conversation_id: str) -> int:
        """Get the number of active clients in a conversation"""
        return len(self.active_connections.get(conversation_id, set()))

    async def send_conversation_status(self, conversation_id: str):
        """Send conversation status to all clients"""
        client_count = await self.get_conversation_clients_count(conversation_id)
        status_message = {
            "type": "status",
            "conversation_id": conversation_id,
            "connected_clients": client_count,
            "timestamp": __import__('time').time()
        }

        await self.broadcast_to_conversation(conversation_id, status_message)


# Singleton accessor -------------------------------------------------------

_websocket_manager_singleton: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """Return the process-wide WebSocket manager instance."""

    global _websocket_manager_singleton

    if _websocket_manager_singleton is None:
        _websocket_manager_singleton = WebSocketManager()

    return _websocket_manager_singleton