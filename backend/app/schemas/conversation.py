from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, ConfigDict


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: str
    sender_type: str
    content: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    priority: str = "normal"
    requires_human: bool = False
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class MessageCreate(BaseModel):
    content: str
    sender_type: str = "guest"  # guest, staff
    channel: Optional[str] = "web_chat"


class ConversationCreate(BaseModel):
    guest_email: EmailStr
    guest_name: str
    booking_reference: Optional[str] = None
    channel: str = "web_chat"


class InquirySubmission(BaseModel):
    guest_name: str
    email: EmailStr
    booking_reference: Optional[str] = None
    inquiry_category: Optional[str] = None
    inquiry_message: str
    conversation_id: Optional[str] = None
    channel: str = "web_chat"


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    guest_id: int
    booking_id: Optional[int] = None
    channel: str
    status: str
    last_intent: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []


class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    guest_name: str
    guest_email: str
    channel: str
    status: str
    last_intent: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    message_count: int = 0
