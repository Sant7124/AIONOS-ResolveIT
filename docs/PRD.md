# Product Requirements Document (PRD)

## Product Name
**AIONOS ResolveIT — AI-Powered Internal IT Service & Resolution Agent**

## Document Version & Temporal Anchor
- **Version**: 1.0.0
- **Simulation Week**: Monday, 21 September 2026 – Friday, 25 September 2026
- **Source of Truth**: *Veridian Corp Data Pack — Assignment 2: Internal Service Agent (IT Support)*

---

### 1. Product Overview
**AIONOS ResolveIT** is an enterprise-grade, agentic AI internal IT service desk system built for Veridian Corp employees and IT support operations. Unlike superficial LLM chatbots, AIONOS ResolveIT behaves as an intelligent, policy-governed IT operations agent. It classifies user intent, queries an authoritative internal Knowledge Base (KB-01 through KB-10 and the Asset Management Policy extract), references historical ticket records (TK-1042 through TK-1051), identifies missing parameters, applies strict deterministic guardrails, executes self-service resolutions, routes escalations, issues structured tickets, provides verifiable policy citations, and maintains an unalterable audit log.

---

### 2. Problem Statement
In high-velocity enterprise environments like Veridian Corp:
1. **L1 Ticket Congestion**: Up to 40% of IT requests involve repetitive self-service tasks (e.g., guest Wi-Fi, 90-day VPN renewals, self-service password resets).
2. **Policy Drift & Hallucination**: Human agents and generic chatbots routinely misinform employees regarding hardware refresh cycles (confusing the 3-year laptop replacement rule with the 4-year Asset Management policy) or mishandle privileged access requests.
3. **Escalation Mishaps**: Critical security events (such as phishing emails being forwarded internally) are often not halted immediately, while valid requests stall due to missing asset tags or lack of documented approvals.
4. **Lack of Auditability**: IT support actions are frequently scattered across email threads and chat transcripts without structured traceability to governing corporate policies.

---

### 3. Target Users
1. **Veridian Employees (End-Users)**:
   - Requesting assistance with authentication, hardware malfunctions, software installations, remote work setups, or network connectivity.
   - Requiring immediate, clear, policy-grounded guidance without jargon.
2. **IT Support Engineers (L1 / L2 Dispatchers)**:
   - Triaging escalated tickets, inspecting agent reasoning, verifying diagnostic evidence (e.g., asset tags, screenshot logs), and executing physical or admin actions.
3. **IT Managers & Department Approvers**:
   - Reviewing requests exceeding default thresholds (e.g., mailbox quota increases > 25GB, contractor VPN access, home office equipment sign-offs).
4. **Information Security & Governance Teams**:
   - Overseeing immediate P1 incident containment (e.g., phishing alerts, unapproved software reviews, server admin access denials).

---

### 4. User Journey
The end-to-end journey follows a 7-stage deterministic agentic loop:
```
[1. User Submission]
       ↓
[2. Intent & Scope Classification]
       ↓
[3. Knowledge Retrieval & Historical Check]
       ↓
[4. Information Completeness Evaluation]
       ├── (Missing Critical Info) → Prompt Clarification Question (Wait)
       └── (Complete) → Proceed
       ↓
[5. Policy Enforcement & Decision Engine]
       ├── Instant Resolution (Self-Service)
       ├── Guided Workflow (Diagnostics)
       └── Escalation & Ticket Generation (Dual Approval / Security / Finance)
       ↓
[6. Structured Response with Policy Citations]
       ↓
[7. Audit Event Recording]
```

---

### 5. Business Goals & Success Metrics
- **Zero Policy Hallucination (100% Policy Grounding)**: Every substantive instruction or decision MUST map directly to an authoritative KB/Asset document.
- **Deflection of Standard L1 Requests**: Target ≥ 35% automated resolution for cataloged self-service tasks (guest Wi-Fi, password reset portal links, standard VPN renewals).
- **Zero Security Policy Breaches**: 100% immediate containment instructions for security incidents (KB-09) and 0% unauthorized granting of admin privileges (KB-08 / TK-1050 precedent).
- **Reduced Ticket Cycle Time**: Reduce mean time to first response (MTTFR) to < 3 seconds.
- **Explainability**: 100% of agent resolutions must display the exact policy ID, clause snippet, and decision rationale.

---

### 6. Functional Requirements
1. **Natural Language Understanding**: Multi-turn conversational interface capable of parsing technical and colloquial employee requests.
2. **Deterministic Intent Classifier**: Mapping inquiries to 7 core IT domains:
   - Authentication (KB-01)
   - Network & Remote Access (KB-02, KB-07)
   - Hardware & Peripherals (KB-03, KB-05, Asset Management Policy)
   - Software & Applications (KB-04, KB-08)
   - Email & Collaboration (KB-06)
   - Facilities & WFH (KB-10)
   - Information Security (KB-09)
