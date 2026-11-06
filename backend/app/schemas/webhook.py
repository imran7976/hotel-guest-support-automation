from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class WebhookInquiryPayload(BaseModel):
    guest_name: str
    email: str
    inquiry_message: str
    booking_reference: Optional[str] = None
    inquiry_category: Optional[str] = None
    channel: Optional[str] = "webhook"


class WebhookCallbackPayload(BaseModel):
    workflow_name: str
    execution_id: Optional[str] = None
    status: str  # success, failed
    trigger_event: str
    error_message: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class WorkflowLogResponse(BaseModel):
    id: int
    workflow_name: str
    execution_id: Optional[str] = None
    trigger_event: str
    status: str
    error_message: Optional[str] = None
    payload_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

