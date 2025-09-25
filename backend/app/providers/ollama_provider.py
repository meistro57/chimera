from typing import List, AsyncIterator
import httpx
import json
from .base import AIProvider, ChatMessage

class OllamaProvider(AIProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        super().__init__(None, model)
        self.base_url = base_url.rstrip('/')
        self.headers = {"Content-Type": "application/json"}

    async def chat(self, messages: List[ChatMessage], stream: bool = False, **kwargs) -> AsyncIterator[str]:
        formatted_messages = self.format_messages(messages)

        # Convert to Ollama format
        prompt = self._messages_to_prompt(formatted_messages)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": kwargs.get('temperature', 0.7),
                "num_predict": kwargs.get('max_tokens', 1500)
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                if stream:
                    async with client.stream(
                        "POST",
                        f"{self.base_url}/api/generate",
                        headers=self.headers,
                        json=payload
                    ) as response:
                        async for line in response.aiter_lines():
                            if line:
                                try:
                                    json_data = json.loads(line)
                                    if json_data.get("response"):
                                        yield json_data["response"]
                                    if json_data.get("done"):
                                        break
                                except json.JSONDecodeError:
                                    continue
                else:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        headers=self.headers,
                        json=payload
                    )
                    response_data = response.json()
                    yield response_data.get("response", "")

        except Exception as e:
            yield f"Error from Ollama: {str(e)}"

    def _messages_to_prompt(self, messages: List[dict]) -> str:
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"
        prompt += "Assistant: "
        return prompt

    async def get_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                models_data = response.json()
                return [model["name"] for model in models_data.get("models", [])]
        except Exception:
            return ["llama2", "mistral", "codellama"]

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False