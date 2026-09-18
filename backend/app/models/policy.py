from sqlalchemy import Column, String, Text, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class Policy(Base):
    __tablename__ = "policies"

    id = Column(String(50), primary_key=True, index=True)  # e.g., "KB-01", "ASSET-01"
    title = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    source_text = Column(Text, nullable=False)  # Verbatim from Data Pack
    
    # Structured policy components
    conditions = Column(JSON, default=list)  # List of condition strings
    required_approvals = Column(JSON, default=list)  # List of required approval authorities
    allowed_actions = Column(JSON, default=list)  # Permitted actions
    prohibited_actions = Column(JSON, default=list)  # Prohibited actions (e.g. forwarding phishing)
    escalation_required = Column(Boolean, default=False)
    resolution_steps = Column(JSON, default=list)  # Step-by-step resolution procedure
    time_constraints = Column(String(200), nullable=True)  # SLAs, notice times, expiration
    
    # Document source attribution
    source_document = Column(String(200), default="Assignment 2_DataPack_InternalServiceAgent.pdf")
    source_page = Column(Integer, default=1)
    issuer = Column(String(150), nullable=True)
    last_updated = Column(String(50), nullable=True)

    # Relationships
    sources = relationship("SourceReference", back_populates="policy", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Policy(id='{self.id}', title='{self.title}')>"
