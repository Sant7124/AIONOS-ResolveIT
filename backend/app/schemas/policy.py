from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class SourceReferenceSchema(BaseModel):
    id: str
    policy_id: str
    document_name: str
    section_name: str
    page_number: int
    exact_quote: str
    context_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PolicyBaseSchema(BaseModel):
    id: str
    title: str
    category: str
    summary: str
    source_text: str
    conditions: List[str] = []
    required_approvals: List[str] = []
    allowed_actions: List[str] = []
    prohibited_actions: List[str] = []
    escalation_required: bool = False
    resolution_steps: List[str] = []
    time_constraints: Optional[str] = None
    source_document: str = "Assignment 2_DataPack_InternalServiceAgent.pdf"
    source_page: int = 1
    issuer: Optional[str] = None
    last_updated: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PolicyResponseSchema(PolicyBaseSchema):
    sources: List[SourceReferenceSchema] = []
