"""Comprehensive Benchmark Test Suite for Veridian IT Copilot Agent.
Covers all 15 core enterprise scenarios required by the assignment.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database.session import Base
from app.database.seed import seed_policies, seed_employee_requests, seed_tickets
from app.agents.it_agent import ITServiceAgent
from app.schemas.agent import AgentChatRequest

@pytest.fixture(scope="module")
def agent_fixture():
    """Initializes and seeds an isolated in-memory test database, returns ITServiceAgent instance and session."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    seed_policies(db)
    seed_employee_requests(db)
    seed_tickets(db)
    agent = ITServiceAgent(db)
    yield agent, db
    db.close()

# Scenario 1: Account locked after 6 attempts
def test_scenario_01_account_lockout(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="I'm locked out of my account, tried my password 6 times.",
        employee_name="Karan Mehta",
        employee_email="karan.mehta@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent == "account_lockout"
    assert resp.action == "ticket"
    assert "KB-01" in [s.policy_id for s in resp.sources]
    assert resp.ticket_id is not None
    assert "manual" in resp.message.lower() or "locked" in resp.message.lower()

# Scenario 2: Guest Wi-Fi for tomorrow
def test_scenario_02_guest_wifi(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="Can I get Wi-Fi access for a guest visiting our office tomorrow?",
        employee_name="Vikram Chawla",
        employee_email="vikram.chawla@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent == "guest_wifi"
    assert resp.action == "resolve"
    assert resp.ticket_id is None
    assert "KB-07" in [s.policy_id for s in resp.sources]
    assert "kiosk" in resp.message.lower()
    assert "24 hours" in resp.message.lower()

# Scenario 3: Non-catalog software
def test_scenario_03_non_catalog_software(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="Need approval to install a data-analysis tool that's not in the software catalog.",
        employee_name="Ritu Bhatia",
        employee_email="ritu.bhatia@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent == "software_installation"
    assert resp.action in ("ticket", "escalate")
    assert "KB-04" in [s.policy_id for s in resp.sources]
    assert "3–5 business days" in resp.message or "3-5" in resp.message
    assert resp.ticket_details.assigned_team == "Information Security (Infosec)"

# Scenario 4: Expired VPN
def test_scenario_04_expired_vpn(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="My VPN stopped working this morning, says credentials expired.",
        employee_name="Sanjay Oberoi",
        employee_email="sanjay.oberoi@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent in ("vpn_expired", "vpn_access")
    assert resp.action == "resolve"
    assert resp.ticket_id is None
    assert "KB-02" in [s.policy_id for s in resp.sources]
    assert "90 days" in resp.message

# Scenario 5: Printer issue
def test_scenario_05_printer_issue(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="Printer on the 3rd floor keeps showing 'paper jam' even though there's no jam.",
        employee_name="Meera Iyer",
        employee_email="meera.iyer@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent == "printer_issue"
    assert "KB-05" in [s.policy_id for s in resp.sources]
    # Recommends spooler restart first and asks for asset tag if problem persists
    assert "spooler" in resp.message.lower()
    assert "asset tag" in resp.message.lower()

# Scenario 6: Phishing email with dangerous forwarding
def test_scenario_06_phishing_incident(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="I think I got a phishing email asking for my login — forwarding it to a few teammates to check.",
        employee_name="Ananya Reddy",
        employee_email="ananya.reddy@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent == "security_incident"
    assert resp.action in ("ticket", "escalate")
    assert "KB-09" in [s.policy_id for s in resp.sources]
    assert "security@veridian-corp.example" in resp.message
    # Emergency warning must be present!
    assert "NOT to click" in resp.message or "MUST NOT be forwarded" in resp.message
    assert resp.ticket_details.priority == "P1 - Critical"

# Scenario 7: Expense tool login problem
def test_scenario_07_expense_tool_login(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="I can't log into the expense tool, keeps saying invalid credentials.",
        employee_name="Sneha Kulkarni",
        employee_email="sneha.kulkarni@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent == "expense_tool_access"
    assert "KB-08" in [s.policy_id for s in resp.sources]
    assert "finance" in resp.message.lower()

# Scenario 8: Admin access request
def test_scenario_08_admin_access_rejected(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="Can someone give me admin access to the finance reporting server? Need it urgently for month-end.",
        employee_name="Kavya Pillai",
        employee_email="kavya.pillai@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent == "admin_access"
    assert resp.action in ("reject", "escalate")
    assert "KB-08" in [s.policy_id for s in resp.sources]
    assert "business justification" in resp.message.lower() or "tk-1050" in resp.message.lower()

# Scenario 9: Laptop 3.5 years old and completely dead
def test_scenario_09_laptop_dead_3_point_5_years(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="My laptop won't turn on at all, it's completely dead, had it about 3.5 years now.",
        employee_name="Aditi Sharma",
        employee_email="aditi.sharma@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent == "laptop_replacement"
    assert resp.action in ("ticket", "escalate")
    source_ids = [s.policy_id for s in resp.sources]
    assert "KB-03" in source_ids
    assert "ASSET-01" in source_ids
    assert "Finance" in resp.message
    assert resp.ticket_id is not None

# Scenario 10: Laptop 2 years old with flickering screen
def test_scenario_10_laptop_2_years_screen_flicker(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="Laptop screen is flickering on and off, had it 2 years, might just need a fix not a replacement.",
        employee_name="Aman Gupta",
        employee_email="aman.gupta@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent in ("laptop_replacement", "hardware_issue")
    assert resp.action in ("ticket", "escalate")
    source_ids = [s.policy_id for s in resp.sources]
    assert "KB-03" in source_ids
    assert "ASSET-01" in source_ids
    # Must specify repair / diagnostic rather than replacement!
    assert "diagnostic" in resp.message.lower() or "repair" in resp.message.lower()

# Scenario 11: WFH equipment request (4 days remote)
def test_scenario_11_wfh_equipment(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="I've started working from home 4 days a week, how do I get a monitor?",
        employee_name="Farhan Ali",
        employee_email="farhan.ali@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent == "wfh_equipment"
    assert resp.action in ("escalate", "ticket")
    assert "KB-10" in [s.policy_id for s in resp.sources]
    assert "manager" in resp.message.lower()
    assert "finance" in resp.message.lower()

# Scenario 12: Contractor VPN request
def test_scenario_12_contractor_vpn(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="New contractor joining my team next week, they'll need VPN access.",
        employee_name="Nikhil Bansal",
        employee_email="nikhil.bansal@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent in ("vpn_access", "vpn_expired")
    assert resp.action in ("escalate", "ticket")
    assert "KB-02" in [s.policy_id for s in resp.sources]
    assert "manager" in resp.message.lower()
    assert "access request form" in resp.message.lower()

# Scenario 13: Mailbox full
def test_scenario_13_mailbox_quota(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="My mailbox is full and I can't send emails.",
        employee_name="Rohit Desai",
        employee_email="rohit.desai@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent == "mailbox_quota"
    assert "KB-06" in [s.policy_id for s in resp.sources]
    assert "archive" in resp.message.lower()
    assert "25gb" in resp.message.lower() or "50gb" in resp.message.lower()

# Scenario 14: Vague "it's not working" request (Clarification without hallucination)
def test_scenario_14_vague_request_triggers_clarification(agent_fixture):
    agent, db = agent_fixture
    req = AgentChatRequest(
        message="hey can you help, its not working",
        employee_name="Rahul Menon",
        employee_email="rahul.menon@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.intent == "unknown_it_issue"
    # MUST ask targeted follow-up question and NOT hallucinate a fix
    assert resp.action == "ask"
    assert len(resp.follow_up_questions) > 0
    assert resp.ticket_id is None
    assert "device" in resp.message.lower() or "system" in resp.message.lower()

# Scenario 15: Duplicate ticket prevention / ticket update
def test_scenario_15_duplicate_ticket_prevention(agent_fixture):
    agent, db = agent_fixture
    # S. Iyer already has active ticket TK-1043: "Laptop replacement (3.2 yrs old)"
    req = AgentChatRequest(
        message="Checking on my laptop replacement, it's completely dead and 3.2 yrs old.",
        employee_name="S. Iyer",
        employee_email="s.iyer@veridian-corp.example"
    )
    resp = agent.process_message(req)
    # Must recognize existing active ticket and NOT create a new duplicate ticket!
    assert resp.action == "update_ticket"
    assert resp.ticket_id == "TK-1043"
    assert "TK-1043" in resp.message
    assert "active ticket on file" in resp.message or "Notice:" in resp.message
