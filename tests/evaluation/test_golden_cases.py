"""Automated Golden Test Runner executing all 20 deterministic benchmark scenarios.
Validates Intent, Action, Policy Grounding, Citations, Ticket Lifecycle, and Audit Trails.
"""
import json
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.database.seed import seed_policies, seed_employee_requests, seed_tickets
from app.agents.it_agent import ITServiceAgent
from app.schemas.agent import AgentChatRequest

GOLDEN_CASES_PATH = Path(__file__).resolve().parent / "golden_cases.json"

def load_golden_cases():
    with open(GOLDEN_CASES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("cases", [])

@pytest.fixture
def fresh_agent():
    """Create an isolated, seeded in-memory SQLite database for each test case."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        seed_policies(db)
        seed_employee_requests(db)
        seed_tickets(db)
        agent = ITServiceAgent(db)
        yield agent, db
    finally:
        db.close()

@pytest.mark.parametrize("case", load_golden_cases(), ids=lambda c: f"Case_{c['case_id']:02d}_{c['title'].replace(' ', '_')}")
def test_golden_case_execution(fresh_agent, case):
    agent, db = fresh_agent

    req = AgentChatRequest(
        message=case["input_message"],
        employee_name=case["employee_name"],
        employee_email=case["employee_email"]
    )

    resp = agent.process_message(req)

    # 1. Verify Intent Classification
    assert resp.intent == case["expected_intent"], (
        f"Case {case['case_id']} Intent mismatch: got '{resp.intent}', expected '{case['expected_intent']}'"
    )

    # 2. Verify Deterministic Action
    assert resp.action == case["expected_action"], (
        f"Case {case['case_id']} Action mismatch: got '{resp.action}', expected '{case['expected_action']}'"
    )

    # 3. Verify Policy Grounding & Citations
    actual_policy_ids = [s.policy_id for s in resp.sources]
    for expected_pid in case["expected_policy_ids"]:
        assert expected_pid in actual_policy_ids, (
            f"Case {case['case_id']} missing expected policy {expected_pid} in citations: {actual_policy_ids}"
        )
    if not case["expected_policy_ids"]:
        assert len(actual_policy_ids) == 0 or resp.action == "ask", (
            f"Case {case['case_id']} should not cite policies without grounding: {actual_policy_ids}"
        )

    # 4. Verify Ticket Creation / Duplicate Prevention
    if case["expected_action"] == "update_ticket":
        assert resp.ticket_id == "TK-1043", f"Case {case['case_id']} expected reference to TK-1043, got {resp.ticket_id}"
    elif case["expected_ticket"]:
        assert resp.ticket_id is not None, f"Case {case['case_id']} expected ticket creation, got None"
    else:
        assert resp.ticket_id is None, f"Case {case['case_id']} unexpected ticket created: {resp.ticket_id}"

    # 5. Verify Priority if ticket/escalation
    if case.get("expected_priority") and resp.ticket_details:
        assert resp.ticket_details.priority == case["expected_priority"]

    # 6. Verify Content: Required and Forbidden phrases
    msg_lower = resp.message.lower()
    for req_phrase in case.get("required_phrases", []):
        assert req_phrase.lower() in msg_lower, (
            f"Case {case['case_id']} message missing required phrase '{req_phrase}'. Response: {resp.message}"
        )

    for forbid_phrase in case.get("forbidden_phrases", []):
        assert forbid_phrase.lower() not in msg_lower, (
            f"Case {case['case_id']} message contained forbidden phrase '{forbid_phrase}'. Response: {resp.message}"
        )

    # 7. Verify Audit Event Generation
    assert resp.audit_event_id is not None
    assert resp.audit_event_id.startswith("EV-")
