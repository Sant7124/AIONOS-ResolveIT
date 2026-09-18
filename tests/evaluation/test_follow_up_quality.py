"""Evaluation suite for Multi-Turn Clarification and Follow-Up Quality.
Validates requirements from Master Prompt 6:
- Agent asks only necessary questions when information is genuinely insufficient.
- Questions are targeted and relevant to the specific policy condition.
- Answers are stored in persistent conversation context.
- Conversation resumes correctly without losing original context.
- Agent does not repeat already answered questions.
"""
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.database.seed import seed_policies, seed_employee_requests, seed_tickets
from app.agents.it_agent import ITServiceAgent
from app.schemas.agent import AgentChatRequest
from app.models.conversation import Conversation, ConversationMessage

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

def test_vague_request_asks_targeted_clarification(agent_and_db):
    """Verify that vague 'its not working' triggers targeted clarification without hallucinating a resolution."""
    agent, _ = agent_and_db
    req = AgentChatRequest(message="hey can you help, its not working")
    resp = agent.process_message(req)

    assert resp.action == "ask"
    assert resp.intent == "unknown_it_issue"
    assert resp.ticket_id is None
    assert len(resp.follow_up_questions) > 0
    # Must ask targeted technical questions
    assert any("device" in q.lower() or "system" in q.lower() or "application" in q.lower() for q in resp.follow_up_questions)

def test_multi_turn_laptop_resolution_does_not_repeat_questions(agent_and_db):
    """Multi-turn flow:
    Turn 1: 'My laptop screen is completely dead and won't turn on.' (Missing device age)
    -> Agent asks for age.
    Turn 2: 'It is 3.5 years old.'
    -> Agent resumes context, does NOT repeat the age question, and creates dual-approval ticket!
    """
    agent, db = agent_and_db
    conv_id = str(uuid.uuid4())

    # Turn 1: Symptom provided, age omitted
    req1 = AgentChatRequest(
        conversation_id=conv_id,
        message="My laptop won't turn on at all, completely dead.",
        employee_name="TurnTester",
        employee_email="tester@veridian-corp.example"
    )
    resp1 = agent.process_message(req1)
    assert resp1.action == "ask"
    assert "old" in resp1.message.lower() or "age" in resp1.message.lower()
    assert resp1.ticket_id is None

    # Check conversation state in database
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    assert conv.current_state == "CLARIFYING"
    assert conv.active_intent == "laptop_replacement"

    # Turn 2: User provides age
    req2 = AgentChatRequest(
        conversation_id=conv_id,
        message="I have had it for 3.5 years.",
        employee_name="TurnTester",
        employee_email="tester@veridian-corp.example"
    )
    resp2 = agent.process_message(req2)

    # Must resolve/ticket without re-asking
    assert resp2.action in ("ticket", "escalate")
    assert resp2.ticket_id is not None
    assert "3.5" in resp2.message or "Finance" in resp2.message
    assert "KB-03" in [s.policy_id for s in resp2.sources]
    assert "ASSET-01" in [s.policy_id for s in resp2.sources]
    assert len(resp2.follow_up_questions) == 0

def test_printer_two_step_troubleshooting_sequence(agent_and_db):
    """Multi-turn printer flow:
    Turn 1: 'Printer on 2nd floor is jammed.'
    -> Recommends spooler restart (KB-05).
    Turn 2: 'I restarted the spooler, still not printing. The asset tag is VER-PRN-02-04.'
    -> Logs technician ticket with asset tag without re-asking for spooler restart.
    """
    agent, _ = agent_and_db
    conv_id = str(uuid.uuid4())

    # Turn 1: Initial report
    req1 = AgentChatRequest(
        conversation_id=conv_id,
        message="The 2nd floor printer keeps saying paper jam."
    )
    resp1 = agent.process_message(req1)
    assert resp1.action == "resolve"
    assert "spooler" in resp1.message.lower()

    # Turn 2: Persistent failure + Asset tag
    req2 = AgentChatRequest(
        conversation_id=conv_id,
        message="I restarted the print spooler, still broken. Asset tag is VER-PRN-02-04."
    )
    resp2 = agent.process_message(req2)
    assert resp2.action == "ticket"
    assert resp2.ticket_id is not None
    assert "VER-PRN-02-04" in resp2.message
    assert "KB-05" in [s.policy_id for s in resp2.sources]

def test_agent_does_not_ask_redundant_questions_when_data_present(agent_and_db):
    """When all information is present in the first message, agent MUST NOT ask follow-up questions."""
    agent, _ = agent_and_db
    req = AgentChatRequest(
        message="My laptop won't turn on at all, it's completely dead, had it about 3.5 years now."
    )
    resp = agent.process_message(req)
    assert resp.action != "ask"
    assert len(resp.follow_up_questions) == 0
    assert resp.ticket_id is not None
