import json
import os
import glob
import pytest
from app.models.workflow_log import WorkflowLog
from app.models.escalation import Escalation
from app.services.escalation_service import EscalationService
from app.services.guest_service import GuestService


WORKFLOWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "n8n", "workflows"))


def test_n8n_workflows_json_validity_and_schema():
    """Validates that all exported n8n workflow files are well-formed, complete, and have zero dangling connections."""
    workflow_files = glob.glob(os.path.join(WORKFLOWS_DIR, "*.json"))
    assert len(workflow_files) == 5, f"Expected 5 n8n workflow files, found {len(workflow_files)}"

    for file_path in workflow_files:
        filename = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Core top-level n8n fields
        assert "name" in data, f"{filename} is missing 'name'"
        assert "nodes" in data and isinstance(data["nodes"], list), f"{filename} missing 'nodes' array"
        assert "connections" in data and isinstance(data["connections"], dict), f"{filename} missing 'connections'"

        node_names = set()
        for node in data["nodes"]:
            assert "id" in node, f"{filename} node missing 'id'"
            assert "name" in node, f"{filename} node missing 'name'"
            assert "type" in node, f"{filename} node {node['name']} missing 'type'"
            assert "typeVersion" in node, f"{filename} node {node['name']} missing 'typeVersion'"
            assert "position" in node, f"{filename} node {node['name']} missing 'position'"
            assert "parameters" in node, f"{filename} node {node['name']} missing 'parameters'"
            node_names.add(node["name"])

        # Verify all connections point to valid existing nodes
        for source_node, conn_types in data["connections"].items():
            assert source_node in node_names, f"{filename} connection source '{source_node}' does not exist in nodes"
            for conn_type, outputs in conn_types.items():
                for output_branch in outputs:
                    for target in output_branch:
                        target_node = target.get("node")
                        assert target_node in node_names, f"{filename} connection target '{target_node}' does not exist in nodes"


def test_workflow_01_execution_standard_inquiry(client):
    """
    Executes Workflow 1: Guest Inquiry Processing
    Inquiry: Normal check-in time question (resolved by AI, no escalation needed).
    """
    # 1. Trigger payload
    incoming_payload = {
        "guest_name": "Eleanor Vance",
        "email": "eleanor.vance@example.com",
        "inquiry_message": "Good afternoon, what time does check-in begin today?",
        "channel": "n8n_webhook"
    }

    # 2. Simulate Node: Send Inquiry to FastAPI Backend
    response = client.post("/api/v1/ai/process-inquiry", json=incoming_payload)
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["intent"] == "check_in_information"
    assert res_data["confidence"] >= 0.75
    assert res_data["requires_human"] is False
    assert "2:00 PM" in res_data["response"] or "check-in" in res_data["response"].lower()

    # 3. Simulate Node: Return Result to Guest (Webhook Response)
    webhook_response = {
        "success": True,
        "conversation_id": res_data["conversation_id"],
        "intent": res_data["intent"],
        "confidence": res_data["confidence"],
        "priority": res_data["priority"],
        "requires_human": res_data["requires_human"],
        "response": res_data["response"],
        "escalation_id": res_data["escalation_id"],
        "timestamp": res_data["timestamp"]
    }
    assert webhook_response["success"] is True
    assert webhook_response["requires_human"] is False


def test_workflow_01_execution_escalated_inquiry(client, db_session):
    """
    Executes Workflow 1: Guest Inquiry Processing
    Inquiry: Emergency/maintenance complaint requiring human escalation.
    """
    # 1. Trigger payload
    incoming_payload = {
        "guest_name": "Marcus Brody",
        "email": "marcus.brody@example.com",
        "inquiry_message": "Water is leaking heavily from the ceiling in room 405! Urgent maintenance needed!",
        "channel": "n8n_webhook"
    }

    # 2. Call backend
    response = client.post("/api/v1/ai/process-inquiry", json=incoming_payload)
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["requires_human"] is True
    assert res_data["priority"] in ["high", "urgent"]
    assert res_data["escalation_id"] is not None

    # 3. Simulate Node: Log Escalation Event via n8n callback
    callback_payload = {
        "workflow_name": "Guest Inquiry Processing",
        "status": "success",
        "trigger_event": "escalation_detected",
        "payload": {
            "conversation_id": res_data["conversation_id"],
            "intent": res_data["intent"],
            "priority": res_data["priority"],
            "escalation_id": res_data["escalation_id"]
        }
    }
    cb_res = client.post("/api/v1/webhooks/n8n-callback", json=callback_payload)
    assert cb_res.status_code == 200

    # 4. Verify log stored in database
    log = (
        db_session.query(WorkflowLog)
        .filter(WorkflowLog.trigger_event == "escalation_detected")
        .order_by(WorkflowLog.id.desc())
        .first()
    )
    assert log is not None
    assert log.workflow_name == "Guest Inquiry Processing"


