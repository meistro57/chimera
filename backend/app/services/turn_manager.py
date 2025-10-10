import asyncio
import random
import json
from typing import List, Optional
from ..core.redis_client import redis_client

class TurnManager:
    def __init__(self):
        self.active_conversations = {}

    async def start_conversation(self, conversation_id: str, participants: List[str]):
        """Initialize a new conversation with AI participants"""
        self.active_conversations[conversation_id] = {
            "participants": participants,
            "current_turn": 0,
            "is_active": True,
            "last_speaker": None
        }

        # Store in Redis for persistence
        await redis_client.set(
            f"conversation:{conversation_id}:state",
            json.dumps({
                "participants": participants,
                "current_turn": 0,
                "is_active": True,
                "last_speaker": None
            }),
            ex=3600  # 1 hour expiry
        )

    async def get_next_speaker(self, conversation_id: str) -> Optional[str]:
        """Determine which AI should speak next"""
        conversation_state = await self._get_conversation_state(conversation_id)
        if not conversation_state or not conversation_state["is_active"]:
            return None

        participants = conversation_state["participants"]
        last_speaker = conversation_state.get("last_speaker")

        # Remove last speaker from next options to avoid immediate repetition
        available_speakers = [p for p in participants if p != last_speaker]

        if not available_speakers:
            available_speakers = participants

        # Add some randomness with weighted selection
        # Philosopher: 30%, Comedian: 40%, Scientist: 30%
        weights = {
            "philosopher": 0.3,
            "comedian": 0.4,
            "scientist": 0.3
        }

        # Calculate weighted random selection
        total_weight = sum(weights.get(speaker, 1.0) for speaker in available_speakers)
        r = random.random() * total_weight

        current_weight = 0
        for speaker in available_speakers:
            current_weight += weights.get(speaker, 1.0)
            if r <= current_weight:
                return speaker

        # Fallback to random selection
        return random.choice(available_speakers)

    async def update_last_speaker(self, conversation_id: str, speaker: str):
        """Update who spoke last in the conversation"""
        conversation_state = await self._get_conversation_state(conversation_id)
        if conversation_state:
            conversation_state["last_speaker"] = speaker
            conversation_state["current_turn"] += 1

            # Update local state
            if conversation_id in self.active_conversations:
                self.active_conversations[conversation_id] = conversation_state

            # Update Redis
            await redis_client.set(
                f"conversation:{conversation_id}:state",
                json.dumps(conversation_state),
                ex=3600
            )

    async def stop_conversation(self, conversation_id: str):
        """Stop an active conversation"""
        if conversation_id in self.active_conversations:
            self.active_conversations[conversation_id]["is_active"] = False

        # Update Redis
        conversation_state = await self._get_conversation_state(conversation_id)
        if conversation_state:
            conversation_state["is_active"] = False
            await redis_client.set(
                f"conversation:{conversation_id}:state",
                json.dumps(conversation_state),
                ex=3600
            )

    async def _get_conversation_state(self, conversation_id: str) -> Optional[dict]:
        """Get conversation state from local cache or Redis"""
        # Try local cache first
        if conversation_id in self.active_conversations:
            return self.active_conversations[conversation_id]

        # Try Redis
        state_str = await redis_client.get(f"conversation:{conversation_id}:state")
        if state_str:
            try:
                state = json.loads(state_str)
                self.active_conversations[conversation_id] = state
                return state
            except Exception:
                pass

        return None

    async def add_natural_delay(self, persona: str) -> float:
        """Add natural delay based on persona characteristics"""
        base_delays = {
            "philosopher": (3, 8),  # Longer pause for deep thinking
            "comedian": (1, 4),     # Quick wit
            "scientist": (2, 6)     # Methodical thinking
        }

        min_delay, max_delay = base_delays.get(persona, (2, 5))
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
        return delay