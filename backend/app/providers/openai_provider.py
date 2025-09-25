from typing import List, AsyncIterator
import openai
from .base import AIProvider, ChatMessage

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model)
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def chat(self, messages: List[ChatMessage], stream: bool = False, **kwargs) -> AsyncIterator[str]:
        formatted_messages = self.format_messages(messages)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                stream=stream,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1500)
            )

            if stream:
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content

        except Exception as e:
            yield f"Error from OpenAI: {str(e)}"

    async def get_models(self) -> List[str]:
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data if 'gpt' in model.id.lower()]
        except Exception:
            return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]

    async def health_check(self) -> bool:
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False