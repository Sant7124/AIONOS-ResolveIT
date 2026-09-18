# AIONOS ResolveIT

> **AI-Powered Internal IT Service & Resolution Agent**  
> *An AIONOS Agentic AI Factory Enterprise Production System*

---

## 1. Executive Summary

**AIONOS ResolveIT** is a production-oriented, policy-governed internal IT service desk agent developed for Veridian Corp. Grounded strictly in the authoritative **Assignment 2 Data Pack**, the agent automates Level-1 IT triage, enforces corporate policy boundaries, reconciles overlapping regulations, guides self-service resolutions, safely escalates critical security events and approval bottlenecks, and maintains an immutable audit trail.

### Product Tenets
1. **Policy First**: Zero policy hallucination. Only policies present in the Data Pack (`KB-01` to `KB-10` and `ASSET-01`) are recognized.
2. **Dual-Layer Decision Architecture**: An outer deterministic rule engine enforces hard constraints (security containment, admin privilege restrictions, lockout thresholds) so the LLM cannot override company policy.
3. **Multi-Policy Harmonization**: Handles complex cross-policy intersections (e.g. reconciling `KB-03` 3-year laptop replacement with `ASSET-01` 4-year Finance refresh cycle).
4. **Interactive Clarification**: Never guesses on underspecified inquiries (e.g. `REQ-15` *"hey can you help, its not working"*).
5. **Auditable & Explainable**: Every decision generates a structured audit event with verbatim policy citations.
6. **100% Offline Defensible**: Fully functional out-of-the-box using the built-in deterministic provider without requiring third-party cloud API keys.

---

## 2. System Architecture

```
/
├── frontend/                     # React 18 + TypeScript + Vite + Tailwind CSS Console
│   ├── src/
│   │   ├── components/           # Header, Sidebar, AgentWorkspace, KnowledgeBase, TicketQueue, etc.
│   │   ├── services/             # Type-safe API client
│   │   ├── types/                # TypeScript domain models
│   │   └── App.tsx               # Primary application orchestrator
│   └── package.json
│
├── backend/                      # Python FastAPI Enterprise Service
│   ├── app/
│   │   ├── api/                  # REST API routes (/health, /api/info, /api/policies, etc.)
│   │   ├── core/                 # Configuration & environment settings
│   │   ├── agents/               # LLM provider abstraction & agent orchestration
│   │   ├── policy/               # Deterministic policy guardrails & business rules
│   │   ├── retrieval/            # Grounded knowledge base & ticket precedent search
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic input/output schemas
│   │   ├── database/             # SQLite persistence layer
│   │   ├── audit/                # Immutable audit logger
│   │   └── main.py               # FastAPI application entry point
│   ├── tests/                    # Automated pytest test suite
│   ├── requirements.txt
│   └── .env.example
│
├── data/                         # Ground Truth Data Pack Fixtures
│   ├── policies/                 # KB-01 to KB-10 + Asset Management Extract JSON
│   ├── employee_requests/        # REQ-01 to REQ-15 Benchmark Scenarios
│   ├── tickets/                  # TK-1042 to TK-1051 Seed Tickets & Precedents
│   └── seed/
│
├── docs/                         # Formal Engineering Specifications
│   ├── PRD.md                    # 20-Section Product Requirements Document
│   ├── ARCHITECTURE.md           # Deep-dive System Architecture & Mermaid Diagrams
│   ├── FLOW.md                   # Agentic Workflow & Decision Trees
│   ├── ASSUMPTIONS.md            # Environmental Assumptions & Temporal Anchoring
│   ├── AI_TOOLS.md               # AI Provider Abstraction (Mock, OpenAI, Gemini)
│   └── DEMO_SCRIPT.md            # 15-Minute Technical Demonstration Guide
│
└── README.md
```

---

## 3. Quick Start (Local Setup)

### Prerequisites
- **Python**: 3.10+ (tested on Python 3.13)
- **Node.js**: 18+ (tested on Node 22)
- **npm**: 9+

---

### Step 1: Start the FastAPI Backend

```bash
# From repository root
cd backend

# Install Python dependencies
python -m pip install -r requirements.txt

# Run the backend server
python -m uvicorn app.main:app --reload --port 8000
```

- API Server: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

---

### Step 2: Start the Enterprise Frontend Console

In a separate terminal window:

```bash
# From repository root
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```

- Frontend Console: `http://localhost:5173`

---

## 4. Automated Testing & Verification

Run the automated backend test suite:
```bash
python -m pytest backend/tests/test_health.py -v
```

Run frontend typecheck and production build:
```bash
cd frontend
npm run build
```

---

## 5. Temporal Simulation Context
- **Simulation Week**: Monday, 21 September 2026 – Friday, 25 September 2026.
- **Reference Date**: `2026-09-21T09:00:00Z`.
- All credential expirations (90 days) and hardware age calculations (e.g. Aditi Sharma's 3.5-year-old laptop) evaluate against this horizon.

---

## 6. Authoritative Ground Truth Data

### Policies (KB-01 through KB-10 + Asset Policy)
- **KB-01**: Password Reset (Self-service portal; manual unlock if > 5 failed attempts).
- **KB-02**: VPN Access (Automatic for full-time; manager sign-off for contractors; 90-day renewal).
- **KB-03**: Laptop Replacement (Eligible after 3 years or verified failure; 2 weeks notice).
- **KB-04**: Software Installation (Catalog self-installed; non-catalog requires 3–5 day Security review).
- **KB-05**: Printer Troubleshooting (Restart spooler first; persists -> log ticket with printer asset tag).
- **KB-06**: Mailbox Quota (Default 25GB; increases >25GB require manager approval and capped at 50GB).
- **KB-07**: Guest Wi-Fi (24-hour credentials at front-desk kiosk; no ticket required).
- **KB-08**: Expense Software Access (Access granted by Finance; IT only supports technical login issues).
- **KB-09**: Security Incident Reporting (Immediate report to `security@veridian-corp.example`; **NEVER** forward internally).
- **KB-10**: Work-From-Home Equipment (>3 days remote eligible for chair/monitor; manager + Finance sign-off; IT ships post-approval).
- **ASSET-01**: Asset Management Policy (Extract) (Standard 4-year refresh; early replacement requires Finance sign-off + IT approval).

### 15 Benchmark Employee Scenarios
The frontend includes one-click loading for all 15 scenarios from Section 2 of the Data Pack (`REQ-01` to `REQ-15`), including complex edge cases:
- `REQ-01`: 3.5-year dead laptop -> triggers dual IT + Finance approval workflow.
- `REQ-02`: Guest Wi-Fi -> zero-ticket self-service deflection.
- `REQ-03`: Locked out after 6 attempts -> manual IT unlock ticket.
- `REQ-08`: Phishing forwarded to teammates -> emergency containment alert + P1 ticket.
- `REQ-10`: Urgent admin server access -> rejection based on precedent `TK-1050`.
- `REQ-15`: *"hey can you help, its not working"* -> clarification loop, no hallucination.

---

## 7. 15-Minute Evaluation Guide
Follow [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) for a structured 6-act demonstration covering ground truth adherence, deflection, security emergency containment, multi-policy harmonization, ambiguity resolution, and audit logs.
