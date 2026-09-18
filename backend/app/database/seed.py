import json
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, init_db
from app.models import Policy, SourceReference, EmployeeRequest, Ticket, AuditEvent
from app.core.config import settings

def load_json(file_path: str):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Fixture file not found: {file_path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def seed_policies(db: Session) -> int:
    data = load_json(settings.POLICIES_PATH)
    count = 0
    for p in data.get("policies", []):
        policy_id = p["id"]
        existing = db.query(Policy).filter(Policy.id == policy_id).first()
        
        section_name = "Asset Management Policy (Extract)" if policy_id == "ASSET-01" else "1. Knowledge Base / Policies"
        
        if existing:
            existing.title = p["title"]
            existing.category = p["category"]
            existing.summary = p["summary"]
            existing.source_text = p["source_text"]
            existing.conditions = p.get("conditions", [])
            existing.required_approvals = p.get("required_approvals", [])
            existing.allowed_actions = p.get("allowed_actions", [])
            existing.prohibited_actions = p.get("prohibited_actions", [])
            existing.escalation_required = p.get("escalation_required", False)
            existing.resolution_steps = p.get("resolution_steps", [])
            existing.time_constraints = p.get("time_constraints")
            existing.source_document = p.get("source_document", "Assignment 2_DataPack_InternalServiceAgent.pdf")
            existing.source_page = p.get("source_page", 1)
            existing.issuer = p.get("issuer")
            existing.last_updated = p.get("last_updated")
        else:
            new_policy = Policy(
                id=policy_id,
                title=p["title"],
                category=p["category"],
                summary=p["summary"],
                source_text=p["source_text"],
                conditions=p.get("conditions", []),
                required_approvals=p.get("required_approvals", []),
                allowed_actions=p.get("allowed_actions", []),
                prohibited_actions=p.get("prohibited_actions", []),
                escalation_required=p.get("escalation_required", False),
                resolution_steps=p.get("resolution_steps", []),
                time_constraints=p.get("time_constraints"),
                source_document=p.get("source_document", "Assignment 2_DataPack_InternalServiceAgent.pdf"),
                source_page=p.get("source_page", 1),
                issuer=p.get("issuer"),
                last_updated=p.get("last_updated")
            )
            db.add(new_policy)

        # Upsert SourceReference
        source_ref = db.query(SourceReference).filter(SourceReference.policy_id == policy_id).first()
        if not source_ref:
            source_ref = SourceReference(
                policy_id=policy_id,
                document_name=p.get("source_document", "Assignment 2_DataPack_InternalServiceAgent.pdf"),
                section_name=section_name,
                page_number=p.get("source_page", 1),
                exact_quote=p["source_text"],
                context_notes=f"Authoritative text for {policy_id}: {p['title']}"
            )
            db.add(source_ref)
        else:
            source_ref.exact_quote = p["source_text"]
            source_ref.page_number = p.get("source_page", 1)
            source_ref.section_name = section_name

        count += 1
    db.commit()
    return count

def seed_employee_requests(db: Session) -> int:
    data = load_json(settings.REQUESTS_PATH)
    count = 0
    for r in data.get("requests", []):
        req_id = r["request_id"]
        existing = db.query(EmployeeRequest).filter(EmployeeRequest.request_id == req_id).first()
        if existing:
            existing.employee = r["employee"]
            existing.email = r["email"]
            existing.date_opened = r["date_opened"]
            existing.request_text = r["request"]
            existing.initial_action_taken = r["initial_action_taken"]
            existing.expected_policy_id = r.get("expected_policy_id")
            existing.cross_reference_policy_id = r.get("cross_reference_policy_id")
            existing.category = r.get("category")
            existing.expected_outcome = r.get("expected_outcome")
            existing.analysis = r.get("analysis")
        else:
            new_req = EmployeeRequest(
                request_id=req_id,
                employee=r["employee"],
                email=r["email"],
                date_opened=r["date_opened"],
                request_text=r["request"],
                initial_action_taken=r["initial_action_taken"],
                expected_policy_id=r.get("expected_policy_id"),
                cross_reference_policy_id=r.get("cross_reference_policy_id"),
                category=r.get("category"),
                expected_outcome=r.get("expected_outcome"),
                analysis=r.get("analysis")
            )
            db.add(new_req)
        count += 1
    db.commit()
    return count

def seed_tickets(db: Session) -> int:
    data = load_json(settings.TICKETS_PATH)
    count = 0
    for t in data.get("tickets", []):
        ticket_id = t["ticket_id"]
        existing = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        
        created_dt = datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")) if "created_at" in t else datetime.utcnow()
        updated_dt = datetime.fromisoformat(t["updated_at"].replace("Z", "+00:00")) if "updated_at" in t else datetime.utcnow()

        if existing:
            existing.employee = t["employee"]
            existing.email = t.get("email")
            existing.category = t.get("category", "General IT")
            existing.issue_summary = t["issue_summary"]
            existing.description = t.get("description")
            existing.status = t["status"]
            existing.is_active = t.get("is_active", not ("Resolved" in t["status"] or "Rejected" in t["status"] or "closed" in t["status"].lower()))
            existing.priority = t.get("priority", "P3 - Medium")
            existing.assigned_team = t.get("assigned_team")
            existing.resolution = t.get("resolution") or t.get("resolution_note")
            existing.precedent_value = t.get("precedent_value")
            existing.source_policy_ids = t.get("source_policy_ids") or ([t["policy_id"]] if "policy_id" in t else [])
            existing.updated_at = updated_dt
        else:
            new_ticket = Ticket(
                ticket_id=ticket_id,
                employee=t["employee"],
                email=t.get("email"),
                category=t.get("category", "General IT"),
                issue_summary=t["issue_summary"],
                description=t.get("description"),
                status=t["status"],
                is_active=t.get("is_active", not ("Resolved" in t["status"] or "Rejected" in t["status"] or "closed" in t["status"].lower())),
                priority=t.get("priority", "P3 - Medium"),
                assigned_team=t.get("assigned_team"),
                resolution=t.get("resolution") or t.get("resolution_note"),
                precedent_value=t.get("precedent_value"),
                source_policy_ids=t.get("source_policy_ids") or ([t["policy_id"]] if "policy_id" in t else []),
                created_at=created_dt,
                updated_at=updated_dt
            )
            db.add(new_ticket)
        count += 1
    # Clean up any transient/test tickets beyond the 10 initial dataset tickets
    db.query(Ticket).filter(~Ticket.ticket_id.in_([f"TK-{i}" for i in range(1042, 1052)])).delete(synchronize_session=False)
    db.commit()
    return count

def seed_initial_audit(db: Session):
    existing = db.query(AuditEvent).filter(AuditEvent.action == "SYSTEM_INITIALIZED").first()
    if not existing:
        event = AuditEvent(
            actor_type="SYSTEM",
            action="SYSTEM_INITIALIZED",
            decision="READY",
            reason="Authoritative Data Pack fixtures seeded successfully.",
            policy_references=["KB-01", "KB-02", "KB-03", "KB-04", "KB-05", "KB-06", "KB-07", "KB-08", "KB-09", "KB-10", "ASSET-01"],
            event_metadata={
                "simulation_window": "Monday, 21 September 2026 – Friday, 25 September 2026",
                "source_document": "Assignment 2_DataPack_InternalServiceAgent.pdf",
                "policies_count": 11,
                "requests_count": 15,
                "tickets_count": 10
            }
        )
        db.add(event)
        db.commit()

def run_seed():
    """Main entrypoint for seeding database idempotently."""
    print("=" * 60)
    print("Veridian IT Copilot — Seeding Authoritative Data Foundation")
    print("=" * 60)
    init_db()
    db = SessionLocal()
    try:
        policy_count = seed_policies(db)
        print(f"[OK] Seeded {policy_count} policies + source references.")
        
        req_count = seed_employee_requests(db)
        print(f"[OK] Seeded {req_count} employee requests (REQ-01 to REQ-15).")
        
        ticket_count = seed_tickets(db)
        print(f"[OK] Seeded {ticket_count} ticket queue records (TK-1042 to TK-1051).")
        
        seed_initial_audit(db)
        print("[OK] Seeded initial system audit event.")
        print("=" * 60)
        print("Database seeding completed successfully. Zero duplicates.")
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
