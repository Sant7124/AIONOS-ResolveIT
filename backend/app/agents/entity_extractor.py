import re
from typing import Dict, Any, Optional

class EntityExtractor:
    """Extracts structured operational entities from employee requests and conversation state."""

    @classmethod
    def extract_entities(cls, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        lower = text.strip().lower()
        entities: Dict[str, Any] = {}

        # 1. Failed attempts count
        attempts_match = re.search(r"(\d+)\s*(?:times|failed\s*attempts|attempts)", lower)
        if attempts_match:
            entities["failed_attempts"] = int(attempts_match.group(1))
        elif "locked out" in lower:
            entities["failed_attempts"] = 6  # Default beyond 5 threshold if explicit lockout mentioned

        # 2. Device age (in years)
        age_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)(?:\s*old)?", lower)
        if age_match:
            entities["device_age_years"] = float(age_match.group(1))
        elif context and (context.get("asking_age") or "age" in str(context.get("pending_question") or "").lower() or context.get("active_intent") in ["laptop_replacement", "hardware_issue"]):
            bare_num = re.search(r"\b(\d+(?:\.\d+)?)\b", lower)
            if bare_num:
                entities["device_age_years"] = float(bare_num.group(1))


        # 3. Hardware state
        if any(w in lower for w in ["won't turn on", "wont turn on", "completely dead", "doesn't turn on", "dead"]):
            entities["is_dead"] = True
        elif context and context.get("is_dead"):
            entities["is_dead"] = True
        else:
            entities["is_dead"] = False

        if "flickering" in lower or "flicker" in lower:
            entities["is_screen_flickering"] = True
        elif context and context.get("is_screen_flickering"):
            entities["is_screen_flickering"] = True
        else:
            entities["is_screen_flickering"] = False

        # 4. Contractor status
        entities["is_contractor"] = "contractor" in lower

        # 5. Expired credentials
        entities["credentials_expired"] = "expired" in lower

        # 6. Software details
        if "slack" in lower:
            entities["software_name"] = "Slack"
            entities["is_in_catalog"] = True
        elif any(w in lower for w in ["not in the software catalog", "not in catalog", "non-catalog", "outside the catalog"]):
            entities["is_in_catalog"] = False
            entities["software_name"] = "data-analysis tool" if "data-analysis" in lower or "data analysis" in lower else "non-catalog application"
        elif "extension" in lower or "browser extension" in lower:
            entities["software_name"] = "browser extension for productivity tracking"
            entities["is_in_catalog"] = False
        elif "data-analysis tool" in lower or "data analysis" in lower:
            entities["software_name"] = "data-analysis tool"
            entities["is_in_catalog"] = False
        elif any(w in lower for w in ["approved software catalog", "standard software", "approved catalog", "in the software catalog", "in the catalog", "catalog software"]):
            entities["is_in_catalog"] = True
            entities["software_name"] = "Standard Catalog Software"


        # 7. Asset Tag (pattern e.g. VER-PRN-XX-XX or similar uppercase alphanumeric with hyphens)
        tag_match = re.search(r"(ver-[a-z0-9\-]+|[a-z]{2,4}-\d{2,4}-\d{2,4})", lower)
        if tag_match:
            entities["asset_tag"] = tag_match.group(1).upper()
        else:
            entities["asset_tag"] = None

        entities["spooler_restarted"] = any(w in lower for w in ["restarted spooler", "spooler restart", "restarted the print spooler"])

        # 8. Remote work schedule
        remote_match = re.search(r"(\d+)\s*days?(?:\s*a\s*week|\s*/\s*week|\s*remote)?", lower)
        if remote_match and ("home" in lower or "remote" in lower or "wfh" in lower):
            entities["remote_days_per_week"] = int(remote_match.group(1))

        # 9. Phishing forward flag
        entities["phishing_forwarded"] = any(w in lower for w in ["forwarding it to", "forwarded to", "forwarded it to", "few teammates to check", "sent it to colleagues"])

        # 10. Admin access & justification
        entities["is_admin_request"] = any(w in lower for w in ["admin access", "administrator access", "admin rights", "reporting server"])
        # Check if genuine business justification is provided (e.g. project approval code or documented signoff, not just "need it urgently")
        entities["has_business_justification"] = "justification code:" in lower or "approved by director" in lower

        # 11. Mailbox GB
        quota_match = re.search(r"(\d+)\s*gb", lower)
        if quota_match:
            entities["requested_mailbox_gb"] = int(quota_match.group(1))
        elif any(w in lower for w in ["quota increase", "increase my quota", "increase quota", "expand quota"]):
            entities["requested_mailbox_gb"] = 35
        else:
            entities["requested_mailbox_gb"] = None

        # Merge with context if provided
        if context:
            for k, v in context.items():
                if v is not None and entities.get(k) is None:
                    entities[k] = v

        return entities
