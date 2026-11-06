from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from app.schemas.room import RoomResponse
from app.schemas.guest import GuestResponse


class BookingBase(BaseModel):
    check_in_date: date
    check_out_date: date
    number_of_guests: int = 1
    special_requests: Optional[str] = None


class BookingCreate(BookingBase):
    guest_id: int
    room_id: int
    total_amount: Decimal


class ModificationRequest(BaseModel):
    new_check_in_date: Optional[date] = None
    new_check_out_date: Optional[date] = None
    new_room_type: Optional[str] = None
    reason: str


class CancellationRequest(BaseModel):
    reason: str
    request_refund: bool = True


class BookingResponse(BookingBase):
    id: int
    booking_reference: str
    guest_id: int
    room_id: int
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    room: Optional[RoomResponse] = None
    guest: Optional[GuestResponse] = None

    class Config:
        from_attributes = True

