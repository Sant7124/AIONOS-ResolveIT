# Formal Assumptions & Environmental Registry

## Product: Veridian IT Copilot
**AI-Powered Internal IT Service & Resolution Agent**

---

### 1. Temporal Anchoring & Simulation Horizon
- **Simulation Week**: Monday, 21 September 2026 – Friday, 25 September 2026.
- **Reference Base Date**: Monday, 21 September 2026 (`2026-09-21T09:00:00Z`).
- **Implications**:
  - All relative dates in requests (e.g. "Mon 21 Sep", "Tue 22 Sep", "tomorrow", "this morning", "next week") are evaluated with respect to the week of Sep 21–25, 2026.
  - Hardware age calculations (e.g. Aditi Sharma REQ-01: "had it about 3.5 years now") benchmark against Sep 2026 (issued approx. March 2023).
  - 90-day VPN credential expiry calculations evaluate within this calendar window.

---

### 2. Authority & Ground Truth Boundaries
- **Strict Data Pack Boundary**: As explicitly mandated in the assignment brief:
  > *"Use only the material below as the source data for your agent. Do not invent policies or information that isn't grounded in one of these sources."*
- **No Hallucinated Policies**: No additional corporate policies, SLA metrics, or approval chains may be invented outside KB-01 through KB-10 and the Asset Management Policy extract.
- **Historical Precedents as Ground Truth**:
  - The 10 historical tickets (TK-1042 to TK-1051) represent binding organizational precedents:
    - **TK-1050** establishes that administrative/privileged access requests submitted without written business justification and proper manager authorization must be rejected.
    - **TK-1045** demonstrates that mailbox quotas can be increased up to 35GB (below the 50GB cap) when backed by manager approval.
    - **TK-1043** confirms that laptop replacements between 3 and 4 years old require Finance sign-off in addition to IT approval.

---

### 3. Cross-Policy Harmonization
- **Laptop Replacement Policy Conflict Resolution**:
  - **KB-03** states: *"Laptops are eligible for replacement after 3 years of service, or earlier in case of verified hardware failure. Requests must be raised at least 2 weeks in advance of intended replacement."*
  - **Asset Management Policy (Extract)** states: *"All company-issued hardware, including laptops and monitors, follows a standard 4-year refresh cycle from date of issue. Early replacement outside this cycle requires Finance sign-off in addition to IT approval."*
  - **Harmonized Assumption**:
    - Under 3 years: Ineligible unless verified hardware failure is confirmed by diagnostic IT review. Requires both IT approval and Finance sign-off.
    - Between 3.0 and 4.0 years (e.g., REQ-01 3.5 years): Eligible under KB-03, but because it falls outside the standard 4-year Finance cycle, **it requires Finance sign-off in addition to IT approval**.
    - Over 4.0 years: Standard lifecycle replacement requiring standard IT fulfillment.

---

### 4. Security Incident Emergency Protocol
- **KB-09 Strict Enforcement**:
  - Suspected phishing emails, malware, or unauthorized access attempts must be routed immediately to `security@veridian-corp.example`.
  - In **REQ-08**, Ananya Reddy stated: *"forwarding it to a few teammates to check"*.
  - **Assumption**: The agent must treat internal forwarding of a suspected phishing email as an active security hazard. It must immediately issue a prominent warning advising the employee to notify recipients not to open or click any attachments/links, and escalate a Priority 1 (P1) Security ticket.

---

### 5. Authentication & Identity Boundaries
- All employees in the simulation possess email addresses ending in `@veridian-corp.example`.
- Passwords, secret tokens, or private keys must never be prompted for, ingested, stored, or displayed by the Copilot.
- Self-service portal links and front-desk kiosk procedures are the sanctioned paths for credentials and guest access.

---

### 6. Local & Offline Execution Fallback
- To ensure 100% defensibility and zero reliance on third-party cloud API availability during evaluator testing, the system provides a first-class **Deterministic Mock Provider**.
- When `LLM_PROVIDER=mock` (the default) or when external API keys are omitted, all 15 scenarios and open-ended queries are resolved via the deterministic policy rules engine.
