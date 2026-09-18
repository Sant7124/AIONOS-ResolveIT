"""Evaluation suite for Enterprise Security, Input Sanitization, and Vulnerability Defense.
Validates requirements from Master Prompt 6:
- API keys and environment secrets are never exposed in responses or error payloads.
- User input is validated and sanitized (XSS / dangerous HTML defense).
- Database operations are protected against SQL injection.
- CORS middleware is controlled.
- Errors handle gracefully without exposing internal stack traces or secrets.
"""
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_no_api_keys_or_secrets_exposed_in_health_or_api(client):
    """Verify that neither /health, /api/tickets, /api/policies, nor /api/chat expose secret keys."""
    # Ensure sensitive environment variable is set
    os.environ["SECRET_KEY"] = "super-secret-production-key-998811"
    os.environ["DATABASE_URL"] = "sqlite:///./production_secure.db"

    endpoints = [
        "/health",
        "/api/policies",
        "/api/tickets",
        "/api/requests",
        "/api/audit"
    ]
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200
        text = res.text
        assert "super-secret-production-key-998811" not in text
        assert "SECRET_KEY" not in text

def test_sql_injection_defense_in_chat_and_search(client):
    """Verify SQL injection payloads do not cause database syntax errors or dump unauthorized tables."""
    sql_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE tickets; --",
        "1' UNION SELECT null, null, null--",
        "' OR 1=1 --"
    ]
    for payload in sql_payloads:
        # Test chat endpoint
        res = client.post("/api/chat", json={
            "message": f"My laptop is broken {payload}",
            "employee_name": f"Hacker {payload}"
        })
        # Should gracefully return 200 without 500 error or syntax crash
        assert res.status_code == 200
        data = res.json()
        assert "syntax error" not in data["message"].lower()

        # Test retrieval search endpoint
        search_res = client.post("/api/retrieval/search", json={"query": payload, "top_k": 3})
        assert search_res.status_code == 200


def test_xss_and_html_injection_handling(client):
    """Verify malicious script tags and HTML are handled safely and not executed."""
    xss_payload = "<script>alert('XSS-EXPLOIT');</script><img src=x onerror=alert(1)>"
    res = client.post("/api/chat", json={
        "message": f"Help with software {xss_payload}",
        "employee_name": f"Attacker {xss_payload}",
        "employee_email": "attacker@veridian-corp.example"
    })
    assert res.status_code == 200
    data = res.json()
    # Response message should not execute or unescaped script tag
    assert "<script>alert" not in data["message"]

def test_cors_headers_configured(client):
    """Verify CORS headers are properly set on API responses."""
    res = client.options("/api/chat", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST"
    })
    # Must allow localhost / controlled origins
    assert res.status_code in (200, 204)
    assert "access-control-allow-origin" in res.headers

def test_nonexistent_ticket_error_handling(client):
    """Verify 404 error responses do not leak stack traces or internals."""
    res = client.get("/api/tickets/TK-999999")
    assert res.status_code == 404
    data = res.json()
    assert "detail" in data
    assert "Traceback" not in res.text
    assert "sqlite3" not in res.text
