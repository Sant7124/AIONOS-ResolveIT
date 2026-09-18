from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from app.database.session import Base

class EmployeeRequest(Base):
    __tablename__ = "employee_requests"

    request_id = Column(String(50), primary_key=True, index=True)  # e.g., "REQ-01"
    employee = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    date_opened = Column(String(50), nullable=False)  # e.g., "Mon 21 Sep"
    request_text = Column(Text, nullable=False)
    initial_action_taken = Column(String(200), nullable=False)
    
    # Ground truth benchmark references
    expected_policy_id = Column(String(50), nullable=True)
    cross_reference_policy_id = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    expected_outcome = Column(String(100), nullable=True)
    analysis = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<EmployeeRequest(id='{self.request_id}', employee='{self.employee}')>"
