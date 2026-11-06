import pytest
from app.models.workflow_log import WorkflowLog
from app.core.config import settings


def test_webhook_inbound_inquiry(client):
    payload = {
        "guest_name": "Sarah Connor",
        "email": "sarah@resistance.com",
        "inquiry_message": "What time is breakfast served on Sunday?",
        "booking_reference": "GAH-78901",
        "channel": "webhook"
    }
    res = client.post("/api/v1/webhooks/guest-inquiry", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] in ["hotel_facilities", "dining", "check_in_information"]
    assert len(data["response"]) > 0


def test_webhook_auth_enforcement(client, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "N8N_WEBHOOK_AUTH_TOKEN", "super_secret_token_123")

    payload = {
        "guest_name": "Sarah Connor",
        "email": "sarah@resistance.com",
        "inquiry_message": "What time is breakfast served on Sunday?",
        "channel": "webhook"
    }

    # Missing token should return 403
    res_no_token = client.post("/api/v1/webhooks/guest-inquiry", json=payload)
    assert res_no_token.status_code == 403

    # Invalid token should return 403
    res_bad_token = client.post(
        "/api/v1/webhooks/guest-inquiry",
        json=payload,
        headers={"x-webhook-token": "wrong_token"}
    )
    assert res_bad_token.status_code == 403

    # Valid token should succeed
    res_valid = client.post(
        "/api/v1/webhooks/guest-inquiry",
        json=payload,
        headers={"x-webhook-token": "super_secret_token_123"}
    )
    assert res_valid.status_code == 200



def test_n8n_callback_and_logs(client, db_session):
    callback_payload = {
        "workflow_name": "Complaint Escalation",
        "execution_id": "exec_test_99",
        "status": "success",
        "trigger_event": "complaint_triaged",
        "payload": {"escalation_id": 1}
    }
    res = client.post("/api/v1/webhooks/n8n-callback", json=callback_payload)
    assert res.status_code == 200

    # Retrieve logs endpoint
    res_logs = client.get("/api/v1/webhooks/logs")
    assert res_logs.status_code == 200
    logs = res_logs.json()
    assert len(logs) > 0
    assert any(l["workflow_name"] == "Complaint Escalation" for l in logs)

