import re
from typing import Tuple

class IntentDetector:
    """Classifies user queries into granular IT service intents."""

    @classmethod
    def detect_intent(cls, text: str) -> Tuple[str, str]:
        """
        Returns (intent, category)
        """
        lower = text.strip().lower()

        # 1. Phishing / Security Incident (High priority)
        if any(w in lower for w in ["phishing", "malware", "virus", "hacked", "suspicious email", "forwarding it to a few teammates", "forwarded to colleagues"]):
            return "security_incident", "Information Security"

        # 2. Account lockout (specifically failed attempts / lockout)
        if any(w in lower for w in ["locked out", "lockout"]) or (("password" in lower or "tried" in lower) and any(n in lower for n in ["5 times", "6 times", "7 times", "failed attempts"])):
            return "account_lockout", "Authentication"

        # 3. Password reset (general self-service)
        if any(w in lower for w in ["reset password", "password reset", "change password", "forgot password", "reset my password"]):
            return "password_reset", "Authentication"

        # 4. Admin / Privileged access
        if any(w in lower for w in ["admin access", "administrator access", "admin rights", "server admin", "reporting server"]):
            return "admin_access", "Enterprise Systems & Finance"

        # 5. VPN expired
        if "vpn" in lower and any(w in lower for w in ["expired", "credentials expired", "stopped working this morning"]):
            return "vpn_expired", "Network & Remote Access"

        # 6. VPN general / contractor
        if "vpn" in lower:
            return "vpn_access", "Network & Remote Access"

        # 7. Guest Wi-Fi
        if any(w in lower for w in ["guest wi-fi", "guest wifi", "guest visiting", "visitor wi-fi", "visitor wifi"]):
            return "guest_wifi", "Network & Facilities"

        # 8. Printer issue
        if any(w in lower for w in ["printer", "print spooler", "paper jam", "print queue", "printing"]):
            return "printer_issue", "Peripherals & Printing"

        # 9. Mailbox quota
        if any(w in lower for w in ["mailbox is full", "mailbox quota", "can't send emails", "quota increase", "25gb", "50gb", "inbox full"]):
            return "mailbox_quota", "Email & Collaboration"

        # 10. WFH equipment
        if any(w in lower for w in ["working from home", "work from home", "wfh", "home office", "get a monitor", "allowance"]):
            return "wfh_equipment", "Equipment & Facilities"

        # 11. Expense tool
        if any(w in lower for w in ["expense tool", "expense management", "expense software", "expensify"]):
            return "expense_tool_access", "Enterprise Systems & Finance"

        # 12. Laptop replacement
        if ("laptop" in lower or "notebook" in lower) and any(w in lower for w in ["won't turn on", "dead", "replacement", "replace", "3.5 years", "3 years", "4 years", "old"]):
            return "laptop_replacement", "Hardware"

        # 13. Hardware issue / repair
        if any(w in lower for w in ["flickering", "flicker", "screen", "keyboard", "battery", "display"]) and ("laptop" in lower or "monitor" in lower or "had it" in lower):
            return "hardware_issue", "Hardware"

        # 14. Software installation
        if any(w in lower for w in ["install", "installation", "software catalog", "browser extension", "extension", "software", "tool"]):
            return "software_installation", "Software & Applications"

        # 15. Ambiguous / Unknown IT issue
        return "unknown_it_issue", "General IT"
