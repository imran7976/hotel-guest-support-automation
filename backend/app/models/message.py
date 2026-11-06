from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    sender_type = Column(String(50), index=True, nullable=False)  # guest, ai, staff, system
    content = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    confidence = Column(Float, nullable=True)
    priority = Column(String(50), default="normal", nullable=False)  # low, normal, high, urgent
    requires_human = Column(Boolean, default=False, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

