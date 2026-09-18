import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON
from app.database.session import Base

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    actor_type = Column(String(50), default="AGENT")  # AGENT, EMPLOYEE, SYSTEM, HUMAN_OPERATOR
    
    # Traceability links
    conversation_id = Column(String(36), nullable=True, index=True)
    request_id = Column(String(50), nullable=True, index=True)
    ticket_id = Column(String(50), nullable=True, index=True)
    
    # Event attributes
    action = Column(String(100), nullable=False, index=True)
    # Examples: USER_REQUEST, POLICY_RETRIEVED, FOLLOW_UP_ASKED, POLICY_DECISION, TICKET_CREATED, ESCALATED, RESOLVED
    decision = Column(String(50), nullable=True)  # RESOLVE, CLARIFY, ESCALATE, REJECT
    reason = Column(Text, nullable=True)
    policy_references = Column(JSON, default=list)  # e.g. ["KB-01", "KB-09"]
    event_metadata = Column(JSON, default=dict)  # Arbitrary additional context / parameters

    def __repr__(self):
        return f"<AuditEvent(id='{self.id}', action='{self.action}', timestamp='{self.timestamp}')>"
