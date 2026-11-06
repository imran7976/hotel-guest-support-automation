import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.guest import Guest
from app.schemas.conversation import ConversationSummary


class ConversationService:
    @staticmethod
    def get_by_id(db: Session, conversation_id: str) -> Optional[Conversation]:
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    @staticmethod
    def get_or_create_conversation(
        db: Session,
        guest_id: int,
        conversation_id: Optional[str] = None,
        booking_id: Optional[int] = None,
        channel: str = "web_chat"
    ) -> Conversation:
        if conversation_id:
            conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conv:
                if booking_id and not conv.booking_id:
                    conv.booking_id = booking_id
                    db.commit()
                    db.refresh(conv)
                return conv

        new_id = f"conv_{uuid.uuid4().hex[:12]}"
        conv = Conversation(
            id=new_id,
            guest_id=guest_id,
            booking_id=booking_id,
            channel=channel,
            status="active"
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv

    @staticmethod
    def add_message(
        db: Session,
        conversation_id: str,
        sender_type: str,
        content: str,
        intent: Optional[str] = None,
        confidence: Optional[float] = None,
        priority: str = "normal",
        requires_human: bool = False,
        metadata_json: Optional[Dict[str, Any]] = None
    ) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            content=content,
            intent=intent,
            confidence=confidence,
            priority=priority,
            requires_human=requires_human,
            metadata_json=metadata_json
        )
        db.add(msg)

        # Update parent conversation
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv:
            if intent:
                conv.last_intent = intent
            if requires_human:
                conv.status = "escalated"

        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def get_conversation_history(db: Session, conversation_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Formats conversation turns for LLM chat context."""
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
        history = []
        for msg in reversed(messages):
            role = "assistant" if msg.sender_type == "ai" else "user" if msg.sender_type == "guest" else "system"
            history.append({"role": role, "content": msg.content})
        return history

    @staticmethod
    def list_conversations(
        db: Session,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ConversationSummary]:
        query = db.query(Conversation).join(Guest, Conversation.guest_id == Guest.id)
        if status and status != "all":
            query = query.filter(Conversation.status == status)

        conversations = query.order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

        summaries = []
        for c in conversations:
            last_msg = (
                db.query(Message)
                .filter(Message.conversation_id == c.id)
                .order_by(Message.created_at.desc())
                .first()
            )
            msg_count = db.query(Message).filter(Message.conversation_id == c.id).count()

            summaries.append(
                ConversationSummary(
                    id=c.id,
                    guest_name=f"{c.guest.first_name} {c.guest.last_name}".strip(),
                    guest_email=c.guest.email,
                    channel=c.channel,
                    status=c.status,
                    last_intent=c.last_intent,
                    last_message=last_msg.content[:120] if last_msg else None,
                    last_message_at=last_msg.created_at if last_msg else c.created_at,
                    message_count=msg_count
                )
            )
        return summaries

