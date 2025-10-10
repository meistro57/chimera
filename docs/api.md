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

## Authentication

### User Registration

**Endpoint:** `POST /api/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": "uuid-string",
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2025-10-08T13:28:07.123456"
}
```

### User Login

**Endpoint:** `POST /api/auth/token`

Authenticate user and receive JWT token for API access.

**Request Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Request Body (Form):**
```
username=johndoe&password=securepassword123
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Get User Profile

**Endpoint:** `GET /api/auth/me`

Get current user information (requires authentication token).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "uuid-string",
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2025-10-08T13:28:07.123456"
}
```

### User Logout

**Endpoint:** `POST /api/auth/logout`

Log out user (primarily client-side token removal).

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

## Conversations

### `GET /api/conversations`

List all conversations for the current user.

**Authentication:** Required (JWT Bearer token)
**Headers:**
```
Authorization: Bearer <access_token>
```

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
        "type": "openai",
        "healthy": true,
        "models": ["gpt-4", "gpt-3.5-turbo"]
      },
      {
        "name": "claude",
        "type": "claude",
        "healthy": true,
        "models": ["claude-3-sonnet", "claude-3-haiku"]
      }
    ]
  }
}
```

### `POST /api/providers/config`

Configure API keys for AI providers.

**Authentication:** Optional (works in demo mode)

**Request Body:**
```json
{
  "provider": "openrouter",
  "api_key": "sk-or-v1-..."
}
```

**Response:**
```json
{
  "message": "API key configured for openrouter"
}
```

### `POST /api/providers/test`

Test an AI provider's API key and connectivity.

**Authentication:** Optional (works in demo mode)

**Request Body:**
```json
{
  "provider": "openrouter"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "API key is working correctly",
  "provider": "openrouter",
  "response_sample": "OK"
}
```

**Response (Error):**
```json
{
  "status": "failed",
  "message": "API test failed: Invalid API key",
  "provider": "openrouter"
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
- `401 Unauthorized` - Authentication required or invalid credentials
- `403 Forbidden` - Insufficient permissions for the requested action
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists (e.g., duplicate username)
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Authentication Error Details

- `401 Unauthorized`: Missing or invalid JWT token
- `409 Conflict`: Username or email already registered
- `403 Forbidden`: Accessing another user's resources

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

### `PUT /api/personas/{persona_name}/provider`

Configure which AI provider and model a persona should use. Set to "auto" for automatic selection.

**Authentication:** Optional (works in demo mode)

**Path Parameters:**
- `persona_name`: Name of the persona (e.g., "philosopher")

**Request Body:**
```json
{
  "provider": "openrouter",
  "model": "openai/gpt-4"
}
```

Or set to auto-selection:
```json
{
  "provider": "auto"
}
```

**Response:**
```json
{
  "message": "Updated provider configuration for philosopher"
}
```

## Conversation Management

### `POST /api/conversations/`

Start a new AI conversation. (See conversations.md for details)

### WebSocket Endpoints

WebSocket connections for real-time conversation streaming at: `ws://localhost:8000/ws/conversation/{conversation_id}`

## Cache Management

### Cache Statistics

**Endpoint:** `GET /api/cache/stats`

Get current cache performance statistics and Redis information.

**Authentication:** Optional (admin-level access recommended)

**Response:**
```json
{
  "cache_stats": {
    "cache_size": 47,
    "keyspace_info": {...},
    "cache_enabled": true,
    "cache_hit_rate": "tracked_via_logs"
  },
  "ttl_seconds": 3600
}
```

### Cache Clearing

**Endpoint:** `POST /api/cache/clear`

Clear all cached responses (admin function - use carefully).

**Authentication:** Required (admin-level access)

**Response:**
```json
{
  "message": "Cache invalidated for all personas"
}
```

### Cache Performance Test

**Endpoint:** `POST /api/cache/test`

Test cache performance by triggering a sample AI response (sometimes cached, sometimes fresh).

**Authentication:** Optional

**Response:**
```json
{
  "test_type": "cache_hit",
  "provider": "openai",
  "cache_check_ms": 2.45,
  "total_time_ms": 8.76,
  "from_cache": true,
  "response": "The sum of 2 and 2 is 4."
}
```

## Rate Limits

Default rate limits:
- **API Requests**: 1000 requests per hour per user
- **WebSocket Connections**: 10 concurrent connections per user
- **Messages**: 100 messages per conversation per hour
- **Persona Creation**: 10 custom personas per user

---

For more detailed examples and advanced usage, see the complete API documentation at `/docs` when running the application.