from abc import ABC, abstractmethod
from typing import List, Dict, AsyncIterator, Optional
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str

class AIProvider(ABC):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.provider_name = self.__class__.__name__.lower().replace('provider', '')

    @abstractmethod
    async def chat(self, messages: List[ChatMessage], stream: bool = False, **kwargs) -> AsyncIterator[str]:
        """Send messages and get streaming response"""
        pass

    @abstractmethod
    async def get_models(self) -> List[str]:
        """Get available models for this provider"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is available"""
        pass

    def format_messages(self, messages: List[ChatMessage]) -> List[Dict]:
        """Format messages for the specific provider"""
        return [{"role": msg.role, "content": msg.content} for msg in messages]