from typing import List, Dict, Any
from collections import defaultdict
import json
from datetime import datetime
import uuid

from ..providers.base import ChatMessage
from .persona_manager import PersonaManager
from ..core.config import settings

# Add vector memory imports
import chromadb
from chromadb.config import Settings
from openai import OpenAI

class ConversationMemory:
    """Service to enhance conversation context and memory with vector search"""

    def __init__(self):
        self.persona_manager = PersonaManager()
        # Initialize vector DB - use new ChromaDB API
        import chromadb
        self.client_chroma = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client_chroma.get_or_create_collection(name="conversation_memory")
        
        # OpenAI for embeddings
        self.client_openai = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        if not self.client_openai:
            print("Warning: No OpenAI API key set, vector memory disabled")
        
    def get_embedding(self, text: str):
        """Get OpenAI embedding for text"""
        if not self.client_openai:
            return [0.0] * 1536  # Return zero vector as fallback
        try:
            response = self.client_openai.embeddings.create(
                input=[text],
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            return [0.0] * 1536

    def enhance_context(self, messages: List[ChatMessage], current_persona: str) -> List[ChatMessage]:
        """
        Enhance conversation context with persona-specific memory cues including vector search
        
        Args:
            messages: Original conversation messages
            current_persona: The persona who will respond next
        
        Returns:
            Enhanced message list with memory cues
        """
        if not messages:
            return messages
        
        # Get keyword-based memory enhancement
        keyword_enhanced = self._get_keyword_memory(messages, current_persona)
        
        # Add vector-based memory
        vector_enhanced = self._add_vector_memory(keyword_enhanced, current_persona)
        
        return vector_enhanced

    def _add_vector_memory(self, messages: List[ChatMessage], current_persona: str) -> List[ChatMessage]:
        """Add vector-based memory enhancements (placeholder for now)"""
        # For now, just return messages unchanged since vector memory requires API keys
        return messages
        
    def store_message(self, message: Dict[str, Any], conversation_id: str):
        """Store a message in the vector database for memory"""
        content = message.get('content', '')
        if not content:
            return
            
        embedding = self.get_embedding(content)
        metadata = {
            'persona': message.get('persona_name', message.get('sender', 'unknown')),
            'conversation_id': conversation_id,
            'timestamp': message.get('timestamp', datetime.now().isoformat())
        }
        
        self.collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
            ids=[f"{conversation_id}_{message.get('id', str(uuid.uuid4()))}"]
        )

    def _default_memory(self, messages: List[ChatMessage], current_persona: str) -> List[ChatMessage]:
        """Default memory processing - just adds some context"""
        # Always include the first starter message and recent messages
        if len(messages) > 10:
            # Keep the first message (starter) and last 9 messages
            enhanced = [messages[0]] + messages[-9:]
        else:
            enhanced = messages.copy()

        return enhanced

    def _get_keyword_memory(self, messages: List[ChatMessage], current_persona: str) -> List[ChatMessage]:
        """Route to persona-specific memory processing"""
        if current_persona == "philosopher":
            return self._get_philosopher_memory(messages, current_persona)
        elif current_persona == "comedian":
            return self._get_comedian_memory(messages, current_persona)
        elif current_persona == "scientist":
            return self._get_scientist_memory(messages, current_persona)
        else:
            return self._default_memory(messages, current_persona)

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