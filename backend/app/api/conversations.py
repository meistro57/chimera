from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from ..core.database import get_database
from ..models import Conversation, Message, User
from ..services.conversation_orchestrator import ConversationOrchestrator
from ..services.persona_manager import PersonaManager
from ..services.response_cache import response_cache
from ..providers.base import ChatMessage

router = APIRouter()

# Global instances
orchestrator = ConversationOrchestrator()
persona_manager = PersonaManager()

class ConversationCreate(BaseModel):
    title: str = "AI Conversation"
    participants: List[str] = ["philosopher", "comedian", "scientist"]

class ConversationResponse(BaseModel):
    id: str
    title: str
    participants: List[str]
    created_at: str

@router.get("/conversations")
async def list_conversations(db: Session = Depends(get_database)):
    """List all conversations (simplified for MVP)"""
    # For MVP, return mock data
    return [
        {
            "id": "demo-conversation",
            "title": "AI Philosophy Discussion",
            "participants": ["philosopher", "comedian", "scientist"],
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]

@router.post("/conversations")
async def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_database)
):
    """Create a new conversation"""
    # For MVP, return a simple response
    conversation_id = f"conv_{__import__('time').time()}"

    return {
        "id": conversation_id,
        "title": conversation_data.title,
        "participants": conversation_data.participants,
        "created_at": __import__('datetime').datetime.utcnow().isoformat() + "Z"
    }

@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, db: Session = Depends(get_database)):
    """Get conversation details"""
    if conversation_id == "demo-conversation":
        return {
            "id": "demo-conversation",
            "title": "AI Philosophy Discussion",
            "participants": ["philosopher", "comedian", "scientist"],
            "created_at": "2024-01-01T00:00:00Z"
        }

    raise HTTPException(status_code=404, detail="Conversation not found")

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    db: Session = Depends(get_database)
):
    """Get conversation messages"""
    # For MVP, return empty list
    return []

@router.post("/conversations/{conversation_id}/start")
async def start_conversation(conversation_id: str):
    """Start AI conversation"""
    participants = ["philosopher", "comedian", "scientist"]

    success = await orchestrator.start_conversation(conversation_id, participants)

    if success:
        return {
            "status": "started",
            "conversation_id": conversation_id,
            "participants": participants
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to start conversation")

@router.post("/conversations/{conversation_id}/stop")
async def stop_conversation(conversation_id: str):
    """Stop AI conversation"""
    await orchestrator.stop_conversation(conversation_id)

    return {
        "status": "stopped",
        "conversation_id": conversation_id
    }

@router.get("/providers")
async def list_providers():
    """List available AI providers"""
    providers = []

    # Check provider health
    for name, provider in orchestrator.providers.items():
        try:
            is_healthy = await provider.health_check()
            models = await provider.get_models()
        except Exception:
            is_healthy = False
            models = []

        providers.append({
            "name": name,
            "type": provider.provider_name,
            "healthy": is_healthy,
            "models": models[:3]  # Limit to first 3 models
        })

    return providers

@router.get("/personas")
async def list_personas():
    """List available personas"""
    personas = persona_manager.get_all_personas()
    return {
        name: {
            "name": persona["name"],
            "display_name": persona["display_name"],
            "avatar_color": persona["avatar_color"],
            "personality_traits": persona["personality_traits"]
        }
        for name, persona in personas.items()
    }

@router.get("/cache/stats")
async def get_cache_stats():
    """Get response cache statistics"""
    stats = await response_cache.get_cache_stats()
    return {
        "cache_stats": stats,
        "ttl_seconds": response_cache.cache_ttl
    }

@router.post("/cache/clear")
async def clear_cache():
    """Clear all cached responses (admin function)"""
    # In a production environment, you might want to add authentication here
    # For MVP, we'll allow clearing cache (could use Redis FLUSHDB if needed)

    # For now, we'll just invalidate by persona clearing
    # In future, we could implement full cache clearing
    for persona in ["philosopher", "scientist", "comedian"]:
        await response_cache.invalidate_persona_cache(persona)

    return {"message": "Cache invalidated for all personas"}

@router.post("/cache/test")
async def test_cache_performance():
    """Test cache performance with sample conversation"""
    import time

    test_conversation_id = "cache_test_conversation"
    test_messages = [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="What is 2+2?")
    ]

    test_persona_params = {"temperature": 0.7, "max_tokens": 100}

    if not orchestrator.providers:
        return {"error": "No AI providers configured"}

    # Pick first available provider
    test_provider = list(orchestrator.providers.values())[0]

    # Test cache miss (fresh response)
    start_time = time.time()
    cached_response = await response_cache.get_cached_response(
        test_provider.provider_name, test_messages, test_persona_params
    )
    cache_check_time = time.time()

    # Generate fresh response
    if not cached_response:
        fresh_response = ""
        async for chunk in test_provider.chat(test_messages, stream=False, **test_persona_params):
            fresh_response += chunk
        fresh_response = fresh_response.strip()

        # Cache it
        await response_cache.cache_response(
            test_provider.provider_name, test_messages, test_persona_params, fresh_response
        )

        return {
            "test_type": "cache_miss",
            "provider": test_provider.provider_name,
            "cache_check_ms": round((cache_check_time - start_time) * 1000, 2),
            "response_time_ms": round((time.time() - cache_check_time) * 1000, 2),
            "total_time_ms": round((time.time() - start_time) * 1000, 2),
            "from_cache": False,
            "response": fresh_response[:200] + "..." if len(fresh_response) > 200 else fresh_response
        }
    else:
        return {
            "test_type": "cache_hit",
            "provider": test_provider.provider_name,
            "cache_check_ms": round((cache_check_time - start_time) * 1000, 2),
            "total_time_ms": round((time.time() - start_time) * 1000, 2),
            "from_cache": True,
            "response": cached_response[:200] + "..." if len(cached_response) > 200 else cached_response
        }