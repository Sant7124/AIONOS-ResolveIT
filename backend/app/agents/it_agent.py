import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, ConversationMessage
from app.models.agent_decision import AgentDecision
from app.models.audit_event import AuditEvent
from app.models.policy import Policy
from app.schemas.agent import (
    AgentChatRequest, 
    AgentChatResponse, 
    SourceCitationSchema, 
    TicketDetailsSchema
)
from app.retrieval.retrieval_service import PolicyRetrievalService
from app.services.ticket_service import TicketService
from app.agents.intent_detector import IntentDetector
from app.agents.entity_extractor import EntityExtractor
from app.agents.sufficiency_checker import SufficiencyChecker
from app.policy.rules_engine import RulesEngine, PolicyEvaluationResult

class ITServiceAgent:
    """Core Enterprise IT Service Agent executing the policy-grounded workflow."""

    def __init__(self, db: Session):
        self.db = db
        self.retriever = PolicyRetrievalService(db)

    def process_message(self, request: AgentChatRequest) -> AgentChatResponse:
        message_text = request.message.strip()
        employee_name = request.employee_name or "Employee"
        employee_email = request.employee_email or "employee@veridian-corp.example"

        # 1. Manage Conversation Session
        conv_id = request.conversation_id or str(uuid.uuid4())
        conversation = self.db.query(Conversation).filter(Conversation.id == conv_id).first()
        is_continuing_clarification = False
        prior_context = {}

        if not conversation:
            conversation = Conversation(
                id=conv_id,
                employee_name=employee_name,
                employee_email=employee_email,
                current_state="INITIAL",
                context_data={}
            )
            self.db.add(conversation)
            self.db.commit()
        else:
            # Check if we are resuming an active clarification
            if conversation.current_state == "CLARIFYING" and conversation.active_intent:
                is_continuing_clarification = True
                prior_context = conversation.context_data or {}

        # Log incoming employee message
        user_msg = ConversationMessage(
            conversation_id=conv_id,
            sender_type="EMPLOYEE",
            content=message_text
        )
        self.db.add(user_msg)
        self.db.commit()

        # 2. Intent Detection & Classification with Conversation Memory
        detected_intent, detected_category = IntentDetector.detect_intent(message_text)

        if is_continuing_clarification:
            # If the user is responding to a pending question, preserve the active intent
            if detected_intent in ["unknown_it_issue", "general_inquiry"] or not detected_intent:
                intent = conversation.active_intent
                category = conversation.active_category or detected_category
            else:
                intent = detected_intent
                category = detected_category
        else:
            intent = detected_intent
            category = detected_category

        # 3. Entity Extraction with Prior Context Synthesis
        extraction_context = {
            **prior_context,
            **(request.context or {}),
            "pending_question": conversation.pending_question,
            "active_intent": intent
        }
        new_entities = EntityExtractor.extract_entities(message_text, context=extraction_context)
        
        # Merge accumulated entities across conversation turns
        entities = {**prior_context}
        for k, v in new_entities.items():
            if v is not None:
                entities[k] = v

        # 4. Grounded Policy Retrieval
        # Search using both original issue and any clarifying details
        search_query = message_text
        if is_continuing_clarification and conversation.pending_question:
            search_query = f"{conversation.active_intent.replace('_', ' ')} {message_text}"
        retrieval_resp = self.retriever.search(query=search_query, top_k=3)
        retrieved_policies = retrieval_resp.results

        # 5. Ticket History Lookup & Duplicate Ticket Prevention
        active_related_ticket = TicketService.find_related_ticket(
            self.db,
            employee=employee_name,
            category=category,
            keywords=[intent, entities.get("software_name"), "laptop", "printer", "vpn"]
        )

        # If the user is asking about an existing open ticket, reference or update it directly
        is_ticket_status_inquiry = any(w in message_text.lower() for w in ["update", "status", "waiting", "ticket", "follow up", "following up", "when will"])
        if active_related_ticket and is_ticket_status_inquiry:
            ticket_id = active_related_ticket.ticket_id
            updated_ticket = TicketService.update_ticket(
                self.db,
                ticket_id=ticket_id,
                append_description=f"Employee inquiry: {message_text}"
            )
            reply_text = (
                f"Notice: You already have an active ticket on file: {ticket_id} ({active_related_ticket.status}). "
                f"Assigned Team: {active_related_ticket.assigned_team or 'IT Operations'}. "
                f"Issue: {active_related_ticket.issue_summary}. "
                f"To avoid duplicate tickets, your update has been appended to the existing ticket."
            )
            ticket_details = TicketDetailsSchema(
                ticket_id=ticket_id,
                status=updated_ticket.status if updated_ticket else active_related_ticket.status,
                priority=active_related_ticket.priority,
                assigned_team=active_related_ticket.assigned_team,
                issue_summary=active_related_ticket.issue_summary
            )
            citations = self._build_citations(active_related_ticket.source_policy_ids or [r.policy_id for r in retrieved_policies[:1]])
            
            audit_id = self._record_audit(
                action="TICKET_UPDATED_PREVENT_DUPLICATE",
                conversation_id=conv_id,
                decision="UPDATE_TICKET",
                reason=f"Active ticket {ticket_id} referenced to prevent duplicate creation.",
                policy_refs=[c.policy_id for c in citations],
                ticket_id=ticket_id,
                metadata={
                    "employee_name": employee_name,
                    "employee_email": employee_email,
                    "raw_message": message_text,
                    "existing_ticket_id": ticket_id
                }
            )

            # Store Agent Message
            agent_msg = ConversationMessage(
                conversation_id=conv_id,
                sender_type="AGENT",
                content=reply_text
            )
            self.db.add(agent_msg)
            self.db.commit()

            return AgentChatResponse(
                conversation_id=conv_id,
                intent=intent,
                category=category,
                action="update_ticket",
                status=f"Referenced Active Ticket {ticket_id}",
                message=reply_text,
                ticket_id=ticket_id,
                ticket_details=ticket_details,
                sources=citations,
                audit_event_id=audit_id
            )

        # 6. Sufficiency Check
        is_sufficient, follow_ups, sufficiency_reason = SufficiencyChecker.check_sufficiency(
            intent=intent,
            entities=entities,
            raw_text=message_text
        )

        # If information is still insufficient, formulate targeted follow-up (Action: ASK)
        if not is_sufficient:
            conversation.current_state = "CLARIFYING"
            conversation.active_intent = intent
            conversation.active_category = category
            conversation.pending_question = follow_ups[0] if follow_ups else None
            conversation.context_data = entities
            self.db.commit()

            # Prepare citations from matched policies (empty if issue is completely unknown/ambiguous)
            citations = [] if intent == "unknown_it_issue" else self._build_citations([r.policy_id for r in retrieved_policies[:1]])


            # Audit event for follow-up asked
            audit_id = self._record_audit(
                action="FOLLOW_UP_ASKED",
                conversation_id=conv_id,
                decision="CLARIFY",
                reason=sufficiency_reason,
                policy_refs=[c.policy_id for c in citations],
                metadata={
                    "employee_name": employee_name,
                    "employee_email": employee_email,
                    "raw_message": message_text,
                    "intent": intent,
                    "follow_up_questions": follow_ups,
                    "extracted_entities": entities,
                    "is_multi_turn": is_continuing_clarification
                }
            )

            # Store Agent Message
            reply_text = (
                f"To assist you safely and apply corporate policy accurately, I need a little more information:\n"
                + "\n".join([f"• {q}" for q in follow_ups])
            )
            agent_msg = ConversationMessage(
                conversation_id=conv_id,
                sender_type="AGENT",
                content=reply_text
            )
            self.db.add(agent_msg)
            self.db.commit()

            return AgentChatResponse(
                conversation_id=conv_id,
                intent=intent,
                category=category,
                action="ask",
                status="Waiting on User Information",
                message=reply_text,
                follow_up_questions=follow_ups,
                sources=citations,
                audit_event_id=audit_id
            )

        # 7. Policy Evaluation via Deterministic Rules Engine
        eval_result = self._evaluate_policy_rules(intent, entities, message_text)

        # 8. Duplicate Ticket Prevention vs Ticket Generation
        ticket_id = None
        ticket_details = None
        
        # Canonical action mapping matching assignment specification: resolve|ask|ticket|escalate|update_ticket|reject
        action_map = {
            "CREATE_TICKET": "ticket",
            "RESOLVE": "resolve",
            "ASK": "ask",
            "ESCALATE": "escalate",
            "REJECT": "reject",
            "UPDATE_TICKET": "update_ticket"
        }
        final_action = action_map.get(eval_result.action, eval_result.action.lower())
        final_message = eval_result.message

        if eval_result.action in ("CREATE_TICKET", "ESCALATE") and eval_result.ticket_summary:
            # Check if an existing active ticket already covers this issue
            if active_related_ticket:
                # Reference existing ticket instead of creating a duplicate!
                ticket_id = active_related_ticket.ticket_id
                final_action = "update_ticket"
                updated_ticket = TicketService.update_ticket(
                    self.db,
                    ticket_id=ticket_id,
                    append_description=f"New employee inquiry: {message_text}"
                )
                final_message = (
                    f"Notice: You already have an active ticket on file: {ticket_id} ({active_related_ticket.status}). "
                    f"To avoid confusion and duplicate tracking, your latest request has been appended to the existing ticket.\n\n"
                    f"{eval_result.message}"
                )
                ticket_details = TicketDetailsSchema(
                    ticket_id=ticket_id,
                    status=updated_ticket.status if updated_ticket else active_related_ticket.status,
                    priority=active_related_ticket.priority,
                    assigned_team=active_related_ticket.assigned_team,
                    issue_summary=active_related_ticket.issue_summary
                )
            else:
                # Create a new ticket
                new_ticket = TicketService.create_ticket(
                    self.db,
                    employee=employee_name,
                    email=employee_email,
                    category=category,
                    issue_summary=eval_result.ticket_summary,
                    description=eval_result.ticket_description or message_text,
                    priority=eval_result.priority,
                    assigned_team=eval_result.assigned_team or eval_result.escalation_team or "IT Helpdesk",
                    source_policy_ids=eval_result.policy_ids,
                    status=eval_result.status
                )
                ticket_id = new_ticket.ticket_id
                ticket_details = TicketDetailsSchema(
                    ticket_id=new_ticket.ticket_id,
                    status=new_ticket.status,
                    priority=new_ticket.priority,
                    assigned_team=new_ticket.assigned_team,
                    issue_summary=new_ticket.issue_summary
                )

        # 9. Grounded Citations (ensuring only retrieved or rule-governed policies are cited)
        citations = self._build_citations(eval_result.policy_ids)

        # 10. Record Immutable Audit Event
        audit_id = self._record_audit(
            action=f"POLICY_DECISION_{eval_result.action}",
            conversation_id=conv_id,
            decision=eval_result.action,
            reason=eval_result.status,
            policy_refs=eval_result.policy_ids,
            ticket_id=ticket_id,
            metadata={
                "employee_name": employee_name,
                "employee_email": employee_email,
                "raw_message": message_text,
                "intent": intent,
                "category": category,
                "escalation_team": eval_result.escalation_team,
                "extracted_entities": entities,
                "duplicate_ticket_prevented": active_related_ticket is not None
            }
        )

        # Record Agent Decision
        decision_rec = AgentDecision(
            conversation_id=conv_id,
            ticket_id=ticket_id,
            decision_type=eval_result.action,
            reasoning=eval_result.status,
            cited_policy_ids=eval_result.policy_ids,
            action_summary=final_message[:200]
        )
        self.db.add(decision_rec)

        # Store Agent Message
        agent_msg = ConversationMessage(
            conversation_id=conv_id,
            sender_type="AGENT",
            content=final_message
        )
        # Update Conversation State based on evaluation action
        if eval_result.action == "ASK":
            conversation.current_state = "CLARIFYING"
            conversation.active_intent = intent
            conversation.active_category = category
            conversation.pending_question = eval_result.follow_up_questions[0] if eval_result.follow_up_questions else None
            conversation.context_data = entities
        elif eval_result.action == "RESOLVE":
            conversation.current_state = "RESOLVED"
            conversation.pending_question = None
            conversation.context_data = entities
        elif eval_result.action == "ESCALATE":
            conversation.current_state = "ESCALATED"
            conversation.pending_question = None
            conversation.context_data = entities
        elif eval_result.action == "REJECT":
            conversation.current_state = "REJECTED"
            conversation.pending_question = None
            conversation.context_data = entities
        else:
            conversation.current_state = "IN_PROGRESS"
            conversation.pending_question = None
            conversation.context_data = entities

        self.db.commit()

        return AgentChatResponse(
            conversation_id=conv_id,
            intent=intent,
            category=category,
            action=final_action,
            status=eval_result.status,
            message=final_message,
            follow_up_questions=eval_result.follow_up_questions,
            ticket_id=ticket_id,
            ticket_details=ticket_details,
            escalation_team=eval_result.escalation_team,
            sources=citations,
            audit_event_id=audit_id
        )

    def _evaluate_policy_rules(self, intent: str, entities: Dict[str, Any], raw_text: str) -> PolicyEvaluationResult:
        """Route to the deterministic rule engine based on classified intent."""
        if intent in ["account_lockout", "password_reset"]:
            return RulesEngine.evaluate_password(entities.get("failed_attempts"))

        elif intent in ["vpn_access", "vpn_expired"]:
            return RulesEngine.evaluate_vpn(
                is_contractor=entities.get("is_contractor", False),
                is_expired=entities.get("credentials_expired", False),
                has_manager_approval=entities.get("has_manager_approval", False)
            )

        elif intent in ["laptop_replacement", "hardware_issue"]:
            return RulesEngine.evaluate_laptop(
                age_years=entities.get("device_age_years"),
                is_dead_or_hardware_failure=entities.get("is_dead", False),
                is_screen_flicker_repairable=entities.get("is_screen_flickering", False)
            )

        elif intent == "software_installation":
            return RulesEngine.evaluate_software(
                software_name=entities.get("software_name", "requested software"),
                is_catalog=entities.get("is_in_catalog")
            )

        elif intent == "printer_issue":
            return RulesEngine.evaluate_printer(
                spooler_restarted=entities.get("spooler_restarted", False),
                asset_tag=entities.get("asset_tag")
            )

        elif intent == "mailbox_quota":
            return RulesEngine.evaluate_mailbox_quota(
                requested_gb=entities.get("requested_mailbox_gb"),
                has_manager_approval=entities.get("has_manager_approval", False)
            )

        elif intent == "guest_wifi":
            return RulesEngine.evaluate_guest_wifi()

        elif intent == "expense_tool_access":
            is_login = any(w in raw_text.lower() for w in ["login", "log in", "log into", "invalid credentials", "password", "credentials"])
            return RulesEngine.evaluate_expense_tool(
                is_login_issue=is_login,
                is_admin_request=False,
                has_justification=False,
                account_exists=entities.get("expense_account_exists")
            )


        elif intent == "admin_access":
            return RulesEngine.evaluate_expense_tool(
                is_login_issue=False,
                is_admin_request=True,
                has_justification=entities.get("has_business_justification", False)
            )

        elif intent == "security_incident":
            return RulesEngine.evaluate_security_incident(
                is_phishing=True,
                was_forwarded=entities.get("phishing_forwarded", False)
            )

        elif intent == "wfh_equipment":
            return RulesEngine.evaluate_wfh_equipment(
                remote_days=entities.get("remote_days_per_week"),
                has_manager_signoff=entities.get("has_manager_signoff", False)
            )

        elif intent == "unsupported_mac_policy":
            return RulesEngine.evaluate_unsupported_mac()

        elif intent == "vpn_duration_inquiry":
            return RulesEngine.evaluate_vpn_duration_inquiry()

        elif intent == "admin_approval_governance":
            return RulesEngine.evaluate_admin_approval_governance()

        elif intent == "printer_sla_inquiry":
            return RulesEngine.evaluate_printer_sla()

        elif intent == "unsupported_weekend_policy":
            return RulesEngine.evaluate_weekend_support()

        elif intent in ["prompt_injection", "prompt_injection_admin", "prompt_injection_phishing", "prompt_injection_roleplay"]:
            return RulesEngine.evaluate_prompt_injection(raw_text)

        else:
            return PolicyEvaluationResult(
                action="ASK",
                status="Clarification Required",
                message="Please describe which system or device you require assistance with.",
                policy_ids=[],
                follow_up_questions=["What specific IT service or device is having an issue?"]
            )


    def _build_citations(self, policy_ids: List[str]) -> List[SourceCitationSchema]:
        """Look up official policy titles and statements from the database."""
        citations: List[SourceCitationSchema] = []
        for pid in policy_ids:
            policy = self.db.query(Policy).filter(Policy.id == pid).first()
            if policy:
                citations.append(SourceCitationSchema(
                    policy_id=policy.id,
                    title=policy.title,
                    statement=policy.source_text
                ))
        return citations

    def _record_audit(
        self,
        action: str,
        conversation_id: Optional[str],
        decision: Optional[str],
        reason: Optional[str],
        policy_refs: List[str],
        ticket_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create an immutable AuditEvent record."""
        event_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
        event = AuditEvent(
            id=event_id,
            timestamp=datetime.now(timezone.utc),
            actor_type="AGENT",
            conversation_id=conversation_id,
            ticket_id=ticket_id,
            action=action,
            decision=decision,
            reason=reason,
            policy_references=policy_refs,
            event_metadata=metadata or {}
        )
        self.db.add(event)
        self.db.commit()
        return event_id
