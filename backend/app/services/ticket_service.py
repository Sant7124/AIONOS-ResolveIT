import re
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ticket import Ticket

class TicketService:
    """Enterprise Ticket Service handling lifecycle and duplicate ticket prevention."""

    @staticmethod
    def _generate_next_ticket_id(db: Session) -> str:
        """Find the highest numeric TK-XXXX and increment."""
        tickets = db.query(Ticket.ticket_id).all()
        max_num = 1051
        for (t_id,) in tickets:
            match = re.search(r"TK-(\d+)", t_id)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        return f"TK-{max_num + 1}"

    @classmethod
    def create_ticket(
        cls,
        db: Session,
        employee: str,
        email: Optional[str],
        category: str,
        issue_summary: str,
        description: Optional[str] = None,
        priority: str = "P3 - Medium",
        assigned_team: Optional[str] = None,
        source_policy_ids: Optional[List[str]] = None,
        status: str = "Active — assigned"
    ) -> Ticket:
        """Create and persist a new enterprise ticket."""
        ticket_id = cls._generate_next_ticket_id(db)
        new_ticket = Ticket(
            ticket_id=ticket_id,
            employee=employee,
            email=email,
            category=category,
            issue_summary=issue_summary,
            description=description,
            status=status,
            is_active=True,
            priority=priority,
            assigned_team=assigned_team,
            source_policy_ids=source_policy_ids or [],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        return new_ticket

    @staticmethod
    def get_ticket(db: Session, ticket_id: str) -> Optional[Ticket]:
        return db.query(Ticket).filter(Ticket.ticket_id == ticket_id.upper()).first()

    @staticmethod
    def list_active_tickets(db: Session) -> List[Ticket]:
        """Return all open, actionable tickets."""
        return db.query(Ticket).filter(Ticket.is_active == True).all()

    @staticmethod
    def update_ticket(
        db: Session,
        ticket_id: str,
        status: Optional[str] = None,
        resolution: Optional[str] = None,
        append_description: Optional[str] = None
    ) -> Optional[Ticket]:
        """Update an existing ticket."""
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id.upper()).first()
        if not ticket:
            return None
        if status is not None:
            ticket.status = status
            if "Resolved" in status or "closed" in status.lower() or "Rejected" in status:
                ticket.is_active = False
        if resolution is not None:
            ticket.resolution = resolution
        if append_description is not None:
            ticket.description = f"{ticket.description or ''}\n\n[Update {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}]: {append_description}"
        ticket.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def find_related_ticket(
        db: Session,
        employee: str,
        category: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> Optional[Ticket]:
        """
        Check if a relevant active ticket already exists for the employee to prevent duplicate creation.
        Matches active tickets where the employee matches, and either category or issue keywords match.
        """
        if not employee:
            return None

        clean_emp = employee.strip().lower()
        # Query active tickets
        active_tickets = db.query(Ticket).filter(Ticket.is_active == True).all()

        for t in active_tickets:
            t_emp = (t.employee or "").strip().lower()
            # Check for name match or partial name match (e.g. "Ritu Bhatia" vs "Ritu")
            emp_match = clean_emp in t_emp or t_emp in clean_emp or (clean_emp.split()[0] in t_emp.split())
            if not emp_match:
                continue

            # If employee matched, check if category or issue matches
            if category and t.category and t.category.lower() == category.lower():
                return t

            if keywords:
                summary_lower = (t.issue_summary or "").lower()
                desc_lower = (t.description or "").lower()
                for kw in keywords:
                    if kw.lower() in summary_lower or kw.lower() in desc_lower:
                        return t

        return None
