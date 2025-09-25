from typing import List, AsyncIterator
import google.generativeai as genai
from .base import AIProvider, ChatMessage

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        super().__init__(api_key, model)
        genai.configure(api_key=api_key)
        self.model_instance = genai.GenerativeModel(model)

    async def chat(self, messages: List[ChatMessage], stream: bool = False, **kwargs) -> AsyncIterator[str]:
        # Convert messages to Gemini format
        conversation_history = []
        current_content = ""

        for msg in messages:
            if msg.role == "system":
                current_content = f"System: {msg.content}\n"
            elif msg.role == "user":
                current_content += f"User: {msg.content}"
                conversation_history.append(current_content)
                current_content = ""
            elif msg.role == "assistant":
                current_content += f"Assistant: {msg.content}\n"

        try:
            if stream:
                response = await self.model_instance.generate_content_async(
                    conversation_history[-1] if conversation_history else current_content,
                    stream=True,
                    generation_config={
                        "temperature": kwargs.get('temperature', 0.7),
                        "max_output_tokens": kwargs.get('max_tokens', 1500)
                    }
                )
                async for chunk in response:
                    if chunk.text:
                        yield chunk.text
            else:
                response = await self.model_instance.generate_content_async(
                    conversation_history[-1] if conversation_history else current_content,
                    generation_config={
                        "temperature": kwargs.get('temperature', 0.7),
                        "max_output_tokens": kwargs.get('max_tokens', 1500)
                    }
                )
                yield response.text

        except Exception as e:
            yield f"Error from Gemini: {str(e)}"

    async def get_models(self) -> List[str]:
        return ["gemini-pro", "gemini-pro-vision"]

    async def health_check(self) -> bool:
        try:
            response = await self.model_instance.generate_content_async("test")
            return bool(response.text)
        except Exception:
            return False