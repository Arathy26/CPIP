"""
Interview Readiness Routes

Interview scores come ONLY from mock interviews recorded by a human
assessor (mentor / trainer / placement officer). No invented numbers.
Route gathers data; interview_readiness_agent (pure function) decides.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.agents.interview_readiness_agent import interview_readiness_agent, validate_interview_result
from app.data import seed_data

router = APIRouter()


class InterviewAssessmentRequest(BaseModel):
    student_id: int
    assessed_by: str = Field(..., description="Name or role of the human assessor")
    aptitude_score: Optional[float] = Field(None, ge=0, le=100)
    technical_score: Optional[float] = Field(None, ge=0, le=100)
    communication_score: Optional[float] = Field(None, ge=0, le=100)
    project_explanation_score: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


@router.post("/interview-assessments")
def record_interview_assessment(data: InterviewAssessmentRequest):
    """Mentor records the result of a mock interview. Leave a dimension out if it was not assessed."""
    if not seed_data.get_student(data.student_id):
        raise HTTPException(status_code=404, detail=f"Student {data.student_id} not found")
    if not data.assessed_by.strip():
        raise HTTPException(status_code=400, detail="assessed_by is required")

    payload = data.dict()
    score_keys = ["aptitude_score", "technical_score", "communication_score", "project_explanation_score"]
    if all(payload[k] is None for k in score_keys):
        raise HTTPException(status_code=400, detail="At least one dimension score is required")
    payload["assessed_by"] = data.assessed_by.strip()

    saved = seed_data.add_interview_assessment(data.student_id, payload)
    return {"success": True, "assessment": saved, "message": "Mock interview assessment recorded"}


@router.get("/interview-assessments/{student_id}")
def list_interview_assessments(student_id: int):
    if not seed_data.get_student(student_id):
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    history = seed_data.get_interview_assessments(student_id)
    return {"student_id": student_id, "total": len(history), "assessments": history}


@router.get("/interview-readiness/{student_id}")
def get_interview_readiness(student_id: int):
    student = seed_data.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    scores, evidence = seed_data.get_latest_interview_scores(student_id)
    interview_result = interview_readiness_agent(scores)
    validation = validate_interview_result(interview_result)

    return {
        "student_id": student_id,
        "interview_readiness_analysis": interview_result,
        "evidence": evidence,
        "validation": validation,
        "message": "Interview readiness assessment completed"
    }


@router.get("/interview-readiness")
def list_all_interview_readiness():
    results = []
    for student in seed_data.get_all_students():
        scores, _ = seed_data.get_latest_interview_scores(student["id"])
        interview_result = interview_readiness_agent(scores)
        results.append({
            "student_id": student["id"],
            "interview_readiness_score": interview_result["interview_readiness_score"],
            "readiness_level": interview_result["readiness_level"],
            "dimensions_assessed": interview_result["dimensions_assessed"],
            "weak_dimensions": interview_result["weak_dimensions"]
        })

    return {
        "total_students": len(results),
        "interview_readiness": results,
        "message": "All interview readiness assessments retrieved"
    }
