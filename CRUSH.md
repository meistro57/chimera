# CRUSH.md - Chimera AI Chat Development Guide

## Build, Lint, Test Commands

### Full Stack Development
- `make dev` - Setup and start development environment
- `make build` - Build Docker images
- `make up` - Start production stack
- `make down` - Stop all services
- `make logs` - View real-time container logs

### Backend (Python/FastAPI)
- `make dev-backend` - Start FastAPI with hot reload
- `make backend-test` - Run unit tests (pytest)
- `make backend-test-integration` - Run integration tests
- `make backend-lint` - Run flake8 linting
- `cd backend && python -m pytest tests/ -v` - Run all tests
- `cd backend && python -m pytest tests/test_conversation_integration.py -v` - Run integration tests only
- `cd backend && python -m pytest tests/test_api_integration.py -v` - Run API integration tests
- `cd backend && python -m pytest --cov=app --cov-report=html` - Run tests with coverage report
- `make migrate` - Apply database migrations
- `make migrate-auto` - Generate and apply auto-migrations

### Frontend (React)
- `make dev-frontend` - Start Vite dev server with hot reload
- `cd frontend && npm run build` - Build for production
- `cd frontend && npm run lint` - Run ESLint
- `cd frontend && npm run test` - Run tests (if configured)

### Single Test Execution
- `cd backend && python -m pytest tests/test_file.py::TestClass::test_method -v`
- `cd backend && python -m pytest -k "test_name_pattern"`
- `cd frontend && npm run test -- --testNamePattern="test_name" --watchAll=false`

## Code Style Guidelines

### Python (Backend)
- **Imports**: Group stdlib → third-party → local, blank line between groups
- **Type Hints**: Mandatory for all public functions/methods, use `from __future__ import annotations`
- **Naming**: snake_case functions/variables, PascalCase classes, UPPER_CASE constants
- **Error Handling**: Specific exception types, log structured data, avoid bare except
- **Async**: Async context managers for resources, no blocking calls in async functions
- **Classes**: `@dataclass` for simple data containers, `__slots__` for performance-critical classes
- **Docstrings**: Google/NumPy format, type information in annotations only

### React/JavaScript (Frontend)
- **Components**: PascalCase naming, functional components with hooks preferred
- **Hooks**: Custom hooks for shared logic, exhaustive deps in useEffect
- **JSX**: Multi-line props separate, organize by type (event handlers → other props → children)
- **Styling**: Tailwind utility classes only, consistent spacing/layout system
- **Error Boundaries**: Catch React errors, meaningful fallback UI
- **Imports**: Group React → third-party → local → types, absolute imports preferred

### General
- **Comments**: None needed - write self-documenting code
- **File Organization**: One concept per file, < 300 lines target
- **Dependencies**: Pin concrete versions, update regularly, minimize bundle size
- **Security**: Environment variables only, no secrets in code, input validation

## Common Agent Tasks

### Running/Debugging
- **API Endpoints**: FastAPI uses `app.main:app` - debug with `uvicorn --reload app.main:app`
- **WebSocket Connections**: Connections handled in `websocket_manager.py`, check Redis pubsub
- **Database Issues**: Check `sqlite:///backend/chimera.db` or PostgreSQL connection
- **AI Provider Issues**: Test with curl, check API keys in environment variables

### Database Migration
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic current  # Check current revision
```

### Adding New Features
1. **Backend**: Add to `app/api/routes.py` and `app/services/`
2. **Frontend**: Add components in `src/components/`, update API calls in `src/services/api.js`
3. **Database**: Create migration with alembic if schema changes
4. **Test**: Add corresponding tests in backend/tests/

## Troubleshooting Common Issues

- **WebSocket disconnects**: Check Redis connectivity and session management
- **AI provider timeouts**: Configure longer timeouts for streaming responses
- **Memory issues**: Monitor conversation history size, implement pagination
- **CORS errors**: Verify origins list in FastAPI CORS middleware

## Recommended Project Improvements

### Code Architecture
- **Break up large services**: `conversation_orchestrator.py` (~400 lines) should be split into focused managers
- **Add proper ABC for providers**: `providers/base.py` lacks abstract methods for streaming/AI interactions
- **Database connection pooling**: Move from SQLite to PostgreSQL for production concurrency

### Development Workflow
- **Pre-commit hooks**: Add black/isort/ruff formatting for consistent style
- **API documentation**: Enable FastAPI aut-docs, add OpenAPI spec validation
- **Environment management**: Add `.env.example` with all required variables
- **Makefile defaults**: Add PHONY declarations, enable parallel builds

### Testing & Quality
- **Integration tests**: Add tests for full conversation flows, not just unit tests
- **Mock external APIs**: Create fixtures for OpenAI/Anthropic API responses
- **Load testing**: Add benchmarks for concurrent WebSocket connections
- **Code coverage**: Target >90% for critical services, currently ~30%

### Configuration
- **Pydantic config validation**: All config should validate ranges/types at startup
- **Provider configuration**: Move all API endpoints/keys to config files
- **Feature flags**: Add toggles for experimental features (new AI models, etc.)

### Performance
- **Response caching**: Currently only basic implementation, add TTL/management
- **Connection optimization**: Persistent HTTP connections to AI providers
- **Memory management**: Conversation history should have size limits/rotation