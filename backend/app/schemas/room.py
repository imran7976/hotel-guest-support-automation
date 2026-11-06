from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
