import asyncio
import json
import random
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models import Conversation, Message
from ..providers.base import ChatMessage
from ..providers import OpenAIProvider, ClaudeProvider, DeepSeekProvider, GeminiProvider, LMStudioProvider, OllamaProvider
from ..core.config import settings
from .persona_manager import PersonaManager
from .turn_manager import TurnManager
from .websocket_manager import WebSocketManager, get_websocket_manager

class ConversationOrchestrator:
    def __init__(self, websocket_manager: Optional[WebSocketManager] = None):
        self.persona_manager = PersonaManager()
        self.turn_manager = TurnManager()
        self.websocket_manager = websocket_manager or get_websocket_manager()
        self.providers = self._initialize_providers()

    def _initialize_providers(self) -> Dict[str, Any]:
        """Initialize all available AI providers"""
        providers = {}

        # OpenAI
        if settings.openai_api_key:
            providers["openai"] = OpenAIProvider(settings.openai_api_key, "gpt-3.5-turbo")

        # Claude
        if settings.anthropic_api_key:
            providers["claude"] = ClaudeProvider(settings.anthropic_api_key, "claude-3-haiku-20240307")

        # DeepSeek
        if settings.deepseek_api_key:
            providers["deepseek"] = DeepSeekProvider(settings.deepseek_api_key)

        # Gemini
        if settings.google_ai_api_key:
            providers["gemini"] = GeminiProvider(settings.google_ai_api_key)

        # Local providers (always available if endpoints are up)
        providers["lm_studio"] = LMStudioProvider(settings.lm_studio_url)
        providers["ollama"] = OllamaProvider(settings.ollama_url)

        # Provider to persona mapping for intelligent selection
        self.provider_persona_assignment = {
            "philosopher": ["openai", "claude", "deepseek"],  # Prefer OpenAI for deep thinking
            "comedian": ["claude", "openai", "deepseek"],     # Claude for humor
            "scientist": ["openai", "deepseek", "claude"],    # DeepSeek for logic
        }

        return providers

    async def start_conversation(self, conversation_id: str, participants: List[str]) -> bool:
        """Start an AI conversation with specified participants"""
        try:
            # Initialize turn management
            await self.turn_manager.start_conversation(conversation_id, participants)

            # Send initial message to kick off the conversation
            await self._send_initial_message(conversation_id)

            # Start the conversation loop
            asyncio.create_task(self._conversation_loop(conversation_id))

            return True
        except Exception as e:
            print(f"Error starting conversation: {e}")
            return False

    async def _send_initial_message(self, conversation_id: str):
        """Send an initial message to start the conversation"""
        initial_message = {
            "type": "system",
            "content": "Welcome to the AI conversation! The participants will now begin discussing.",
            "sender": "system",
            "timestamp": asyncio.get_event_loop().time()
        }

        await self.websocket_manager.broadcast_to_conversation(
            conversation_id,
            initial_message
        )

    async def _conversation_loop(self, conversation_id: str):
        """Main conversation loop where AIs take turns speaking"""
        try:
            for turn in range(20):  # Limit to 20 turns for now
                # Get next speaker
                next_speaker = await self.turn_manager.get_next_speaker(conversation_id)
                if not next_speaker:
                    break

                # Add natural delay and typing indicator
                await self._show_typing_indicator(conversation_id, next_speaker)
                delay = await self.turn_manager.add_natural_delay(next_speaker)

                # Generate response
                response = await self._generate_response(conversation_id, next_speaker)
                if not response:
                    continue

                # Save and broadcast message
                await self._save_and_broadcast_message(conversation_id, next_speaker, response)

                # Update turn state
                await self.turn_manager.update_last_speaker(conversation_id, next_speaker)

                # Add pause between messages
                await asyncio.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"Error in conversation loop: {e}")

    async def _show_typing_indicator(self, conversation_id: str, speaker: str):
        """Show typing indicator for the current speaker"""
        persona = self.persona_manager.get_persona(speaker)
        typing_message = {
            "type": "typing",
            "persona": speaker,
            "persona_name": persona["display_name"],
            "content": f"{persona['display_name']} is typing...",
            "timestamp": asyncio.get_event_loop().time()
        }

        await self.websocket_manager.broadcast_to_conversation(
            conversation_id,
            typing_message
        )

    async def _generate_response(self, conversation_id: str, persona: str) -> Optional[str]:
        """Generate a response from the specified persona"""
        try:
            # Get conversation history
            messages = await self._get_conversation_history(conversation_id)

            # Add persona system prompt
            system_prompt = self.persona_manager.get_system_prompt(persona)
            if system_prompt:
                messages.insert(0, ChatMessage(role="system", content=system_prompt))

            # Get provider for this persona
            provider = await self._select_provider_for_persona(persona)
            if not provider:
                return "I'm having trouble connecting to my AI brain right now! 🤖"

            # Generate response with persona parameters
            persona_params = self.persona_manager.get_persona_params(persona)

            response_text = ""
            async for chunk in provider.chat(messages, stream=True, **persona_params):
                response_text += chunk

            return response_text.strip()

        except Exception as e:
            print(f"Error generating response for {persona}: {e}")
            return None

    async def _get_conversation_history(self, conversation_id: str) -> List[ChatMessage]:
        """Get recent conversation history"""
        db: Session = SessionLocal()
        try:
            # Query recent messages for this conversation (last 20 for context)
            messages_query = db.query(Message).filter(
                Message.conversation_id == uuid.UUID(conversation_id)
            ).order_by(Message.created_at).limit(20).all()

            conversation_messages = []
            for msg in messages_query:
                role = "user" if msg.sender_type == "user" else "assistant"
                conversation_messages.append(ChatMessage(role=role, content=msg.content))

            # If no history, start with a random conversation starter
            if not conversation_messages:
                starters = [
                    "Let's have an interesting conversation about technology and its impact on society.",
                    "What are your thoughts on artificial intelligence and its future?",
                    "How do you think creativity will evolve with AI assistance?",
                    "What's the most important philosophical question of our time?",
                    "Can you discuss the balance between privacy and security in the digital age?",
                    "What makes a joke truly funny, from a philosophical standpoint?",
                    "How should society approach the ethical development of AI?"
                ]
                starter = ChatMessage(role="user", content=random.choice(starters))
                conversation_messages.append(starter)

            return conversation_messages

        finally:
            db.close()

    async def _select_provider_for_persona(self, persona: str):
        """Select the best available AI provider for the given persona"""
        # Get preferred providers for this persona
        preferred = self.provider_persona_assignment.get(persona, list(self.providers.keys()))

        # Try preferred providers first
        for provider_name in preferred:
            if provider_name in self.providers:
                provider = self.providers[provider_name]
                if await provider.health_check():
                    return provider

        # Fallback to any available provider
        for name, provider in self.providers.items():
            if await provider.health_check():
                return provider

        return None

    async def _save_and_broadcast_message(self, conversation_id: str, persona: str, content: str):
        """Save message to database and broadcast to websocket clients"""
        # Create message object
        persona_info = self.persona_manager.get_persona(persona)
        message = {
            "type": "message",
            "id": f"msg_{asyncio.get_event_loop().time()}",
            "conversation_id": conversation_id,
            "sender_type": "ai",
            "sender_id": persona,
            "persona": persona,
            "persona_name": persona_info["display_name"],
            "avatar_color": persona_info["avatar_color"],
            "content": content,
            "timestamp": asyncio.get_event_loop().time()
        }

        # Save to database
        await self._save_message_to_database(message)

        # Broadcast to websocket clients
        await self.websocket_manager.broadcast_to_conversation(conversation_id, message)

    async def _save_message_to_database(self, message_dict: Dict[str, Any]):
        """Save message to database"""
        from datetime import datetime
        import uuid

        # Create a database session
        db: Session = SessionLocal()

        try:
            # Create Message instance
            db_message = Message(
                id=uuid.uuid4(),
                conversation_id=uuid.UUID(message_dict["conversation_id"]),
                sender_type=message_dict["sender_type"],
                sender_id=message_dict.get("sender_id", ""),
                persona=message_dict.get("persona", ""),
                content=message_dict["content"],
                metadata={
                    "persona_name": message_dict.get("persona_name", ""),
                    "avatar_color": message_dict.get("avatar_color", ""),
                    "timestamp": message_dict["timestamp"]
                },
                created_at=datetime.fromtimestamp(message_dict["timestamp"])
            )

            db.add(db_message)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error saving message to database: {e}")
        finally:
            db.close()

    async def stop_conversation(self, conversation_id: str):
        """Stop an active conversation"""
        await self.turn_manager.stop_conversation(conversation_id)