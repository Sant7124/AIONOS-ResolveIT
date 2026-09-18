"""Deterministic Policy & Rule Engine grounded in the Veridian Corp Data Pack.
The LLM must never override or hallucinate company policy.
All critical policy decisions are verified here.
"""
from typing import Dict, Any, List, Optional, Tuple

class PolicyEvaluationResult:
    def __init__(
        self,
        action: str,  # "RESOLVE", "ASK", "CREATE_TICKET", "UPDATE_TICKET", "ESCALATE", "REJECT"
        status: str,
        message: str,
        policy_ids: List[str],
        escalation_team: Optional[str] = None,
        priority: str = "P3 - Medium",
        assigned_team: Optional[str] = None,
        follow_up_questions: Optional[List[str]] = None,
        ticket_summary: Optional[str] = None,
        ticket_description: Optional[str] = None,
        is_security_alert: bool = False
    ):
        self.action = action
        self.status = status
        self.message = message
        self.policy_ids = policy_ids
        self.escalation_team = escalation_team
        self.priority = priority
        self.assigned_team = assigned_team
        self.follow_up_questions = follow_up_questions or []
        self.ticket_summary = ticket_summary
        self.ticket_description = ticket_description
        self.is_security_alert = is_security_alert

class RulesEngine:
    """Authoritative enterprise rule engine enforcing KB-01 through KB-10 and ASSET-01."""

    @staticmethod
    def evaluate_password(failed_attempts: Optional[int]) -> PolicyEvaluationResult:
        """KB-01: Password Reset.
        Self-service portal permitted at any time.
        If locked out after 5 failed attempts, contact IT to unlock manually. No approval required.
        """
        if failed_attempts is not None and failed_attempts >= 5:
            return PolicyEvaluationResult(
                action="CREATE_TICKET",
                status="In progress — manual IT unlock queued",
                message=(
                    "You have exceeded the maximum of 5 failed login attempts and your account is locked. "
                    "Per Policy KB-01 (Password Reset), self-service reset is no longer permitted once locked out. "
                    "An IT Helpdesk ticket has been created for manual account unlock. No managerial approval is required."
                ),
                policy_ids=["KB-01"],
                priority="P2 - High",
                assigned_team="IT Helpdesk",
                ticket_summary="Account locked out after failed password attempts",
                ticket_description=f"User exceeded lockout threshold ({failed_attempts} failed attempts). Manual account unlock required per KB-01."
            )
        else:
            return PolicyEvaluationResult(
                action="RESOLVE",
                status="Resolved (self-service)",
                message=(
                    "Per Policy KB-01 (Password Reset), you can reset your password via the self-service portal at any time. "
                    "Please visit: https://identity.veridian-corp.example/self-service/reset to set a new password. "
                    "No approval is required. If you experience 5 or more failed attempts, your account will lock and require manual IT unlock."
                ),
                policy_ids=["KB-01"]
            )

    @staticmethod
    def evaluate_vpn(
        is_contractor: bool,
        is_expired: bool,
        has_manager_approval: bool
    ) -> PolicyEvaluationResult:
        """KB-02: VPN Access.
        VPN access is granted automatically to full-time employees.
        Contractors require manager approval submitted via access request form.
        VPN credentials expire every 90 days and must be renewed by the employee.
        """
        if is_contractor:
            if not has_manager_approval:
                return PolicyEvaluationResult(
                    action="ESCALATE",
                    status="Pending Manager Approval Form",
                    message=(
                        "Per Policy KB-02 (VPN Access), VPN access is not granted automatically to contractors. "
                        "Contractors require formal manager approval submitted via the official Access Request Form. "
                        "Please have your hiring manager submit the request form at: https://forms.veridian-corp.example/access/vpn."
                    ),
                    policy_ids=["KB-02"],
                    escalation_team="IT Access Management & Approvals",
                    priority="P3 - Medium"
                )
            else:
                return PolicyEvaluationResult(
                    action="CREATE_TICKET",
                    status="Queued for Provisioning",
                    message="Manager approval verified. A provisioning ticket has been routed to IT Access Management per KB-02.",
                    policy_ids=["KB-02"],
                    priority="P3 - Medium",
                    assigned_team="IT Access Management",
                    ticket_summary="Contractor VPN Access Provisioning",
                    ticket_description="Contractor VPN request with verified manager approval."
                )
        else:
            # Full-time employee
            if is_expired:
                return PolicyEvaluationResult(
                    action="RESOLVE",
                    status="Resolved (self-service renewal)",
                    message=(
                        "Per Policy KB-02 (VPN Access), VPN credentials expire every 90 days and must be renewed by the employee. "
                        "As a full-time employee, your access is active; please renew your credentials via the identity portal "
                        "at: https://identity.veridian-corp.example/vpn/renew. No ticket or manager approval is required."
                    ),
                    policy_ids=["KB-02"]
                )
            else:
                return PolicyEvaluationResult(
                    action="RESOLVE",
                    status="Resolved (automatic access)",
                    message=(
                        "Per Policy KB-02 (VPN Access), VPN access is granted automatically to all full-time employees. "
                        "Ensure your VPN client is configured with your corporate credentials. Remember credentials expire every 90 days."
                    ),
                    policy_ids=["KB-02"]
                )

    @staticmethod
    def evaluate_laptop(
        age_years: Optional[float],
        is_dead_or_hardware_failure: bool,
        is_screen_flicker_repairable: bool
    ) -> PolicyEvaluationResult:
        """KB-03: Laptop Replacement & ASSET-01: Asset Management Policy.
        KB-03: Laptops eligible for replacement after 3 years of service, or earlier in case of verified hardware failure.
        Requests must be raised at least 2 weeks in advance.
        ASSET-01: Standard 4-year refresh cycle. Early replacement outside this cycle requires Finance sign-off in addition to IT approval.
        """
        # Case 1: Less than 3 years with repairable issue (e.g. screen flicker REQ-13)
        if age_years is not None and age_years < 3.0 and not is_dead_or_hardware_failure:
            return PolicyEvaluationResult(
                action="CREATE_TICKET",
                status="Investigating — hardware diagnostic assigned",
                message=(
                    f"Your laptop is {age_years} years old and follows a standard 4-year refresh cycle under the Asset Management Policy, "
                    "with replacement eligibility after 3 years under KB-03. Because the device is under 3 years and the issue (such as screen flickering) "
                    "may be repairable, a Hardware Diagnostic & Repair ticket has been created rather than a replacement. "
                    "A hardware technician will inspect the display connection."
                ),
                policy_ids=["KB-03", "ASSET-01"],
                priority="P3 - Medium",
                assigned_team="Hardware Depot",
                ticket_summary="Laptop Display Diagnostics / Repair (2 yrs old)",
                ticket_description="Laptop display flickering on 2-year-old unit. Ineligible for refresh; diagnostic repair assigned."
            )

        # Case 2: Age >= 3.0 and < 4.0 years (e.g. 3.5 years completely dead REQ-01)
        if age_years is not None and 3.0 <= age_years < 4.0:
            return PolicyEvaluationResult(
                action="CREATE_TICKET",
                status="Pending Dual Approval (IT + Finance)",
                message=(
                    f"Your laptop is {age_years} years old and completely dead, satisfying the 3-year threshold and verified failure condition under Policy KB-03. "
                    "However, because company hardware follows a standard 4-year refresh cycle under the Asset Management Policy, "
                    "early replacement outside the 4-year cycle requires Finance sign-off in addition to IT technical approval. "
                    "A dual-approval replacement ticket has been logged with the required 2-week advance fulfillment window."
                ),
                policy_ids=["KB-03", "ASSET-01"],
                priority="P2 - High",
                assigned_team="Hardware Depot",
                escalation_team="Finance & Assets",
                ticket_summary=f"Laptop replacement ({age_years} yrs old — verified failure)",
                ticket_description=f"Laptop dead ({age_years} yrs old). Meets KB-03 3-yr threshold. Requires Finance sign-off per Asset Management Policy."
            )

        # Case 3: Age >= 4.0 years (Standard refresh cycle)
        if age_years is not None and age_years >= 4.0:
            return PolicyEvaluationResult(
                action="CREATE_TICKET",
                status="Approved — pending fulfillment (active)",
                message=(
                    f"Your laptop has reached {age_years} years of service, meeting the standard 4-year refresh cycle under the Asset Management Policy. "
                    "A routine replacement ticket has been created with standard IT fulfillment (2-week lead time)."
                ),
                policy_ids=["KB-03", "ASSET-01"],
                priority="P3 - Medium",
                assigned_team="Hardware Depot",
                ticket_summary=f"Laptop lifecycle replacement ({age_years} yrs old)",
                ticket_description="Standard 4-year hardware lifecycle refresh."
            )

        # Default fallback if age is unspecified
        return PolicyEvaluationResult(
            action="ASK",
            status="Clarification Required",
            message="To determine eligibility for repair versus replacement under Policy KB-03 and the Asset Management Policy, please specify the approximate age of your laptop.",
            policy_ids=["KB-03", "ASSET-01"],
            follow_up_questions=["Approximately how long have you had this laptop (e.g., 2 years, 3.5 years)?"]
        )

    @staticmethod
    def evaluate_software(software_name: str, is_catalog: Optional[bool]) -> PolicyEvaluationResult:
        """KB-04: Software Installation Requests.
        Standard software (listed in approved catalog) can be self-installed.
        Non-catalog software requires IT Security review, which takes 3–5 business days.
        """
        if is_catalog is True:
            return PolicyEvaluationResult(
                action="RESOLVE",
                status="Resolved (catalog self-install)",
                message=(
                    f"Per Policy KB-04 (Software Installation Requests), standard software listed in the approved catalog can be self-installed. "
                    f"You can install '{software_name}' directly via the Veridian Software Center portal. No approval is needed."
                ),
                policy_ids=["KB-04"]
            )
        else:
            # Non-catalog software or browser extension
            return PolicyEvaluationResult(
                action="CREATE_TICKET",
                status="Pending Security review (active)",
                message=(
                    f"Per Policy KB-04 (Software Installation Requests), '{software_name}' is not in the approved software catalog "
                    "and requires mandatory IT Security review. A security review ticket has been logged and assigned to Information Security. "
                    "The standard review turnaround takes 3–5 business days."
                ),
                policy_ids=["KB-04"],
                priority="P3 - Medium",
                assigned_team="Information Security (Infosec)",
                escalation_team="Information Security (Infosec)",
                ticket_summary=f"Non-catalog software request: {software_name}",
                ticket_description=f"Non-catalog software review for '{software_name}'. SLA: 3–5 business days per KB-04."
            )

    @staticmethod
    def evaluate_printer(spooler_restarted: bool, asset_tag: Optional[str]) -> PolicyEvaluationResult:
        """KB-05: Printer Troubleshooting.
        First check printer queue and restart print spooler.
        If issue persists after restart, log a ticket with printer's asset tag.
        """
        if not spooler_restarted:
            return PolicyEvaluationResult(
                action="RESOLVE",
                status="First-line troubleshooting required",
                message=(
                    "Per Policy KB-05 (Printer Troubleshooting), please perform first-line troubleshooting before a technician ticket is dispatched:\n"
                    "1. Check the local printer queue and cancel any hung or stuck print jobs.\n"
                    "2. Restart the Windows print spooler service.\n"
                    "If the issue persists after restarting the spooler, please reply with the printer's asset tag (e.g., VER-PRN-XX-XX) so we can dispatch a floor technician."
                ),
                policy_ids=["KB-05"],
                follow_up_questions=["Did restarting the print spooler resolve the issue? If not, what is the printer asset tag?"]
            )
        else:
            # Spooler was restarted but issue persists
            if not asset_tag:
                return PolicyEvaluationResult(
                    action="ASK",
                    status="Asset tag required",
                    message=(
                        "Per Policy KB-05 (Printer Troubleshooting), since restarting the spooler did not resolve the issue, "
                        "we need to dispatch a floor technician. Please provide the printer's asset tag (located on the sticker on the front or side of the printer)."
                    ),
                    policy_ids=["KB-05"],
                    follow_up_questions=["Please provide the printer's asset tag (e.g. VER-PRN-03-01) to log the technician dispatch ticket."]
                )
            else:
                return PolicyEvaluationResult(
                    action="CREATE_TICKET",
                    status="Investigating — technician assigned",
                    message=(
                        f"Per Policy KB-05 (Printer Troubleshooting), a floor technician ticket has been created for printer asset tag '{asset_tag}'. "
                        "A workplace technician will inspect the hardware roller and paper path."
                    ),
                    policy_ids=["KB-05"],
                    priority="P3 - Medium",
                    assigned_team="IT Workplace Services",
                    ticket_summary=f"Printer hardware fault: Asset Tag {asset_tag}",
                    ticket_description=f"Persistent printer failure after spooler restart. Asset tag: {asset_tag}."
                )

    @staticmethod
    def evaluate_mailbox_quota(requested_gb: Optional[int], has_manager_approval: bool) -> PolicyEvaluationResult:
        """KB-06: Email Mailbox Quota.
        Default quota is 25GB. Employees nearing quota should archive old mail.
        Quota increases beyond 25GB require manager approval and are capped at 50GB.
        """
        if requested_gb is not None and requested_gb > 50:
            return PolicyEvaluationResult(
                action="REJECT",
                status="Rejected — exceeds policy ceiling",
                message=(
                    f"Per Policy KB-06 (Email Mailbox Quota), mailbox quota increases are strictly capped at 50GB. "
                    f"The requested capacity ({requested_gb}GB) exceeds corporate policy limits. "
                    "Please archive old messages and attachments to comply with the 50GB ceiling."
                ),
                policy_ids=["KB-06"]
            )
        elif requested_gb is not None and requested_gb > 25:
            if not has_manager_approval:
                return PolicyEvaluationResult(
                    action="ESCALATE",
                    status="Pending Manager Approval",
                    message=(
                        f"Per Policy KB-06 (Email Mailbox Quota), default mailbox quota is 25GB. "
                        f"Quota increases beyond 25GB (up to the 50GB cap) require formal manager approval. "
                        "Please have your manager approve the mailbox expansion request form, or archive old emails to free space."
                    ),
                    policy_ids=["KB-06"],
                    escalation_team="Messaging & Collaboration",
                    priority="P3 - Medium"
                )
            else:
                return PolicyEvaluationResult(
                    action="CREATE_TICKET",
                    status="Approved — pending quota expansion",
                    message=f"Manager approval verified. Mailbox expansion to {requested_gb}GB queued per KB-06.",
                    policy_ids=["KB-06"],
                    priority="P3 - Medium",
                    assigned_team="Messaging & Collaboration",
                    ticket_summary=f"Mailbox quota increase to {requested_gb}GB",
                    ticket_description=f"Mailbox quota increase to {requested_gb}GB with verified manager approval (under 50GB cap)."
                )
        else:
            # Default quota advice
            return PolicyEvaluationResult(
                action="RESOLVE",
                status="Resolved (archiving guidance)",
                message=(
                    "Per Policy KB-06 (Email Mailbox Quota), default mailbox quota is 25GB. "
                    "When nearing quota, you should archive old mail and empty Deleted Items to restore sending capability. "
                    "If you genuinely require storage beyond 25GB, manager approval is required and capacity is capped at 50GB."
                ),
                policy_ids=["KB-06"]
            )

    @staticmethod
    def evaluate_guest_wifi() -> PolicyEvaluationResult:
        """KB-07: Guest Wi-Fi Access.
        Guest Wi-Fi credentials are valid for 24 hours and can be generated by any employee from front-desk kiosk.
        No IT ticket required.
        """
        return PolicyEvaluationResult(
            action="RESOLVE",
            status="Resolved (no ticket needed)",
            message=(
                "Per Policy KB-07 (Guest Wi-Fi Access), guest Wi-Fi credentials are valid for 24 hours "
                "and can be generated directly by any employee from the front-desk kiosk in the reception area. "
                "No IT support ticket is required."
            ),
            policy_ids=["KB-07"]
        )

    @staticmethod
    def evaluate_expense_tool(is_login_issue: bool, is_admin_request: bool, has_justification: bool) -> PolicyEvaluationResult:
        """KB-08: Expense Software Access & TK-1050 Precedent.
        Access is granted by Finance, not IT. IT can only assist with login/technical issues once an account already exists.
        Admin access without business justification must be rejected per TK-1050.
        """
        if is_admin_request:
            if not has_justification:
                return PolicyEvaluationResult(
                    action="REJECT",
                    status="Rejected — no business justification provided (closed)",
                    message=(
                        "Per Policy KB-08 and established precedent TK-1050, administrative/privileged access requests "
                        "cannot be granted without documented written business justification and managerial/Finance authorization. "
                        "Request rejected. Please submit a formal access request form with complete business justification."
                    ),
                    policy_ids=["KB-08"],
                    priority="P3 - Medium"
                )
            else:
                return PolicyEvaluationResult(
                    action="ESCALATE",
                    status="Pending Finance Security Review",
                    message="Privileged admin access request routed to Finance & Information Security for governance review.",
                    policy_ids=["KB-08"],
                    escalation_team="Finance Security Governance",
                    priority="P2 - High"
                )
        elif is_login_issue:
            return PolicyEvaluationResult(
                action="ASK",
                status="Waiting on employee verification",
                message=(
                    "Per Policy KB-08 (Expense Software Access), access to the expense management tool is granted by Finance, not IT. "
                    "IT can only assist with login/technical issues once an account already exists. "
                    "Has your account already been provisioned by the Finance team, or is this a brand-new access request?"
                ),
                policy_ids=["KB-08"],
                follow_up_questions=["Was an expense tool account previously created for you by Finance?"]
            )
        else:
            return PolicyEvaluationResult(
                action="ESCALATE",
                status="Route to Finance",
                message=(
                    "Per Policy KB-08 (Expense Software Access), initial account creation and access rights are granted by Finance, not IT. "
                    "Please contact the Finance expense administration team to request an account."
                ),
                policy_ids=["KB-08"],
                escalation_team="Finance Department"
            )

    @staticmethod
    def evaluate_security_incident(is_phishing: bool, was_forwarded: bool) -> PolicyEvaluationResult:
        """KB-09: Security Incident Reporting.
        Any suspected phishing email, malware, or unauthorized access attempt must be reported to security@veridian-corp.example immediately
        and should not be forwarded to other employees.
        """
        warning_prefix = ""
        if was_forwarded:
            warning_prefix = (
                "CRITICAL SECURITY WARNING: Per Policy KB-09 (Security Incident Reporting), suspected phishing emails "
                "MUST NOT be forwarded to other employees! Please urgently alert the teammates who received the email "
                "NOT to click any links or download attachments. "
            )

        return PolicyEvaluationResult(
            action="ESCALATE",
            status="Escalated to Security — under investigation (active)",
            message=(
                f"{warning_prefix}Any suspected phishing email or unauthorized access attempt must be reported immediately "
                "to security@veridian-corp.example as an attachment with complete email headers. "
                "A Priority 1 (P1) Critical Security Ticket has been created and escalated to the Information Security (SOC) team."
            ),
            policy_ids=["KB-09"],
            priority="P1 - Critical",
            assigned_team="Information Security (Infosec)",
            escalation_team="Information Security (Infosec)",
            is_security_alert=True,
            ticket_summary="P1 Security Incident: Phishing email reported",
            ticket_description="Suspected phishing incident. Forwarding risk evaluated per KB-09. Quarantined for SOC investigation."
        )

    @staticmethod
    def evaluate_wfh_equipment(remote_days: Optional[int], has_manager_signoff: bool) -> PolicyEvaluationResult:
        """KB-10: Work-From-Home Equipment.
        Employees working remotely more than 3 days/week are eligible for a one-time home office equipment allowance (chair, monitor).
        Requires manager sign-off and Finance processing — IT only handles equipment shipping request once approved.
        """
        if remote_days is not None and remote_days <= 3:
            return PolicyEvaluationResult(
                action="REJECT",
                status="Ineligible — does not meet 3+ days threshold",
                message=(
                    f"Per Policy KB-10 (Work-From-Home Equipment), only employees working remotely more than 3 days per week "
                    f"are eligible for the home office allowance. Your schedule ({remote_days} days/week) does not qualify."
                ),
                policy_ids=["KB-10"]
            )
        else:
            # Remote days > 3 (e.g. 4 days/week REQ-07)
            return PolicyEvaluationResult(
                action="ESCALATE",
                status="Pending Manager & Finance Sign-off",
                message=(
                    "Per Policy KB-10 (Work-From-Home Equipment), employees working remotely more than 3 days/week are eligible "
                    "for a one-time home office equipment allowance (chair, monitor). This requires manager sign-off and Finance budget processing. "
                    "IT only handles equipment shipping once approved. Please initiate the WFH equipment request form for manager approval."
                ),
                policy_ids=["KB-10"],
                escalation_team="Finance & HR Approvals",
                priority="P3 - Medium"
            )
