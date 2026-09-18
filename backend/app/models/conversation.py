import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(50), ForeignKey("employee_requests.request_id", ondelete="SET NULL"), nullable=True)
    employee_name = Column(String(100), nullable=False)
    employee_email = Column(String(150), nullable=False)
    current_state = Column(String(50), default="INITIAL")  # INITIAL, CLARIFYING, RESOLVED, ESCALATED
    active_intent = Column(String(100), nullable=True)
    active_category = Column(String(100), nullable=True)
    pending_question = Column(Text, nullable=True)
    context_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")
    decisions = relationship("AgentDecision", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id='{self.id}', state='{self.current_state}')>"

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_type = Column(String(50), nullable=False)  # EMPLOYEE, AGENT, SYSTEM
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<ConversationMessage(id='{self.id}', sender='{self.sender_type}')>"
