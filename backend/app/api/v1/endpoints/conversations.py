from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.conversation import (
    ConversationResponse,
    ConversationSummary,
    ConversationCreate,
    MessageResponse,
    MessageCreate
)
from app.services.conversation_service import ConversationService
from app.services.guest_service import GuestService
from app.services.booking_service import BookingService

router = APIRouter()


@router.get("", response_model=List[ConversationSummary])
def list_conversations(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return ConversationService.list_conversations(db, status=status, skip=skip, limit=limit)


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conv_in: ConversationCreate,
    db: Session = Depends(get_db)
):
    guest = GuestService.get_or_create(db, guest_name=conv_in.guest_name, email=conv_in.guest_email)
    booking_id = None
    if conv_in.booking_reference:
        booking = BookingService.get_by_reference(db, conv_in.booking_reference)
        if booking:
            booking_id = booking.id

    return ConversationService.get_or_create_conversation(
        db=db,
        guest_id=guest.id,
        booking_id=booking_id,
        channel=conv_in.channel
    )



@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = ConversationService.get_by_id(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def post_conversation_message(
    conversation_id: str,
    message_in: MessageCreate,
    db: Session = Depends(get_db)
):
    conv = ConversationService.get_by_id(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg = ConversationService.add_message(
        db=db,
        conversation_id=conversation_id,
        sender_type=message_in.sender_type,
        content=message_in.content
    )
    return msg

