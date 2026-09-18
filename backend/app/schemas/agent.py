from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AgentChatRequest(BaseModel):
    message: str = Field(..., description="The user's inquiry or IT service request")
    employee_name: Optional[str] = Field("Employee", description="Name of the employee")
    employee_email: Optional[str] = Field("employee@veridian-corp.example", description="Email of the employee")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID for multi-turn context")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Session context or preloaded entities")

class SourceCitationSchema(BaseModel):
    policy_id: str
    title: str
    statement: str

class TicketDetailsSchema(BaseModel):
    ticket_id: str
    status: str
    priority: str
    assigned_team: Optional[str] = None
    issue_summary: str

class AgentChatResponse(BaseModel):
    conversation_id: str
    intent: str
    category: str
    action: str  # "resolve", "ask", "ticket", "update_ticket", "escalate", "reject"
    status: str
    message: str
    follow_up_questions: List[str] = []
    ticket_id: Optional[str] = None
    ticket_details: Optional[TicketDetailsSchema] = None
    escalation_team: Optional[str] = None
    sources: List[SourceCitationSchema] = []
    audit_event_id: str
