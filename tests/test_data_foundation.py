"""Comprehensive test suite for the Veridian IT Copilot Structured Data Foundation."""
import pytest
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, init_db
from app.models import Policy, SourceReference, EmployeeRequest, Ticket, AuditEvent
from app.retrieval.retrieval_service import PolicyRetrievalService
from app.database.seed import seed_policies, seed_employee_requests, seed_tickets

@pytest.fixture(scope="module")
def db_session():
    """Module-level database session fixture."""
    init_db()
    session = SessionLocal()
    # Seed data to ensure clean state
    seed_policies(session)
    seed_employee_requests(session)
    seed_tickets(session)
    yield session
    session.close()

def test_all_ten_kb_policies_exist(db_session: Session):
    """Verify that all 10 KB policies from Section 1 exist with non-empty conditions and verbatim text."""
    for i in range(1, 11):
        kb_id = f"KB-{i:02d}"
        policy = db_session.query(Policy).filter(Policy.id == kb_id).first()
        assert policy is not None, f"Missing policy: {kb_id}"
        assert len(policy.title) > 0, f"Empty title for {kb_id}"
        assert len(policy.source_text) > 0, f"Missing source text for {kb_id}"
        assert len(policy.conditions) > 0, f"Missing conditions for {kb_id}"
        assert policy.source_document == "Assignment 2_DataPack_InternalServiceAgent.pdf"
        assert policy.source_page in (1, 2)

def test_asset_management_policy_exists(db_session: Session):
    """Verify that the Asset Management Policy extract exists with 4-year cycle condition."""
    asset_pol = db_session.query(Policy).filter(Policy.id == "ASSET-01").first()
    assert asset_pol is not None, "Missing Asset Management Policy"
    assert "4-year" in asset_pol.source_text or "4-year" in "".join(asset_pol.conditions)
    assert "Finance sign-off" in asset_pol.required_approvals or "Finance sign-off" in asset_pol.source_text
    assert asset_pol.issuer == "Finance & Assets"

def test_all_fifteen_employee_requests_exist(db_session: Session):
    """Verify that all 15 employee requests (REQ-01 through REQ-15) exist with valid Veridian emails."""
    reqs = db_session.query(EmployeeRequest).all()
    assert len(reqs) >= 15
    for i in range(1, 16):
        req_id = f"REQ-{i:02d}"
        req = db_session.query(EmployeeRequest).filter(EmployeeRequest.request_id == req_id).first()
        assert req is not None, f"Missing employee request {req_id}"
        assert req.email.endswith("@veridian-corp.example"), f"Invalid email domain for {req.employee}"
        assert len(req.request_text) > 0

def test_all_ten_tickets_exist(db_session: Session):
    """Verify that all 10 tickets (TK-1042 through TK-1051) exist."""
    tickets = db_session.query(Ticket).all()
    assert len(tickets) >= 10
    ticket_ids = {t.ticket_id for t in tickets}
    for i in range(1042, 1052):
        t_id = f"TK-{i}"
        assert t_id in ticket_ids, f"Missing ticket {t_id}"

def test_closed_ticket_statuses_preserved(db_session: Session):
    """Verify that closed historical precedent tickets have is_active=False and exact status preserved."""
    closed_cases = {
        "TK-1042": "Resolved (closed)",
        "TK-1045": "Approved at 35GB (closed)",
        "TK-1046": "Resolved (closed)",
        "TK-1049": "Resolved (closed)",
        "TK-1050": "Rejected — no business justification provided (closed)",
        "TK-1051": "Resolved (closed)"
    }
    for t_id, expected_status in closed_cases.items():
        ticket = db_session.query(Ticket).filter(Ticket.ticket_id == t_id).first()
        assert ticket is not None, f"Missing ticket {t_id}"
        assert ticket.status == expected_status, f"Status mismatch for {t_id}: got '{ticket.status}', expected '{expected_status}'"
        assert ticket.is_active is False, f"Ticket {t_id} should be marked inactive (closed precedent)"
        assert ticket.precedent_value is not None, f"Missing precedent value for {t_id}"

