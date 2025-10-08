from sqlalchemy import Column, String, Boolean
from sqlalchemy.types import JSON
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class AIProvider(Base):
    __tablename__ = "ai_providers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    provider_type = Column(String(50))  # 'openai', 'anthropic', etc.
    api_endpoint = Column(String(500))
    model_name = Column(String(100))
    default_parameters = Column(JSON, default={})
    is_active = Column(Boolean, default=True)