from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "Chimera Multi-AI Chat"
    debug: bool = True
    secret_key: str = "your-secret-key-here"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/chimera"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # AI Provider API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    deepseek_api_key: str = ""
    google_ai_api_key: str = ""

    # Local AI Providers
    lm_studio_url: str = "http://localhost:1234"
    ollama_url: str = "http://localhost:11434"

    class Config:
        env_file = ".env"

settings = Settings()