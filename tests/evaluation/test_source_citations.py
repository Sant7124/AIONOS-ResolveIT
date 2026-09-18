"""Evaluation suite for Source Traceability and Citation Integrity.
Validates requirements from Master Prompt 6:
- Every grounded answer has valid policy source IDs.
- Invalid policy IDs (e.g. KB-99, POLICY-X) cannot appear.
- Citations correspond strictly to retrieved/evaluated policies.
- Unrelated policies are not cited.
- Verbatim source statements match the database Knowledge Base.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.database.seed import seed_policies, seed_employee_requests, seed_tickets
from app.agents.it_agent import ITServiceAgent
from app.schemas.agent import AgentChatRequest
from app.models.policy import Policy

@pytest.fixture
def agent_and_db():
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

def test_only_canonical_policy_ids_in_citations(agent_and_db):
    """Verify that only valid canonical IDs (KB-01 through KB-10 and ASSET-01) ever appear in citations."""
    agent, db = agent_and_db
    valid_ids = {p.id for p in db.query(Policy.id).all()}
    assert len(valid_ids) == 11

    # Test across multiple distinct domains
    queries = [
        "I need a password reset",
        "How do I get VPN access?",
        "My laptop screen is flickering",
        "Can I install software?",
        "Printer has a paper jam",
        "My mailbox is full",
        "Guest Wi-Fi tomorrow",
        "Expense tool credentials invalid",
        "Phishing email reported",
        "WFH equipment monitor"
    ]

    for q in queries:
        resp = agent.process_message(AgentChatRequest(message=q))
        for source in resp.sources:
            assert source.policy_id in valid_ids, f"Invalid policy ID found: {source.policy_id}"
            assert len(source.title) > 0
            assert len(source.statement) > 0

def test_citations_match_database_verbatim(agent_and_db):
    """Verify citation statements match database source_text verbatim with zero hallucination."""
    agent, db = agent_and_db
    resp = agent.process_message(AgentChatRequest(message="What is the policy for password resets?"))
    for s in resp.sources:
        db_policy = db.query(Policy).filter(Policy.id == s.policy_id).first()
        assert db_policy is not None
        assert s.statement == db_policy.source_text
        assert s.title == db_policy.title

def test_unrelated_policies_are_not_cited(agent_and_db):
    """Verify that queries for password reset do NOT cite VPN or Printer policies."""
    agent, _ = agent_and_db
    resp = agent.process_message(AgentChatRequest(message="I forgot my password, need to reset it."))
    cited_ids = [s.policy_id for s in resp.sources]
    assert "KB-01" in cited_ids
    assert "KB-02" not in cited_ids
    assert "KB-05" not in cited_ids
    assert "KB-09" not in cited_ids

def test_cross_policy_citations_for_laptop_refresh(agent_and_db):
    """Verify that laptop refresh queries cite BOTH KB-03 (3-yr service) and ASSET-01 (4-yr cycle)."""
    agent, _ = agent_and_db
    resp = agent.process_message(AgentChatRequest(
        message="My laptop won't turn on at all, it's completely dead, had it about 3.5 years now."
    ))
    cited_ids = [s.policy_id for s in resp.sources]
    assert "KB-03" in cited_ids
    assert "ASSET-01" in cited_ids
    assert len(cited_ids) == 2

def test_invalid_policy_id_filtering(agent_and_db):
    """Verify that internal citation builder strips any non-existent policy ID."""
    agent, _ = agent_and_db
    citations = agent._build_citations(["KB-01", "KB-99", "NONEXISTENT-01", "ASSET-01"])
    cited_ids = [c.policy_id for c in citations]
    assert "KB-01" in cited_ids
    assert "ASSET-01" in cited_ids
    assert "KB-99" not in cited_ids
    assert "NONEXISTENT-01" not in cited_ids
