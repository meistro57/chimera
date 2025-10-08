from typing import List, Dict, Any
from collections import defaultdict
import json

from ..providers.base import ChatMessage
from .persona_manager import PersonaManager

class ConversationMemory:
    """Service to enhance conversation context and memory"""

    def __init__(self):
        self.persona_manager = PersonaManager()
        self.memory_filters = {
            "philosopher": self._get_philosopher_memory,
            "comedian": self._get_comedian_memory,
            "scientist": self._get_scientist_memory
        }

    def enhance_context(self, messages: List[ChatMessage], current_persona: str) -> List[ChatMessage]:
        """
        Enhance conversation context with persona-specific memory cues

        Args:
            messages: Original conversation messages
            current_persona: The persona who will respond next

        Returns:
            Enhanced message list with memory cues
        """
        if not messages:
            return messages

        # Get memory filter for current persona
        memory_func = self.memory_filters.get(current_persona, self._default_memory)

        # Apply memory enhancement
        return memory_func(messages, current_persona)

    def _default_memory(self, messages: List[ChatMessage], current_persona: str) -> List[ChatMessage]:
        """Default memory processing - just adds some context"""
        # Always include the first starter message and recent messages
        if len(messages) > 10:
            # Keep the first message (starter) and last 9 messages
            enhanced = [messages[0]] + messages[-9:]
        else:
            enhanced = messages.copy()

        return enhanced

    def _get_philosopher_memory(self, messages: List[ChatMessage], current_persona: str) -> List[ChatMessage]:
        """Philosopher benefits from deep contextual memory and philosophical themes"""
        if len(messages) <= 5:
            return messages

        # Keep first message and more historical context for philosophical depth
        enhanced = [messages[0]]

        # Include messages that reference philosophical concepts or questions
        philosophical_keywords = [
            "meaning", "existence", "conscious", "free will", "morality", "ethics",
            "reality", "truth", "purpose", "human nature", "mind", "soul"
        ]

        relevant_messages = []
        for msg in messages[1:-4]:  # Middle messages, exclude very recent ones
            content_lower = msg.content.lower()
            if any(keyword in content_lower for keyword in philosophical_keywords):
                relevant_messages.append(msg)

        # Add most relevant historical messages plus recent conversation
        enhanced.extend(relevant_messages[-3:])  # Up to 3 relevant older messages
        enhanced.extend(messages[-6:])  # Last 6 messages for recent context

        # Deduplicate while preserving order
        seen = set()
        deduplicated = []
        for msg in enhanced:
            if msg.content not in seen:
                deduplicated.append(msg)
                seen.add(msg.content)

        return deduplicated[:12]  # Limit total context

    def _get_comedian_memory(self, messages: List[ChatMessage], current_persona: str) -> List[ChatMessage]:
        """Comedian focuses on recent humorous exchanges and setup opportunities"""
        if len(messages) < 3:
            return messages

        # Keep recent messages for comedic timing
        enhanced = messages[-8:]  # Last 8 messages for fresh humor

        # Always include the starter if it's funny or set up humor
        if messages and self._is_funny_setup(messages[0]):
            enhanced.insert(0, messages[0])

        return enhanced

    def _get_scientist_memory(self, messages: List[ChatMessage], current_persona: str) -> List[ChatMessage]:
        """Scientist needs factual context and logical progression"""
        if len(messages) <= 3:
            return messages

        enhanced = [messages[0]]  # Keep starter for context

        # Look for factual claims that might need correction or validation
        scientific_context = []
        for msg in messages[1:]:
            if self._contains_factual_claim(msg):
                scientific_context.append(msg)

        # Include up to 3 recent factual contexts
        enhanced.extend(scientific_context[-3:])
        # Include recent messages for current context
        enhanced.extend(messages[-4:])

        # Remove duplicates and limit context
        seen = set()
        deduplicated = []
        for msg in enhanced:
            if msg.content not in seen:
                deduplicated.append(msg)
                seen.add(msg.content)

        return deduplicated[:10]

    def _is_funny_setup(self, message: ChatMessage) -> bool:
        """Check if a message sets up humor well"""
        funny_indicators = [
            "joke", "funny", "laugh", "ridiculous", "absurd", "weird",
            "prefer", "instead", "rather", "kitchen appliance"
        ]
        content_lower = message.content.lower()
        return any(indicator in content_lower for indicator in funny_indicators)

    def _contains_factual_claim(self, message: ChatMessage) -> bool:
        """Check if message contains factual claims that scientist would engage with"""
        factual_indicators = [
            "research", "study", "evidence", "data", "fact", "prove",
            "scientifically", "according to", "study shows", "facts show"
        ]
        content_lower = message.content.lower()
        return any(indicator in content_lower for indicator in factual_indicators)