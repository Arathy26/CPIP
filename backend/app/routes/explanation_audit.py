"""
Explanation and Audit Routes
- Explanation is built from the REAL outputs of every agent.
- Every explanation request saves an audit record (decision trail).
- Audit history is read from the audit_logs table.
"""

from fastapi import APIRouter, HTTPException
from app.data import seed_data
from app.agents.explanation_agent import validate_explanation_result
from app.services.orchestrator import run_full_pipeline

router = APIRouter()


@router.get("/explanation-audit/{student_id}")
def get_explanation_audit(student_id: int):
    result = run_full_pipeline(student_id, event_type="ReadinessExplained")
    if result.get("error"):
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    explanation = result["explanation"]
    return {
        "student_id": student_id,
        "explanation": explanation,
        "scores": result["scores"],
        "audit": result["audit"],
        "validation": validate_explanation_result(explanation),
        "message": "Explanation generated and audit record saved",
    }


@router.get("/audit-logs/{student_id}")
def get_audit_logs(student_id: int, limit: int = 50):
    if not seed_data.get_student(student_id):
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    logs = seed_data.get_audit_logs(student_id, limit=min(max(limit, 1), 200))
    return {"student_id": student_id, "total": len(logs), "audit_logs": logs}
