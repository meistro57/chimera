from typing import List, AsyncIterator
import httpx
import json
from .base import AIProvider, ChatMessage

class LMStudioProvider(AIProvider):
    def __init__(self, base_url: str = "http://localhost:1234", model: str = "local-model"):
        super().__init__(None, model)
        self.base_url = base_url.rstrip('/')
        self.headers = {"Content-Type": "application/json"}

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
            async with httpx.AsyncClient(timeout=60.0) as client:
                if stream:
                    async with client.stream(
                        "POST",
                        f"{self.base_url}/v1/chat/completions",
                        headers=self.headers,
                        json=payload
                    ) as response:
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
                    response = await client.post(
                        f"{self.base_url}/v1/chat/completions",
                        headers=self.headers,
                        json=payload
                    )
                    response_data = response.json()
                    yield response_data["choices"][0]["message"]["content"]

        except Exception as e:
            yield f"Error from LM Studio: {str(e)}"

    async def get_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/v1/models")
                models_data = response.json()
                return [model["id"] for model in models_data.get("data", [])]
        except Exception:
            return ["local-model"]

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/v1/models")
                return response.status_code == 200
        except Exception:
            return False