3. **Grounded Retrieval Engine**: Exact match and semantic matching against corporate policy documents, returning Policy IDs, titles, and governing text.
4. **Ticket Context Awareness**: Real-time cross-referencing against the 10 existing ticket queue items to verify historical precedents (e.g., TK-1050 admin rejection precedent).
5. **Interactive Clarification Engine**: Automated follow-up questioning when mandatory parameters are absent (e.g., missing asset tag for printers, unspecified failure details).
6. **Escalation & Ticket Creation**: Automatic creation of structured tickets with priority (P1 Critical, P2 High, P3 Medium, P4 Low), category, assigned queue, and approval gates.
7. **Audit Log System**: Structured JSON-based audit log capturing timestamp, employee, request, retrieved policy, decision, action, and reasoning.

---

### 7. Non-Functional Requirements
- **Performance**: API response time < 1000ms for retrieval & policy evaluation; streaming UI support.
- **Local Portability**: Runs locally out-of-the-box with zero mandatory external SaaS accounts (offline deterministic mock mode included).
- **Reliability & Fail-Safety**: If an external LLM fails or is unconfigured, system falls back gracefully to the deterministic rule engine without crashing.
- **Maintainability**: Clear separation between UI presentation, API routes, agentic orchestration, retrieval layer, and persistence models.

---

### 8. Agent Responsibilities & Boundary Definition
| Responsibility | Agent Bound |
|---|---|
| **Understands User Intent** | Yes, categorizes issue and extracts entities (age, device, software name). |
| **Applies Policy** | Yes, enforces KB-01 through KB-10 and Asset Management guidelines. |
| **Executes Self-Service** | Yes, provides direct links, renewal instructions, kiosk directions. |
| **Grants Privileged Access** | **NO.** Strictly prohibited. Must route to formal approval workflow. |
| **Overrides Approvals** | **NO.** Quota > 25GB, contractor VPN, WFH equipment require human sign-off. |
| **Bypasses Security Review** | **NO.** Non-catalog software must undergo 3–5 day Infosec review. |

---

### 9. Policy-Grounding Rules
1. **Rule of Canonical Precedence**: The system must NOT generate any statement, SLA, or requirement not present in the supplied Data Pack.
2. **Dual-Policy Hardware Reconciliation**:
   - KB-03 permits laptop replacement after 3 years or upon verified hardware failure (with 2 weeks advance notice).
   - Asset Management Policy requires a standard 4-year refresh cycle.
   - **Resolution Rule**: If laptop is between 3 and 4 years (e.g., REQ-01, 3.5 years), replacement is eligible under KB-03 but **MUST mandate Finance sign-off** in addition to IT approval.
3. **Explicit Citation Requirement**: Every response must clearly present `Policy Reference: [KB-XX: Title]`.

---

### 10. Escalation Rules
- **P1 Security Emergency**:
  - *Trigger*: Phishing (KB-09), malware, unauthorized access attempts, or forwarding malicious emails.
  - *Action*: Immediate warning banner, instruction NOT to forward, automatic escalation to `security@veridian-corp.example`.
- **Administrative / Privileged Access**:
  - *Trigger*: Admin access requests to core servers/tools (KB-08, TK-1050).
  - *Action*: Reject automatic granting; require written business justification and managerial/security sign-off.
- **Non-Catalog Software Installation**:
  - *Trigger*: Request for application not listed in approved catalog (KB-04).
  - *Action*: Route to IT Security review with 3–5 business days SLA.
- **Commercial & Expense Approvals**:
  - *Trigger*: Expense tool provisioning (KB-08), WFH monitor/chair allowance (KB-10).
  - *Action*: Direct to Finance approval workflow; IT handles shipping only post-approval.

---

### 11. Ticket Lifecycle Workflow
```
[Initiated] 
    ↓
[Evaluation: Resolution vs Ticket]
    ├── (Self-Service) → [Status: Resolved (closed)]
    └── (Action Required) → [Status: Active]
              ├── Type: Security Review (SLA: 3-5 days)
              ├── Type: Finance Sign-off Pending
              ├── Type: Technician Investigation (Asset Tag Required)
              └── Type: Manager Approval Required
```

---

### 12. Audit Requirements
Every interaction produces an immutable audit record containing:
- `event_id`: UUIDv4
- `timestamp`: ISO-8601 (anchored in simulation date September 2026)
- `employee_id` / `email`: Requester identity
- `raw_prompt`: Exact text submitted
- `intent_detected`: Classified category
- `retrieved_policies`: List of matched Policy IDs with match confidence
- `decision_outcome`: `RESOLVE`, `CLARIFY`, `ESCALATE`, `REJECT`
- `action_taken`: Concrete system action (ticket generated, link sent, warning raised)
- `policy_citation`: Quoted text from Data Pack

