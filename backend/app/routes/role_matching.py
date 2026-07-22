"""
Role Matching Routes
API endpoints for role matching recommendations
"""

from fastapi import APIRouter, HTTPException
from app.agents.role_matching_agent import role_matching_agent, validate_role_match_result

router = APIRouter()

# Candidate profiles with readiness scores
CANDIDATE_PROFILES = {
    1: {
        "profile": {
            "candidate_id": 1,
            "skills": ["Python", "React", "SQL"],
            "target_role": "Full Stack Developer"
        },
        "readiness_scores": {
            "skill_gap_score": 65,
            "portfolio_score": 50,
            "resume_score": 100,
            "interview_readiness_score": 70
        }
    },
    2: {
        "profile": {
            "candidate_id": 2,
            "skills": ["Python", "FastAPI", "SQL", "Docker"],
            "target_role": "Backend Developer"
        },
        "readiness_scores": {
            "skill_gap_score": 85,
            "portfolio_score": 100,
            "resume_score": 100,
            "interview_readiness_score": 80
        }
    },
    3: {
        "profile": {
            "candidate_id": 3,
            "skills": ["Python", "React", "SQL"],
            "target_role": "Full Stack Developer"
        },
        "readiness_scores": {
            "skill_gap_score": 75,
            "portfolio_score": 75,
            "resume_score": 80,
            "interview_readiness_score": 70
        }
    }
}


@router.get("/role-match/{student_id}")
def get_role_match(student_id: int):
    """
    Get role matching recommendations for a student.
    
    Args:
        student_id: ID of the student
        
    Returns:
        Role matching recommendations with fit scores
    """
    
    if student_id not in CANDIDATE_PROFILES:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    candidate_data = CANDIDATE_PROFILES[student_id]
    
    # Run Role Matching Agent
    role_result = role_matching_agent(
        candidate_data["profile"],
        candidate_data["readiness_scores"]
    )
    
    # Validate result
    validation = validate_role_match_result(role_result)
    
    return {
        "student_id": student_id,
        "role_match_analysis": role_result,
        "validation": validation,
        "message": "Role matching completed successfully"
    }


@router.get("/role-match")
def list_all_role_matches():
    """
    Get role matching recommendations for all students.
    
    Returns:
        List of role recommendations for all students
    """
    
    results = []
    
    for student_id in CANDIDATE_PROFILES:
        candidate_data = CANDIDATE_PROFILES[student_id]
        role_result = role_matching_agent(
            candidate_data["profile"],
            candidate_data["readiness_scores"]
        )
        
        results.append({
            "student_id": student_id,
            "top_recommendation": role_result["recommended_roles"][0] if role_result["recommended_roles"] else None,
            "total_matches": len(role_result["all_matches"])
        })
    
    return {
        "total_students": len(results),
        "role_matches": results,
        "message": "All role matches retrieved"
    }