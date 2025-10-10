from typing import List, Dict, AsyncIterator, Optional
import asyncio
import random
from .base import AIProvider, ChatMessage

class DemoProvider(AIProvider):
    """Simple demo provider that returns pre-written responses for testing without API keys"""

    def __init__(self, model: Optional[str] = None):
        super().__init__(api_key="demo", model="demo")
        self.provider_name = "demo"
        self.responses = {
            "philosopher": [
                "What a profound question. Let us consider the nature of existence itself. Throughout the ages, great thinkers like Socrates and Descartes have pondered similar conundrums...",
                "The essence of consciousness lies at the intersection of being and perception. As Heidegger might argue, our very existence is defined by our questioning of it.",
                "Ah, the eternal struggle between determinism and free will. This touches upon the fundamental paradox of human agency in a universe of physical laws."
            ],
            "comedian": [
                "Haha, you just hit the cosmic joke button! 😂 Why did the philosopher go to the party? To ponder the meaning of 'party'!",
                "Oh man, that's a philosophical crisis waiting to happen! Let me lighten it up with some existential humor... Did you hear about the optimistic mathematician?",
                "Whoa, deep thoughts incoming! Quick, somebody pass the snacks before we get too serious! 🍿"
            ],
            "scientist": [
                "Based on empirical evidence and current scientific understanding, this phenomenon can be explained through the lens of quantum mechanics and evolutionary biology...",
                "Let me break this down systematically. From a scientific perspective, we've observed patterns that suggest causal relationships between these variables.",
                "According to well-documented studies and observational data, this represents an interesting intersection of natural selection and environmental adaptation."
            ]
        }

    async def chat(self, messages: List[ChatMessage], stream: bool = False, **kwargs) -> AsyncIterator[str]:
        """Generate a demo response"""
        # Get persona from kwargs or default to random
        persona = kwargs.get("persona", random.choice(list(self.responses.keys())))

        # Get a random response for this persona
        responses = self.responses.get(persona, self.responses["philosopher"])
        response = random.choice(responses)

        if stream:
            # Simulate streaming by yielding chunks
            words = response.split()
            for word in words:
                yield word + " "
                await asyncio.sleep(0.05)  # Small delay to simulate streaming
        else:
            yield response

    async def get_models(self) -> List[str]:
        """Return demo models"""
        return ["demo-philosopher", "demo-comedian", "demo-scientist"]

    async def health_check(self) -> bool:
        """Demo provider is always healthy"""
        return True