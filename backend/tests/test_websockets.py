# test_websockets.py
"""End-to-end websocket API tests using WebSocketTestSession."""

import asyncio

import anyio
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.api import websockets as ws_router
from app.core.redis_client import redis_client


class DummyRedis:
    """Lightweight Redis stand-in for websocket tests."""

    def __init__(self):
        self.published: list[tuple[str, str]] = []

    async def publish(self, channel: str, message: str) -> None:
        self.published.append((channel, message))

    async def close(self) -> None:  # pragma: no cover - graceful shutdown helper
        return None


@pytest.fixture()
def anyio_backend():
    """Force anyio to use asyncio backend to avoid optional trio dependency."""

    return "asyncio"


@pytest.fixture(autouse=True)
async def reset_websocket_manager(monkeypatch):
    """Reset connection state and stub Redis before each test."""

    dummy_redis = DummyRedis()
    monkeypatch.setattr("app.core.redis_client.redis.from_url", lambda *a, **k: dummy_redis)
    redis_client.redis = dummy_redis

    ws_router.websocket_manager.active_connections.clear()
    ws_router.websocket_manager.connection_timeout = 0.2
    ws_router.websocket_manager.heartbeat_interval = 0.05

    if ws_router.websocket_manager._heartbeat_task and not ws_router.websocket_manager._heartbeat_task.done():
        ws_router.websocket_manager._heartbeat_task.cancel()
        try:
            await ws_router.websocket_manager._heartbeat_task
        except asyncio.CancelledError:
            pass
    ws_router.websocket_manager._heartbeat_task = None

    yield

    if ws_router.websocket_manager._heartbeat_task and not ws_router.websocket_manager._heartbeat_task.done():
        ws_router.websocket_manager._heartbeat_task.cancel()
        with anyio.move_on_after(0.2):
            try:
                await ws_router.websocket_manager._heartbeat_task
            except asyncio.CancelledError:
                pass
    ws_router.websocket_manager._heartbeat_task = None
    ws_router.websocket_manager.active_connections.clear()


@pytest.fixture()
def websocket_client():
    """Create a minimal FastAPI instance that supports WebSocket connections."""

    app_instance = FastAPI()
    app_instance.include_router(ws_router.router, prefix="/ws")

    with TestClient(app_instance) as client:
        yield client


@pytest.mark.anyio("asyncio")
async def test_websocket_connect_and_status(websocket_client: TestClient):
    with websocket_client.websocket_connect("/ws/conversation/conv-1") as session:
        first = session.receive_json()
        status = session.receive_json()

    assert first["type"] == "connection"
    assert status["type"] == "status"
    assert status["connected_clients"] >= 0


@pytest.mark.anyio("asyncio")
async def test_invalid_json_handling(websocket_client: TestClient, caplog):
    with websocket_client.websocket_connect("/ws/conversation/conv-2") as session:
        session.receive_json()
        session.receive_json()

        session.send_text("not-json")
        error = session.receive_json()

    assert error["type"] == "error"
    assert error["code"] == "invalid_json"
    assert any("Invalid JSON received" in rec.message for rec in caplog.records)


@pytest.mark.anyio("asyncio")
async def test_ping_pong_round_trip(websocket_client: TestClient):
    with websocket_client.websocket_connect("/ws/conversation/conv-3") as session:
        session.receive_json()
        session.receive_json()

        session.send_json({"type": "ping"})
        pong = session.receive_json()

    assert pong["type"] == "pong"


@pytest.mark.anyio("asyncio")
async def test_force_disconnect_and_reason(websocket_client: TestClient):
    with websocket_client.websocket_connect("/ws/conversation/conv-4") as session:
        session.receive_json()
        session.receive_json()

        session.send_json({"type": "disconnect", "reason": "test_case"})
        disconnect_notice = session.receive_json()

        assert disconnect_notice["type"] == "disconnect"
        assert disconnect_notice["reason"] == "test_case"

        with pytest.raises(WebSocketDisconnect):
            session.receive_text()


@pytest.mark.anyio("asyncio")
async def test_heartbeat_timeout_disconnects_stale_session(websocket_client: TestClient):
    with websocket_client.websocket_connect("/ws/conversation/conv-6") as session:
        session.receive_json()
        session.receive_json()

        await anyio.sleep(0.35)
        error = session.receive_json()

        assert error["type"] == "error"
        assert error["code"] == "heartbeat_timeout"

        await anyio.sleep(0.05)
        assert "conv-6" not in ws_router.websocket_manager.active_connections


@pytest.mark.anyio("asyncio")
async def test_reconnect_sends_status_update(websocket_client: TestClient):
    # First connection
    with websocket_client.websocket_connect("/ws/conversation/conv-5") as session:
        session.receive_json()
        session.receive_json()

    # Reconnect should still provide connection + status
    with websocket_client.websocket_connect("/ws/conversation/conv-5") as session:
        reconnect_msg = session.receive_json()
        status_msg = session.receive_json()

    assert reconnect_msg["type"] == "connection"
    assert status_msg["type"] == "status"
    assert status_msg["connected_clients"] >= 1


@pytest.mark.anyio("asyncio")
async def test_status_broadcast_on_disconnect_and_reconnect(websocket_client: TestClient):
    # Connect two clients to verify status broadcasts during disconnect/reconnect lifecycle
    with websocket_client.websocket_connect("/ws/conversation/conv-7") as session_a:
        session_a.receive_json()
        session_a.receive_json()

        with websocket_client.websocket_connect("/ws/conversation/conv-7") as session_b:
            session_b.receive_json()
            status_b = session_b.receive_json()

            assert status_b["type"] == "status"
            assert status_b["connected_clients"] >= 2

            session_b.send_json({"type": "disconnect", "reason": "test"})
            session_b.receive_json()
            with pytest.raises(WebSocketDisconnect):
                session_b.receive_text()

            status_after_disconnect = session_a.receive_json()

        # After reconnect, status should reflect active client(s)
        with websocket_client.websocket_connect("/ws/conversation/conv-7") as session_c:
            session_c.receive_json()
            status_after_reconnect = session_c.receive_json()

    assert status_after_disconnect["type"] == "status"
    assert status_after_disconnect["connected_clients"] >= 1
    assert status_after_reconnect["type"] == "status"
    assert status_after_reconnect["connected_clients"] >= 1
