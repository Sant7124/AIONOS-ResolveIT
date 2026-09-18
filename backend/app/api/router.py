from typing import List, Optional
from datetime import datetime, timezone
import uuid
import re
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.config import settings
from app.models import Policy, Ticket, EmployeeRequest, AuditEvent
from app.schemas.policy import PolicyResponseSchema
from app.schemas.ticket import TicketCreateSchema, TicketResponseSchema, TicketUpdateSchema
from app.schemas.request import EmployeeRequestCreateSchema, EmployeeRequestResponseSchema
from app.schemas.audit import AuditEventResponseSchema
from app.schemas.retrieval import RetrievalQuerySchema, RetrievalResponseSchema
from app.schemas.agent import AgentChatRequest, AgentChatResponse, AgentStatusResponse
from app.retrieval.retrieval_service import PolicyRetrievalService
from app.services.ticket_service import TicketService
from app.agents.it_agent import ITServiceAgent
from app.models.conversation import Conversation

api_router = APIRouter()

# ---------------------------------------------------------------------------
# System & Diagnostics Endpoints
# ---------------------------------------------------------------------------

@api_router.get("/info", tags=["System"])
def get_system_info(db: Session = Depends(get_db)):
    """Return system information and metadata grounded in the canonical Data Pack."""
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

@api_router.get("/agent/status", response_model=AgentStatusResponse, tags=["Agent"])
def get_agent_status(db: Session = Depends(get_db)):
    """
    Return comprehensive operational readiness of the IT Copilot agent:
    - Operational status
    - AI Provider connectivity & model
    - Knowledge Base loaded count (KB-01 to KB-10 and ASSET-01)
    - Relational Database engine connectivity
    """
    db_connected = False
    policy_count = 0
    active_tickets = 0
    try:
        policy_count = db.query(Policy).count()
        active_tickets = db.query(Ticket).filter(Ticket.is_active == True).count()
        db_connected = True
    except Exception:
        db_connected = False

    kb_loaded = policy_count >= 11

    # AI Provider connectivity verification
    ai_connected = True
    ai_provider = settings.LLM_PROVIDER
    if ai_provider == "openai" and not settings.OPENAI_API_KEY:
        ai_connected = False
    elif ai_provider == "gemini" and not settings.GEMINI_API_KEY:
        ai_connected = False

    operational = db_connected and kb_loaded
    status_summary = "Operational" if operational and ai_connected else ("Degraded (Deterministic Fallback Active)" if operational else "Offline")

    return AgentStatusResponse(
        operational=operational,
        status=status_summary,
        ai_provider_connected=ai_connected,
        ai_provider_name=ai_provider,
        knowledge_base_loaded=kb_loaded,
        knowledge_base_policy_count=policy_count,
        database_connected=db_connected,
        active_tickets_count=active_tickets,
        simulation_date=settings.SIMULATION_BASE_DATE,
        details={
            "rules_engine": "Deterministic Corporate Governance Active",
            "fallback_mode": "Auto-failover enabled to deterministic engine",
            "zero_hallucination_enforced": True
        }
    )

# ---------------------------------------------------------------------------
# Conversational Agent Endpoints (Both /chat and /agent/chat supported)
# ---------------------------------------------------------------------------

@api_router.post("/chat", response_model=AgentChatResponse, tags=["Agent"])
@api_router.post("/agent/chat", response_model=AgentChatResponse, tags=["Agent"])
def chat_with_agent(
    request: AgentChatRequest,
    db: Session = Depends(get_db)
):
    """
    Execute the policy-grounded enterprise IT service agent workflow:
    Intent Detection -> Entity Extraction -> Grounded Policy Retrieval ->
    Ticket History / Duplicate Check -> Sufficiency Verification ->
    Deterministic Rules Evaluation -> Ticket Generation/Update -> Immutable Audit.
    """
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
        "active_intent": conv.active_intent,
        "pending_question": conv.pending_question,
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

# ---------------------------------------------------------------------------
# Employee Requests Endpoints
# ---------------------------------------------------------------------------

@api_router.get("/requests", tags=["Requests"])
def get_requests(db: Session = Depends(get_db)):
    """Retrieve employee requests from the database record."""
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

@api_router.get("/requests/{request_id}", response_model=EmployeeRequestResponseSchema, tags=["Requests"])
def get_request_by_id(request_id: str, db: Session = Depends(get_db)):
    """Retrieve a single employee request by its canonical ID (e.g. REQ-01)."""
    req = db.query(EmployeeRequest).filter(
        (EmployeeRequest.request_id == request_id.upper()) | (EmployeeRequest.request_id == request_id)
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail=f"Employee request '{request_id}' not found.")
    return EmployeeRequestResponseSchema(
        request_id=req.request_id,
        employee=req.employee,
        email=req.email,
        date_opened=req.date_opened,
        request=req.request_text,
        initial_action_taken=req.initial_action_taken,
        expected_policy_id=req.expected_policy_id,
        cross_reference_policy_id=req.cross_reference_policy_id,
        category=req.category,
        expected_outcome=req.expected_outcome,
        analysis=req.analysis
    )

