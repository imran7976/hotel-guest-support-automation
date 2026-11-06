import pytest
from app.services.guest_service import GuestService
from app.schemas.guest import GuestCreate


def test_create_and_retrieve_guest(db_session):
    guest = GuestService.get_or_create(
        db_session,
        guest_name="Alice Wonderland",
        email="alice@wonderland.com",
        phone="+1-555-9988"
    )
    assert guest.id is not None
    assert guest.first_name == "Alice"
    assert guest.last_name == "Wonderland"
    assert guest.email == "alice@wonderland.com"

    # Fetch by email
    fetched = GuestService.get_by_email(db_session, "alice@wonderland.com")
    assert fetched is not None
    assert fetched.id == guest.id


def test_guest_api_endpoints(client):
    # GET guests list
    response = client.get("/api/v1/guests")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # POST new guest via API
    new_guest_payload = {
        "first_name": "David",
        "last_name": "Miller",
        "email": "david.miller@example.demo",
        "phone": "+1-555-7722",
        "vip_status": False
    }
    create_res = client.post("/api/v1/guests", json=new_guest_payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["email"] == "david.miller@example.demo"

    # Duplicate email prevention
    dup_res = client.post("/api/v1/guests", json=new_guest_payload)
    assert dup_res.status_code == 400
