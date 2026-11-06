from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.escalation import EscalationResponse, EscalationUpdate, EscalationCreate
from app.services.escalation_service import EscalationService
from app.api.v1.endpoints.auth import get_current_admin
from app.models.admin_user import AdminUser

router = APIRouter()


@router.get("", response_model=List[EscalationResponse])
def get_escalations(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return EscalationService.list_escalations(db, status=status, priority=priority, skip=skip, limit=limit)


@router.post("", response_model=EscalationResponse, status_code=status.HTTP_201_CREATED)
def create_manual_escalation(
    escalation_in: EscalationCreate,
    db: Session = Depends(get_db)
):
    escalation = EscalationService.create_escalation(
        db=db,
        conversation_id=escalation_in.conversation_id,
        guest_id=escalation_in.guest_id,
        inquiry_text=escalation_in.inquiry_text,
        category=escalation_in.category,
        escalation_reason=escalation_in.escalation_reason,
        priority=escalation_in.priority,
        booking_id=escalation_in.booking_id
    )
    return escalation


@router.patch("/{escalation_id}", response_model=EscalationResponse)
def update_escalation(
    escalation_id: int,
    update_in: EscalationUpdate,
    db: Session = Depends(get_db),
    current_admin: Optional[AdminUser] = Depends(get_current_admin)
):
    staff_id = current_admin.id if current_admin else None
    escalation = EscalationService.update_escalation(
        db=db,
        escalation_id=escalation_id,
        update_in=update_in,
        staff_id=staff_id
    )
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation ticket not found")
    return escalation

