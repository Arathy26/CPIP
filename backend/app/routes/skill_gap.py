"""
Skill Gap Routes
API endpoints for skill gap evaluation
"""

from fastapi import APIRouter, HTTPException
from app.agents.skill_gap_agent import skill_gap_agent, validate_gap_result

router = APIRouter()

# Sample role requirements (from database design)
ROLE_REQUIREMENTS = {
    "AI Engineer": {
        "required_skills": ["Python", "Machine Learning", "TensorFlow", "Data Analysis"],
        "mandatory_skills": ["Python", "Machine Learning"]
    },
    "Backend Developer": {
        "required_skills": ["Python", "FastAPI", "SQL", "Docker"],
        "mandatory_skills": ["Python", "FastAPI", "SQL"]
    },
    "Full Stack Developer": {
        "required_skills": ["Python", "React", "SQL", "APIs"],
        "mandatory_skills": ["Python", "React", "SQL"]
    }
}

# Sample student skills (from CPIP_Seed_Data.json)
STUDENT_SKILLS = {
    1: ["Python", "React", "SQL"],  # Arathy
    2: ["Python", "FastAPI", "SQL"],  # Archana
    3: ["Python", "React", "SQL"]  # Anamika
}

# Student target roles
STUDENT_TARGET_ROLES = {
    1: "AI Engineer",
    2: "Backend Developer",
    3: "Full Stack Developer"
}


@router.get("/skill-gap/{student_id}")
def get_skill_gap(student_id: int):
    """
    Get skill gap analysis for a student.
    
    Args:
        student_id: ID of the student
        
    Returns:
        Skill gap analysis with score and missing skills
    """
    
    # Check if student exists
    if student_id not in STUDENT_SKILLS:
        raise HTTPException(
            status_code=404,
            detail=f"Student {student_id} not found"
        )
    
    # Get student data
    candidate_skills = STUDENT_SKILLS[student_id]
    target_role = STUDENT_TARGET_ROLES[student_id]
    
    # Check if role exists
    if target_role not in ROLE_REQUIREMENTS:
        raise HTTPException(
            status_code=404,
            detail=f"Role {target_role} not found"
        )
    
    # Get role requirements
    role_data = ROLE_REQUIREMENTS[target_role]
    required_skills = role_data["required_skills"]
    mandatory_skills = role_data["mandatory_skills"]
    
    # Run Skill Gap Agent
    gap_result = skill_gap_agent(
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        mandatory_skills=mandatory_skills
    )
    
    # Validate result
    validation = validate_gap_result(gap_result)
    
    # Return gap analysis with validation
    return {
        "student_id": student_id,
        "target_role": target_role,
        "candidate_skills": candidate_skills,
        "gap_analysis": gap_result,
        "validation": validation,
        "message": "Skill gap analysis completed successfully"
    }


@router.get("/skill-gap")
def list_all_skill_gaps():
    """
    Get skill gap analysis for all students.
    
    Returns:
        List of all student skill gaps
    """
    
    results = []
    
    for student_id in STUDENT_SKILLS:
        candidate_skills = STUDENT_SKILLS[student_id]
        target_role = STUDENT_TARGET_ROLES[student_id]
        role_data = ROLE_REQUIREMENTS[target_role]
        
        gap_result = skill_gap_agent(
            candidate_skills=candidate_skills,
            required_skills=role_data["required_skills"],
            mandatory_skills=role_data["mandatory_skills"]
        )
        
        results.append({
            "student_id": student_id,
            "target_role": target_role,
            "gap_score": gap_result["gap_score"],
            "readiness_level": gap_result["readiness_level"]
        })
    
    return {
        "total_students": len(results),
        "skill_gaps": results,
        "message": "All skill gaps retrieved"
    }