import uuid
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class SourceReference(Base):
    __tablename__ = "source_references"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id = Column(String(50), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True)
    document_name = Column(String(200), default="Assignment 2_DataPack_InternalServiceAgent.pdf", nullable=False)
    section_name = Column(String(100), nullable=False)  # e.g., "1. Knowledge Base / Policies"
    page_number = Column(Integer, nullable=False)
    exact_quote = Column(Text, nullable=False)
    context_notes = Column(Text, nullable=True)

    # Relationship
    policy = relationship("Policy", back_populates="sources")

    def __repr__(self):
        return f"<SourceReference(policy_id='{self.policy_id}', page={self.page_number})>"
