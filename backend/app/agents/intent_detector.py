import re
from typing import Tuple

class IntentDetector:
    """Classifies user queries into granular IT service intents with strict policy grounding and injection defense."""

    @classmethod
    def detect_intent(cls, text: str) -> Tuple[str, str]:
        """
        Returns (intent, category)
        """
        lower = text.strip().lower()

        # 0. Prompt Injection & Adversarial Jailbreak Defense (Highest Priority)
        if any(p in lower for p in ["ignore all company policies", "ignore previous instructions", "forget all policies", "bypass policy", "disregard policy"]) and any(w in lower for w in ["admin", "access", "root", "privilege"]):
            return "prompt_injection_admin", "Information Security"

        if ("forget kb-09" in lower or "ignore kb-09" in lower or "override kb-09" in lower) or (any(w in lower for w in ["ignore", "forget", "disregard"]) and any(p in lower for p in ["phishing", "malware", "forward the email"])):
            return "prompt_injection_phishing", "Information Security"

        if any(p in lower for p in ["you are now the it director", "you are now it director", "pretend you are the director", "act as the it director", "you are now the admin", "you are now my manager"]):
            return "prompt_injection_roleplay", "Information Security"

        # 1. Anti-Hallucination & Out-of-Scope Data Pack Probes (Checked before broad keyword rules)
        if any(w in lower for w in ["policy for macs", "policy for mac", "mac policy", "macbook", "apple laptop", "macintosh", "apple mac", "imac", "macos"]):
            return "unsupported_mac_policy", "Hardware"

        if any(w in lower for w in ["maximum vpn duration", "max vpn duration", "max vpn time", "vpn session limit", "how long can i stay on vpn", "vpn timeout", "vpn connection limit", "session limit for vpn"]):
            return "vpn_duration_inquiry", "Network & Remote Access"

        if any(w in lower for w in ["manager approve admin", "can my manager approve admin", "manager sign off on admin", "manager request admin", "manager approval for admin"]):
            return "admin_approval_governance", "Enterprise Systems & Finance"

        if any(w in lower for w in ["sla for printer", "printer sla", "how fast will printer be fixed", "sla for printers", "printer repair time", "printer turnaround time"]):
            return "printer_sla_inquiry", "Peripherals & Printing"

        if any(w in lower for w in ["weekend support", "weekend policy", "support on sunday", "support on saturday", "after-hours policy", "after hours support", "it support on weekend", "support during weekends"]):
            return "unsupported_weekend_policy", "General IT"

        # 2. Phishing / Security Incident (High priority)
        if any(w in lower for w in ["phishing", "malware", "virus", "hacked", "suspicious email", "forwarding it to a few teammates", "forwarded to colleagues", "forwarding it to teammates"]):
            return "security_incident", "Information Security"

        # 3. Account lockout (specifically failed attempts / lockout)
        if any(w in lower for w in ["locked out", "lockout"]) or (("password" in lower or "tried" in lower) and any(n in lower for n in ["5 times", "6 times", "7 times", "failed attempts"])):
            return "account_lockout", "Authentication"

        # 4. Password reset (general self-service)
        if any(w in lower for w in ["reset password", "password reset", "change password", "forgot password", "reset my password", "forgot my password"]):
            return "password_reset", "Authentication"

        # 5. Admin / Privileged access
        if any(w in lower for w in ["admin access", "administrator access", "admin rights", "server admin", "reporting server"]):
            return "admin_access", "Enterprise Systems & Finance"

        # 6. VPN expired
        if "vpn" in lower and any(w in lower for w in ["expired", "credentials expired", "stopped working this morning"]):
            return "vpn_expired", "Network & Remote Access"

        # 7. VPN general / contractor / full-time
        if "vpn" in lower:
            return "vpn_access", "Network & Remote Access"

        # 8. Guest Wi-Fi
        if ("guest" in lower or "visitor" in lower) and ("wi-fi" in lower or "wifi" in lower):
            return "guest_wifi", "Network & Facilities"


        # 9. Printer issue
        if any(w in lower for w in ["printer", "print spooler", "paper jam", "print queue", "printing"]):
            return "printer_issue", "Peripherals & Printing"

        # 10. Mailbox quota
        if any(w in lower for w in ["mailbox is full", "mailbox quota", "can't send emails", "quota increase", "25gb", "50gb", "inbox full", "mailbox full"]):
            return "mailbox_quota", "Email & Collaboration"

        # 11. WFH equipment
        if any(w in lower for w in ["working from home", "work from home", "wfh", "home office", "get a monitor", "allowance"]):
            return "wfh_equipment", "Equipment & Facilities"

        # 12. Expense tool
        if any(w in lower for w in ["expense tool", "expense management", "expense software", "expensify"]):
            return "expense_tool_access", "Enterprise Systems & Finance"

        # 13. Hardware issue / repair
        if any(w in lower for w in ["flickering", "flicker", "screen", "keyboard", "battery", "display"]) and ("laptop" in lower or "monitor" in lower or "had it" in lower or "fix" in lower):
            return "hardware_issue", "Hardware"

        # 14. Laptop replacement
        if ("laptop" in lower or "notebook" in lower) and any(w in lower for w in ["won't turn on", "dead", "replacement", "replace", "3.5 years", "3 years", "4 years", "old"]):
            return "laptop_replacement", "Hardware"


        # 15. Software installation
        if any(w in lower for w in ["install", "installation", "software catalog", "browser extension", "extension", "software", "tool"]):
            return "software_installation", "Software & Applications"

        # 16. Ambiguous / Unknown IT issue
        return "unknown_it_issue", "General IT"

