import asyncio
import json
import random
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models import Conversation, Message
from ..providers.base import ChatMessage
from ..providers import OpenAIProvider, ClaudeProvider, DeepSeekProvider, GeminiProvider, LMStudioProvider, OllamaProvider, OpenRouterProvider, DemoProvider
from ..core.config import settings
from .persona_manager import PersonaManager
from .turn_manager import TurnManager
from .websocket_manager import WebSocketManager, get_websocket_manager
from .conversation_starter import ConversationStarter
from .conversation_memory import ConversationMemory
from .topic_analyzer import TopicAnalyzer
from .response_cache import response_cache
from ..core.logging_config import conversation_logger

class ConversationOrchestrator:
    def __init__(self, websocket_manager: Optional[WebSocketManager] = None):
        self.persona_manager = PersonaManager()
        self.turn_manager = TurnManager()
        self.conversation_starter = ConversationStarter()
        self.conversation_memory = ConversationMemory()
        self.topic_analyzer = TopicAnalyzer()
        self.websocket_manager = websocket_manager or get_websocket_manager()
        self.providers = self._initialize_providers()

    def _initialize_providers(self, fresh_settings=None) -> Dict[str, Any]:
        """Initialize all available AI providers"""
        if fresh_settings:
            active_settings = fresh_settings
        else:
            active_settings = settings
        
        providers = {}

        # OpenAI
        if active_settings.openai_api_key:
            providers["openai"] = OpenAIProvider(active_settings.openai_api_key, "gpt-3.5-turbo")

        # Claude
        if active_settings.anthropic_api_key:
            providers["claude"] = ClaudeProvider(active_settings.anthropic_api_key, "claude-3-haiku-20240307")

        # DeepSeek
        if active_settings.deepseek_api_key:
            providers["deepseek"] = DeepSeekProvider(active_settings.deepseek_api_key)

        # Gemini
        if active_settings.google_ai_api_key:
            providers["gemini"] = GeminiProvider(active_settings.google_ai_api_key)

        # OpenRouter
        if active_settings.openrouter_api_key:
            providers["openrouter"] = OpenRouterProvider(active_settings.openrouter_api_key, "openai/gpt-3.5-turbo")

        # Local providers (always available if endpoints are up)
        providers["lm_studio"] = LMStudioProvider(settings.lm_studio_url)
        providers["ollama"] = OllamaProvider(settings.ollama_url)

        # Demo provider (always available for testing without API keys)
        providers["demo"] = DemoProvider()

        # Provider to persona mapping for intelligent selection
        self.provider_persona_assignment = {
            "philosopher": ["openai", "claude", "deepseek", "openrouter", "demo"],  # Prefer OpenAI for deep thinking, then OpenRouter
            "comedian": ["claude", "openai", "deepseek", "openrouter", "demo"],     # Claude for humor
            "scientist": ["openai", "deepseek", "claude", "openrouter", "demo"],    # DeepSeek for logic
        }

        return providers

    async def get_participants(self, conversation_id: str) -> List[str]:
        """Get participants for a conversation"""
        state = await self.turn_manager._get_conversation_state(conversation_id)
        return state.get("participants", []) if state else []

    async def start_conversation(self, conversation_id: str, participants: List[str]) -> bool:
        """Start an AI conversation with specified participants"""
        try:
            print(f"DEBUG: start_conversation called with conversation_id={conversation_id}, participants={participants}")

            # Initialize turn management
            await self.turn_manager.start_conversation(conversation_id, participants)

            # Start logging this conversation
            conversation_logger.start_conversation_log(conversation_id, participants)

            # Log conversation start event
            conversation_logger.log_event(conversation_id, "conversation_start", {
                "participants": participants,
                "participant_count": len(participants)
            })

            # Send initial message to kick off the conversation
            await self._send_initial_message(conversation_id)

            # Start the conversation loop
            asyncio.create_task(self._conversation_loop(conversation_id))

            print(f"DEBUG: Conversation started successfully for {conversation_id}")
            return True
        except Exception as e:
            conversation_logger.log_event(conversation_id, "error", {"error": str(e), "context": "conversation_start"})
            print(f"DEBUG: Error starting conversation: {e}")
            return False

    async def _send_initial_message(self, conversation_id: str):
        """Send an initial message to start the conversation"""
        initial_message = {
            "type": "system",
            "content": "Welcome to the AI conversation! The participants will now begin discussing.",
            "sender": "system",
            "timestamp": asyncio.get_event_loop().time()
        }

        # Log the system message
        conversation_logger.log_message(conversation_id, initial_message)

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

                # Check for topic shift and route conversation if needed
                await self._check_topic_routing(conversation_id, turn + 1)

                # Add pause between messages
                await asyncio.sleep(random.uniform(1, 3))

        except Exception as e:
            conversation_logger.log_event(conversation_id, "error", {"error": str(e), "context": "conversation_loop"})
            print(f"Error in conversation loop: {e}")

        # Conversation ended
        conversation_logger.log_event(conversation_id, "conversation_end", {
            "total_turns": turn + 1,
            "reason": "conversation_loop_completed"
        })

        # Finalize logging
        conversation_logger.end_conversation_log(conversation_id)

    async def _check_topic_routing(self, conversation_id: str, turn_count: int):
        """Check if conversation should shift topics and inject new starter if needed"""
        try:
            # Get recent messages for analysis
            db: Session = SessionLocal()
            try:
                recent_messages_query = db.query(Message).filter(
                    Message.conversation_id == uuid.UUID(conversation_id)
                ).order_by(Message.created_at.desc()).limit(10).all()

                recent_contents = [msg.content for msg in reversed(recent_messages_query)][:10]

                # Analyze current topics
                topic_scores = self.topic_analyzer.analyze_conversation_topics(recent_contents)

                # Get participants
                participants = await self.get_participants(conversation_id)

                # Check for topic shift suggestion
                shift_topic = self.topic_analyzer.suggest_topic_shift(topic_scores, participants, turn_count)

                if shift_topic:
                    # Generate follow-up topic starter
                    new_starter = self.topic_analyzer.get_topic_based_follow_up(shift_topic, participants)

                    # Create routing message
                    routing_message = {
                        "type": "system",
                        "content": f"The conversation naturally evolves to a new topic: {new_starter}",
                        "sender": "system",
                        "timestamp": asyncio.get_event_loop().time()
                    }

                    # Log the routing event
                    conversation_logger.log_event(conversation_id, "topic_shift", {
                        "new_topic": new_starter,
                        "routing_message": routing_message["content"]
                    })

                    # Save and broadcast routing message
                    await self._save_message_to_database(routing_message)
                    await self.websocket_manager.broadcast_to_conversation(conversation_id, routing_message)

                    # Log the routing message itself
                    conversation_logger.log_message(conversation_id, routing_message)

                    # Add brief pause for routing
                    await asyncio.sleep(2)

            finally:
                db.close()

        except Exception as e:
            print(f"Error in topic routing: {e}")

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
            participants = await self.get_participants(conversation_id)
            messages = await self._get_conversation_history(conversation_id, participants)

            # Enhance context with persona-specific memory
            enhanced_messages = self.conversation_memory.enhance_context(messages, persona)

            # Add persona system prompt
            system_prompt = self.persona_manager.get_system_prompt(persona)
            if system_prompt:
                enhanced_messages.insert(0, ChatMessage(role="system", content=system_prompt))

            # Get provider for this persona
            provider = await self._select_provider_for_persona(persona)
            if not provider:
                return "I'm having trouble connecting to my AI brain right now! 🤖"

            # Get persona parameters
            persona_params = self.persona_manager.get_persona_params(persona)

            # Override model if manually configured for this persona
            persona_provider_config = self.persona_manager.get_persona_provider_config(persona)
            if persona_provider_config.get("model"):
                # Override the model parameter if manually configured
                persona_params["model"] = persona_provider_config["model"]
                print(f"DEBUG: Overriding model to {persona_provider_config['model']} for persona {persona}")

            # Check for cached response first
            cached_response = await response_cache.get_cached_response(
                provider.provider_name, enhanced_messages, persona_params
            )

            if cached_response:
                # Log cache hit
                conversation_logger.log_event(conversation_id, "cache_hit", {
                    "persona": persona,
                    "provider": provider.provider_name
                })
                return cached_response

            # Generate new response with persona parameters
            response_text = ""
            async for chunk in provider.chat(enhanced_messages, stream=True, **persona_params):
                response_text += chunk

            response_text = response_text.strip()

            # Cache the response for future use
            if response_text:
                await response_cache.cache_response(
                    provider.provider_name, enhanced_messages, persona_params, response_text
                )

                # Log cache storage
                conversation_logger.log_event(conversation_id, "cache_store", {
                    "persona": persona,
                    "provider": provider.provider_name,
                    "response_length": len(response_text)
                })

            return response_text

        except Exception as e:
            print(f"Error generating response for {persona}: {e}")
            return None

    async def _get_conversation_history(self, conversation_id: str, participants: List[str]) -> List[ChatMessage]:
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

            # If no history, start with a smart conversation starter
            if not conversation_messages:
                starter_content = self.conversation_starter.get_random_starter(participants)
                starter = ChatMessage(role="user", content=starter_content)
                conversation_messages.append(starter)

            return conversation_messages

        finally:
            db.close()

    async def _select_provider_for_persona(self, persona: str):
        """Select the best available AI provider for the given persona"""
        print(f"DEBUG: Selecting provider for persona {persona}")

        # First, check if persona has manual provider configuration
        persona_config = self.persona_manager.get_persona_provider_config(persona)
        print(f"DEBUG: Persona config: {persona_config}")

        if persona_config.get("provider") and persona_config["provider"] != "auto":
            manual_provider = persona_config["provider"]
            manual_model = persona_config.get("model")

            # Check if the manually configured provider is available and healthy
            if manual_provider in self.providers:
                provider = self.providers[manual_provider]
                if await provider.health_check():
                    print(f"DEBUG: Using manually configured provider {manual_provider} for persona {persona}")
                    # Set the model if specified, otherwise use provider's default
                    if manual_model:
                        provider.model = manual_model
                        print(f"DEBUG: Using manually configured model {manual_model} for persona {persona}")
                    return provider
                else:
                    print(f"DEBUG: Manually configured provider {manual_provider} is not healthy")

        # Auto-selection fallbacks (only if manual provider is not healthy or set to "auto")
        print(f"DEBUG: Falling back to auto-selection for persona {persona}")

        # Try preferred providers first (excluding demo if real providers are available)
        preferred_providers = self.provider_persona_assignment.get(persona, list(self.providers.keys()))
        for provider_name in preferred_providers:
            if provider_name != "demo" and provider_name in self.providers:
                provider = self.providers[provider_name]
                if await provider.health_check():
                    print(f"DEBUG: Selected preferred provider {provider_name} for persona {persona}")
                    return provider

        # If no preferred providers, try any real provider
        for name, provider in self.providers.items():
            if name != "demo":  # Skip demo provider if possible
                if await provider.health_check():
                    print(f"DEBUG: Selected fallback provider {name} for persona {persona}")
                    return provider

        # Last resort: use demo provider
        demo_provider = self.providers.get("demo")
        if demo_provider and await demo_provider.health_check():
            print(f"DEBUG: Using demo provider for persona {persona}")
            return demo_provider

        print(f"DEBUG: No provider available for persona {persona}")
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

        # Log the message
        conversation_logger.log_message(conversation_id, message)

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
                extra_metadata={
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

    async def reload_providers(self):
        """Reload providers to pick up new API keys"""
        print("DEBUG: Reloading providers")
        # Create fresh settings object to get updated environment variables
        from ..core.config import Settings
        fresh_settings = Settings()
        self.providers = self._initialize_providers(fresh_settings)
        print(f"DEBUG: Reloaded providers: {list(self.providers.keys())}")

    async def stop_conversation(self, conversation_id: str):
        """Stop an active conversation"""
        await self.turn_manager.stop_conversation(conversation_id)

        # Log conversation end if we were logging
        conversation_logger.log_event(conversation_id, "conversation_end", {
            "reason": "manual_stop"
        })
        conversation_logger.end_conversation_log(conversation_id)