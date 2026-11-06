# n8n Workflow Automation Architecture & Import Guide

This document describes the 5 automated n8n workflows that power the **AI-Powered Hotel Guest Support Automation System**.

All workflow JSON files are exportable, standalone, and located in:
`backend/n8n/workflows/`

---

## Workflows Inventory

| File | Workflow Name | Trigger | Core Action | Output / Destination |
| :--- | :--- | :--- | :--- | :--- |
| `01_guest_inquiry_processing.json` | **Guest Inquiry Processing** | Webhook `POST /webhook/guest-inquiry` | Payload validation, AI intent routing via FastAPI, escalation check | Returns JSON to guest, syncs conversation |
| `02_complaint_escalation.json` | **Complaint Escalation** | Webhook `POST /webhook/complaint-escalation` | Urgency triage, MySQL record synchronization, alerts team | Dispatches alert to Duty Manager |
| `03_automated_guest_followup.json` | **Automated Guest Follow-up** | Schedule Trigger (Every 4 Hours) | Queries pending unresolved tickets, drafts follow-up | Queues follow-up message & logs activity |
| `04_daily_support_summary.json` | **Daily Support Summary** | Schedule Trigger (`0 23 * * *` Daily Cron) | Pulls analytics KPIs, categorizes volume, formats digest | Writes daily report to DB, alerts General Manager |
| `05_workflow_error_monitoring.json` | **Workflow Error Monitoring** | Global Error Trigger | Captures execution stack traces, records failure log | Alerts On-call Admin, outputs retry instruction |

---

## Detailed Node Architecture by Workflow

### 1. Workflow 1: Guest Inquiry Processing
* **Nodes**:
  1. `Guest Inquiry Webhook`: Ingress path `/guest-inquiry`, method `POST`, `responseMode: "responseNode"`.
  2. `Validate Required Fields`: JavaScript code node enforcing non-empty `guest_name`, `email`, and `inquiry_message`.
  3. `Send Inquiry to FastAPI Backend`: HTTP Request node sending payload to `POST /api/v1/ai/process-inquiry`.
  4. `Check Human Escalation`: If node evaluating boolean condition `requires_human == true`.
  5. `Log Escalation Event`: HTTP Request node recording `escalation_detected` event in `workflow_logs` via `POST /api/v1/webhooks/n8n-callback`. Uses direct node referencing `$('Send Inquiry to FastAPI Backend').item.json` to prevent context loss.
  6. `Return Result to Guest`: RespondToWebhook node returning JSON with `success`, `conversation_id`, `intent`, `confidence`, `priority`, `requires_human`, `response`, and `escalation_id`.

### 2. Workflow 2: Complaint Escalation
* **Nodes**:
  1. `Complaint Webhook Trigger`: Ingress path `/complaint-escalation`, method `POST`.
  2. `Triage Category & Priority`: Code node determining whether repeated issues or urgent phrases escalate priority to `urgent`.
  3. `Sync Record via Backend`: HTTP Request node synchronizing triage status in MySQL via `/api/v1/webhooks/n8n-callback`.
  4. `Notify Support Duty Team`: HTTP Request node logging duty manager dispatch alert.
  5. `Return Escalation Confirmation`: Returns confirmation payload with `notification_dispatched: true`.

### 3. Workflow 3: Automated Guest Follow-up
* **Nodes**:
  1. `Periodic Follow-up Schedule`: Schedule Trigger configured for 4-hour intervals.
  2. `Fetch Unresolved Inquiries`: HTTP Request node fetching `GET /api/v1/escalations?status=pending&limit=10`.
  3. `Generate Follow-up Message`: Code node generating courteous, personalized check-in messages. Returns `[]` if no pending tickets exist, preventing false notifications.
  4. `Queue Message & Log Activity`: Records queued follow-up activity in `workflow_logs` via `/api/v1/webhooks/n8n-callback`.

### 4. Workflow 4: Daily Support Summary
* **Nodes**:
  1. `Daily Midnight Trigger`: `n8n-nodes-base.scheduleTrigger` (v1.2) executing at `0 23 * * *`.
  2. `Retrieve Daily Support Stats`: HTTP Request node fetching `GET /api/v1/analytics/daily-summary`.
  3. `Format Daily Digest`: Formats executive audit digest with inquiry breakdown and AI operational metrics.
  4. `Store Report in MySQL`: HTTP Request node storing `daily_audit_completed` payload.
  5. `Notify Hotel Administrator`: Dispatches daily summary notification to `admin@grandhotelazure.demo`.

### 5. Workflow 5: Workflow Error Monitoring
* **Nodes**:
  1. `Global Workflow Error Trigger`: `n8n-nodes-base.errorTrigger` catching unhandled workflow failures.
  2. `Parse Error Context`: Code node extracting failed workflow name, execution ID, and sanitized error message.
  3. `Record Failure in MySQL`: HTTP Request node recording `status: "failed"` with recommended retry endpoint in `workflow_logs`.
  4. `Notify Ops Administrator`: Dispatches critical operational failure alert.

---

## How to Import Workflows into n8n

### Method A: Single-Click UI Import
1. Open your n8n web instance (e.g. `http://localhost:5678`).
2. In the top-right menu of the canvas, click **Workflows** → **Import from File...** (or press `Ctrl+O`).
3. Select any file from `backend/n8n/workflows/` (e.g. `01_guest_inquiry_processing.json`).
4. Activate the workflow by toggling the switch in the upper-right corner.

### Method B: Environment Configuration
The workflows utilize dynamic environment variables:
- `FASTAPI_BACKEND_URL`: URL of the FastAPI backend (defaults to `http://backend:8000` in Docker or `http://localhost:8000` locally).
- `N8N_WEBHOOK_AUTH_TOKEN`: Security token passed in headers for protected triggers.
