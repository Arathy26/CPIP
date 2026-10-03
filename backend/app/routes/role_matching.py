"""
Role Matching Route
Matches a student to roles recruiters have posted in CPIP.
Route gathers data; role_matching_agent (pure function) decides.
No external APIs. No hardcoded roles.
"""

from fastapi import APIRouter, HTTPException
from app.agents.role_matching_agent import role_matching_agent, validate_role_match_result
from app.data import seed_data

router = APIRouter()


@router.get("/role-match/{student_id}")
def get_role_match(student_id: int):
    student = seed_data.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    profile = {
        "candidate_id": student_id,
        "skills": student.get("skills", []),
        "target_role": student.get("target_role"),
    }
    role_requirements = seed_data.get_all_target_roles()

    result = role_matching_agent(profile, role_requirements=role_requirements)
    validation = validate_role_match_result(result)

    return {
        "student_id": student_id,
        "role_matches": result["recommended_roles"],
        "total_roles_analyzed": result["total_roles_analyzed"],
        "recommendation_summary": result["recommendation_summary"],
        "validation": validation,
    }
