"""Evaluation suite for Ticket Lifecycle, Duplicate Prevention, and Precedents.
Validates requirements from Master Prompt 6:
- Active ticket detection
- Duplicate prevention (update existing ticket rather than creating duplicate)
- Closed ticket history preservation (TK-1050 precedent rejection)
- Sequential ticket ID generation (TK-1052+)
- Ticket updates and append description with timestamps
- Complete audit trail linking to tickets
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.database.seed import seed_policies, seed_employee_requests, seed_tickets
from app.agents.it_agent import ITServiceAgent
from app.services.ticket_service import TicketService
from app.schemas.agent import AgentChatRequest
from app.models.ticket import Ticket
from app.models.audit_event import AuditEvent

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

def test_active_ticket_detection_and_duplicate_prevention(agent_and_db):
    """Verify that employee with existing open ticket (TK-1043) gets ticket update, NOT duplicate creation."""
    agent, db = agent_and_db
    initial_ticket_count = db.query(Ticket).count()

    req = AgentChatRequest(
        message="Checking on my laptop replacement, it's completely dead and 3.2 yrs old.",
        employee_name="S. Iyer",
        employee_email="s.iyer@veridian-corp.example"
    )
    resp = agent.process_message(req)

    assert resp.action == "update_ticket"
    assert resp.ticket_id == "TK-1043"
    # Verify NO new ticket row was added
    assert db.query(Ticket).count() == initial_ticket_count

    # Verify ticket description was appended
    updated_ticket = db.query(Ticket).filter(Ticket.ticket_id == "TK-1043").first()
    assert updated_ticket.is_active is True
    assert "Checking on my laptop replacement" in updated_ticket.description

def test_closed_precedent_ticket_cannot_be_overridden(agent_and_db):
    """Verify TK-1050 (Admin access rejected without justification) is preserved and authoritative."""
    agent, db = agent_and_db
    tk_1050 = db.query(Ticket).filter(Ticket.ticket_id == "TK-1050").first()
    assert tk_1050 is not None
    assert tk_1050.is_active is False
    assert "Rejected" in tk_1050.status
    assert tk_1050.precedent_value is not None

    # New request with no justification must be rejected matching TK-1050
    req = AgentChatRequest(
        message="Can someone give me admin access to the finance reporting server? Need it urgently.",
        employee_name="Kavya Pillai",
        employee_email="kavya.pillai@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.action == "reject"
    assert "TK-1050" in resp.message
    assert resp.ticket_id is None

def test_sequential_ticket_id_generation(agent_and_db):
    """Verify that new tickets generate sequential IDs above TK-1051 (e.g. TK-1052, TK-1053)."""
    agent, db = agent_and_db
    req1 = AgentChatRequest(
        message="I'm locked out of my account after 6 attempts.",
        employee_name="Alice Cooper",
        employee_email="alice.cooper@veridian-corp.example"
    )
    resp1 = agent.process_message(req1)
    assert resp1.ticket_id == "TK-1052"

    req2 = AgentChatRequest(
        message="I'm locked out of my account after 6 attempts.",
        employee_name="Bob Dylan",
        employee_email="bob.dylan@veridian-corp.example"
    )
    resp2 = agent.process_message(req2)
    assert resp2.ticket_id == "TK-1053"


def test_ticket_service_status_transition(agent_and_db):
    """Verify TicketService status transitions properly toggle is_active flag."""
    _, db = agent_and_db
    t = TicketService.get_ticket(db, "TK-1044")
    assert t.is_active is True

    # Resolving sets is_active to False
    TicketService.update_ticket(db, ticket_id="TK-1044", status="Resolved (closed)", resolution="Security review completed.")
    updated = TicketService.get_ticket(db, "TK-1044")
    assert updated.status == "Resolved (closed)"
    assert updated.is_active is False

def test_ticket_linked_to_immutable_audit_event(agent_and_db):
    """Verify that every ticket action generates an immutable AuditEvent linked to the ticket ID."""
    agent, db = agent_and_db
    req = AgentChatRequest(
        message="I'm locked out of my account, tried my password 6 times.",
        employee_name="Karan Mehta",
        employee_email="karan.mehta@veridian-corp.example"
    )
    resp = agent.process_message(req)
    assert resp.audit_event_id is not None

    event = db.query(AuditEvent).filter(AuditEvent.id == resp.audit_event_id).first()
    assert event is not None
    assert event.ticket_id == resp.ticket_id
    assert event.actor_type == "AGENT"
    assert "KB-01" in event.policy_references
    assert event.timestamp is not None
