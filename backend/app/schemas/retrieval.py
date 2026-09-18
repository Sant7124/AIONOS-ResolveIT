from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class RetrievalQuerySchema(BaseModel):
    query: str
    employee_email: Optional[str] = None
    top_k: int = 3

class SourceMetadataSchema(BaseModel):
    document_name: str
    page_number: int
    section: str
    required_approvals: List[str] = []
    time_constraints: Optional[str] = None
    prohibited_actions: List[str] = []

class RetrievalResultSchema(BaseModel):
    policy_id: str
    policy_title: str
    category: str
    relevant_text: str
    relevance_score: float
    source_metadata: SourceMetadataSchema

class RetrievalResponseSchema(BaseModel):
    query: str
    results_count: int
    results: List[RetrievalResultSchema]
    has_authoritative_match: bool
