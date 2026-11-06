# REST API Reference & Swagger Specifications

The backend is built with **FastAPI** providing OpenAPI 3.1 and Swagger UI documentation at:
`http://localhost:8000/docs`

---

## Base URL
`/api/v1`

---

## Authentication Endpoints

### 1. `POST /api/v1/auth/login`
Authenticates hotel staff and returns JWT Bearer token.
- **Request Body**:
```json
{
  "email": "admin@grandhotelazure.demo",
  "password": "AdminHotel2025!"
}
```
- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

## AI & Guest Support Endpoints

### 2. `POST /api/v1/ai/process-inquiry`
The core intelligent concierge endpoint. Ingests guest input, performs intent classification, queries RAG hotel knowledge, calls OpenAI (or smart local fallback), enforces hotel business rules, saves conversation, and escalates if required.

- **Request Body**:
```json
{
  "guest_name": "John Smith",
  "email": "john@example.com",
  "inquiry_message": "Hello, I have a booking for tomorrow. Could you tell me the check-in time and whether I can request an early check-in?",
  "booking_reference": "GAH-78901",
  "channel": "web_chat"
}
```

- **Response `200 OK`**:
```json
{
  "conversation_id": "conv_a8f93e2b10",
  "guest_id": 1,
  "intent": "check_in_information",
  "confidence": 0.95,
  "priority": "normal",
  "requires_human": false,
  "response": "Hello John, thank you for contacting Grand Azure Resort. Our standard check-in time is 2:00 PM (14:00) and check-out is 11:00 AM. Early check-in prior to 2:00 PM is subject to room availability upon arrival...",
  "escalation_id": null,
  "retrieved_knowledge": [
    "Standard Check-in and Check-out Times",
    "Early Check-in Policy"
  ],
  "timestamp": "2026-11-06T06:30:00.000Z"
}
```

---

## Booking Management Endpoints

### 3. `GET /api/v1/bookings`
List hotel reservations with optional `?status=` filter (`confirmed`, `pending_modification`, `pending_cancellation`, `cancelled`).

### 4. `GET /api/v1/bookings/{booking_reference}`
Retrieve full booking record, guest contact info, and room specs.

### 5. `POST /api/v1/bookings/{booking_id}/modification-request`
Submit reservation dates or room change request. Updates booking status to `pending_modification` and spawns human escalation ticket.

### 6. `POST /api/v1/bookings/{booking_id}/cancellation-request`
Submit reservation cancellation request with refund inquiry. Updates booking status to `pending_cancellation` and creates manager approval ticket.

---

## Escalation Management Endpoints

### 7. `GET /api/v1/escalations`
Query active escalation tickets. Supports `?status=pending` and `?priority=urgent`.

### 8. `PATCH /api/v1/escalations/{escalation_id}`
Allows hotel staff to update status (`in_progress`, `resolved`) and append staff resolution messages to the guest conversation thread.

---

## Hotel Knowledge Base (RAG) Endpoints

### 9. `GET /api/v1/knowledge`
List all active hotel policies and FAQ records with optional `?category=` filter.

### 10. `POST /api/v1/knowledge`
Create new factual policy document.

### 11. `PUT /api/v1/knowledge/{knowledge_id}`
Update existing knowledge content.

### 12. `DELETE /api/v1/knowledge/{knowledge_id}`
Soft or hard delete an outdated hotel policy.

---

## Webhooks & n8n Automation Endpoints

### 13. `POST /api/v1/webhooks/guest-inquiry`
Inbound webhook called by external channels or n8n workflow.

### 14. `POST /api/v1/webhooks/n8n-callback`
Callback receiver logging asynchronous task completion and errors from n8n nodes.

### 15. `GET /api/v1/webhooks/logs`
Live telemetry audit log of automation execution events.

