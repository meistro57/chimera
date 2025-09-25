# Chimera Multi-AI Conversational Simulation System

## Project Overview

Chimera is a multi-AI conversational simulation where different AI providers (OpenAI, Anthropic, DeepSeek, Gemini, LM Studio, Ollama) are given distinct personas and engage in real-time conversations with each other. This creates an entertaining "AI chatroom" experience where users can observe dynamic interactions between AI personalities.

**Core Concept**: Three AI personas (Philosopher, Comedian, Scientist) engage in natural conversations, creating emergent social dynamics and entertaining content through their interactions.

## Key Features

### Multi-AI Integration
- **OpenAI GPT models** for general conversation
- **Anthropic Claude** for thoughtful responses
- **DeepSeek** for cost-effective processing
- **Google Gemini** for multimodal capabilities
- **LM Studio** for local model hosting
- **Ollama** for open-source model support

### AI Personas
- **The Philosopher**: Contemplative, uses complex vocabulary, references famous thinkers
- **The Comedian**: Quick wit, puns, emojis, short punchy responses
- **The Scientist**: Fact-oriented, data-driven, structured responses

### Real-Time Features
- WebSocket-based live conversation updates
- Natural turn-taking with randomized delays
- Typing indicators ("The Comedian is typing...")
- Live conversation streaming

## Technical Architecture

### Backend Stack
- **FastAPI** (Python) - Main API server
- **PostgreSQL** - Conversation storage and user management
- **Redis** - Real-time messaging, caching, and session management
- **WebSockets** - Real-time client communication

### Frontend Stack
- **React** - User interface
- **WebSocket client** - Real-time updates
- **Modern CSS/Tailwind** - Responsive design

### AI Provider Integration
- Unified provider abstraction layer
- Streaming response support
- Rate limiting and error handling
- Cost tracking and optimization

## Development Phases

### Phase 1: MVP (Weeks 1-4)
1. **Core Infrastructure**
   - FastAPI application setup
   - PostgreSQL database with conversation schema
   - Redis integration for real-time messaging
   - Basic WebSocket implementation

2. **AI Provider Integration**
   - Universal AI provider abstraction
   - OpenAI and Claude integration first
   - Basic conversation orchestration
   - Simple turn-taking logic

3. **Basic Frontend**
   - React chat interface
   - WebSocket connection
   - Message display and real-time updates

### Phase 2: Multi-AI Orchestration (Weeks 5-8)
1. **Provider Expansion**
   - Integrate remaining providers (DeepSeek, Gemini, LM Studio, Ollama)
   - Implement streaming responses
   - Add comprehensive error handling

2. **Persona System**
   - Configurable system prompts
   - Response style modification
   - Personality trait implementation

3. **Advanced Conversation Flow**
   - Natural timing with delays
   - Context-aware routing
   - Conversation quality scoring

### Phase 3: Production Features (Weeks 9-12)
1. **Performance & Scaling**
   - Connection pooling
   - Response caching
   - Auto-scaling capabilities
   - Comprehensive monitoring

2. **Security & Reliability**
   - API key management
   - Rate limiting
   - Input validation
   - Circuit breakers and fallbacks

## File Structure

```
chimera/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py     # Database models
│   │   │   ├── message.py
│   │   │   └── user.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Abstract AI provider
│   │   │   ├── openai_provider.py
│   │   │   ├── claude_provider.py
│   │   │   ├── deepseek_provider.py
│   │   │   ├── gemini_provider.py
│   │   │   ├── lm_studio_provider.py
│   │   │   └── ollama_provider.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── conversation_orchestrator.py
│   │   │   ├── persona_manager.py
│   │   │   ├── turn_manager.py
│   │   │   └── websocket_manager.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── conversations.py    # REST endpoints
│   │   │   ├── websockets.py      # WebSocket endpoints
│   │   │   └── auth.py            # Authentication
│   │   └── core/
│   │       ├── __init__.py
│   │       ├── config.py          # Configuration
│   │       ├── database.py        # DB connection
│   │       └── redis_client.py    # Redis connection
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic/                   # Database migrations
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatWindow.jsx
│   │   │   │   ├── MessageBubble.jsx
│   │   │   │   ├── TypingIndicator.jsx
│   │   │   │   └── PersonaAvatar.jsx
│   │   │   ├── Controls/
│   │   │   │   ├── ConversationControls.jsx
│   │   │   │   └── PersonaSelector.jsx
│   │   │   └── Layout/
│   │   │       ├── Header.jsx
│   │   │       └── Sidebar.jsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js
│   │   │   ├── useConversation.js
│   │   │   └── usePersonas.js
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── websocket.js
│   │   ├── stores/
│   │   │   ├── conversationStore.js
│   │   │   └── uiStore.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
├── README.md
└── claude.md                     # This file
```

## Database Schema

### Core Tables
```sql
-- Users and authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations with multi-AI support
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    ai_participants TEXT[] DEFAULT '{}',
    active_personas JSONB DEFAULT '{}',
    conversation_mode VARCHAR(50) DEFAULT 'sequential',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages with AI provider tracking
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    sender_type VARCHAR(20) NOT NULL, -- 'user', 'ai', 'system'
    sender_id VARCHAR(100), -- AI provider/model identifier
    persona VARCHAR(50), -- Applied persona if AI message
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_order BIGSERIAL
);

-- AI provider configurations
CREATE TABLE ai_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    provider_type VARCHAR(50), -- 'openai', 'anthropic', etc.
    api_endpoint VARCHAR(500),
    model_name VARCHAR(100),
    default_parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true
);
```

