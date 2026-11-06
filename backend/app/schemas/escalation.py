from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.guest import GuestResponse


class EscalationBase(BaseModel):
    conversation_id: str
    guest_id: int
    booking_id: Optional[int] = None
    inquiry_text: str
    category: str
    priority: str = "normal"  # low, normal, high, urgent
    escalation_reason: str


class EscalationCreate(EscalationBase):
    pass


class EscalationUpdate(BaseModel):
    status: Optional[str] = None  # pending, assigned, in_progress, resolved
    priority: Optional[str] = None
    staff_response: Optional[str] = None
    assigned_staff_id: Optional[int] = None


class EscalationResponse(EscalationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    staff_response: Optional[str] = None
    assigned_staff_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    guest: Optional[GuestResponse] = None
