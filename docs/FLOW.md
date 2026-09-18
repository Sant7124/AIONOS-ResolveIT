# Process Flow Documentation

## Product: Veridian IT Copilot
**Agentic Workflow & Decision Trees**

---

### 1. End-to-End Agentic Execution Pipeline

Every user request submitted to the agent executes via the following deterministic 10-step sequence:

```mermaid
sequenceDiagram
    autonumber
    actor Employee
    participant UI as Enterprise IT Console
    participant Gateway as FastAPI Router
    participant Agent as Agent Orchestrator
    participant Retrieval as RAG Retrieval Engine
    participant Guard as Deterministic Policy Guard
    participant DB as SQLite / Audit Logger

    Employee->>UI: Submits Request (e.g. "My laptop won't turn on, had it 3.5 yrs")
    UI->>Gateway: POST /api/agent/chat (payload + employee context)
    Gateway->>Agent: Process Request
    Agent->>Retrieval: Search KB Policies & Ticket Precedents
    Retrieval-->>Agent: Returns Matches (KB-03, ASSET-01, TK-1043)
    Agent->>Guard: Evaluate Entity Completeness & Rules
    alt Missing Critical Information (e.g. REQ-15 "it's not working")
        Guard-->>Agent: Trigger CLARIFY (Prompt for device/account details)
        Agent->>DB: Log Audit Event (Outcome: CLARIFY)
        Agent-->>UI: Return Diagnostic Clarification Questions
        UI-->>Employee: Present Structured Clarification Prompt
    else Actionable Request
        Guard->>Guard: Check Hard Constraints (Phishing/Admin/Lockout)
        alt P1 Security Emergency (e.g. REQ-08 Phishing Forwarded)
            Guard-->>Agent: Immediate Quarantine & P1 Security Ticket
        else Standard Self-Service (e.g. REQ-02 Guest Wi-Fi)
            Guard-->>Agent: Resolve directly with self-service guidance (No ticket)
        else Policy Requiring Approvals (e.g. REQ-01 Dual IT/Finance)
            Guard-->>Agent: Create Escalated Ticket with Dual Approval flags
        end
        Agent->>DB: Persist Ticket & Write Audit Event
        Agent-->>UI: Return Structured Response + Policy Citations + Action Summary
        UI-->>Employee: Render Resolution / Ticket Card + Policy Intelligence
    end
```

---

### 2. Decision Trees by Category

#### 2.1 Hardware Replacement & Diagnostics (KB-03 & ASSET-01)
```mermaid
flowchart TD
    Start[Hardware Request Submitted] --> CheckAge{Verify Device Age}
    CheckAge -- "< 3 Years" --> CheckFailure{Verified Hardware Failure?}
    CheckFailure -- "No (e.g. REQ-13 Screen Flicker)" --> RouteRepair[Route to Hardware Diagnostic & Repair Technician<br/>Do NOT issue replacement ticket]
    CheckFailure -- "Yes (Verified Unrecoverable)" --> EarlyReq[Eligible for Early Replacement<br/>Requires Finance Sign-off + IT Approval]
    CheckAge -- ">= 3 Years and < 4 Years (e.g. REQ-01 3.5 yrs)" --> DualApprove[Eligible per KB-03 (>3 yrs)<br/>Mandate Finance Sign-off per ASSET-01 (<4 yrs)<br/>2 Weeks advance notice notice]
    CheckAge -- ">= 4 Years" --> StandardRefresh[Eligible per standard 4-year cycle<br/>Standard IT Approval]
```

#### 2.2 Security Incident Containment (KB-09)
```mermaid
flowchart TD
    SecStart[Suspected Security Incident Submitted] --> PhishCheck{Type of Incident}
    PhishCheck -- "Phishing / Malware / Breach" --> ForwardCheck{Has user forwarded email internally?}
    ForwardCheck -- "Yes (e.g. REQ-08)" --> EmergencyAction["CRITICAL WARNING:<br/>1. Cease forwarding immediately.<br/>2. Notify teammates to ignore/not click.<br/>3. Forward solely to security@veridian-corp.example.<br/>4. Auto-escalate P1 Security Ticket."]
    ForwardCheck -- "No" --> StdSecAction["Instruct user to report to security@veridian-corp.example.<br/>Log P1 Security Ticket."]
```

#### 2.3 Access & Authentication (KB-01, KB-02, KB-08)
```mermaid
flowchart TD
    AuthStart[Authentication / Access Request] --> SubType{Determine Subtype}
    
    SubType -- "Password Issue (KB-01)" --> LockoutCheck{Attempts >= 5?}
    LockoutCheck -- "Yes (e.g. REQ-03, 6 attempts)" --> ManualUnlock[Self-service locked.<br/>IT Helpdesk Manual Account Unlock Ticket required.<br/>No managerial approval needed.]
    LockoutCheck -- "No (< 5 attempts)" --> SelfResetPortal[Direct user to Self-Service Password Portal.<br/>No ticket required.]

    SubType -- "VPN Access (KB-02)" --> EmpType{Full-time or Contractor?}
    EmpType -- "Full-time (e.g. REQ-05)" --> CheckExpired{Credentials Expired?}
    CheckExpired -- "Yes (90-day renewal)" --> SelfRenewal[Guide employee to 90-day self-renewal workflow.]
    CheckExpired -- "No / New Setup" --> AutoProvision[Automatic access granted.]
    EmpType -- "Contractor (e.g. REQ-11)" --> MgrForm[Manager must submit formal Access Request Form.<br/>Manager approval mandatory.]

    SubType -- "Privileged / Admin Access (KB-08, TK-1050)" --> RejectGrant["DO NOT GRANT DIRECTLY.<br/>Precedent TK-1050: Mandatory written business justification +<br/>Manager & Security approval."]
```

---

### 3. Missing Information Resolution Loop

When an employee submits an ambiguous or underspecified prompt (e.g. **REQ-15**: *"hey can you help, its not working"* or **REQ-06** without asset tag):

```mermaid
flowchart LR
    A[Raw Ambiguous Input] --> B[Intent Confidence < 0.6 or Missing Slot]
    B --> C[Generate Targeted Clarification]
    C --> D[Render Interactive Input Card in UI]
    D --> E[Employee Supplies Missing Parameter]
    E --> F[Re-evaluate Complete Request]
    F --> G[Execute Grounded Decision]
```

Clarification Rules:
1. **Never guess the system**: If an employee says "it's not working", ask:
   - What device, application, or network are you using?
   - What specific error message or visual behavior is occurring?
   - When did the issue begin?
2. **Missing Asset Tag (Printers - KB-05)**:
   - Provide print spooler restart instructions.
   - Prompt: "If the spooler restart does not clear the paper jam, please provide the printer asset tag (e.g., VER-PRN-02-04) so we can dispatch a floor technician."