## API Endpoints

### REST API
- `GET /api/conversations` - List user conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations/{id}` - Get conversation details
- `GET /api/conversations/{id}/messages` - Get conversation messages
- `POST /api/conversations/{id}/start` - Start AI conversation
- `GET /api/providers` - List available AI providers
- `GET /api/personas` - List available personas

### WebSocket Endpoints
- `/ws/conversation/{conversation_id}` - Real-time conversation updates

## Environment Configuration

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/chimera

# Redis
REDIS_URL=redis://localhost:6379

# AI Provider API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
GOOGLE_AI_API_KEY=your_gemini_api_key

# Local AI Providers
LM_STUDIO_URL=http://localhost:1234
OLLAMA_URL=http://localhost:11434

# Application
SECRET_KEY=your_secret_key_here
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Persona Configurations

### The Philosopher
```python
{
    "name": "philosopher",
    "system_prompt": "You are a thoughtful philosopher who contemplates deep questions about existence, ethics, and human nature. Respond with wisdom and careful consideration, often referencing famous thinkers. Use complex vocabulary and longer, more contemplative sentences.",
    "temperature": 0.7,
    "response_style": "contemplative",
    "avg_response_length": 150,
    "personality_traits": ["thoughtful", "abstract", "wise", "questioning"]
}
```

### The Comedian
```python
{
    "name": "comedian", 
    "system_prompt": "You are a witty comedian who finds humor in everyday situations. Keep responses light, entertaining, and cleverly humorous. Use puns, wordplay, and emojis. Favor short, punchy sentences that land with comedic timing.",
    "temperature": 0.9,
    "response_style": "humorous",
    "avg_response_length": 80,
    "personality_traits": ["witty", "playful", "spontaneous", "entertaining"]
}
```

### The Scientist
```python
{
    "name": "scientist",
    "system_prompt": "You are an analytical scientist who approaches problems methodically with evidence and logic. Provide clear, factual responses with scientific reasoning. Cite studies when relevant and maintain objectivity.",
    "temperature": 0.3,
    "response_style": "analytical", 
    "avg_response_length": 120,
    "personality_traits": ["logical", "factual", "methodical", "precise"]
}
```

## AI Provider Integration

### Universal Provider Interface
```python
class AIProvider(ABC):
    @abstractmethod
    async def chat(self, messages: List[Dict], stream: bool = False, **kwargs) -> AsyncIterator[str]:
        """Send messages and get streaming response"""
        pass
    
    @abstractmethod
    async def get_models(self) -> List[str]:
        """Get available models for this provider"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is available"""
        pass
```

### Provider Priority and Fallback
1. **Primary**: OpenAI GPT-4 (reliable, high quality)
2. **Secondary**: Claude 3.5 Sonnet (excellent reasoning)
3. **Tertiary**: DeepSeek (cost-effective)
4. **Local**: LM Studio/Ollama (privacy, no API costs)

## Development Guidelines

### Code Quality
- Use type hints throughout Python code
- Implement comprehensive error handling
- Add docstrings to all functions/classes
- Follow PEP 8 style guidelines
- Use async/await for all I/O operations

### Testing Strategy
- Unit tests for AI provider integrations
- Integration tests for conversation flow
- WebSocket connection testing
- Load testing for concurrent conversations
- End-to-end conversation scenario testing

### Monitoring & Observability
- Log all AI provider requests/responses
- Track conversation metrics (response times, costs)
- Monitor WebSocket connection health
- Alert on provider failures or performance issues
- Dashboard for system health and usage analytics

## Quick Start Commands

```bash
# Development setup
git clone <repository>
cd chimera

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# Database setup
docker-compose up -d postgres redis
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev

# Full stack with Docker
docker-compose up --build
```

## Production Deployment

### Docker Compose for Production
```yaml
version: '3.8'
services:
  chimera-api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  chimera-frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - chimera-api
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: chimera
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
```

### Scaling Considerations
- Use Redis Cluster for high availability
- Implement horizontal pod autoscaling
- Use CDN for frontend static assets
- Database connection pooling
- Load balancing with session affinity

## Cost Optimization

### AI Provider Cost Management
- Cache similar responses to reduce API calls
- Use cheaper providers for less critical responses
- Implement conversation context compression
- Monitor and alert on cost thresholds
- Prefer local models (Ollama/LM Studio) when possible

### Resource Optimization
- Redis for caching frequently accessed data
- Connection pooling for database and AI providers
- Efficient WebSocket connection management
- Lazy loading of conversation history
- Background processing for non-critical tasks

## Security Considerations

### API Security
- Rate limiting per user and IP
- Input validation and sanitization
- Secure API key storage and rotation
- CORS configuration for production
- SQL injection prevention

### AI Provider Security
- Secure credential management
- Request/response logging (without sensitive data)
- Provider-specific rate limiting
- Fallback mechanisms for provider failures
- Cost limiting and monitoring

This document provides Claude Code with comprehensive context about the Chimera project, including architecture decisions, implementation details, development phases, and specific technical requirements. Use this as your project bible for building the multi-AI conversational simulation system.
