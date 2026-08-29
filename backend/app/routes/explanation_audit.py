"""
Explanation and Audit Routes
"""

from fastapi import APIRouter, HTTPException
from app.data import seed_data

router = APIRouter()


@router.get("/explanation-audit/{student_id}")
def get_explanation_audit(student_id: int):
    student = seed_data.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    scores = seed_data.get_readiness_scores(student_id)
    
    audit_record = {
        "student_id": student_id,
        "target_role": student.get("target_role"),
        "skill_gap_score": scores.get("skill_gap_score", 0),
        "portfolio_score": scores.get("portfolio_score", 0),
        "resume_score": scores.get("resume_score", 0),
        "interview_readiness_score": scores.get("interview_readiness_score", 0),
    }
    
    return {
        "student_id": student_id,
        "audit_log": audit_record,
        "message": "Audit trail generated successfully"
    }