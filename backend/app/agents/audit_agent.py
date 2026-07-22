"""
Audit Agent
Records decision trails for transparency and accountability
"""

from datetime import datetime

def audit_agent(audit_input):
    """
    Creates audit log entry for a decision.
    
    Args:
        audit_input: Dictionary with decision information
        {
            "candidate_id": 1,
            "event_type": "readiness_evaluation",
            "scores": {...},
            "recommendation": "Interview Ready",
            "decision_reason": "All dimensions strong",
            "agent_inputs": {...},
            "timestamp": "2026-07-20T05:30:00"
        }
        
    Returns:
        Dictionary with audit record
    """
    
    candidate_id = audit_input.get("candidate_id")
    event_type = audit_input.get("event_type", "unknown")
    scores = audit_input.get("scores", {})
    recommendation = audit_input.get("recommendation", "No recommendation")
    decision_reason = audit_input.get("decision_reason", "Not specified")
    timestamp = audit_input.get("timestamp", datetime.now().isoformat())
    
    # Create audit record
    audit_record = {
        "audit_id": f"audit_{candidate_id}_{event_type}_{timestamp}",
        "candidate_id": candidate_id,
        "event_type": event_type,
        "timestamp": timestamp,
        "decision": recommendation,
        "reason": decision_reason,
        "scores_used": scores,
        "audit_status": "recorded",
        "audit_note": f"Candidate {candidate_id}: {event_type} → {recommendation} (Reason: {decision_reason})"
    }
    
    return audit_record


def validate_audit_result(result):
    """
    Validates audit record.
    
    Args:
        result: The output from audit_agent()
        
    Returns:
        Dictionary with validation status
    """
    
    required_fields = ["audit_id", "candidate_id", "decision", "timestamp"]
    
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        return {
            "valid": False,
            "errors": f"Missing fields: {missing_fields}"
        }
    
    return {
        "valid": True,
        "message": "Audit record is valid and complete"
    }