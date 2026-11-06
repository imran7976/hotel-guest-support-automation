from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel


class RoomBase(BaseModel):
    room_number: str
    room_type: str
    price_per_night: Decimal
    floor: int = 1
    status: str = "available"
    max_occupancy: int = 2
    amenities: Optional[str] = None
    description: Optional[str] = None


class RoomCreate(RoomBase):
    pass


class RoomResponse(RoomBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

