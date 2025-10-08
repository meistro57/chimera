# Chimera API Reference

Complete documentation for the Chimera Multi-AI Conversational Simulation API.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Response Format

All API responses follow this standard format:

```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Responses

Standard error format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

## Health Check

### `GET /health`

Basic health check for the API and its dependencies.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 3600
  }
}
```

### `GET /health/providers`

Check AI provider connectivity and status.

**Response:**
```json
{
  "success": true,
  "data": {
    "providers": {
      "openai": {
        "status": "healthy",
        "models": ["gpt-4", "gpt-3.5-turbo"],
        "response_time_ms": 150
      },
      "claude": {
        "status": "healthy",
        "models": ["claude-3-sonnet", "claude-3-haiku"],
        "response_time_ms": 200
      }
    }
  }
}
```

## Conversations

### `GET /api/conversations`

List all conversations for the current user.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `status` (optional): Filter by status (`active`, `completed`, `archived`)

**Response:**
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Philosophy vs Science Debate",
        "participants": ["philosopher", "scientist", "comedian"],
        "status": "active",
        "message_count": 25,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_items": 45
    }
  }
}
```

### `POST /api/conversations`

Create a new conversation.

**Request Body:**
```json
{
  "title": "The Great AI Debate",
  "participants": ["philosopher", "scientist", "comedian"],
  "topic": "The ethics of artificial intelligence"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "conversation": {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "The Great AI Debate",
      "participants": ["philosopher", "scientist", "comedian"],
      "status": "created",
      "created_at": "2024-01-15T11:00:00Z"
    }
  }
}
```

### `GET /api/conversations/{conversation_id}`

Get detailed information about a specific conversation.

### `GET /api/conversations/{conversation_id}/messages`

Get messages for a conversation.

**Query Parameters:**
- `page` (optional): Page number
- `limit` (optional): Messages per page (max 200)
- `since` (optional): ISO timestamp to get messages after

### `POST /api/conversations/{conversation_id}/start`

Start an AI conversation with an optional topic.

**Request Body:**
```json
{
  "topic": "The future of human-AI collaboration",
  "initial_speaker": "philosopher"
}
```

## Personas

### `GET /api/personas`

Get all available AI personas.

**Response:**
```json
{
  "success": true,
  "data": {
    "personas": [
      {
        "name": "philosopher",
        "display_name": "The Philosopher",
        "description": "A contemplative thinker who ponders deep questions about existence, ethics, and human nature.",
        "personality_traits": ["thoughtful", "abstract", "wise", "questioning"],
        "emoji": "🧠",
        "sample_messages": [
          "But what does it truly mean to exist?",
          "Perhaps we should examine this from first principles..."
        ]
      }
    ]
  }
}
```

## AI Providers

### `GET /api/providers`

Get all available AI providers and their status.

**Response:**
```json
{
  "success": true,
  "data": {
    "providers": [
      {
        "name": "openai",
        "display_name": "OpenAI",
        "status": "active",
        "available_models": [
          {
            "name": "gpt-4",
            "display_name": "GPT-4",
            "context_length": 8192,
            "cost_per_1k_tokens": 0.03
          }
        ]
      }
    ]
  }
}
```

## WebSocket API

Real-time conversation updates via WebSocket.

### Connection
Connect to: `/ws/conversation/{conversation_id}`

### Message Types

**New Message:**
```json
{
  "type": "message",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440020",
    "persona": "philosopher",
    "content": "The nature of consciousness remains one of philosophy's greatest mysteries...",
    "created_at": "2024-01-15T11:15:00Z"
  }
}
```

**Typing Indicator:**
```json
{
  "type": "typing",
  "data": {
    "persona": "scientist",
    "is_typing": true,
    "estimated_response_time_ms": 2000
  }
}
```

## Error Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Persona Management

Tools for managing AI personas in conversations.

### `GET /api/personas/`

Retrieve all available personas including defaults and custom ones.

**Response:**
```json
{
  "success": true,
  "data": {
    "default": [
      {
        "name": "philosopher",
        "display_name": "The Philosopher",
        "avatar_color": "#6366f1",
        "personality_traits": ["thoughtful", "abstract", "wise"],
        "system_prompt": "..."
      }
    ],
    "custom": [
      {
        "name": "awakening_mind",
        "display_name": "The Awakening Mind",
        "avatar_color": "#8b5cf6",
        "personality_traits": ["spiritual", "wisdom", "cosmic"],
        "system_prompt": "..."
      }
    ]
  }
}
```

### `POST /api/personas/create`

Create a new custom persona.

**Request Body:**
```json
{
  "name": "your_persona_name",
  "display_name": "Your Persona Display Name",
  "system_prompt": "Describe the persona's personality and behavior...",
  "temperature": 0.7,
  "avatar_color": "#6366f1",
  "personality_traits": ["trait1", "trait2", "trait3"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Persona created successfully",
    "persona": {
      "name": "your_persona_name",
      "display_name": "Your Persona Display Name",
      "system_prompt": "Description...",
      "temperature": 0.7,
      "avatar_color": "#6366f1",
      "personality_traits": ["trait1", "trait2", "trait3"]
    }
  }
}
```

**Validation Rules:**
- `name`: Required, alphanumeric + hyphens/underscores only, unique
- `display_name`: Required, user-friendly name
- `system_prompt`: Required, describes persona behavior
- `temperature`: Required, 0.0-2.0 range
- `avatar_color`: Required, hex color code
- `personality_traits`: Optional array of tags

## Conversation Management

### `POST /api/conversations/`

Start a new AI conversation. (See conversations.md for details)

### WebSocket Endpoints

WebSocket connections for real-time conversation streaming at: `ws://localhost:8000/ws/conversation/{conversation_id}`

## Rate Limits

Default rate limits:
- **API Requests**: 1000 requests per hour per user
- **WebSocket Connections**: 10 concurrent connections per user
- **Messages**: 100 messages per conversation per hour
- **Persona Creation**: 10 custom personas per user

---

For more detailed examples and advanced usage, see the complete API documentation at `/docs` when running the application.