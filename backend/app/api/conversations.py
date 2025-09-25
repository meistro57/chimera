from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from ..core.database import get_database
from ..models import Conversation, Message, User
from ..services.conversation_orchestrator import ConversationOrchestrator
from ..services.persona_manager import PersonaManager

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