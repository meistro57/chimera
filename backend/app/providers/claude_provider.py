from typing import List, AsyncIterator
import anthropic
from .base import AIProvider, ChatMessage

class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        super().__init__(api_key, model)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def chat(self, messages: List[ChatMessage], stream: bool = False, **kwargs) -> AsyncIterator[str]:
        formatted_messages = self.format_messages(messages)

        # Extract system message if present
        system_message = ""
        user_messages = []
        for msg in formatted_messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)

        try:
            if stream:
                async with self.client.messages.stream(
                    model=self.model,
                    max_tokens=kwargs.get('max_tokens', 1500),
                    temperature=kwargs.get('temperature', 0.7),
                    system=system_message if system_message else None,
                    messages=user_messages
                ) as stream:
                    async for text in stream.text_stream:
                        yield text
            else:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=kwargs.get('max_tokens', 1500),
                    temperature=kwargs.get('temperature', 0.7),
                    system=system_message if system_message else None,
                    messages=user_messages
                )
                yield response.content[0].text

        except Exception as e:
            yield f"Error from Claude: {str(e)}"

    async def get_models(self) -> List[str]:
        return [
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229"
        ]

    async def health_check(self) -> bool:
        try:
            await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False