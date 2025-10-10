from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from datetime import datetime
from ..core.database import Base

class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    display_name = Column(String(100))
    system_prompt = Column(String(2000))
    temperature = Column(Float, default=0.7)
    avatar_color = Column(String(20))
    personality_traits = Column(JSON)  # List of strings
    provider = Column(String(50), default="auto")  # AI provider (openai, anthropic, etc.)
    model = Column(String(100), nullable=True)  # Specific model for the provider
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)