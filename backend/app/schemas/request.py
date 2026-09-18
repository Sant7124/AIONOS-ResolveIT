from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class EmployeeRequestCreateSchema(BaseModel):
    employee: str = Field(..., description="Full name of employee submitting the request")
    email: str = Field(..., description="Corporate email address")
    request_text: str = Field(..., description="Natural language description of the IT issue")
    category: Optional[str] = Field("General IT", description="IT problem category")
    expected_policy_id: Optional[str] = Field(None, description="Ground truth policy ID if known")
    cross_reference_policy_id: Optional[str] = Field(None, description="Cross reference policy ID if applicable")
    expected_outcome: Optional[str] = Field(None, description="Expected resolution outcome")

class EmployeeRequestResponseSchema(BaseModel):
    request_id: str
    employee: str
    email: str
    date_opened: str
    request: str
    initial_action_taken: Optional[str] = None
    expected_policy_id: Optional[str] = None
    cross_reference_policy_id: Optional[str] = None
    category: str
    expected_outcome: Optional[str] = None
    analysis: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
