# n8n Workflow Automation Architecture & Import Guide

This document describes the 5 automated n8n workflows that power the **AI-Powered Hotel Guest Support Automation System**.

All workflow JSON files are exportable, standalone, and located in:
`backend/n8n/workflows/`

---

## Workflows Inventory

| File | Workflow Name | Trigger | Core Action | Output / Destination |
| :--- | :--- | :--- | :--- | :--- |
| `01_guest_inquiry_processing.json` | **Guest Inquiry Processing** | Webhook `POST /webhook/guest-inquiry` | Payload validation, AI intent routing via FastAPI, escalation check | Returns JSON to guest, syncs conversation |
| `02_complaint_escalation.json` | **Complaint Escalation** | Webhook `POST /webhook/complaint-escalation` | Urgency triage, MySQL record synchronization, alerts team | Dispatches email/ticket alert to Duty Manager |
| `03_automated_guest_followup.json` | **Automated Guest Follow-up** | Cron / Schedule (Every 4 Hours) | Queries pending unresolved tickets, drafts follow-up | Queues follow-up message & logs activity |
| `04_daily_support_summary.json` | **Daily Support Summary** | Cron (Daily at 23:00) | Pulls analytics KPIs, categorizes volume, formats digest | Writes daily report to DB, alerts General Manager |
| `05_workflow_error_monitoring.json` | **Workflow Error Monitoring** | Global Error Trigger | Captures execution stack traces, records failure log | Alerts On-call Admin, outputs retry instruction |

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

---

## End-to-End Workflow Testing via Curl

### Test Workflow 1 (Guest Inquiry Webhook)
```bash
curl -X POST http://localhost:8000/api/v1/webhooks/guest-inquiry \
  -H "Content-Type: application/json" \
  -d '{
    "guest_name": "John Smith",
    "email": "john@example.com",
    "inquiry_message": "What time is check in?",
    "booking_reference": "GAH-78901"
  }'
```

### Test Workflow 2 (Complaint Escalation)
```bash
curl -X POST http://localhost:8000/api/v1/webhooks/guest-inquiry \
  -H "Content-Type: application/json" \
  -d '{
    "guest_name": "John Smith",
    "email": "john@example.com",
    "inquiry_message": "My air conditioning is broken and I called reception twice already."
  }'
```
Inspect the database `escalations` and `workflow_logs` tables to observe the automated triage!

