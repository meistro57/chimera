from pydantic import BaseModel, Field
from typing import List
import os

class Settings(BaseModel):
    # Application
    app_name: str = "Chimera Multi-AI Chat"
    debug: bool = True
    demo_mode: bool = Field(default_factory=lambda: os.getenv("CHIMERA_DEMO_MODE", "false").lower() == "true")
    secret_key: str = "your-secret-key-here"
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./chimera.db")

    # Redis
    redis_url: str = "redis://localhost:6379"

    # AI Provider API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    deepseek_api_key: str = ""
    google_ai_api_key: str = ""
    openrouter_api_key: str = ""

    # Local AI Providers
    lm_studio_url: str = "http://localhost:1234"
    ollama_url: str = "http://localhost:11434"

settings = Settings()