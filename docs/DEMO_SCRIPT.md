# 15-Minute Technical Demonstration Script

## AIONOS ResolveIT — Evaluator Presentation Guide

This guide is designed for presenting a complete, defensible 15-minute technical walk-through to an AIONOS evaluator.

---

### Act 1: Introduction & Source Grounding (Minutes 0:00 – 3:00)
- **Goal**: Establish rigor and adherence to the Veridian Corp Data Pack.
- **Narrative**:
  - Show the Data Pack PDF source and explain how the system models KB-01 through KB-10, the Asset Management Policy extract, the 10 existing tickets, and 15 employee requests.
  - Highlight the core product tenet: **Dual-Layer Architecture**. The LLM operates under strict deterministic policy guardrails and cannot hallucinate or override policies.
  - Show the architecture diagram from `docs/ARCHITECTURE.md`.

---

### Act 2: Instant Self-Service & Zero-Ticket Deflection (Minutes 3:00 – 6:00)
- **Goal**: Demonstrate how common L1 inquiries are resolved immediately without ticket overhead.
- **Demo Scenario 1: REQ-02 (Vikram Chawla - Guest Wi-Fi)**:
  - *Click Scenario REQ-02*: "Can I get Wi-Fi access for a guest visiting our office tomorrow?"
  - *Observe*:
    - Intent detected: `Guest Wi-Fi Access`
    - Grounded citation: `KB-07: Guest Wi-Fi Access`
    - Outcome: `Resolved (no ticket needed)`. Clear instruction that any employee can generate 24h credentials at the front-desk kiosk.
- **Demo Scenario 2: REQ-05 (Sanjay Oberoi - VPN Credential Expired)**:
  - *Click Scenario REQ-05*: "My VPN stopped working this morning, says credentials expired."
  - *Observe*:
    - Citation: `KB-02: VPN Access` (90-day renewal cycle).
    - Outcome: Directs full-time employee to the self-service renewal workflow.

---

### Act 3: Multi-Policy Harmonization & Dual Approvals (Minutes 6:00 – 9:00)
- **Goal**: Show real-world enterprise nuance where multiple corporate policies intersect.
- **Demo Scenario 3: REQ-01 (Aditi Sharma - 3.5-year-old Dead Laptop)**:
  - *Click Scenario REQ-01*: "My laptop won’t turn on at all, it’s completely dead, had it about 3.5 years now."
  - *Observe*:
    - Cross-Policy Reconciliation:
      - `KB-03` allows replacement after 3 years or early failure with 2 weeks notice.
      - `ASSET-01` sets a 4-year refresh cycle, requiring **Finance sign-off** in addition to IT approval for early replacement (< 4 years).
    - Outcome: Creates structured ticket tagged for **Dual Approval** (IT + Finance).

---

### Act 4: High-Risk Security Escalation & Containment (Minutes 9:00 – 12:00)
- **Goal**: Demonstrate active hazard detection and immediate containment.
- **Demo Scenario 4: REQ-08 (Ananya Reddy - Phishing Forwarded Internally)**:
  - *Click Scenario REQ-08*: "I think I got a phishing email asking for my login — forwarding it to a few teammates to check."
  - *Observe*:
    - Agent catches the dangerous phrase: *"forwarding it to a few teammates to check"*.
    - Immediate High-Visibility Warning: Cites `KB-09` explicitly forbidding forwarding.
    - Instructs user to alert recipients and route to `security@veridian-corp.example`.
    - Automatically files a **P1 Critical Security Ticket**.
- **Demo Scenario 5: REQ-10 (Kavya Pillai - Urgent Admin Server Access)**:
  - *Click Scenario REQ-10*: "Can someone give me admin access to the finance reporting server? Need it urgently for month-end."
  - *Observe*:
    - Rejection of unilateral admin grant.
    - Cites precedent ticket **TK-1050** (Rejected admin access).
    - Requires formal written business justification and manager sign-off.

---

### Act 5: Ambiguity Handling & Diagnostic Questioning (Minutes 12:00 – 14:00)
- **Goal**: Prove the agent never hallucinates when given incomplete information.
- **Demo Scenario 6: REQ-15 (Rahul Menon - "hey can you help, its not working")**:
  - *Click Scenario REQ-15*.
  - *Observe*:
    - Agent refuses to guess.
    - State: `CLARIFICATION_REQUIRED`.
    - Prompts interactive diagnostic options: Is it Hardware, Account/Login, Network, or Software?
    - Demonstrates true agentic inquiry.

---

### Act 6: Observability, Historical Queue & Audit Logs (Minutes 14:00 – 15:00)
- **Goal**: Show production-grade auditability.
- **Walkthrough**:
  - Switch to **Ticket Queue** tab: View all 10 historical tickets (TK-1042 to TK-1051) and newly generated tickets.
  - Switch to **Audit Trail** tab: Inspect timestamped JSON audit records showing prompt, policy ID, decision outcome, and reason codes.
  - Conclude demonstration.
