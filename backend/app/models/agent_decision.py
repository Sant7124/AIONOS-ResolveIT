import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    request_id = Column(String(50), ForeignKey("employee_requests.request_id", ondelete="SET NULL"), nullable=True)
    ticket_id = Column(String(50), ForeignKey("tickets.ticket_id", ondelete="SET NULL"), nullable=True)
    
    decision_type = Column(String(50), nullable=False)  # RESOLVE, CLARIFY, ESCALATE, REJECT
    reasoning = Column(Text, nullable=False)
    cited_policy_ids = Column(JSON, default=list)  # e.g., ["KB-03", "ASSET-01"]
    action_summary = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="decisions")

    def __repr__(self):
        return f"<AgentDecision(id='{self.id}', type='{self.decision_type}')>"
