from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_number = Column(String(20), unique=True, index=True, nullable=False)
    room_type = Column(String(100), index=True, nullable=False)
    price_per_night = Column(Numeric(10, 2), nullable=False)
    floor = Column(Integer, default=1, nullable=False)
    status = Column(String(50), default="available", index=True, nullable=False)  # available, occupied, maintenance
    max_occupancy = Column(Integer, default=2, nullable=False)
    amenities = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    bookings = relationship("Booking", back_populates="room")

