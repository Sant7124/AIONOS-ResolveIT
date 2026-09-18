from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON
from app.database.session import Base

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(String(50), primary_key=True, index=True)  # e.g., "TK-1042"
    employee = Column(String(100), nullable=False)
    email = Column(String(150), nullable=True)
    category = Column(String(100), nullable=False, index=True)
    issue_summary = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status fields: active vs closed
    status = Column(String(100), nullable=False, index=True)  # e.g. "Resolved (closed)", "Pending Security review (active)"
    is_active = Column(Boolean, default=True, index=True)
    
    priority = Column(String(50), default="P3 - Medium")  # P1 - Critical, P2 - High, P3 - Medium, P4 - Low
    assigned_team = Column(String(100), nullable=True)
    resolution = Column(Text, nullable=True)
    precedent_value = Column(Text, nullable=True)
    
    # Grounding & Policy Traceability
    source_policy_ids = Column(JSON, default=list)  # e.g. ["KB-02"]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Ticket(id='{self.ticket_id}', status='{self.status}', active={self.is_active})>"