---

### 13. Source Citation Requirements
UI elements must visually highlight citations using a dedicated "Policy Intelligence" card:
- Badge displaying `Policy ID` (e.g. `KB-04`, `ASSET-01`)
- Title of the policy
- Exact excerpt text from the official documentation
- Direct link to official policy guidelines

---

### 14. Enterprise UI/UX Requirements
- **Design System**: Dark navy / deep slate palette (`#080d1a`, `#0f172a`, `#1e293b`) with high-contrast electric cyan (`#06b6d4`) and crisp white typography.
- **Tri-Pane Workspace**:
  1. *Left Navigation*: Service Desk Console, Ticket Queue, Policy Knowledge Base, Scenario Test Bench (REQ-01 to REQ-15).
  2. *Center Command Center*: Live agent chat stream, interactive clarification cards, action resolution badges.
  3. *Right Context Inspector*: Grounded Policy Citations, Historical Precedent Tickets, Real-Time Audit Log.
- **Quick-Fill Scenarios**: Instant selector for all 15 employee requests from the Data Pack for rapid evaluator demonstration.

---

### 15. Error Handling & Edge Cases
- **Ambiguous Inputs** (e.g., REQ-15 "hey can you help, its not working"):
  - Agent must not hallucinate an issue.
  - Automatically transitions to `CLARIFICATION_REQUIRED` state and prompts structured diagnostic questions.
- **Backend Disconnection / LLM Outage**:
  - Automatic fallback to deterministic rules engine.
  - UI displays visible system status indicator (Offline / Fallback / Live).

---

### 16. Security & Privacy Principles
- Zero unauthorized privilege escalation.
- Passwords and secret credentials must never be requested or displayed in plaintext.
- Strict validation of employee email domains (`@veridian-corp.example`).

---

### 17. Evaluation Strategy & Benchmark Matrix
Validation test suite testing all 15 requests from the Data Pack:
- REQ-01: Hardware age 3.5 yr -> Dual IT/Finance approval ticket generated.
- REQ-02: Guest Wi-Fi -> Kiosk self-service, no ticket required.
- REQ-03: Password lockout (6 attempts) -> Manual IT unlock required (exceeds 5 attempts).
- REQ-04: Non-catalog software -> 3-5 day Security review ticket generated.
- REQ-05: VPN expired -> 90-day renewal self-service instructions.
- REQ-06: Printer jam -> Spooler restart check + Asset Tag prompt.
- REQ-07: WFH monitor -> Manager sign-off + Finance processing.
- REQ-08: Phishing forward -> Emergency warning to cease forwarding + P1 Security alert.
- REQ-09: Mailbox quota full -> Archiving tips + Manager approval form for >25GB (max 50GB).
- REQ-10: Admin access -> Deny direct grant + business justification requirement.
- REQ-11: Contractor VPN -> Manager approval submission requirement.
- REQ-12: Expense tool login -> Check account creation with Finance vs IT login issue.
- REQ-13: Laptop screen flicker (2 yrs) -> Hardware diagnostic repair ticket, NO replacement.
- REQ-14: Browser extension -> Security review routing.
- REQ-15: Underspecified "its not working" -> Clarification prompt, no hallucination.

---

### 18. Demo Scenarios (15-Minute Evaluator Script)
1. **0:00 - 3:00**: Architecture, Ground Truth constraints, Data Pack alignment.
2. **3:00 - 6:00**: Instant Self-Service & Deflection (REQ-02 Guest Wi-Fi, REQ-05 VPN Renewal).
3. **6:00 - 9:00**: Complex Policy Conflict & Multi-Approval (REQ-01 3.5-yr Laptop Replacement vs Asset Management 4-yr cycle).
4. **9:00 - 12:00**: Critical Security Incident (REQ-08 Phishing with dangerous forwarding behavior).
5. **12:00 - 14:00**: Ambiguity Handling (REQ-15 Incomplete request & diagnostic follow-up).
6. **14:00 - 15:00**: Ticket Queue, Historical Precedents (TK-1050 Admin Rejection), and Audit Logs.

---

### 19. Future Scalability
- Vector Database pluggability (ChromaDB / Qdrant) via modular retrieval interface.
- Slack / Microsoft Teams Webhook adapter.
- ITSM bi-directional sync (ServiceNow, Jira Service Management).

---

### 20. Explicitly Out-of-Scope Functionality
- Direct automated resetting of Active Directory passwords bypassing official self-service portal.
- Unilateral provisioning of administrative server credentials.
- Purchasing or ordering hardware without Finance department budget sign-off.