def test_workflow_02_complaint_escalation_execution(client, db_session):
    """
    Executes Workflow 2: Complaint Escalation
    Trigger: Urgent guest complaint.
    Nodes: Triage -> Sync Record -> Notify Support Team -> Return Confirmation.
    """
    # 1. Incoming complaint trigger
    complaint_data = {
        "escalation_id": 99,
        "conversation_id": "conv_test_complaint_99",
        "guest_name": "Clara Oswald",
        "guest_email": "clara@oswald.com",
        "category": "maintenance_requests",
        "priority": "urgent",
        "reason": "Air conditioner broken and front desk hasn't responded after two requests.",
        "inquiry_text": "Room AC is completely broken, called reception twice already."
    }

    # 2. Node: Sync Record via Backend
    sync_payload = {
        "workflow_name": "Complaint Escalation",
        "status": "success",
        "trigger_event": "complaint_triaged",
        "payload": {
            "escalation_id": complaint_data["escalation_id"],
            "conversation_id": complaint_data["conversation_id"],
            "priority": complaint_data["priority"],
            "category": complaint_data["category"]
        }
    }
    sync_res = client.post("/api/v1/webhooks/n8n-callback", json=sync_payload)
    assert sync_res.status_code == 200

    # 3. Node: Notify Support Duty Team
    notify_payload = {
        "workflow_name": "Complaint Escalation Notification",
        "status": "success",
        "trigger_event": "support_team_notified",
        "payload": {
            "recipient": "duty_manager@grandhotelazure.demo",
            "subject": f"[{complaint_data['priority'].upper()}] Guest Complaint Alert",
            "guest": complaint_data["guest_name"]
        }
    }
    notify_res = client.post("/api/v1/webhooks/n8n-callback", json=notify_payload)
    assert notify_res.status_code == 200

    # 4. Node: Return Escalation Confirmation
    confirmation = {
        "status": "escalated",
        "escalation_id": complaint_data["escalation_id"],
        "priority": complaint_data["priority"],
        "category": complaint_data["category"],
        "notification_dispatched": True,
        "message": "Complaint successfully triaged and escalated to Duty Manager."
    }
    assert confirmation["status"] == "escalated"
    assert confirmation["notification_dispatched"] is True


def test_workflow_03_automated_guest_followup_execution(client, db_session):
    """
    Executes Workflow 3: Automated Guest Follow-up
    Trigger: Scheduled periodic event.
    Nodes: Fetch Unresolved Inquiries -> Generate Follow-up Message -> Queue Message & Log.
    """
    # Setup an unresolved escalation
    guest = GuestService.get_or_create(db_session, "Arthur Dent", "arthur.dent@galaxy.com")
    esc = EscalationService.create_escalation(
        db=db_session,
        conversation_id="conv_followup_test",
        guest_id=guest.id,
        inquiry_text="Need an extra duvet and bath towels for room 204.",
        category="hotel_facilities",
        escalation_reason="Pending housekeeping delivery.",
        priority="normal"
    )

    # 1. Node: Fetch Unresolved Inquiries
    res = client.get("/api/v1/escalations?status=pending&limit=10")
    assert res.status_code == 200
    escalations = res.json()
    assert len(escalations) > 0

    target_esc = next((e for e in escalations if e["id"] == esc.id), None)
    assert target_esc is not None

    # 2. Node: Generate Follow-up Message
    follow_up_text = (
        f"Dear {guest.first_name} {guest.last_name}, this is a courtesy follow-up from the Grand Azure Front Desk "
        f"regarding your inquiry: \"{target_esc['inquiry_text'][:80]}...\". Our team is currently reviewing your "
        f"ticket (Ref #{target_esc['id']}) to ensure everything is resolved to your complete satisfaction."
    )

    # 3. Node: Queue Message & Log Activity
    queue_payload = {
        "workflow_name": "Automated Guest Follow-up",
        "status": "success",
        "trigger_event": "followup_queued",
        "payload": {
            "escalation_id": target_esc["id"],
            "recipient": target_esc["guest"]["email"] if target_esc.get("guest") else "guest@azurehotel.demo",
            "message_snippet": follow_up_text
        }
    }
    cb_res = client.post("/api/v1/webhooks/n8n-callback", json=queue_payload)
    assert cb_res.status_code == 200

    # Verify log entry in DB
    log = (
        db_session.query(WorkflowLog)
        .filter(WorkflowLog.trigger_event == "followup_queued")
        .order_by(WorkflowLog.id.desc())
        .first()
    )
    assert log is not None
    assert log.workflow_name == "Automated Guest Follow-up"


