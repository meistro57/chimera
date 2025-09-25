# Chimera Architecture Guide

Comprehensive overview of the Chimera Multi-AI Conversational Simulation system architecture.

## 🏗️ System Overview

Chimera is designed as a distributed, real-time system that orchestrates conversations between multiple AI providers playing distinct personas. The architecture emphasizes scalability, reliability, and extensibility.

### Core Principles

1. **Modularity**: Each component is independently deployable and testable
2. **Scalability**: Horizontal scaling supported at every layer
3. **Reliability**: Graceful degradation and fault tolerance
4. **Extensibility**: Easy addition of new AI providers and personas
5. **Real-time**: Sub-second message delivery and responsive interactions

## 📊 High-Level Architecture

```
                           ┌─────────────────┐
                           │   Load Balancer │
                           │    (Nginx)      │
                           └─────────┬───────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
          ┌─────────▼──────────┐              ┌──────▼──────────┐
          │  Frontend (React)  │              │  CDN (Static)   │
          │  - UI Components   │              │  - Assets       │
          │  - WebSocket Client│              │  - Images       │
          └─────────┬──────────┘              └─────────────────┘
                    │
                    │ WebSocket/HTTP
                    │
          ┌─────────▼──────────┐
          │  API Gateway       │
          │  - Rate Limiting   │
          │  - Authentication  │
          │  - Request Routing │
          └─────────┬──────────┘
                    │
      ┌─────────────┴─────────────┐
      │                           │
┌─────▼──────┐           ┌────────▼────────┐
│ REST API   │           │ WebSocket API   │
│ - FastAPI  │           │ - Real-time     │
│ - CRUD Ops │           │ - Broadcasting  │
└─────┬──────┘           └────────┬────────┘
      │                           │
      └─────────┬───────────────────┘
                │
      ┌─────────▼──────────┐
      │ Business Logic     │
      │ - Orchestrator     │
      │ - Persona Manager  │
      │ - Turn Manager     │
      └─────────┬──────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼────┐ ┌────▼────┐ ┌───▼────────┐
│Database│ │ Redis   │ │AI Providers│
│PostreSQL│ │Cache/Pub│ │- OpenAI    │
│        │ │Sub      │ │- Claude    │
└────────┘ └─────────┘ │- Local     │
                       └────────────┘
```

## 🔧 Component Architecture

### Frontend Layer

#### React Application Structure
```
frontend/src/
├── components/
│   ├── Chat/
│   │   ├── ChatWindow.tsx          # Main chat interface
│   │   ├── MessageBubble.tsx       # Individual message display
│   │   ├── TypingIndicator.tsx     # "AI is typing..." indicator
│   │   └── PersonaAvatar.tsx       # AI persona visual representation
│   ├── Controls/
│   │   ├── ConversationControls.tsx# Start/stop/pause controls
│   │   └── PersonaSelector.tsx     # Choose AI participants
│   └── Layout/
│       ├── Header.tsx              # App header
│       └── Sidebar.tsx             # Navigation and settings
├── hooks/
│   ├── useWebSocket.ts             # WebSocket connection management
│   ├── useConversation.ts          # Conversation state management
│   └── usePersonas.ts              # Persona configuration
├── services/
│   ├── api.ts                      # REST API client
│   └── websocket.ts                # WebSocket client
└── stores/
    ├── conversationStore.ts        # Global conversation state
    └── uiStore.ts                  # UI state management
```

**Key Design Decisions:**
- **TypeScript**: Full type safety for complex AI provider integrations
- **React Hooks**: Functional components for better performance
- **Real-time Updates**: WebSocket-first design for instant message delivery
- **State Management**: Zustand for lightweight, performant state management

### Backend Layer

#### API Server (FastAPI)

```
backend/app/
├── main.py                         # Application entry point
├── core/
│   ├── config.py                   # Configuration management
│   ├── database.py                 # Database connection
│   └── redis_client.py             # Redis connection
├── models/
│   ├── conversation.py             # Database models
│   ├── message.py
│   └── user.py
├── api/
│   ├── conversations.py            # REST endpoints
│   ├── websockets.py               # WebSocket endpoints
│   └── auth.py                     # Authentication
├── services/
│   ├── conversation_orchestrator.py# Core conversation logic
│   ├── persona_manager.py          # Persona configuration
│   ├── turn_manager.py             # Turn-taking logic
│   └── websocket_manager.py        # WebSocket connection management
└── providers/
    ├── base.py                     # Abstract AI provider
    ├── openai_provider.py          # OpenAI integration
    ├── claude_provider.py          # Anthropic Claude integration
    └── [other providers...]
```

