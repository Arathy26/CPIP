"""
Interview Readiness Routes
API endpoints for interview readiness evaluation
"""

from fastapi import APIRouter, HTTPException
from app.agents.interview_readiness_agent import interview_readiness_agent, validate_interview_result
from app.data import seed_data

router = APIRouter()

def _build_interview_scores(student, resume):
    """Derive interview dimension scores from real resume data."""
    skills = student.get("skills", [])
    projects = resume.get("projects", []) if resume else []
    github = student.get("github_link", None)
    linkedin = student.get("linkedin_id", None)

    technical_score = min(50 + len(skills) * 5, 100)
    project_score = min(50 + len(projects) * 10, 100)
    communication_score = 60
    if github:
        communication_score += 15
    if linkedin:
        communication_score += 15
    communication_score = min(communication_score, 100)
    aptitude_score = 65

    return {
        "aptitude_score": aptitude_score,
        "technical_score": technical_score,
        "communication_score": communication_score,
        "project_explanation_score": project_score,
    }


@router.get("/interview-readiness/{student_id}")
def get_interview_readiness(student_id: int):
    student = seed_data.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    resume = seed_data.get_resume(student_id)
    scores = _build_interview_scores(student, resume)

    interview_result = interview_readiness_agent(scores)
    validation = validate_interview_result(interview_result)

    return {
        "student_id": student_id,
        "interview_readiness_analysis": interview_result,
        "validation": validation,
        "message": "Interview readiness assessment completed"
    }


@router.get("/interview-readiness")
def list_all_interview_readiness():
    results = []

    for student in seed_data.get_all_students():
        student_id = student["id"]
        resume = seed_data.get_resume(student_id)
        scores = _build_interview_scores(student, resume)
        interview_result = interview_readiness_agent(scores)

        results.append({
            "student_id": student_id,
            "interview_readiness_score": interview_result["interview_readiness_score"],
            "readiness_level": interview_result["readiness_level"],
            "weak_dimensions": interview_result["weak_dimensions"]
        })

    return {
        "total_students": len(results),
        "interview_readiness": results,
        "message": "All interview readiness assessments retrieved"
    }