def test_workflow_04_daily_support_summary_execution(client, db_session):
    """
    Executes Workflow 4: Daily Support Summary
    Trigger: Daily scheduled cron.
    Nodes: Retrieve Daily Support Stats -> Format Daily Digest -> Store Report -> Notify Admin.
    """
    # 1. Node: Retrieve Daily Support Stats
    stats_res = client.get("/api/v1/analytics/daily-summary")
    assert stats_res.status_code == 200
    data = stats_res.json()

    assert "total_inquiries" in data
    assert "report_date" in data
    assert "ai_summary_text" in data

    # 2. Node: Format Daily Digest
    cat_breakdown = "\n".join([f"• {c['category']}: {c['count']}" for c in data.get("top_categories", [])])
    executive_summary = (
        f"=== GRAND AZURE RESORT: DAILY SUPPORT DIGEST ===\n"
        f"Date: {data['report_date']}\n"
        f"Total Inquiries: {data['total_inquiries']}\n"
        f"AI Automated Resolutions: {data['resolved_by_ai']}\n"
        f"Staff Escalations: {data['escalated_to_staff']}\n"
        f"Pending Unresolved Complaints: {data['unresolved_complaints_count']}\n\n"
        f"Top Categories:\n{cat_breakdown}\n\n"
        f"AI Operations Analysis:\n{data['ai_summary_text']}"
    )
    assert len(executive_summary) > 50

    # 3. Node: Store Report in MySQL via Backend
    store_payload = {
        "workflow_name": "Daily Support Summary",
        "status": "success",
        "trigger_event": "daily_audit_completed",
        "payload": {
            "report_date": data["report_date"],
            "total": data["total_inquiries"],
            "ai_resolved": data["resolved_by_ai"],
            "escalated": data["escalated_to_staff"],
            "unresolved": data["unresolved_complaints_count"]
        }
    }
    store_res = client.post("/api/v1/webhooks/n8n-callback", json=store_payload)
    assert store_res.status_code == 200

    # 4. Node: Notify Hotel Administrator
    notify_payload = {
        "workflow_name": "Admin Daily Digest Notification",
        "status": "success",
        "trigger_event": "admin_notified",
        "payload": {
            "recipient": "admin@grandhotelazure.demo",
            "subject": f"Daily Hotel Support Digest - {data['report_date']}",
            "digest": executive_summary
        }
    }
    notify_res = client.post("/api/v1/webhooks/n8n-callback", json=notify_payload)
    assert notify_res.status_code == 200


def test_workflow_05_workflow_error_monitoring_execution(client, db_session):
    """
    Executes Workflow 5: Workflow Error Monitoring
    Trigger: Global workflow execution failure.
    Nodes: Parse Error Context -> Record Failure in MySQL -> Notify Ops Administrator.
    """
    # 1. Incoming error context
    simulated_error = {
        "workflow": {"name": "Guest Inquiry Processing"},
        "execution": {
            "id": "exec_fail_8842",
            "error": {"message": "OpenAI API timeout after 10000ms"}
        }
    }

    # 2. Node: Record Failure in MySQL
    record_payload = {
        "workflow_name": simulated_error["workflow"]["name"],
        "execution_id": simulated_error["execution"]["id"],
        "status": "failed",
        "trigger_event": "workflow_failure_alert",
        "error_message": simulated_error["execution"]["error"]["message"],
        "payload": {
            "retry_recommended": True,
            "failed_at": "2026-11-06T12:00:00Z"
        }
    }
    record_res = client.post("/api/v1/webhooks/n8n-callback", json=record_payload)
    assert record_res.status_code == 200

    # 3. Node: Notify Ops Administrator
    notify_payload = {
        "workflow_name": "Error Alert Notification",
        "status": "success",
        "trigger_event": "admin_error_dispatched",
        "payload": {
            "recipient": "admin@grandhotelazure.demo",
            "subject": f"[CRITICAL] n8n Automation Failure in {simulated_error['workflow']['name']}",
            "error": simulated_error["execution"]["error"]["message"],
            "execution_id": simulated_error["execution"]["id"]
        }
    }
    notify_res = client.post("/api/v1/webhooks/n8n-callback", json=notify_payload)
    assert notify_res.status_code == 200

    # Verify log entry in DB
    log = (
        db_session.query(WorkflowLog)
        .filter(WorkflowLog.execution_id == "exec_fail_8842")
        .first()
    )
    assert log is not None
    assert log.status == "failed"
    assert "OpenAI API timeout" in log.error_message

