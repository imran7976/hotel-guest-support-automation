from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.conversation import (
    ConversationResponse,
    ConversationSummary,
    MessageResponse,
    MessageCreate
)
from app.services.conversation_service import ConversationService
from app.services.guest_service import GuestService

router = APIRouter()


@router.get("", response_model=List[ConversationSummary])
def list_conversations(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return ConversationService.list_conversations(db, status=status, skip=skip, limit=limit)


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

