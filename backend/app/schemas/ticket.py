from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class TicketBaseSchema(BaseModel):
    ticket_id: str
    employee: str
    email: Optional[str] = None
    category: str
    issue_summary: str
    description: Optional[str] = None
    status: str
    is_active: bool = True
    priority: str = "P3 - Medium"
    assigned_team: Optional[str] = None
    resolution: Optional[str] = None
    precedent_value: Optional[str] = None
    source_policy_ids: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class TicketCreateSchema(BaseModel):
    ticket_id: Optional[str] = None
    employee: str
    email: Optional[str] = None
    category: str
    issue_summary: str
    description: Optional[str] = None
    priority: str = "P3 - Medium"
    assigned_team: Optional[str] = None
    source_policy_ids: List[str] = []

class TicketResponseSchema(TicketBaseSchema):
    created_at: datetime
    updated_at: datetime
