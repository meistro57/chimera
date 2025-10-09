"""Tests for the public FastAPI HTTP endpoints.

These tests intentionally avoid hitting external services (databases,
Redis, third-party AI providers, etc.).  To achieve this we spin up the
application with an in-memory SQLite database, override the
``get_current_user`` dependency so that authentication is bypassed, and
patch the global ``orchestrator`` used inside the conversations router
with a lightweight stub implementation.  The stub only exposes the
behaviour that the tests rely on (``providers`` and
``start_conversation``).

The goal of the tests is to make sure that the high-level HTTP routes
return sensible responses without depending on a complex runtime
environment.  This keeps the test-suite fast and deterministic.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Iterator, List

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Configure environment **before** importing the application so that the
# database engine is created against an in-memory SQLite database.  This keeps
# the tests isolated and avoids creating artefacts on disk.
# ---------------------------------------------------------------------------
os.environ.setdefault("DATABASE_URL", "sqlite://")

# Ensure the backend package is importable when running the tests from the
# repository root.
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))


from app.main import app  # noqa: E402  (import after env configuration)
from app.api import auth, conversations  # noqa: E402
from app.core.database import Base, SessionLocal, engine, get_database  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402


# ---------------------------------------------------------------------------
# Test helpers / stubs
# ---------------------------------------------------------------------------

class _StubProvider:
    """Minimal stand-in for an AI provider used in list_providers."""

    provider_name = "stub"

    async def health_check(self) -> bool:  # pragma: no cover - trivial
        return True

    async def get_models(self) -> List[str]:  # pragma: no cover - trivial
        return ["stub-model"]


class _StubOrchestrator:
    """Simplified orchestrator used to bypass external dependencies."""

    def __init__(self) -> None:
        self.providers: Dict[str, _StubProvider] = {"stub": _StubProvider()}

    async def start_conversation(self, conversation_id: str, participants: List[str]) -> bool:
        return True


class _StubUser:
    """Simple object with the attributes the API accesses."""

    def __init__(self) -> None:
        self.id = "test-user"
        self.username = "test"
        self.email = "test@example.com"


async def _override_get_current_user() -> _StubUser:
    return _StubUser()


def _override_get_database() -> Iterator[Session]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def _create_schema() -> Iterator[None]:
    """Create the database schema once for the test session."""

    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def _client_fixture() -> Iterator[TestClient]:
    """Return a ``TestClient`` with dependencies and orchestrator overridden."""

    original_orchestrator = conversations.orchestrator

    conversations.orchestrator = _StubOrchestrator()
    app.dependency_overrides[get_database] = _override_get_database
    app.dependency_overrides[auth.get_current_user] = _override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    conversations.orchestrator = original_orchestrator
    app.dependency_overrides.pop(get_database, None)
    app.dependency_overrides.pop(auth.get_current_user, None)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_create_conversation(client: TestClient) -> None:
    response = client.post("/api/conversations", json={"title": "Test Conv"})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Conv"
    assert data["participants"] == ["philosopher", "comedian", "scientist"]
    assert "id" in data


def test_get_conversation_messages_empty(client: TestClient) -> None:
    create_response = client.post("/api/conversations", json={"title": "Another"})
    conversation_id = create_response.json()["id"]

    response = client.get(f"/api/conversations/{conversation_id}/messages")

    assert response.status_code == 200
    assert response.json() == []


def test_get_unknown_conversation_returns_404(client: TestClient) -> None:
    response = client.get("/api/conversations/not-real")

    assert response.status_code == 404


def test_list_providers(client: TestClient) -> None:
    response = client.get("/api/providers")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data and data[0]["name"] == "stub"
    assert data[0]["healthy"] is True
