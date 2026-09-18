"""End-to-End System Integration Test Suite for AIONOS ResolveIT.
Validates all requirements from Master Prompt 5:
- Test cases A through J
- Multi-turn persistent conversation state
- Duplicate ticket prevention
- REST API endpoint completeness and contracts
- Deterministic policy grounding and audit logging
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import init_db, SessionLocal
from app.models import Policy, Ticket, EmployeeRequest, AuditEvent, Conversation
from app.database.seed import seed_policies, seed_employee_requests, seed_tickets, seed_initial_audit

@pytest.fixture(scope="module")
def client():
    """Setup test database and FastAPI test client."""
    init_db()
    db = SessionLocal()
    try:
        if db.query(Policy).count() == 0:
            seed_policies(db)
            seed_employee_requests(db)
            seed_tickets(db)
            seed_initial_audit(db)
    finally:
        db.close()

    with TestClient(app) as test_client:
        yield test_client

# ===========================================================================
# 1. Test Cases A through J from Master Prompt 5
# ===========================================================================

def test_scenario_a_account_locked_6_times(client):
    """A. 'My account is locked. I tried my password 6 times.'
    Expected: IT manual unlock path (KB-01, P2 ticket).
    """
    res = client.post("/api/chat", json={
        "message": "My account is locked. I tried my password 6 times.",
        "employee_name": "Rohan Mehta",
        "employee_email": "rohan.mehta@veridian-corp.example"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] in ["ticket", "update_ticket"]
    assert "manual" in data["message"].lower() or "unlock" in data["message"].lower()
    assert any(s["policy_id"] == "KB-01" for s in data["sources"])
    assert data["ticket_id"] is not None

def test_scenario_b_guest_wifi(client):
    """B. 'I need guest Wi-Fi tomorrow.'
    Expected: Explain 24-hour guest Wi-Fi generation through front desk kiosk; no IT ticket.
    """
    res = client.post("/api/chat", json={
        "message": "I need guest Wi-Fi tomorrow.",
        "employee_name": "Priya Sen",
        "employee_email": "priya.sen@veridian-corp.example"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] == "resolve"
    assert data["ticket_id"] is None
    assert "24 hours" in data["message"] or "kiosk" in data["message"]
    assert any(s["policy_id"] == "KB-07" for s in data["sources"])

def test_scenario_c_non_catalog_data_analysis(client):
    """C. 'I want to install a non-catalog data-analysis tool.'
    Expected: Security review / escalation (KB-04).
    """
    res = client.post("/api/chat", json={
        "message": "I want to install a non-catalog data-analysis tool.",
        "employee_name": "Marcus Vance",
        "employee_email": "marcus.vance@veridian-corp.example"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] in ["ticket", "escalate", "update_ticket"]
    assert "security" in data["message"].lower()
    assert any(s["policy_id"] == "KB-04" for s in data["sources"])
    assert "Security" in (data["escalation_team"] or data["ticket_details"]["assigned_team"])

def test_scenario_d_expired_vpn(client):
    """D. 'My VPN credentials expired.'
    Expected: VPN renewal guidance (KB-02).
    """
    res = client.post("/api/chat", json={
        "message": "My VPN credentials expired.",
        "employee_name": "Anita Roy",
        "employee_email": "anita.roy@veridian-corp.example"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] == "resolve"
    assert "renew" in data["message"].lower()
    assert "90 days" in data["message"]
    assert any(s["policy_id"] == "KB-02" for s in data["sources"])

def test_scenario_e_phishing_warning_not_to_forward(client):
    """E. 'I think I received a phishing email.'
    Expected: Immediate Security escalation and warning not to forward it to coworkers.
    """
    res = client.post("/api/chat", json={
        "message": "I think I received a phishing email.",
        "employee_name": "Vikram Patel",
        "employee_email": "vikram.patel@veridian-corp.example"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] in ["escalate", "ticket", "update_ticket"]
    assert "not forward" in data["message"].lower()
    assert "security@veridian-corp.example" in data["message"]
    assert any(s["policy_id"] == "KB-09" for s in data["sources"])
    assert data["ticket_details"]["priority"] == "P1 - Critical"

def test_scenario_f_expense_tool_credentials(client):
    """F. 'My expense tool says invalid credentials.'
    Expected: IT can assist with technical/login issue if account exists; if account existence is unknown, ask necessary question.
    """
    res = client.post("/api/chat", json={
        "message": "My expense tool says invalid credentials.",
        "employee_name": "Deepak Joshi",
        "employee_email": "deepak.joshi@veridian-corp.example"
    })
    assert res.status_code == 200
    data = res.json()
    # Should ask whether account already exists or was provisioned by Finance
    assert data["action"] == "ask"
    assert len(data["follow_up_questions"]) > 0
    assert any(s["policy_id"] == "KB-08" for s in data["sources"])

def test_scenario_g_admin_access_finance(client):
    """G. 'Can I get admin access to finance reporting?'
    Expected: Do not grant it automatically. Determine authorization/business justification and route appropriately based only on supplied data.
    """
    res = client.post("/api/chat", json={
        "message": "Can I get admin access to finance reporting?",
        "employee_name": "Carlos Gomez",
        "employee_email": "carlos.gomez@veridian-corp.example"
    })
    assert res.status_code == 200
    data = res.json()
    # Admin access without pre-approved justification is rejected per precedent TK-1050
    assert data["action"] in ["reject", "escalate"]
    assert "justification" in data["message"].lower() or "authorization" in data["message"].lower()
    assert any(s["policy_id"] == "KB-08" for s in data["sources"])

def test_scenario_h_laptop_dead_3_point_5_years(client):
    """H. 'My laptop is dead and 3.5 years old.'
    Expected: Apply laptop replacement + asset policy carefully; do not oversimplify.
    """
    res = client.post("/api/chat", json={
        "message": "My laptop is dead and 3.5 years old.",
        "employee_name": "Rachel Zane",
        "employee_email": "rachel.zane@veridian-corp.example"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] in ["ticket", "update_ticket"]
    assert "3.5" in data["message"] or "3" in data["message"]
    assert "finance" in data["message"].lower()  # Early replacement (<4 yrs) requires Finance signoff
    assert any(s["policy_id"] in ["KB-03", "ASSET-01"] for s in data["sources"])

def test_scenario_i_laptop_screen_flickers_2_years(client):
    """I. 'My laptop screen flickers. It is 2 years old.'
    Expected: Do not automatically approve replacement; investigate hardware failure and policy eligibility.
    """
    res = client.post("/api/chat", json={
        "message": "My laptop screen flickers. It is 2 years old.",
        "employee_name": "Devin Clark",
        "employee_email": "devin.clark@veridian-corp.example"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] in ["ticket", "update_ticket"]
    assert "diagnostic" in data["message"].lower() or "repair" in data["message"].lower()
    # Does NOT grant replacement, creates diagnostic ticket
    assert "replacement" not in data["status"].lower()
    assert any(s["policy_id"] in ["KB-03", "ASSET-01"] for s in data["sources"])

def test_scenario_j_vague_request(client):
    """J. 'hey can you help, its not working'
    Expected: Ask a useful clarification question.
    """
    res = client.post("/api/chat", json={
        "message": "hey can you help, its not working",
        "employee_name": "Samir Khan",
        "employee_email": "samir.khan@veridian-corp.example"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] == "ask"
    assert len(data["follow_up_questions"]) > 0
    assert "device" in data["follow_up_questions"][0].lower() or "system" in data["follow_up_questions"][0].lower()

# ===========================================================================
# 2. Multi-turn Persistent Conversation State Flow
# ===========================================================================

def test_multi_turn_conversation_continuity(client):
    """Verify that multi-turn dialogue maintains context and interprets answers properly:
    Turn 1: 'My laptop is flickering.' -> Agent asks 'How old is the laptop?'
    Turn 2: '2 years.' -> Agent synthesizes age and logs diagnostic repair ticket!
    """
    # Turn 1: User introduces issue without age
    t1_res = client.post("/api/chat", json={
        "message": "My laptop is flickering.",
        "employee_name": "Elena Rostova",
        "employee_email": "elena.rostova@veridian-corp.example"
    })
    assert t1_res.status_code == 200
    t1_data = t1_res.json()
    assert t1_data["action"] == "ask"
    assert "how old" in t1_data["follow_up_questions"][0].lower() or "age" in t1_data["follow_up_questions"][0].lower()
    conv_id = t1_data["conversation_id"]

    # Turn 2: User answers with just "2 years."
    t2_res = client.post("/api/chat", json={
        "message": "2 years.",
        "employee_name": "Elena Rostova",
        "employee_email": "elena.rostova@veridian-corp.example",
        "conversation_id": conv_id
    })
    assert t2_res.status_code == 200
    t2_data = t2_res.json()
    # Must NOT treat "2 years." as an unknown issue!
    assert t2_data["action"] in ["ticket", "update_ticket"]
    assert "diagnostic" in t2_data["message"].lower() or "repair" in t2_data["message"].lower()
    assert t2_data["conversation_id"] == conv_id

# ===========================================================================
# 3. Duplicate Ticket Prevention
# ===========================================================================

def test_duplicate_ticket_prevention(client):
    """When an employee has an active ticket and submits a new inquiry in the same category,
    the system must append to the existing ticket rather than creating a duplicate.
    """
    # Create first ticket
    res1 = client.post("/api/chat", json={
        "message": "My laptop won't turn on, it is completely dead and 4.5 years old.",
        "employee_name": "Alex Mercer",
        "employee_email": "alex.mercer@veridian-corp.example"
    })
    assert res1.status_code == 200
    first_ticket_id = res1.json()["ticket_id"]
    assert first_ticket_id is not None

    # Submit second inquiry for the same employee about laptop hardware
    res2 = client.post("/api/chat", json={
        "message": "Still waiting on my laptop replacement, any update?",
        "employee_name": "Alex Mercer",
        "employee_email": "alex.mercer@veridian-corp.example"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    # Must update or reference the existing ticket!
    assert data2["action"] == "update_ticket"
    assert data2["ticket_id"] == first_ticket_id

# ===========================================================================
# 4. REST API Endpoint Completeness & Contracts
# ===========================================================================

def test_rest_api_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "aionos-resolveit-api"

def test_rest_api_agent_status(client):
    res = client.get("/api/agent/status")
    assert res.status_code == 200
    data = res.json()
    assert data["operational"] is True
    assert data["database_connected"] is True
    assert data["knowledge_base_loaded"] is True
    assert data["knowledge_base_policy_count"] >= 11
    assert "status" in data

def test_rest_api_requests_crud(client):
    # GET /api/requests
    res = client.get("/api/requests")
    assert res.status_code == 200
    requests = res.json()["requests"]
    assert len(requests) >= 15

    # GET /api/requests/{id}
    res_single = client.get("/api/requests/REQ-01")
    assert res_single.status_code == 200
    assert res_single.json()["request_id"] == "REQ-01"

    # POST /api/requests
    post_res = client.post("/api/requests", json={
        "employee": "Kavita Rao",
        "email": "kavita.rao@veridian-corp.example",
        "request_text": "Need access to new design repository",
        "category": "Software & Applications"
    })
    assert post_res.status_code == 201
    created_req = post_res.json()
    assert created_req["employee"] == "Kavita Rao"
    assert created_req["request_id"].startswith("REQ-")

def test_rest_api_tickets_crud(client):
    # GET /api/tickets
    res = client.get("/api/tickets")
    assert res.status_code == 200
    tickets = res.json()["tickets"]
    assert len(tickets) >= 10

    # GET /api/tickets/{id}
    res_ticket = client.get("/api/tickets/TK-1042")
    assert res_ticket.status_code == 200
    assert res_ticket.json()["ticket_id"] == "TK-1042"

    # PATCH /api/tickets/{id}
    patch_res = client.patch("/api/tickets/TK-1042", json={
        "status": "Resolved",
        "resolution": "Account unlocked by admin",
        "append_notes": "Employee successfully verified over phone."
    })
    assert patch_res.status_code == 200
    updated_t = patch_res.json()
    assert updated_t["status"] == "Resolved"

def test_rest_api_policies_crud(client):
    # GET /api/policies
    res = client.get("/api/policies")
    assert res.status_code == 200
    policies = res.json()["policies"]
    assert len(policies) >= 11

    # GET /api/policies/{id}
    res_kb01 = client.get("/api/policies/KB-01")
    assert res_kb01.status_code == 200
    assert res_kb01.json()["id"] == "KB-01"

    res_asset = client.get("/api/policies/ASSET-01")
    assert res_asset.status_code == 200
    assert res_asset.json()["id"] == "ASSET-01"

def test_rest_api_audit_endpoints(client):
    # GET /api/audit
    res = client.get("/api/audit?limit=20")
    assert res.status_code == 200
    events = res.json()
    assert isinstance(events, list)
    assert len(events) > 0

    # GET /api/audit/{request_id}
    first_event = events[0]
    target_id = first_event.get("conversation_id") or first_event.get("ticket_id") or "TK-1042"
    res_filtered = client.get(f"/api/audit/{target_id}")
    assert res_filtered.status_code == 200
    assert isinstance(res_filtered.json(), list)
