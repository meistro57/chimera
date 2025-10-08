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
from ..api.auth import get_current_user
import secrets

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
async def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    """List all conversations for the current user"""
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).all()

    return [
        {
            "id": conv.id,
            "user_id": conv.user_id,
            "title": conv.title or "Untitled Conversation",
            "participants": conv.ai_participants or [],
            "is_public": conv.is_public or False,
            "share_token": conv.share_token if conv.is_public else None,
            "created_at": conv.created_at.isoformat() + "Z" if conv.created_at else None,
            "updated_at": conv.updated_at.isoformat() + "Z" if conv.updated_at else None
        }
        for conv in conversations
    ]

@router.post("/conversations")
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Create a new conversation"""
    db_conversation = Conversation(
        id=str(uuid4()),
        user_id=current_user.id,
        title=conversation_data.title,
        ai_participants=conversation_data.participants,
        active_personas={}
    )

    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return {
        "id": db_conversation.id,
        "user_id": db_conversation.user_id,
        "title": db_conversation.title,
        "participants": db_conversation.ai_participants,
        "created_at": db_conversation.created_at.isoformat() if db_conversation.created_at else None,
        "updated_at": db_conversation.updated_at.isoformat() if db_conversation.updated_at else None
    }

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get conversation details"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title or "Untitled Conversation",
        "participants": conversation.ai_participants or [],
        "active_personas": conversation.active_personas or {},
        "conversation_mode": conversation.conversation_mode,
        "is_public": conversation.is_public or False,
        "share_token": conversation.share_token if conversation.is_public else None,
        "created_at": conversation.created_at.isoformat() + "Z" if conversation.created_at else None,
        "updated_at": conversation.updated_at.isoformat() + "Z" if conversation.updated_at else None
    }

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
    limit: int = 50,
    offset: int = 0
):
    """Get conversation messages"""
    # Verify user owns this conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages for this conversation
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.message_order).offset(offset).limit(limit).all()

    return [
        {
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "sender_type": msg.sender_type,
            "sender_id": msg.sender_id,
            "persona": msg.persona,
            "content": msg.content,
            "metadata": msg.metadata or {},
            "created_at": msg.created_at.isoformat() + "Z" if msg.created_at else None
        }
        for msg in messages
    ]

@router.post("/conversations/{conversation_id}/start")
async def start_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Start AI conversation"""
    # Verify user owns this conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    participants = conversation.ai_participants or ["philosopher", "comedian", "scientist"]

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
async def stop_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Stop AI conversation"""
    # Verify user owns this conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await orchestrator.stop_conversation(conversation_id)

    return {
        "status": "stopped",
        "conversation_id": conversation_id
    }

@router.post("/conversations/{conversation_id}/share")
async def share_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Toggle sharing status for a conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Toggle sharing status
    if conversation.is_public:
        # Make private
        conversation.is_public = False
        conversation.share_token = None
        status = "made_private"
    else:
        # Make public
        conversation.is_public = True
        conversation.share_token = secrets.token_urlsafe(16)  # Generate a secure token
        status = "made_public"

    db.commit()
    db.refresh(conversation)

    return {
        "status": status,
        "conversation_id": conversation_id,
        "is_public": conversation.is_public,
        "share_token": conversation.share_token
    }

@router.get("/public/conversations/{share_token}")
async def get_public_conversation(
    share_token: str,
    db: Session = Depends(get_database)
):
    """Get public conversation details by share token"""
    conversation = db.query(Conversation).filter(
        Conversation.share_token == share_token,
        Conversation.is_public == True
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Public conversation not found")

    # Get messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.message_order).all()

    return {
        "id": conversation.id,
        "title": conversation.title or "Untitled Conversation",
        "participants": conversation.ai_participants or [],
        "active_personas": conversation.active_personas or {},
        "conversation_mode": conversation.conversation_mode,
        "created_at": conversation.created_at.isoformat() + "Z" if conversation.created_at else None,
        "updated_at": conversation.updated_at.isoformat() + "Z" if conversation.updated_at else None,
        "messages": [
            {
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "sender_type": msg.sender_type,
                "sender_id": msg.sender_id,
                "persona": msg.persona,
                "content": msg.content,
                "metadata": msg.metadata or {},
                "created_at": msg.created_at.isoformat() + "Z" if msg.created_at else None
            }
            for msg in messages
        ]
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