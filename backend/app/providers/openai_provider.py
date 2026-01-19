import asyncio
from typing import List, AsyncIterator

import openai

from .base import AIProvider, ChatMessage


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model)
        self._use_async_client = False
        try:
            self.client = openai.AsyncOpenAI(api_key=api_key)
            self._use_async_client = True
        except AttributeError:
            self.client = openai.OpenAI(api_key=api_key)

    async def chat(self, messages: List[ChatMessage], stream: bool = False, **kwargs) -> AsyncIterator[str]:
        formatted_messages = self.format_messages(messages)
        params = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1500),
        }

        try:
            if self._use_async_client:
                response = await self.client.chat.completions.create(stream=stream, **params)
                if stream:
                    async for chunk in response:
                        try:
                            if chunk.choices[0].delta.content:
                                yield chunk.choices[0].delta.content
                        except Exception:
                            continue
                else:
                    yield response.choices[0].message.content
            else:
                def _sync_call():
                    return self.client.chat.completions.create(stream=False, **params)

                response = await asyncio.to_thread(_sync_call)
                yield response.choices[0].message.content

        except Exception as e:
            yield f"Error from OpenAI: {str(e)}"

    async def get_models(self) -> List[str]:
        try:
            if self._use_async_client:
                models = await self.client.models.list()
            else:
                models = await asyncio.to_thread(self.client.models.list)
            return [model.id for model in models.data if "gpt" in model.id.lower()]
        except Exception:
            return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]

    async def health_check(self) -> bool:
        try:
            if self._use_async_client:
                await self.client.models.list()
            else:
                await asyncio.to_thread(self.client.models.list)
            return True
        except Exception:
            return False
