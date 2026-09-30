from typing import Dict, Any, Tuple


class GreenPolicyValidator:
    """
    Deterministic policy validation for green operational recommendations.
    Enforces organizational constraints, safety rules, and operational protection windows.
    Returns: (policy_status, policy_notes)
    Status values: PASS, BLOCK, REVIEW_REQUIRED
    """

    @staticmethod
    def validate_recommendation(
        category: str,
        action_title: str,
        parameters: Dict[str, Any]
    ) -> Tuple[str, str]:
        title_lower = action_title.lower()
        target = parameters.get("target_system", "").lower()
        operating_hours = parameters.get("operating_hours", "core")

        # 1. Critical Safety & Environmental Protection Policies (Mandatory BLOCK)
        critical_keywords = ["fire", "emergency", "effluent", "etp", "zld", "cctv", "safety", "ventilation"]
        if any(kw in title_lower or kw in target for kw in critical_keywords):
            if "shutdown" in title_lower or "power off" in title_lower or "cutoff" in title_lower:
                return (
                    "BLOCK",
                    "Safety Policy Violation: Critical continuous environmental protection or emergency fire safety systems cannot be powered down or disconnected."
                )

        # 2. Production Protected Windows (REVIEW_REQUIRED)
        if "resize" in title_lower or "scale down" in title_lower or "idle" in title_lower:
            if operating_hours == "core" or parameters.get("is_production", True):
                return (
                    "REVIEW_REQUIRED",
                    "Policy Check: Modifying production workloads requires supervisor sign-off and must be scheduled outside core operational shifts."
                )

        # 3. Off-peak scheduling, batch caching, document digitization (PASS)
        if "cache" in title_lower or "batch" in title_lower or "digitize" in title_lower or "off-peak" in title_lower:
            return (
                "PASS",
                "Policy Verified: Workload optimization and digitization align with enterprise green operational policy without impacting runtime SLAs."
            )

        # Default fallback
        return (
            "PASS",
            "Policy Verified: Standard operational efficiency recommendation."
        )
