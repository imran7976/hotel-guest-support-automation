import datetime
import pytest
from app.services.booking_service import BookingService
from app.schemas.booking import ModificationRequest, CancellationRequest


def test_booking_retrieval(db_session):
    booking = BookingService.get_by_reference(db_session, "GAH-78901")
    assert booking is not None
    assert booking.booking_reference == "GAH-78901"
    assert booking.status == "confirmed"


def test_check_availability(db_session):
    today = datetime.date.today()
    available = BookingService.check_availability(
        db_session,
        check_in_date=today + datetime.timedelta(days=20),
        check_out_date=today + datetime.timedelta(days=25)
    )
    assert len(available) > 0
    assert any(r["room_number"] == "101" for r in available)


def test_booking_modification_creates_escalation(db_session):
    booking = BookingService.get_by_reference(db_session, "GAH-78901")
    mod_req = ModificationRequest(
        new_check_in_date=datetime.date.today() + datetime.timedelta(days=3),
        new_check_out_date=datetime.date.today() + datetime.timedelta(days=6),
        reason="Flight rescheduled by airline"
    )
    result = BookingService.request_modification(db_session, booking.id, mod_req)
    assert result["status"] == "pending_approval"
    assert result["escalation_id"] is not None

    # Check database status was updated
    refreshed_booking = BookingService.get_by_id(db_session, booking.id)
    assert refreshed_booking.status == "pending_modification"


def test_booking_cancellation_requires_human_approval(db_session):
    booking = BookingService.get_by_reference(db_session, "GAH-78901")
    canc_req = CancellationRequest(
        reason="Emergency travel change",
        request_refund=True
    )
    result = BookingService.request_cancellation(db_session, booking.id, canc_req)
    assert result["status"] == "pending_approval"
    assert result["escalation_id"] is not None

    refreshed_booking = BookingService.get_by_id(db_session, booking.id)
    assert refreshed_booking.status == "pending_cancellation"


def test_booking_api_routes(client):
    res = client.get("/api/v1/bookings/GAH-78901")
    assert res.status_code == 200
    assert res.json()["booking_reference"] == "GAH-78901"

    # Non-existent booking
    res_404 = client.get("/api/v1/bookings/INVALID-999")
    assert res_404.status_code == 404


def test_create_booking_api(client):
    today = datetime.date.today()
    payload = {
        "guest_name": "Oliver Queen",
        "guest_email": "oliver@queen.com",
        "check_in_date": (today + datetime.timedelta(days=40)).isoformat(),
        "check_out_date": (today + datetime.timedelta(days=45)).isoformat(),
        "room_type": "Deluxe",
        "number_of_guests": 2,
        "special_requests": "Quiet room high floor please"
    }
    res = client.post("/api/v1/bookings", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["booking_reference"].startswith("GAH-")
    assert data["status"] == "confirmed"
    assert data["total_amount"] is not None


