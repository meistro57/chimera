from typing import List, AsyncIterator
import httpx
import json
from .base import AIProvider, ChatMessage

class DeepSeekProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        super().__init__(api_key, model)
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat(self, messages: List[ChatMessage], stream: bool = False, **kwargs) -> AsyncIterator[str]:
        formatted_messages = self.format_messages(messages)

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": stream,
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 1500)
        }

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                ) as response:
                    if stream:
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]
                                if data.strip() == "[DONE]":
                                    break
                                try:
                                    json_data = json.loads(data)
                                    if json_data.get("choices", [{}])[0].get("delta", {}).get("content"):
                                        yield json_data["choices"][0]["delta"]["content"]
                                except json.JSONDecodeError:
                                    continue
                    else:
                        response_data = await response.json()
                        yield response_data["choices"][0]["message"]["content"]

        except Exception as e:
            yield f"Error from DeepSeek: {str(e)}"

    async def get_models(self) -> List[str]:
        return ["deepseek-chat", "deepseek-coder"]

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception:
            return False