from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from uuid import uuid4
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
    db: Session = Depends(get_database),
    current_user: Optional[User] = Depends(get_current_user)  # Optional for demo
):
    """Get conversation details"""
    # Allow access to demo conversation without authentication
    if conversation_id == "demo-conversation":
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            # Create a demo conversation if it doesn't exist
            conversation = Conversation(
                id="demo-conversation",
                is_public=True,  # Make it public
                title="Demo AI Conversation",
                ai_participants=["philosopher", "comedian", "scientist"],
                active_personas={}
            )
            db.add(conversation)
            db.commit()
        return {
            "id": conversation.id,
            "title": conversation.title or "Untitled Conversation",
            "participants": conversation.ai_participants or [],
            "active_personas": conversation.active_personas or {},
            "conversation_mode": conversation.conversation_mode,
            "is_public": conversation.is_public or False,
            "created_at": conversation.created_at.isoformat() + "Z" if conversation.created_at else None,
            "updated_at": conversation.updated_at.isoformat() + "Z" if conversation.updated_at else None
        }

    # For non-demo conversations, require authentication
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

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
    db: Session = Depends(get_database),
    current_user: Optional[User] = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """Get conversation messages"""
    # Allow access to demo conversation without authentication
    if conversation_id == "demo-conversation":
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            # Recreate if missing
            conversation = Conversation(
                id="demo-conversation",
                is_public=True,
                title="Demo AI Conversation",
                ai_participants=["philosopher", "comedian", "scientist"],
                active_personas={}
            )
            db.add(conversation)
            db.commit()
    else:
        # For non-demo conversations, require authentication
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

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
    db: Session = Depends(get_database),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Start AI conversation"""
    # Allow demo conversation to be started without authentication
    if conversation_id == "demo-conversation":
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            # Recreate if missing
            conversation = Conversation(
                id="demo-conversation",
                is_public=True,
                title="Demo AI Conversation",
                ai_participants=["philosopher", "comedian", "scientist"],
                active_personas={}
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        participants = conversation.ai_participants or ["philosopher", "comedian", "scientist"]
        print(f"DEBUG: Starting demo conversation with participants: {participants}")
        success = await orchestrator.start_conversation(conversation_id, participants)
        if success:
            return {
                "status": "started",
                "conversation_id": conversation_id,
                "participants": participants
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to start conversation")

    # For non-demo conversations, require authentication
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

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
    """List available AI providers with their status"""
    providers = []

    # List of all possible providers, regardless of configuration
    all_provider_names = ["openai", "claude", "deepseek", "gemini", "openrouter"]

    for name in all_provider_names:
        # Check if provider is configured in orchestrator
        if name in orchestrator.providers:
            provider = orchestrator.providers[name]
            try:
                is_healthy = await provider.health_check()
                models = await provider.get_models()
                models_list = models[:3] if models else []
            except Exception:
                is_healthy = False
                models_list = []
        else:
            # Provider not configured
            is_healthy = False
            models_list = []

        providers.append({
            "name": name,
            "type": name,
            "healthy": is_healthy,
            "models": models_list,
            "configured": name in orchestrator.providers
        })

    return providers

@router.get("/personas")
async def list_personas():
    """List available personas with provider config"""
    personas = persona_manager.get_all_personas()
    return {
        name: {
            "name": persona["name"],
            "display_name": persona["display_name"],
            "avatar_color": persona["avatar_color"],
            "personality_traits": persona["personality_traits"],
            "provider": persona.get("provider", "auto"),
            "model": persona.get("model")
        }
        for name, persona in personas.items()
    }

@router.put("/personas/{persona_name}/provider")
async def update_persona_provider(persona_name: str, provider_config: Dict[str, Any]):
    """Update provider and model configuration for a persona"""
    provider = provider_config.get("provider")
    model = provider_config.get("model")

    if not provider:
        raise HTTPException(status_code=400, detail="Provider is required")

    success = persona_manager.update_persona_provider(persona_name, provider, model)
    if not success:
        raise HTTPException(status_code=404, detail="Persona not found or update failed")

    return {"message": f"Updated provider configuration for {persona_name}"}

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

@router.post("/providers/config")
async def update_provider_config(provider_config: Dict[str, Any], db: Session = Depends(get_database)):
    """Update provider configuration (API keys, etc.)"""
    provider_name = provider_config.get("provider")
    api_key = provider_config.get("api_key")

    if not provider_name or not api_key:
        raise HTTPException(status_code=400, detail="Provider name and API key required")

    # Store in environment variable
    import os
    env_var = f"{provider_name.upper()}_API_KEY"
    os.environ[env_var] = api_key

    # Reload the orchestrator providers to pick up the new API key
    await orchestrator.reload_providers()

    return {"message": f"API key configured for {provider_name}"}

@router.post("/providers/test")
async def test_provider(request_data: Dict[str, str]):
    """Test a specific provider to ensure API key is working"""
    provider_name = request_data.get("provider")
    if not provider_name:
        raise HTTPException(status_code=400, detail="Provider name required")

    if provider_name not in orchestrator.providers:
        raise HTTPException(status_code=404, detail=f"Provider {provider_name} not configured")

    provider = orchestrator.providers[provider_name]

    try:
        # Perform a basic health check
        healthy = await provider.health_check()
        if not healthy:
            return {"status": "failed", "message": "Provider health check failed"}

        # Try a simple chat completion to verify the key works
        test_messages = [
            ChatMessage(role="user", content="Hello, please respond with just 'OK' if you can read this.")
        ]

        # Get response (limit to short response)
        response_text = ""
        async for chunk in provider.chat(test_messages, stream=False, max_tokens=10):
            response_text += chunk

        response_text = response_text.strip()

        # Check if we got a reasonable response
        if len(response_text) > 0 and "ok" in response_text.lower():
            return {
                "status": "success",
                "message": "API key is working correctly",
                "provider": provider_name,
                "response_sample": response_text[:50] + "..." if len(response_text) > 50 else response_text
            }
        else:
            return {
                "status": "warning",
                "message": "Got response but it may not be optimal",
                "provider": provider_name,
                "response_sample": response_text[:100] + "..." if len(response_text) > 100 else response_text
            }

    except Exception as e:
        return {
            "status": "failed",
            "message": f"API test failed: {str(e)}",
            "provider": provider_name
        }

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

@router.get("/debug/env")
async def debug_environment():
    """Debug endpoint to check environment variables"""
    return {
        "demo_mode": settings.demo_mode,
        "environment_vars": {
            "openrouter": bool(os.environ.get("OPENROUTER_API_KEY")),
            "openai": bool(os.environ.get("OPENAI_API_KEY")),
            "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "deepseek": bool(os.environ.get("DEEPSEEK_API_KEY")),
            "google": bool(os.environ.get("GOOGLE_AI_API_KEY")),
            "chimera_demo": os.environ.get("CHIMERA_DEMO_MODE")
        },
        "api_keys": {
            "openai": bool(settings.openai_api_key),
            "anthropic": bool(settings.anthropic_api_key),
            "deepseek": bool(settings.deepseek_api_key),
            "google": bool(settings.google_ai_api_key),
            "openrouter": bool(settings.openrouter_api_key)
        },
        "providers_count": len(orchestrator.providers),
        "provider_names": list(orchestrator.providers.keys())
    }