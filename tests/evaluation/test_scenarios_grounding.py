"""Evaluation suite verifying Data Pack Ground Truth adherence."""
import json
from pathlib import Path
import pytest

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

@pytest.fixture
def policies_data():
    with open(DATA_DIR / "policies" / "knowledge_base.json", "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def requests_data():
    with open(DATA_DIR / "employee_requests" / "requests.json", "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def tickets_data():
    with open(DATA_DIR / "tickets" / "seed_tickets.json", "r", encoding="utf-8") as f:
        return json.load(f)

def test_ground_truth_policy_count(policies_data):
    """Verify that all 10 KB policies plus Asset Management policy are present."""
    policies = policies_data.get("policies", [])
    assert len(policies) == 11
    ids = {p["id"] for p in policies}
    expected_ids = {f"KB-{i:02d}" for i in range(1, 11)}.union({"ASSET-01"})
    assert ids == expected_ids

def test_ground_truth_requests_count(requests_data):
    """Verify that all 15 employee requests REQ-01 through REQ-15 exist."""
    reqs = requests_data.get("requests", [])
    assert len(reqs) == 15
    ids = [r["request_id"] for r in reqs]
    assert ids[0] == "REQ-01"
    assert ids[-1] == "REQ-15"

def test_ground_truth_tickets_count(tickets_data):
    """Verify that all 10 ticket records TK-1042 through TK-1051 exist."""
    tix = tickets_data.get("tickets", [])
    assert len(tix) == 10
    ids = [t["ticket_id"] for t in tix]
    assert ids[0] == "TK-1042"
    assert ids[-1] == "TK-1051"

def test_cross_policy_conflict_hardware(requests_data):
    """Verify REQ-01 (3.5 year laptop) identifies both KB-03 and ASSET-01."""
    req_01 = next(r for r in requests_data["requests"] if r["request_id"] == "REQ-01")
    assert req_01["expected_policy_id"] == "KB-03"
    assert req_01["cross_reference_policy_id"] == "ASSET-01"

def test_security_emergency_phishing(requests_data):
    """Verify REQ-08 (phishing forward) triggers KB-09 and emergency escalation."""
    req_08 = next(r for r in requests_data["requests"] if r["request_id"] == "REQ-08")
    assert req_08["expected_policy_id"] == "KB-09"
    assert req_08["expected_outcome"] == "CRITICAL_SECURITY_INTERVENTION"

def test_ambiguity_no_hallucination(requests_data):
    """Verify REQ-15 (it's not working) requires clarification."""
    req_15 = next(r for r in requests_data["requests"] if r["request_id"] == "REQ-15")
    assert req_15["expected_policy_id"] is None
    assert req_15["expected_outcome"] == "REQUEST_MORE_INFORMATION"
