# Development Guide

## Local Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for backend development)
- Node.js 18+ (for frontend development)

### Quick Start
```bash
git clone <repository>
cd chimera

# Start all services (Redis, PostgreSQL)
make dev

# Start backend development server (new terminal)
make dev-backend

# Start frontend development server (new terminal)
make dev-frontend
```

### Development Workflow

#### Database Setup
```bash
# Run migrations
make migrate

# Generate new migration
make migrate-auto

# Reset database (dangerous - loses all data)
make clean
```

#### Running Tests

**Unit Tests**
```bash
# Run all unit tests
make backend-test

# Run specific test file
cd backend && python -m pytest tests/test_providers.py -v

# Run single test method
cd backend && python -m pytest tests/test_orchestrator.py::TestOrchestrator::test_provider_selection -v
```

**Integration Tests**
```bash
# Run all integration tests
make backend-test-integration

# Run conversation integration tests
cd backend && python -m pytest tests/test_conversation_integration.py -v

# Run API integration tests
cd backend && python -m pytest tests/test_api_integration.py -v
```

**Coverage Reports**
```bash
# HTML coverage report
cd backend && python -m pytest --cov=app --cov-report=html

# Terminal coverage report
cd backend && python -m pytest --cov=app --cov-report=term-missing
```

### Code Quality Tools

#### Linting and Formatting
```bash
# Backend linting
make backend-lint

# Frontend linting
cd frontend && npm run lint

# Format code (when available)
# make format
```

#### Pre-commit Hooks (Recommended)
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Architecture Overview

### Backend Components

**API Layer** (`app/api/`)
- `conversations.py` - Conversation management endpoints
- `personsa.py` - Persona configuration endpoints
- `websockets.py` - Real-time WebSocket connections
- `auth.py` - Authentication and authorization

**Service Layer** (`app/services/`)
- `conversation_orchestrator.py` - Main coordination logic
- `persona_manager.py` - AI persona handling
- `turn_manager.py` - Conversation flow control
- `websocket_manager.py` - Real-time messaging
- `response_cache.py` - AI response caching

**Provider Layer** (`app/providers/`)
- `openai_provider.py` - OpenAI GPT integration
- `claude_provider.py` - Anthropic Claude integration
- `gemini_provider.py` - Google Gemini integration
- `deepseek_provider.py` - DeepSeek API integration
- `lm_studio_provider.py` - Local LM Studio support
- `ollama_provider.py` - Local Ollama support

### Frontend Components

**Page Components** (`src/components/`)
- `Chat/ChatWindow.jsx` - Main conversation display
- `Chat/MessageBubble.jsx` - Individual message rendering
- `Chat/TypingIndicator.jsx` - Real-time typing indicators

**Control Components**
- `Controls/ConversationControls.jsx` - Start/stop conversation
- `Controls/PersonaSelector.jsx` - AI persona selection
- `Controls/ConnectionManager.jsx` - WebSocket connection status

**Services**
- `services/api.js` - REST API client
- `services/websocket.js` - WebSocket client
- `hooks/useConversation.js` - Conversation state management
- `hooks/useWebSocket.js` - WebSocket connection management

## Environment Configuration

### Required Environment Variables
```bash
# AI Provider API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
GOOGLE_AI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

# Local AI Services
LM_STUDIO_URL=http://localhost:1234
OLLAMA_URL=http://localhost:11434

# Database
DATABASE_URL=postgresql://chimera:password@localhost:5432/chimera
REDIS_URL=redis://localhost:6379

# Application
SECRET_KEY=your-secret-key-here
DEBUG=true
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Development Environment Variables
Create a `.env` file in the root directory with your API keys. The `.env.example` file shows all available options.

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock external dependencies (AI providers, database, Redis)
- Focus on business logic and error handling
- Location: `backend/tests/test_*.py` (non-integration files)

### Integration Tests
- Test component interactions and data flow
- Use real database connections (SQLite in-memory for speed)
- Mock external APIs but test internal service orchestration
- Location: `backend/tests/test_*_integration.py`

### End-to-End Tests
- Test complete user journeys
- Use actual browser automation (future)
- Test production deployments
- Location: `backend/tests/test_e2e/` (planned)

### Performance Tests
- Load testing for concurrent users
- Memory usage monitoring
- API response time benchmarking
- Marked with `@pytest.mark.performance`

## Debugging

### Backend Debugging
```bash
# Run with debugging enabled
cd backend && python -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --reload

# Connect debugger from your IDE (port 5678)
```

### Frontend Debugging
```bash
# Start with debugging enabled
cd frontend && npm run dev

# Open browser DevTools for React debugging
# Check Network tab for API calls
# Check Console tab for JavaScript errors
```

### Common Issues

**WebSocket Connection Issues**
- Check Redis connectivity: `docker compose logs redis`
- Verify WebSocket URL in frontend
- Check CORS configuration in FastAPI

**AI Provider Errors**
- Verify API keys are set in environment
- Check provider rate limits and credits
- Test manually with curl requests to provider APIs

**Database Connection Issues**
- Verify PostgreSQL container is running
- Check DATABASE_URL configuration
- Run migrations: `make migrate`

**Import/Module Errors**
- Activate virtual environment: `cd backend && source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

## Contributing

### Commit Guidelines
- Use descriptive commit messages
- Keep commits focused on single changes
- Reference issue numbers when applicable
- Sign commits with GPG (recommended)

### Code Review Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Run full test suite locally
4. Submit pull request
5. Address review feedback
6. Merge after approval

### Release Process
1. Update version in `VERSION` file
2. Update CHANGELOG.md (if exists)
3. Create release branch
4. Run full test suite
5. Tag release and deploy

## Performance Optimization

### Backend Performance Tips
- Use async/await for all I/O operations
- Implement response caching for AI queries
- Use connection pooling for database connections
- Monitor memory usage in conversation history

### Frontend Performance Tips
- Implement React.memo for expensive components
- Use lazy loading for components
- Minimize bundle size with tree shaking
- Cache API responses in service worker

### Monitoring
- Check `/health` endpoint for system status
- Monitor WebSocket connection counts
- Track AI provider response times
- Use Redis for caching frequently accessed data

## Troubleshooting

**Issue: Port already in use**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

**Issue: Database migration failures**
```bash
# Check current state
cd backend && alembic current

# Reset to clean state (data loss!)
cd backend && alembic downgrade base
make migrate
```

**Issue: AI responses are slow**
- Check network connectivity to AI provider APIs
- Verify API keys are valid and have credits
- Consider using local models (LM Studio/Ollama) for faster responses

**Issue: WebSocket disconnections**
- Check Redis pub/sub configuration
- Verify client reconnect logic
- Monitor network stability

## Support

- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub discussions for questions
- **Documentation**: This file for development setup and workflow