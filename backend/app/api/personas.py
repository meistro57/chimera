from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.services.persona_manager import PersonaManager
from app.core.logging_config import conversation_logger

router = APIRouter(prefix="/personas", tags=["personas"])

persona_manager = PersonaManager()

@router.get("/", response_model=Dict[str, List[Dict[str, Any]]])
async def get_personas():
    """Get all available personas (default + custom)"""
    personas = persona_manager.get_all_personas()
    # Separate default and custom
    default_personas = {k: v for k, v in personas.items() if "custom" not in v}
    custom_personas = {k: v for k, v in personas.items() if "custom" in v}
    return {"default": list(default_personas.values()), "custom": list(custom_personas.values())}

@router.post("/create")
async def create_persona(persona_data: Dict[str, Any]):
    """Create a new custom persona"""
    required_fields = ["name", "display_name", "system_prompt", "temperature", "avatar_color", "personality_traits"]

    # Validate required fields
    for field in required_fields:
        if field not in persona_data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

    # Validate name (alphanumeric, hyphens, underscores)
    if not persona_data["name"].replace("_", "").replace("-", "").isalnum():
        raise HTTPException(status_code=400, detail="Persona name must contain only letters, numbers, hyphens, and underscores")

    # Validate temperature (0-2)
    if not 0 <= persona_data["temperature"] <= 2:
        raise HTTPException(status_code=400, detail="Temperature must be between 0 and 2")

    # Create persona
    success = persona_manager.create_custom_persona(persona_data)

    if not success:
        raise HTTPException(status_code=409, detail="Persona name already exists")

    # Log the persona creation
    conversation_logger.log_event("system", "persona_created", {
        "name": persona_data["name"],
        "display_name": persona_data["display_name"],
        "personality_traits": persona_data["personality_traits"]
    })

    return {"message": "Persona created successfully", "persona": persona_data}