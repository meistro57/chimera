from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class AIProvider(Base):
    __tablename__ = "ai_providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    provider_type = Column(String(50))  # 'openai', 'anthropic', etc.
    api_endpoint = Column(String(500))
    model_name = Column(String(100))
    default_parameters = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)