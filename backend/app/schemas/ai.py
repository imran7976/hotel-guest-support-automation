from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ExtractedInformation(BaseModel):
    booking_reference: Optional[str] = None
    requested_date: Optional[str] = None
    room_number: Optional[str] = None
    room_type: Optional[str] = None
    guest_name: Optional[str] = None
    complaint_target: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class AIIntentClassification(BaseModel):
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    priority: str = "normal"  # low, normal, high, urgent
    requires_human: bool = False
    escalation_reason: Optional[str] = None
    extracted_information: ExtractedInformation = Field(default_factory=ExtractedInformation)


class AIGeneratedResponse(BaseModel):
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    priority: str = "normal"
    requires_human: bool = False
    response: str
    escalation_reason: Optional[str] = None
    extracted_information: ExtractedInformation = Field(default_factory=ExtractedInformation)


class ProcessInquiryRequest(BaseModel):
    guest_name: str
    email: str
    booking_reference: Optional[str] = None
    inquiry_category: Optional[str] = None
    inquiry_message: str
    conversation_id: Optional[str] = None
    channel: str = "web_chat"


class ProcessInquiryResponse(BaseModel):
    conversation_id: str
    guest_id: int
    intent: str
    confidence: float
    priority: str
    requires_human: bool
    response: str
    escalation_id: Optional[int] = None
    retrieved_knowledge: List[str] = []
    timestamp: str

