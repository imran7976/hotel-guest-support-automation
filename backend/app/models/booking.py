from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Date, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_reference = Column(String(50), unique=True, index=True, nullable=False)
    guest_id = Column(Integer, ForeignKey("guests.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    number_of_guests = Column(Integer, default=1, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="confirmed", index=True, nullable=False)  # confirmed, pending_modification, pending_cancellation, cancelled, completed
    special_requests = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    guest = relationship("Guest", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    conversations = relationship("Conversation", back_populates="booking")
    escalations = relationship("Escalation", back_populates="booking")

