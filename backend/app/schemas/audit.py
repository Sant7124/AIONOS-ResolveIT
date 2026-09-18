from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class AuditEventCreateSchema(BaseModel):
    actor_type: str = "AGENT"
    conversation_id: Optional[str] = None
    request_id: Optional[str] = None
    ticket_id: Optional[str] = None
    action: str
    decision: Optional[str] = None
    reason: Optional[str] = None
    policy_references: List[str] = []
    event_metadata: Dict[str, Any] = {}

class AuditEventResponseSchema(BaseModel):
    id: str
    timestamp: datetime
    actor_type: str
    conversation_id: Optional[str] = None
    request_id: Optional[str] = None
    ticket_id: Optional[str] = None
    action: str
    decision: Optional[str] = None
    reason: Optional[str] = None
    policy_references: List[str] = []
    event_metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)