#### Service Layer Architecture

##### Conversation Orchestrator
The core service that manages multi-AI conversations:

```python
class ConversationOrchestrator:
    def __init__(
        self,
        persona_manager: PersonaManager,
        turn_manager: TurnManager,
        ai_providers: Dict[str, AIProvider],
        websocket_manager: WebSocketManager
    ):
        self.persona_manager = persona_manager
        self.turn_manager = turn_manager
        self.providers = ai_providers
        self.websocket_manager = websocket_manager

    async def start_conversation(
        self,
        conversation_id: UUID,
        topic: str,
        participants: List[str]
    ) -> None:
        """Initialize and start a multi-AI conversation"""

        # 1. Load conversation state
        # 2. Initialize AI personas
        # 3. Generate opening message
        # 4. Start conversation loop

    async def generate_response(
        self,
        conversation_id: UUID,
        responding_persona: str,
        context: List[Message]
    ) -> Message:
        """Generate AI response for a specific persona"""

        # 1. Get persona configuration
        # 2. Select AI provider
        # 3. Build context with persona prompt
        # 4. Generate response with streaming
        # 5. Save and broadcast message
```

### AI Provider Layer

#### Abstract Provider Interface

```python
class AIProvider(ABC):
    """Abstract base class for all AI providers"""

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> AsyncIterator[str]:
        """Send chat messages and return streaming response"""
        pass

    @abstractmethod
    async def get_models(self) -> List[str]:
        """Get list of available models"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider availability"""
        pass
```

### Data Layer

#### Database Schema Design

```sql
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
```

#### Redis Data Structures

```python
class RedisDataStructures:
    """Optimized Redis usage for real-time features"""

    # WebSocket connection management
    WEBSOCKET_CONNECTIONS = "ws:connections:{conversation_id}"

    # Real-time messaging
    MESSAGE_STREAM = "messages:{conversation_id}"
    TYPING_INDICATORS = "typing:{conversation_id}"

    # Conversation state
    CONVERSATION_STATE = "state:{conversation_id}"
    TURN_QUEUE = "turns:{conversation_id}"

    # Performance caching
    PERSONA_CACHE = "personas:{persona_name}"
    PROVIDER_STATUS = "providers:status"

    # Rate limiting
    RATE_LIMIT = "ratelimit:{user_id}:{endpoint}"
```

## 🔄 Message Flow Architecture

### Real-time Message Processing

```
User Input → WebSocket → Message Queue → Conversation Orchestrator
     ↓              ↓            ↓              ↓
Database ← Message Store ← AI Provider ← Context Builder
     ↓              ↓            ↓              ↓
WebSocket Broadcast ← Response ← Generated ← Persona Manager
     ↓
All Connected Clients
```

### WebSocket Management

```python
class WebSocketManager:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.connections: Dict[str, Set[WebSocket]] = defaultdict(set)

    async def broadcast_message(
        self,
        conversation_id: str,
        message: Message
    ) -> None:
        """Broadcast message to all connected clients"""

        websocket_message = {
            "type": "message",
            "data": message.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Local connections
        for websocket in self.connections.get(conversation_id, set()):
            await websocket.send_json(websocket_message)

        # Distributed deployment - publish to Redis
        await self.redis.publish(
            f"broadcast:{conversation_id}",
            json.dumps(websocket_message)
        )
```

## 🚀 Scaling Architecture

### Horizontal Scaling Strategy

#### Application Tier Scaling
- Multiple API server instances behind load balancer
- Session affinity for WebSocket connections
- Shared state via Redis cluster

#### Database Scaling
- Read/write splitting with PostgreSQL replicas
- Connection pooling and query optimization
- Caching frequently accessed data

#### Performance Optimizations
- Multi-level caching (local → Redis → database)
- Connection pooling for databases and AI providers
- Asynchronous processing for non-blocking operations

## 🔒 Security Architecture

### Authentication & Authorization
- JWT-based session management
- Rate limiting per user and endpoint
- Input validation and sanitization
- Secure API key management

### AI Provider Security
- Encrypted API key storage
- Request/response logging (without sensitive data)
- Content filtering for AI safety
- Cost limiting and monitoring

## 📊 Monitoring & Observability

### Application Metrics
- Conversation and message counters
- Response time histograms
- Provider performance tracking
- Error rate monitoring

### Health Monitoring
- Database connectivity checks
- Redis cluster health
- AI provider availability
- WebSocket connection health

---

This architecture provides a robust, scalable foundation for multi-AI conversations while maintaining performance and reliability at scale.