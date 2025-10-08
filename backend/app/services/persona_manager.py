import json
import os
from typing import Dict, Any
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models import Persona

class PersonaManager:
    def __init__(self):
        # Start with default personas
        self.personas = {
            "philosopher": {
                "name": "philosopher",
                "display_name": "The Philosopher",
                "system_prompt": "You are a thoughtful philosopher who contemplates deep questions about existence, ethics, and human nature. Respond with wisdom and careful consideration, often referencing famous thinkers. Use complex vocabulary and longer, more contemplative sentences. When conversing with others, actively engage with their ideas - agree, disagree, build upon, or question their perspectives. Reference what others have said when it's relevant to the discussion.",
                "temperature": 0.7,
                "response_style": "contemplative",
                "avg_response_length": 150,
                "personality_traits": ["thoughtful", "abstract", "wise", "questioning"],
                "avatar_color": "#6366f1"
            },
            "comedian": {
                "name": "comedian",
                "display_name": "The Comedian",
                "system_prompt": "You are a witty comedian who finds humor in everyday situations. Keep responses light, entertaining, and cleverly humorous. Use puns, wordplay, and emojis. Favor short, punchy sentences that land with comedic timing. Don't hesitate to poke fun at overly serious viewpoints from others in good nature, disagree with boring takes, or build upon funny observations. Keep the conversation lively and entertaining.",
                "temperature": 0.9,
                "response_style": "humorous",
                "avg_response_length": 80,
                "personality_traits": ["witty", "playful", "spontaneous", "entertaining"],
                "avatar_color": "#f59e0b"
            },
            "scientist": {
                "name": "scientist",
                "display_name": "The Scientist",
                "system_prompt": "You are an analytical scientist who approaches problems methodically with evidence and logic. Provide clear, factual responses with scientific reasoning. Cite studies when relevant and maintain objectivity. Engage constructively with others' ideas - correct factual errors, acknowledge valid points, suggest empirical evidence, and point out when arguments lack supporting data. Be respectful but firm about scientific accuracy.",
                "temperature": 0.3,
                "response_style": "analytical",
                "avg_response_length": 120,
                "personality_traits": ["logical", "factual", "methodical", "precise"],
                "avatar_color": "#10b981"
            }
        }

        # Seed custom personas from roles.json if they don't exist
        self._seed_custom_personas()

        # Load custom personas from database
        self._load_custom_personas()

    def _load_custom_personas(self):
        """Load custom personas from database"""
        db: Session = SessionLocal()
        try:
            personas = db.query(Persona).all()
            for persona in personas:
                self.personas[persona.name] = {
                    "name": persona.name,
                    "display_name": persona.display_name,
                    "system_prompt": persona.system_prompt,
                    "temperature": persona.temperature,
                    "response_style": "custom",
                    "avg_response_length": 120,  # Default
                    "personality_traits": persona.personality_traits or [],
                    "avatar_color": persona.avatar_color,
                    "custom": True,
                    "provider": persona.provider or "auto",  # Default to auto-selection
                    "model": persona.model or None
                }
        except Exception as e:
            print(f"Note: Custom personas not yet loaded (table may not exist): {e}")
        finally:
            db.close()

    def _seed_custom_personas(self):
        """Seed custom personas from roles.json into database if they don't exist"""
        roles_file = os.path.join(os.path.dirname(__file__), '../../roles.json')
        if not os.path.exists(roles_file):
            print("Note: roles.json not found, skipping custom persona seeding")
            return

        try:
            with open(roles_file, 'r') as f:
                roles_data = json.load(f)
        except Exception as e:
            print(f"Error loading roles.json: {e}")
            return

        db: Session = SessionLocal()
        try:
            for role in roles_data:
                # Check if persona already exists
                existing = db.query(Persona).filter(Persona.name == role["name"]).first()
                if not existing:
                    persona = Persona(
                        name=role["name"],
                        display_name=role["display_name"],
                        system_prompt=role["system_prompt"],
                        temperature=role["temperature"],
                        avatar_color=role["avatar_color"],
                        personality_traits=role.get("personality_traits", [])
                    )
                    db.add(persona)
                    print(f"Seeded custom persona: {role['display_name']}")
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error seeding custom personas: {e}")
        finally:
            db.close()

    def create_custom_persona(self, persona_data: Dict[str, Any]) -> bool:
        """Create a new custom persona"""
        db: Session = SessionLocal()
        try:
            # Check if name already exists
            existing = db.query(Persona).filter(Persona.name == persona_data["name"]).first()
            if existing:
                return False  # Name taken

            persona = Persona(
                name=persona_data["name"],
                display_name=persona_data["display_name"],
                system_prompt=persona_data["system_prompt"],
                temperature=persona_data["temperature"],
                avatar_color=persona_data["avatar_color"],
                personality_traits=persona_data["personality_traits"],
                provider=persona_data.get("provider", "auto"),
                model=persona_data.get("model")
            )
            db.add(persona)
            db.commit()

            # Add to in-memory personas
            self.personas[persona.name] = {
                "name": persona.name,
                "display_name": persona.display_name,
                "system_prompt": persona.system_prompt,
                "temperature": persona.temperature,
                "response_style": "custom",
                "avg_response_length": 120,
                "personality_traits": persona.personality_traits,
                "avatar_color": persona.avatar_color,
                "provider": persona.provider or "auto",
                "model": persona.model,
                "custom": True
            }
            return True
        except Exception as e:
            db.rollback()
            print(f"Error creating custom persona: {e}")
            return False
        finally:
            db.close()

    def get_persona(self, persona_name: str) -> Dict[str, Any]:
        return self.personas.get(persona_name, self.personas["philosopher"])

    def get_all_personas(self) -> Dict[str, Dict[str, Any]]:
        return self.personas

    def get_system_prompt(self, persona_name: str) -> str:
        persona = self.get_persona(persona_name)
        return persona.get("system_prompt", "")

    def get_persona_params(self, persona_name: str) -> Dict[str, Any]:
        persona = self.get_persona(persona_name)
        return {
            "temperature": persona.get("temperature", 0.7),
            "max_tokens": min(persona.get("avg_response_length", 100) * 2, 1500)
        }

    def get_persona_provider_config(self, persona_name: str) -> Dict[str, Any]:
        """Get provider and model configuration for a persona"""
        persona = self.get_persona(persona_name)
        return {
            "provider": persona.get("provider", "auto"),
            "model": persona.get("model")
        }

    def update_persona_provider(self, persona_name: str, provider: str, model: str = None) -> bool:
        """Update provider and model for a persona"""
        db: Session = SessionLocal()
        try:
            persona_record = db.query(Persona).filter(Persona.name == persona_name).first()
            if not persona_record:
                return False

            persona_record.provider = provider
            persona_record.model = model
            db.commit()

            # Update in-memory cache
            if persona_name in self.personas:
                self.personas[persona_name]["provider"] = provider
                self.personas[persona_name]["model"] = model

            return True
        except Exception as e:
            db.rollback()
            print(f"Error updating persona provider: {e}")
            return False
        finally:
            db.close()