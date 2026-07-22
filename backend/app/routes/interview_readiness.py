"""
Interview Readiness Routes
API endpoints for interview readiness evaluation
"""

from fastapi import APIRouter, HTTPException
from app.agents.interview_readiness_agent import interview_readiness_agent, validate_interview_result

router = APIRouter()

# Sample interview dimension scores for students
INTERVIEW_SCORES = {
    1: {  # Arathy
        "aptitude_score": 75,
        "technical_score": 70,
        "communication_score": 65,
        "project_explanation_score": 70
    },
    2: {  # Archana
        "aptitude_score": 85,
        "technical_score": 85,
        "communication_score": 80,
        "project_explanation_score": 85
    },
    3: {  # Anamika
        "aptitude_score": 80,
        "technical_score": 75,
        "communication_score": 75,
        "project_explanation_score": 70
    }
}


@router.get("/interview-readiness/{student_id}")
def get_interview_readiness(student_id: int):
    """
    Get interview readiness assessment for a student.
    
    Args:
        student_id: ID of the student
        
    Returns:
        Interview readiness analysis with dimension breakdown
    """
    
    if student_id not in INTERVIEW_SCORES:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    scores = INTERVIEW_SCORES[student_id]
    
    # Run Interview Readiness Agent
    interview_result = interview_readiness_agent(scores)
    
    # Validate result
    validation = validate_interview_result(interview_result)
    
    return {
        "student_id": student_id,
        "interview_readiness_analysis": interview_result,
        "validation": validation,
        "message": "Interview readiness assessment completed"
    }


@router.get("/interview-readiness")
def list_all_interview_readiness():
    """
    Get interview readiness for all students.
    
    Returns:
        Interview readiness summary for all students
    """
    
    results = []
    
    for student_id in INTERVIEW_SCORES:
        scores = INTERVIEW_SCORES[student_id]
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