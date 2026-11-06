from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class GuestBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    vip_status: bool = False


class GuestCreate(GuestBase):
    pass


class GuestUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    vip_status: Optional[bool] = None


class GuestResponse(GuestBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

