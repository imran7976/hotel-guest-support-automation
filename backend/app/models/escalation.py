from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    guest_id = Column(Integer, ForeignKey("guests.id", ondelete="CASCADE"), index=True, nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True)
    inquiry_text = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    priority = Column(String(50), default="normal", index=True, nullable=False)  # low, normal, high, urgent
    status = Column(String(50), default="pending", index=True, nullable=False)  # pending, assigned, in_progress, resolved
    escalation_reason = Column(String(255), nullable=False)
    staff_response = Column(Text, nullable=True)
    assigned_staff_id = Column(Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="escalations")
    guest = relationship("Guest", back_populates="escalations")
    booking = relationship("Booking", back_populates="escalations")
    assigned_staff = relationship("AdminUser")

