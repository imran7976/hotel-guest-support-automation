from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.escalation import Escalation
from app.models.notification import Notification
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.escalation import EscalationUpdate
from app.core.config import settings
from app.core.logging import logger


class EscalationService:
    @staticmethod
    def get_by_id(db: Session, escalation_id: int) -> Optional[Escalation]:
        return db.query(Escalation).filter(Escalation.id == escalation_id).first()

    @staticmethod
    def list_escalations(
        db: Session,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Escalation]:
        query = db.query(Escalation)
        if status and status != "all":
            query = query.filter(Escalation.status == status)
        if priority and priority != "all":
            query = query.filter(Escalation.priority == priority)
        return query.order_by(Escalation.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_escalation(
        db: Session,
        conversation_id: str,
        guest_id: int,
        inquiry_text: str,
        category: str,
        escalation_reason: str,
        priority: str = "normal",
        booking_id: Optional[int] = None
    ) -> Escalation:
        escalation = Escalation(
            conversation_id=conversation_id,
            guest_id=guest_id,
            booking_id=booking_id,
            inquiry_text=inquiry_text,
            category=category,
            priority=priority,
            status="pending",
            escalation_reason=escalation_reason
        )
        db.add(escalation)

        # Mark conversation as escalated
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv:
            conv.status = "escalated"

        # Dispatch automated notification (Simulated / Safe DEMO mode)
        notif_subject = f"[{priority.upper()}] Escalation Alert: {category.replace('_', ' ').title()}"
        notif_message = (
            f"Escalation ticket created for Conversation {conversation_id}.\n"
            f"Priority: {priority.upper()}\n"
            f"Reason: {escalation_reason}\n"
            f"Guest Inquiry: {inquiry_text}\n"
        )
        notification = Notification(
            recipient=settings.SUPPORT_TEAM_EMAIL,
            channel="email",
            subject=notif_subject,
            message=notif_message,
            status="sent" if settings.MOCK_DELIVERY else "pending"
        )
        db.add(notification)

        db.commit()
        db.refresh(escalation)
        logger.info(f"Escalation {escalation.id} created with priority {priority} for reason: {escalation_reason}")
        return escalation

    @staticmethod
    def update_escalation(
        db: Session,
        escalation_id: int,
        update_in: EscalationUpdate,
        staff_id: Optional[int] = None
    ) -> Optional[Escalation]:
        escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
        if not escalation:
            return None

        if update_in.status:
            escalation.status = update_in.status
            if update_in.status == "resolved":
                escalation.resolved_at = datetime.now(timezone.utc)
                # Also resolve the parent conversation if no other pending escalations
                conv = db.query(Conversation).filter(Conversation.id == escalation.conversation_id).first()
                if conv:
                    conv.status = "active"

        if update_in.priority:
            escalation.priority = update_in.priority
        if update_in.staff_response:
            escalation.staff_response = update_in.staff_response
            # Append staff response to conversation messages
            msg = Message(
                conversation_id=escalation.conversation_id,
                sender_type="staff",
                content=update_in.staff_response,
                priority=escalation.priority,
                requires_human=False
            )
            db.add(msg)

        if update_in.assigned_staff_id or staff_id:
            escalation.assigned_staff_id = update_in.assigned_staff_id or staff_id

        db.commit()
        db.refresh(escalation)
        return escalation

