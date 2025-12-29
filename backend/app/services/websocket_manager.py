# websocket_manager.py
"""WebSocket manager providing connection lifecycle and broadcasting."""

import asyncio
import json
import logging
import time
from typing import Dict, Optional

from fastapi import WebSocket

from ..core.redis_client import redis_client


class WebSocketManager:
    def __init__(
        self,
        heartbeat_interval: float = 15.0,
        connection_timeout: float = 45.0,
    ):
        # Store active connections per conversation with last heartbeat timestamps
        self.active_connections: Dict[str, Dict[WebSocket, float]] = {}
        self.heartbeat_interval = heartbeat_interval
        self.connection_timeout = connection_timeout
        self._heartbeat_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(__name__)

    async def connect(self, websocket: WebSocket, conversation_id: str):
        """Connect a websocket to a conversation"""
        await websocket.accept()

        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = {}

        self.active_connections[conversation_id][websocket] = time.time()
        self._ensure_heartbeat_task()
        self.logger.info(
            "WebSocket connected", extra={"conversation_id": conversation_id}
        )

    def disconnect(
        self,
        websocket: WebSocket,
        conversation_id: str,
        *,
        reason: str = "disconnect",
        detail: Optional[str] = None,
    ):
        """Disconnect a websocket from a conversation"""
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].pop(websocket, None)

            # Clean up empty conversation rooms
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

        self.logger.info(
            "WebSocket disconnected",
            extra={
                "conversation_id": conversation_id,
                "reason": reason,
                "detail": detail,
            },
        )

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific websocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            self.logger.exception(
                "Error sending personal message", extra={"payload": message}
            )

    async def send_error(self, websocket: WebSocket, *, code: str, message: str):
        """Send a structured error payload to the client."""
        await self.send_personal_message(
            {"type": "error", "code": code, "message": message, "timestamp": time.time()},
            websocket,
        )

    async def broadcast_to_conversation(self, conversation_id: str, message: dict):
        """Broadcast a message to all clients in a conversation"""
        if conversation_id not in self.active_connections:
            return

        # Create a copy of the set to avoid modification during iteration
        connections = list(self.active_connections[conversation_id].keys())

        disconnected_connections = []

        for connection in connections:
            try:
                await connection.send_text(json.dumps(message))
                self.mark_heartbeat(conversation_id, connection)
            except Exception:
                self.logger.exception(
                    "Error broadcasting to connection",
                    extra={"conversation_id": conversation_id},
                )
                disconnected_connections.append(connection)

        # Clean up disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection, conversation_id, reason="broadcast_error")

        # Also publish to Redis for scaling across multiple instances
        await self._publish_to_redis(conversation_id, message)

    async def _publish_to_redis(self, conversation_id: str, message: dict):
        """Publish message to Redis for cross-instance communication"""
        try:
            await redis_client.publish(
                f"conversation:{conversation_id}", json.dumps(message)
            )
        except Exception:
            self.logger.exception(
                "Error publishing to Redis", extra={"conversation_id": conversation_id}
            )

    async def get_conversation_clients_count(self, conversation_id: str) -> int:
        """Get the number of active clients in a conversation"""
        return len(self.active_connections.get(conversation_id, {}))

    async def send_conversation_status(self, conversation_id: str):
        """Send conversation status to all clients"""
        client_count = await self.get_conversation_clients_count(conversation_id)
        status_message = {
            "type": "status",
            "conversation_id": conversation_id,
            "connected_clients": client_count,
            "timestamp": time.time(),
        }

        await self.broadcast_to_conversation(conversation_id, status_message)

    def mark_heartbeat(self, conversation_id: str, websocket: WebSocket):
        """Update the last seen timestamp for a websocket."""
        if conversation_id in self.active_connections:
            if websocket in self.active_connections[conversation_id]:
                self.active_connections[conversation_id][websocket] = time.time()

    async def remove_stale_connections(self):
        """Remove connections that have not sent heartbeats within the timeout."""
        now = time.time()
        stale_connections = []

        for conversation_id, connections in list(self.active_connections.items()):
            for websocket, last_seen in list(connections.items()):
                if now - last_seen > self.connection_timeout:
                    stale_connections.append((conversation_id, websocket))

        for conversation_id, websocket in stale_connections:
            await self.send_error(
                websocket,
                code="heartbeat_timeout",
                message="Connection closed due to inactivity.",
            )
            await websocket.close(code=1001)
            self.disconnect(
                websocket,
                conversation_id,
                reason="heartbeat_timeout",
            )
            await self.send_conversation_status(conversation_id)

    def _ensure_heartbeat_task(self):
        """Start the heartbeat monitoring task if needed."""
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            await self.remove_stale_connections()


# Singleton accessor -------------------------------------------------------

_websocket_manager_singleton: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """Return the process-wide WebSocket manager instance."""

    global _websocket_manager_singleton

    if _websocket_manager_singleton is None:
        _websocket_manager_singleton = WebSocketManager()

    return _websocket_manager_singleton
