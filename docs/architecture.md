# System Architecture & Technical Specification

## 1. Overview
The **AI-Powered Hotel Guest Support Automation System** is an enterprise-grade platform designed to automate repetitive hotel front-desk operations, triage guest messages, generate grounded responses via Retrieval-Augmented Generation (RAG), execute business logic validations, manage escalations with human-in-the-loop controls, and synchronize workflows through **n8n** and **MySQL 8**.

---

## 2. Multi-Tier Architecture Diagram

```mermaid
flowchart TD
    %% Clients & Entry Points
    subgraph ClientLayer ["Client & Ingestion Layer"]
        GuestChat["Guest Web Portal / Chat (/chat)"]
        StaffDashboard["Staff Operations Dashboard (Next.js 14)"]
        WebhookTrigger["External Channels / Webhook Ingress"]
    end

    %% Backend Gateway & APIs
    subgraph APILayer ["FastAPI Core Services (Python 3.10+)"]
        RateLimiter["Sliding-Window IP Rate Limiter"]
        InputVal["Pydantic v2 Schema Validation"]
        ConvManager["Guest & Conversation Session Manager"]
        AIEngine["AI Orchestrator Service"]
        BizRules["Business Rule & Safeguard Engine"]
        EscalationService["Escalation & Notification Service"]
        KnowledgeService["Knowledge Management Service (RAG)"]
        BookingService["Booking & Availability Service"]
    end

    %% AI & Retrieval Layer
    subgraph IntelligenceLayer ["AI & Knowledge Subsystem"]
        InjectionDefense["Prompt Injection & Jailbreak Defense"]
        IntentClassifier["Intent Classifier (12 Categories)"]
        RAGRetriever["Hybrid RAG Retrieval Engine"]
        OpenAIClient["OpenAI API (gpt-4o-mini / Local Fallback)"]
    end

    %% Workflow Automation
    subgraph AutomationLayer ["n8n Workflow Automation (v1.0+)"]
        WF1["WF1: Guest Inquiry Processing"]
        WF2["WF2: Complaint Escalation"]
        WF3["WF3: Automated Follow-up"]
        WF4["WF4: Daily Support Summary"]
        WF5["WF5: Error & Failure Monitor"]
    end

    %% Persistence
    subgraph DataLayer ["Persistence & Storage (MySQL 8.0 / SQLite)"]
        MySQLDB[("MySQL 8.0 Relational DB (10 Normalized Tables)")]
        WorkflowLogs[("Workflow Execution & Telemetry Logs")]
    end

    %% Flow connections
    GuestChat -->|REST API POST| RateLimiter
    WebhookTrigger -->|Webhook Payload| RateLimiter
    StaffDashboard -->|JWT Bearer Auth| APILayer

    RateLimiter --> InputVal
    InputVal --> ConvManager
    ConvManager --> AIEngine

    AIEngine --> InjectionDefense
    InjectionDefense --> IntentClassifier
    IntentClassifier --> RAGRetriever
    RAGRetriever -->|Grounded Context Blocks| OpenAIClient
    OpenAIClient -->|Structured JSON Output| BizRules

    BizRules -->|Passed Safeguards| ConvManager
    BizRules -->|Escalation Required| EscalationService

    AIEngine -.->|Async Webhook Dispatch| AutomationLayer
    EscalationService -.->|Trigger Complaint Alert| WF2
    AutomationLayer -->|Callback Updates / Logs| APILayer

    ConvManager --> MySQLDB
    EscalationService --> MySQLDB
    KnowledgeService --> MySQLDB
    BookingService --> MySQLDB
    AutomationLayer --> WorkflowLogs
```

---

