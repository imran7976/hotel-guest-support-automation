import pytest
from app.services.escalation_service import EscalationService
from app.services.guest_service import GuestService
from app.schemas.escalation import EscalationUpdate


def test_escalation_lifecycle(db_session):
    guest = GuestService.get_or_create(db_session, "Robert DeNiro", "robert@hollywood.com")
    
    # Create escalation
    esc = EscalationService.create_escalation(
        db=db_session,
        conversation_id="conv_test_esc_1",
        guest_id=guest.id,
        inquiry_text="Water is dripping from the bathroom ceiling",
        category="maintenance_requests",
        escalation_reason="Urgent plumbing hazard reported by guest.",
        priority="urgent"
    )
    assert esc.id is not None
    assert esc.priority == "urgent"
    assert esc.status == "pending"

    # Update escalation / Staff resolution
    updated = EscalationService.update_escalation(
        db=db_session,
        escalation_id=esc.id,
        update_in=EscalationUpdate(
            status="resolved",
            staff_response="Duty engineer dispatched and repaired pipe fitting at 14:30."
        )
    )
    assert updated.status == "resolved"
    assert updated.staff_response is not None
    assert updated.resolved_at is not None


def test_escalation_api(client):
    res = client.get("/api/v1/escalations")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
