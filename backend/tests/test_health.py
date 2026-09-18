import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Verify that the /health endpoint responds with 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "aionos-resolveit-api"
    assert "version" in data
    assert "simulation_base_date" in data

def test_api_info_endpoint():
    """Verify that /api/info returns grounding metadata from the Data Pack."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["counts"]["policies"] >= 11
    assert data["counts"]["tickets"] == 10
    assert data["counts"]["employee_requests"] == 15

def test_get_policies():
    """Verify that /api/policies returns the 10 KB policies plus Asset Management policy."""
    response = client.get("/api/policies")
    assert response.status_code == 200
    data = response.json()
    assert "policies" in data
    policy_ids = [p["id"] for p in data["policies"]]
    assert "KB-01" in policy_ids
    assert "KB-09" in policy_ids
    assert "ASSET-01" in policy_ids

def test_get_tickets():
    """Verify that /api/tickets returns the initial 10 ticket records."""
    response = client.get("/api/tickets")
    assert response.status_code == 200
    data = response.json()
    assert "tickets" in data
    assert len(data["tickets"]) == 10
    ticket_ids = [t["ticket_id"] for t in data["tickets"]]
    assert "TK-1042" in ticket_ids
    assert "TK-1051" in ticket_ids

def test_get_requests():
    """Verify that /api/requests returns the 15 employee requests."""
    response = client.get("/api/requests")
    assert response.status_code == 200
    data = response.json()
    assert "requests" in data
    assert len(data["requests"]) == 15
    request_ids = [r["request_id"] for r in data["requests"]]
    assert "REQ-01" in request_ids
    assert "REQ-15" in request_ids

def test_get_single_policy():
    """Verify that /api/policies/KB-01 returns detailed policy with conditions and approvals."""
    response = client.get("/api/policies/KB-01")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "KB-01"
    assert data["title"] == "Password Reset"
    assert len(data["conditions"]) > 0
    assert "source_text" in data
    assert data["source_page"] == 1

def test_search_retrieval_endpoint():
    """Verify that POST /api/retrieval/search returns ranked grounded policies."""
    response = client.post(
        "/api/retrieval/search",
        json={"query": "VPN access expired credentials", "top_k": 2}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["results_count"] > 0
    top_match = data["results"][0]
    assert top_match["policy_id"] == "KB-02"
    assert top_match["source_metadata"]["document_name"] == "Assignment 2_DataPack_InternalServiceAgent.pdf"

def test_get_audit_events_endpoint():
    """Verify that GET /api/audit returns audit event trail."""
    response = client.get("/api/audit")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    assert len(events) >= 1
    assert "action" in events[0]

def test_active_tickets_filter():
    """Verify that GET /api/tickets?active_only=true returns only active tickets."""
    response = client.get("/api/tickets?active_only=true")
    assert response.status_code == 200
    data = response.json()
    for t in data["tickets"]:
        assert t["is_active"] is True

