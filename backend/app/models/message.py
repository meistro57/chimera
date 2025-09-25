from sqlalchemy import Column, String, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    sender_type = Column(String(20), nullable=False)  # 'user', 'ai', 'system'
    sender_id = Column(String(100))  # AI provider/model identifier
    persona = Column(String(50))  # Applied persona if AI message
    content = Column(Text, nullable=False)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    message_order = Column(BigInteger, autoincrement=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")