@api_router.post("/requests", response_model=EmployeeRequestResponseSchema, status_code=status.HTTP_201_CREATED, tags=["Requests"])
def create_employee_request(
    payload: EmployeeRequestCreateSchema,
    db: Session = Depends(get_db)
):
    """Submit a new employee IT request into the system."""
    # Find next REQ-XX identifier
    existing_requests = db.query(EmployeeRequest.request_id).all()
    max_num = 15
    for (r_id,) in existing_requests:
        match = re.search(r"REQ-(\d+)", r_id)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    next_req_id = f"REQ-{max_num + 1:02d}"

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_req = EmployeeRequest(
        request_id=next_req_id,
        employee=payload.employee,
        email=payload.email,
        date_opened=now_iso,
        request_text=payload.request_text,
        category=payload.category or "General IT",
        expected_policy_id=payload.expected_policy_id,
        cross_reference_policy_id=payload.cross_reference_policy_id,
        expected_outcome=payload.expected_outcome,
        initial_action_taken="Submitted via API"
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)

    return EmployeeRequestResponseSchema(
        request_id=new_req.request_id,
        employee=new_req.employee,
        email=new_req.email,
        date_opened=new_req.date_opened,
        request=new_req.request_text,
        initial_action_taken=new_req.initial_action_taken,
        expected_policy_id=new_req.expected_policy_id,
        cross_reference_policy_id=new_req.cross_reference_policy_id,
        category=new_req.category,
        expected_outcome=new_req.expected_outcome,
        analysis=new_req.analysis
    )

# ---------------------------------------------------------------------------
# Tickets Endpoints
# ---------------------------------------------------------------------------

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
    tickets = query.order_by(Ticket.ticket_id.desc()).all()
    return {
        "tickets": [
            TicketResponseSchema.model_validate(t).model_dump() for t in tickets
        ]
    }

@api_router.get("/tickets/{ticket_id}", response_model=TicketResponseSchema, tags=["Tickets"])
def get_ticket_by_id(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieve a single ticket by canonical ticket ID (e.g. TK-1042)."""
    ticket = TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket with ID '{ticket_id}' not found.")
    return ticket

@api_router.post("/tickets", response_model=TicketResponseSchema, status_code=status.HTTP_201_CREATED, tags=["Tickets"])
def create_ticket(
    payload: TicketCreateSchema,
    db: Session = Depends(get_db)
):
    """Create a new ticket directly through the ticketing service."""
    # Check for duplicate active ticket
    existing_ticket = TicketService.find_related_ticket(
        db,
        employee=payload.employee,
        category=payload.category,
        keywords=[payload.issue_summary]
    )
    if existing_ticket:
        # Prevent unnecessary duplicate ticket creation
        raise HTTPException(
            status_code=409,
            detail=f"An active related ticket already exists for {payload.employee}: {existing_ticket.ticket_id} ({existing_ticket.status})."
        )

    ticket = TicketService.create_ticket(
        db,
        employee=payload.employee,
        email=payload.email,
        category=payload.category,
        issue_summary=payload.issue_summary,
        description=payload.description,
        priority=payload.priority,
        assigned_team=payload.assigned_team,
        source_policy_ids=payload.source_policy_ids,
        status="Active — assigned"
    )
    return ticket

@api_router.patch("/tickets/{ticket_id}", response_model=TicketResponseSchema, tags=["Tickets"])
def update_ticket(
    ticket_id: str,
    payload: TicketUpdateSchema,
    db: Session = Depends(get_db)
):
    """Update an existing ticket status, resolution, priority, or append notes."""
    ticket = TicketService.update_ticket(
        db,
        ticket_id=ticket_id,
        status=payload.status,
        resolution=payload.resolution,
        priority=payload.priority,
        assigned_team=payload.assigned_team,
        is_active=payload.is_active,
        description=payload.description,
        append_description=payload.append_notes
    )
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket with ID '{ticket_id}' not found.")
    return ticket

# ---------------------------------------------------------------------------
# Policy & Grounding Endpoints
# ---------------------------------------------------------------------------

@api_router.get("/policies", tags=["Policies"])
def get_policies(
    category: Optional[str] = Query(None, description="Filter by policy category"),
    db: Session = Depends(get_db)
):
    """Retrieve authoritative policies with structured conditions, approvals, and source citations."""
    query = db.query(Policy)
    if category:
        query = query.filter(Policy.category == category)
    policies = query.order_by(Policy.id.asc()).all()
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

@api_router.post("/retrieval/search", response_model=RetrievalResponseSchema, tags=["Retrieval"])
def search_knowledge_base(
    query_payload: RetrievalQuerySchema,
    db: Session = Depends(get_db)
):
    """Search the Knowledge Base for an employee inquiry and return ranked, grounded policies with source citations."""
    retriever = PolicyRetrievalService(db)
    return retriever.search(query=query_payload.query, top_k=query_payload.top_k)

# ---------------------------------------------------------------------------
# Audit Trail Endpoints
# ---------------------------------------------------------------------------

@api_router.get("/audit", response_model=List[AuditEventResponseSchema], tags=["Audit"])
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve the immutable audit event trail."""
    return db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()

@api_router.get("/audit/{request_id}", response_model=List[AuditEventResponseSchema], tags=["Audit"])
def get_audit_logs_for_request(
    request_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve audit trail filtered by a specific request_id, conversation_id, or ticket_id."""
    clean_id = request_id.strip()
    events = db.query(AuditEvent).filter(
        (AuditEvent.request_id == clean_id) |
        (AuditEvent.conversation_id == clean_id) |
        (AuditEvent.ticket_id == clean_id.upper()) |
        (AuditEvent.ticket_id == clean_id)
    ).order_by(AuditEvent.timestamp.desc()).all()
    return events