def test_active_ticket_statuses_preserved(db_session: Session):
    """Verify that active open tickets have is_active=True and exact status preserved."""
    active_cases = {
        "TK-1043": "Approved — pending fulfillment (active)",
        "TK-1044": "Pending Security review (active)",
        "TK-1047": "Pending Finance (active)",
        "TK-1048": "Escalated to Security — under investigation (active)"
    }
    for t_id, expected_status in active_cases.items():
        ticket = db_session.query(Ticket).filter(Ticket.ticket_id == t_id).first()
        assert ticket is not None, f"Missing ticket {t_id}"
        assert ticket.status == expected_status, f"Status mismatch for {t_id}: got '{ticket.status}', expected '{expected_status}'"
        assert ticket.is_active is True, f"Ticket {t_id} should be marked active"

def test_policy_ids_remain_stable(db_session: Session):
    """Verify that policy IDs conform to the canonical naming scheme."""
    policies = db_session.query(Policy).all()
    canonical_ids = {f"KB-{i:02d}" for i in range(1, 11)}.union({"ASSET-01"})
    actual_ids = {p.id for p in policies}
    assert actual_ids == canonical_ids

def test_source_references_traceable(db_session: Session):
    """Verify that every policy has a traceable SourceReference linking to the Data Pack."""
    source_refs = db_session.query(SourceReference).all()
    assert len(source_refs) >= 11
    for ref in source_refs:
        assert ref.document_name == "Assignment 2_DataPack_InternalServiceAgent.pdf"
        assert ref.page_number in (1, 2)
        assert len(ref.exact_quote) > 0

def test_retrieval_service_queries(db_session: Session):
    """Verify that the retrieval service returns correct policies, rankings, and source metadata."""
    retriever = PolicyRetrievalService(db_session)
    
    # 1. VPN test
    vpn_res = retriever.search("My VPN stopped working, credentials expired")
    assert vpn_res.results_count > 0
    top_p = vpn_res.results[0]
    assert top_p.policy_id == "KB-02"
    assert "VPN" in top_p.policy_title
    assert top_p.source_metadata.document_name == "Assignment 2_DataPack_InternalServiceAgent.pdf"

    # 2. Guest Wi-Fi test
    wifi_res = retriever.search("Can I get Wi-Fi access for a guest visiting tomorrow?")
    assert wifi_res.results_count > 0
    assert wifi_res.results[0].policy_id == "KB-07"

    # 3. Phishing incident test
    phish_res = retriever.search("I got a phishing email and forwarded it to teammates")
    assert phish_res.results_count > 0
    assert phish_res.results[0].policy_id == "KB-09"
    assert len(phish_res.results[0].source_metadata.prohibited_actions) > 0

    # 4. Laptop replacement cross-policy check
    laptop_res = retriever.search("Laptop won't turn on, had it about 3.5 years")
    retrieved_ids = [r.policy_id for r in laptop_res.results]
    assert "KB-03" in retrieved_ids
    assert "ASSET-01" in retrieved_ids

def test_anti_hallucination_citation_enforcement(db_session: Session):
    """Verify that the retrieval service prevents citing policies that were not retrieved."""
    retriever = PolicyRetrievalService(db_session)
    res = retriever.search("VPN expired")
    
    # Valid citation check
    is_valid, valid_citations = retriever.validate_citations(["KB-02"], res.results)
    assert is_valid is True
    assert valid_citations == ["KB-02"]

    # Hallucinated policy check: KB-99 does not exist, KB-09 was not retrieved for VPN
    is_valid_fake, valid_fake = retriever.validate_citations(["KB-99", "KB-09"], res.results)
    assert is_valid_fake is False
    assert "KB-99" not in valid_fake
    assert "KB-09" not in valid_fake
