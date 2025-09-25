# Current State & Targeted TODOs

This document maps the present capabilities of the Chimera MVP against the remaining work required to unlock a functioning multi-persona simulation.

## Backend

### Current State
- FastAPI app boots with Redis-backed lifespan, CORS, and REST/WebSocket routers already registered.
- Conversation REST endpoints serve mock conversation metadata and start/stop calls pass control to the orchestrator.
- The conversation orchestrator provisions persona, turn, and WebSocket managers and wires up adapters for OpenAI, Claude, DeepSeek, Gemini, LM Studio, and Ollama when credentials are present.
- Persona and turn managers hold in-memory state that selects weighted speakers, emits typing indicators, and simulates natural delays.

### TODO
- [ ] Share a single WebSocket manager instance between the orchestrator and `/ws` router so UI listeners receive streamed turns.
- [ ] Replace the stubbed conversation history helper with persisted message retrieval.
- [ ] Implement database writes inside `_save_and_broadcast_message` using SQLAlchemy sessions.
- [ ] Add proper error logging/observability around provider failures and orchestration loops.
- [ ] Introduce configuration to cap simultaneous conversations and gracefully stop loops on shutdown.

## Data Layer

### Current State
- SQLAlchemy models exist for `User`, `Conversation`, `Message`, and provider metadata but are not exercised.
- Alembic is configured yet no migrations have been generated.

### TODO
- [ ] Generate and apply initial Alembic migrations for the existing models.
- [ ] Create CRUD repository helpers to abstract conversation/message persistence from the orchestrator and API layer.
- [ ] Backfill seed data or fixtures for development demos.

## Provider Integrations

### Current State
- Provider adapters wrap official SDKs or HTTP endpoints for OpenAI, Claude, DeepSeek, Gemini, LM Studio, and Ollama.
- Health checks and model listing methods exist but rely on environment configuration that defaults to blanks/localhost.

### TODO
- [ ] Harden provider configuration validation and surface actionable status via `/api/providers`.
- [ ] Add fallbacks for missing API keys (e.g., skip registration rather than raising during startup).
- [ ] Implement streaming chunk buffering that can fall back to non-streaming responses when a provider lacks streaming APIs.
- [ ] Document provider-specific setup steps in `docs/providers.md`.

## Frontend

### Current State
- React app renders a chat UI with header, chat window, and control sidebar bound to the `demo-conversation` stub.
- `useConversation` and `useWebSocket` hooks connect to the REST and WebSocket endpoints with reconnection logic and typing indicator support.

### TODO
- [ ] Swap hard-coded `demo-conversation` usage for selectable conversations sourced from the API.
- [ ] Persist messages from the WebSocket stream into local history and clear typing indicators when real messages arrive.
- [ ] Add UI states for provider/offline errors propagated from the backend.
- [ ] Flesh out persona styling using theme tokens shared with backend persona metadata.

## DevOps & Tooling

### Current State
- Docker Compose orchestrates Postgres, Redis, FastAPI, and the Vite frontend with Nginx for static assets.
- Makefile provides common developer workflows.

### TODO
- [ ] Add lint/test targets to the Makefile and wire them into CI.
- [ ] Provide `.env.example` values for local provider endpoints and credentials.
- [ ] Document Docker Compose overrides for enabling local LM Studio/Ollama services.

## Testing & Quality

### Current State
- No automated test suites or quality gates are present yet.

### TODO
- [ ] Establish backend unit tests for persona selection, provider orchestration, and API contracts.
- [ ] Stand up frontend component/integration tests (e.g., Vitest + Testing Library).
- [ ] Add pre-commit hooks for formatting, linting, and type checking.

## Immediate Next Steps
- [ ] Wire database persistence (history retrieval + writes) so the orchestrator and REST API operate on real data.
- [ ] Unify WebSocket broadcasting to deliver conversation events to clients.
- [ ] Produce the first Alembic migration and run it inside Docker Compose to validate the data layer.
- [ ] Draft smoke tests that exercise REST + WebSocket flows end-to-end using mock providers.
