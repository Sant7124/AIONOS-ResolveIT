from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.config import settings
from app.models import Policy, Ticket, EmployeeRequest, AuditEvent
from app.schemas.policy import PolicyResponseSchema
from app.schemas.ticket import TicketResponseSchema
from app.schemas.audit import AuditEventResponseSchema
from app.schemas.retrieval import RetrievalQuerySchema, RetrievalResponseSchema
from app.schemas.agent import AgentChatRequest, AgentChatResponse
from app.retrieval.retrieval_service import PolicyRetrievalService
from app.agents.it_agent import ITServiceAgent
from app.models.conversation import Conversation

api_router = APIRouter()

@api_router.get("/info", tags=["System"])
def get_system_info(db: Session = Depends(get_db)):
    """Return system information and metadata grounded in the Veridian Corp Data Pack."""
    policy_count = db.query(Policy).count()
    ticket_count = db.query(Ticket).count()
    request_count = db.query(EmployeeRequest).count()
    audit_count = db.query(AuditEvent).count()

    return {
        "product_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "simulation_base_date": settings.SIMULATION_BASE_DATE,
        "simulation_window": "Monday, 21 September 2026 – Friday, 25 September 2026",
        "active_llm_provider": settings.LLM_PROVIDER,
        "counts": {
            "policies": policy_count,
            "tickets": ticket_count,
            "employee_requests": request_count,
            "audit_events": audit_count
        },
        "status": "ready"
    }

@api_router.get("/policies", tags=["Policies"])
def get_policies(
    category: Optional[str] = Query(None, description="Filter by policy category"),
    db: Session = Depends(get_db)
):
    """Retrieve authoritative policies with structured conditions, approvals, and source citations."""
    query = db.query(Policy)
    if category:
        query = query.filter(Policy.category == category)
    policies = query.all()
    return {
        "policies": [
            PolicyResponseSchema.model_validate(p).model_dump() for p in policies
        ]
    }

@api_router.get("/policies/{policy_id}", response_model=PolicyResponseSchema, tags=["Policies"])
def get_policy_by_id(policy_id: str, db: Session = Depends(get_db)):
    """Retrieve a single policy by its canonical ID (e.g. KB-01, ASSET-01)."""
    policy = db.query(Policy).filter(Policy.id == policy_id.upper()).first()
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy with ID '{policy_id}' not found.")
    return policy

@api_router.get("/tickets", tags=["Tickets"])
def get_tickets(
    active_only: Optional[bool] = Query(None, description="Filter for active open cases vs closed precedents"),
    status: Optional[str] = Query(None, description="Filter by exact status string"),
    db: Session = Depends(get_db)
):
    """Retrieve tickets from the ticketing system record."""
    query = db.query(Ticket)
    if active_only is not None:
        query = query.filter(Ticket.is_active == active_only)
    if status:
        query = query.filter(Ticket.status == status)
    tickets = query.all()
    return {
        "tickets": [
            TicketResponseSchema.model_validate(t).model_dump() for t in tickets
        ]
    }

@api_router.get("/requests", tags=["Requests"])
def get_requests(db: Session = Depends(get_db)):
    """Retrieve the 15 employee requests (REQ-01 to REQ-15) from Section 2 of the Data Pack."""
    requests = db.query(EmployeeRequest).all()
    return {
        "requests": [
            {
                "request_id": r.request_id,
                "employee": r.employee,
                "email": r.email,
                "date_opened": r.date_opened,
                "request": r.request_text,
                "initial_action_taken": r.initial_action_taken,
                "expected_policy_id": r.expected_policy_id,
                "cross_reference_policy_id": r.cross_reference_policy_id,
                "category": r.category,
                "expected_outcome": r.expected_outcome,
                "analysis": r.analysis
            }
            for r in requests
        ]
    }

@api_router.post("/retrieval/search", response_model=RetrievalResponseSchema, tags=["Retrieval"])
def search_knowledge_base(
    query_payload: RetrievalQuerySchema,
    db: Session = Depends(get_db)
):
    """Search the Knowledge Base for an employee inquiry and return ranked, grounded policies with source citations."""
    retriever = PolicyRetrievalService(db)
    return retriever.search(query=query_payload.query, top_k=query_payload.top_k)

@api_router.get("/audit", response_model=List[AuditEventResponseSchema], tags=["Audit"])
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve the immutable audit event trail."""
    return db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()

@api_router.post("/agent/chat", response_model=AgentChatResponse, tags=["Agent"])
def chat_with_agent(
    request: AgentChatRequest,
    db: Session = Depends(get_db)
):
    """Execute the policy-grounded enterprise IT service agent workflow."""
    agent = ITServiceAgent(db)
    return agent.process_message(request)

@api_router.get("/agent/conversations/{conversation_id}", tags=["Agent"])
def get_conversation_history(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve multi-turn conversation messages and state."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {
        "id": conv.id,
        "employee_name": conv.employee_name,
        "employee_email": conv.employee_email,
        "state": conv.current_state,
        "messages": [
            {
                "id": m.id,
                "sender": m.sender_type,
                "content": m.content,
                "created_at": m.created_at.isoformat()
            }
            for m in conv.messages
        ]
    }
