"""
Audit Agent
Builds a structured decision-trail record (inputs, outputs, reason, rules).

Pure function: it BUILDS the record. The caller saves it with
seed_data.save_audit_record(). A record is only "recorded" once saved —
the saved record gets its real database id.
"""

from datetime import datetime


def audit_agent(audit_input):
    """
    Args:
        audit_input: {
            "candidate_id", "event_type",
            "scores": {...}, "agent_outputs": {...},
            "recommendation": str, "decision_reason": str,
            "rules_version": str (optional)
        }
    Returns:
        Audit record dict (not yet saved)
    """
    a = audit_input or {}
    event_type = a.get("event_type") or "unknown"
    return {
        "candidate_id": a.get("candidate_id"),
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "decision": a.get("recommendation") or "No recommendation",
        "reason": a.get("decision_reason") or "Not specified",
        "scores_used": a.get("scores") or {},
        "agent_outputs": a.get("agent_outputs") or {},
        "rules_version": a.get("rules_version"),
        "audit_status": "built_not_saved",
    }


def validate_audit_result(result):
    """Validates audit record."""
    required_fields = ["candidate_id", "event_type", "decision", "timestamp"]
    missing_fields = [field for field in required_fields if field not in result]
    if missing_fields:
        return {"valid": False, "errors": f"Missing fields: {missing_fields}"}
    return {"valid": True, "message": "Audit record is valid and complete"}