## 3. Inquiry Execution Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Guest as Hotel Guest
    participant Frontend as Next.js Web Portal
    participant API as FastAPI Backend
    participant RAG as RAG Knowledge Engine
    participant LLM as OpenAI (gpt-4o-mini)
    participant Rules as Business Safeguard Engine
    participant n8n as n8n Automation Engine
    participant DB as MySQL 8 Database
    actor Staff as Front Desk Staff

    Guest->>Frontend: Submits inquiry ("Cancel booking GAH-78901 & refund me")
    Frontend->>API: POST /api/v1/ai/process-inquiry
    API->>API: Rate Limiter & Pydantic Validation
    API->>DB: Get or create Guest & Conversation session
    API->>API: Intent Classifier identifies "cancellation" (confidence: 0.95)
    API->>RAG: Retrieve grounded cancellation policy documents
    RAG-->>API: Returns 48h cancellation & refund rules
    API->>LLM: Prompt with verified policy context + conversation memory
    LLM-->>API: Structured JSON response
    API->>Rules: Validate against Hotel Business Safeguards
    Note over Rules: Policy Check: AI barred from autonomous refunds.<br/>Enforces requires_human = True & Priority: High.
    Rules->>DB: Log message & generate Escalation Ticket (#4)
    Rules->>n8n: POST /webhook/complaint-escalation (WF2)
    n8n->>DB: Sync escalation record & dispatch staff alert
    API-->>Frontend: Natural language response (polite refusal + escalation notice)
    Frontend-->>Guest: Displays verified policy & confirms staff review
    Staff->>Frontend: Views escalation on live Dashboard & authorizes resolution
```

---

## 4. Core Architectural Subsystems

### A. FastAPI Backend Service Layer (`backend/app/`)
- **FastAPI Core**: Asynchronous ASGI REST API with automatic OpenAPI 3.1 documentation (`/docs` and `/redoc`).
- **Pydantic v2**: Modern schema definitions (`model_config = ConfigDict(from_attributes=True)`) guaranteeing request/response integrity and type safety.
- **Sliding-Window IP Rate Limiting**: In-memory rate limiter per IP with automatic window pruning and background thread locking, preventing API budget drain and DoS attacks.
- **Timing-Attack Resistant Webhooks**: Inbound webhooks use `secrets.compare_digest` to verify incoming authentication tokens in constant time.
- **Strict Role Boundaries**: Unauthenticated requests cannot access administrative features.

### B. AI & RAG Subsystem (`backend/app/ai/`)
1. **Adversarial & Prompt Injection Defense**:
   - High-priority regex and pattern analyzer intercepting prompt injection phrases (`ignore previous instructions`, `you are now a pirate`, `system override`, `reveal prompt`, `output 'hacked'`).
   - Implements automated containment: overrides priority to `high`, triggers human review, and sanitizes output to preserve system safety.
2. **Intent Classification & Entity Extraction**:
   - 12 standardized categories covering all typical hospitality operations.
   - Extracts booking references (`GAH-XXXXX`), room numbers (`Room 302`), requested dates, and complaint targets.
3. **Hybrid RAG Knowledge Retrieval**:
   - Evaluates token matches across all active hotel knowledge documents without artificial category barriers.
   - Applies relevance boosts for title matches, keyword matches, and category alignments.
4. **Business Rule Guardrails (`business_rules.py`)**:
   - **Financial Protection**: Strips unauthorized refund claims and requires managerial sign-off.
   - **Modification Guard**: Demands reservation desk approval for date or room upgrades.
   - **Emergency Dispatch Protocol**: Elevates fire, smoke, gas leaks, and medical emergencies to `urgent` priority with emergency instructions.

### C. n8n Automation Engine (`backend/n8n/workflows/`)
5 exportable production workflows:
- **Workflow 1: Guest Inquiry Processing**: Validates payload, invokes FastAPI AI inference, determines escalation status, and logs executions.
- **Workflow 2: Complaint Escalation**: Urgent complaint triage, MySQL state synchronization, and Duty Manager alerting.
- **Workflow 3: Automated Guest Follow-up**: Scheduled polling of unresolved tickets, drafting personalized check-in messages.
- **Workflow 4: Daily Support Summary**: Daily midnight cron calculating volume, resolution ratios, and executive digest.
- **Workflow 5: Workflow Error Monitoring**: Global Error Trigger capturing stack traces, recording failure records, and alerting administrators.

### D. Next.js 14 Dashboard (`frontend/`)
- Modern, responsive operations console built with Next.js 14 App Router, React 18, TypeScript, and Tailwind CSS.
- 8 dedicated views: Executive Dashboard, Conversations, Interactive AI Chat Sandbox, Booking Management, Escalations Triage, Knowledge Base CRUD, Automation Telemetry Monitoring, and Settings.
