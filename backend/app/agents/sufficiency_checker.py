from typing import Dict, Any, List, Tuple

class SufficiencyChecker:
    """Evaluates information sufficiency for policy execution without over-questioning."""

    @classmethod
    def check_sufficiency(
        cls,
        intent: str,
        entities: Dict[str, Any],
        raw_text: str
    ) -> Tuple[bool, List[str], str]:
        """
        Returns (is_sufficient, follow_up_questions, explanation)
        """
        lower = raw_text.strip().lower()

        # 1. Unknown / Ambiguous request (e.g. REQ-15: "hey can you help, its not working")
        if intent == "unknown_it_issue" or (len(raw_text.split()) < 8 and "not working" in lower and not any(k in lower for k in ["vpn", "laptop", "printer", "email", "wifi", "screen", "password"])):
            return False, [
                "Which specific system, application, or hardware device is not working (e.g., laptop, VPN, email, printer, or software)?",
                "What error message or behavior are you experiencing?"
            ], "The request does not specify which technical service or device is experiencing an issue."

        # 2. Hardware / Laptop issue without age or symptom
        if intent in ["laptop_replacement", "hardware_issue"]:
            has_symptom = entities.get("is_dead") or entities.get("is_screen_flickering") or "broken" in lower or "won't turn on" in lower or "flicker" in lower
            has_age = entities.get("device_age_years") is not None
            if has_symptom and not has_age:
                return False, [
                    "How old is the laptop?"
                ], "Laptop service policy (KB-03 and Asset Management) requires the device age to evaluate repair versus lifecycle replacement eligibility."
            elif not has_symptom and not has_age:
                return False, [
                    "What specific problem are you experiencing with your laptop (e.g., won't turn on, physical damage, display flickering)?",
                    "How old is the laptop?"
                ], "Laptop service policy requires device age and verified failure details."
            elif not has_symptom and has_age:
                return False, [
                    "What specific problem or failure are you experiencing with your laptop?"
                ], "Laptop service policy requires verified hardware failure details."

        # 3. Software installation without software name
        if intent == "software_installation":
            if not entities.get("software_name") and "catalog" not in lower:
                return False, [
                    "What is the exact name and version of the software application or browser extension you are requesting?"
                ], "Software installation policy requires the application title to verify against the catalog."

        # 4. Expense tool without knowing if account already exists
        # Note: Handled by RulesEngine as an informational step

        # Everything required is present
        return True, [], "All necessary policy parameters are present."
