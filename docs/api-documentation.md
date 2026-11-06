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
The core intelligent concierge endpoint. Rate limited per client IP (60 req/min). Ingests guest input, performs intent classification, queries RAG hotel knowledge, calls OpenAI (or smart local fallback), enforces hotel business rules, saves conversation, and escalates if required.

- **Headers**:
  - `Content-Type: application/json`
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

- **Rate Limit Response `429 Too Many Requests`**:
```json
{
  "detail": "Rate limit exceeded. Maximum 60 requests per minute allowed."
}
```

---

## Booking Management Endpoints

### 3. `GET /api/v1/bookings`
List hotel reservations with optional `?status=` filter (`confirmed`, `pending_modification`, `pending_cancellation`, `cancelled`).

### 4. `POST /api/v1/bookings`
Creates a new verified confirmed hotel booking with automatic guest account resolution, room availability conflict checks, and unique reference generation.
- **Request Body**:
```json
{
  "guest_name": "Oliver Queen",
  "guest_email": "oliver@queen.com",
  "check_in_date": "2026-12-01",
  "check_out_date": "2026-12-05",
  "room_type": "Deluxe",
  "number_of_guests": 2,
  "special_requests": "Quiet room high floor please"
}
```
- **Response `201 Created`**:
```json
{
  "id": 12,
  "booking_reference": "GAH-C8F41",
  "guest_id": 8,
  "room_id": 3,
  "check_in_date": "2026-12-01",
  "check_out_date": "2026-12-05",
  "total_amount": "1280.00",
  "status": "confirmed",
  "created_at": "2026-11-06T12:00:00Z"
}
```

### 5. `GET /api/v1/bookings/{booking_reference}`
Retrieve full booking record, guest contact info, and room specs.

### 6. `POST /api/v1/bookings/{booking_id}/modification-request`
Submit reservation dates or room change request. Updates booking status to `pending_modification` and spawns human escalation ticket.

### 7. `POST /api/v1/bookings/{booking_id}/cancellation-request`
Submit reservation cancellation request with refund inquiry. Updates booking status to `pending_cancellation` and creates manager approval ticket.

---

## Conversation Management Endpoints

### 8. `GET /api/v1/conversations`
List active and past guest conversation sessions with last intent and message timestamps.

### 9. `POST /api/v1/conversations`
Creates or retrieves an active conversation session for a guest.
- **Request Body**:
```json
{
  "guest_name": "Tony Stark",
  "guest_email": "tony@stark.com",
  "booking_reference": "GAH-78901",
  "channel": "web_chat"
}
```
- **Response `201 Created`**:
```json
{
  "id": "conv_49a8fe01d3",
  "guest_id": 15,
  "booking_id": 1,
  "channel": "web_chat",
  "status": "active",
  "created_at": "2026-11-06T12:00:00Z",
  "messages": []
}
```

---

## Escalation Management Endpoints

### 10. `GET /api/v1/escalations`
Query active escalation tickets. Supports `?status=pending` and `?priority=urgent`.

### 11. `PATCH /api/v1/escalations/{escalation_id}`
Allows hotel staff to update status (`in_progress`, `resolved`) and append staff resolution messages to the guest conversation thread.

---

## Hotel Knowledge Base (RAG) Endpoints

### 12. `GET /api/v1/knowledge`
List all active hotel policies and FAQ records with optional `?category=` filter.

### 13. `POST /api/v1/knowledge`
Create new factual policy document.

### 14. `PUT /api/v1/knowledge/{knowledge_id}`
Update existing knowledge content.

### 15. `DELETE /api/v1/knowledge/{knowledge_id}`
Soft or hard delete an outdated hotel policy.

---

## Webhooks & n8n Automation Endpoints

### 16. `POST /api/v1/webhooks/guest-inquiry`
Inbound webhook called by external channels or n8n workflow. Verified with constant-time token comparison via `X-Webhook-Token` header.

### 17. `POST /api/v1/webhooks/n8n-callback`
Callback receiver logging asynchronous task completion and errors from n8n nodes.

### 18. `GET /api/v1/webhooks/logs`
Live telemetry audit log of automation execution events.
