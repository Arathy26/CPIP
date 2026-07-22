"""
Resume Readiness Routes
API endpoints for resume readiness evaluation
"""

from fastapi import APIRouter, HTTPException
from app.agents.resume_readiness_agent import resume_readiness_agent, validate_resume_result

router = APIRouter()

# Sample resume data (from CPIP_Seed_Data.json)
STUDENT_RESUMES = {
    1: {  # Arathy
        "education": "B.Tech Computer Science",
        "skills": ["Python", "React", "SQL"],
        "projects": ["CPIP Project"],
        "contact": {"email": "arathy@email.com", "phone": "9876543210"},
        "role_alignment": "AI Engineer"
    },
    2: {  # Archana
        "education": "B.Tech Computer Science",
        "skills": ["Python", "FastAPI", "SQL", "Docker"],
        "projects": ["Backend API", "Database Design"],
        "contact": {"email": "archana@email.com", "phone": "9876543211"},
        "role_alignment": "Backend Developer"
    },
    3: {  # Anamika
        "education": "B.Tech Information Technology",
        "skills": ["Python", "React", "SQL"],
        "projects": ["Full Stack App"],
        "contact": {"email": "anamika@email.com"},
        "role_alignment": None  # Missing role alignment
    }
}


@router.get("/resume-readiness/{student_id}")
def get_resume_readiness(student_id: int):
    """
    Get resume readiness analysis for a student.
    
    Args:
        student_id: ID of the student
        
    Returns:
        Resume readiness analysis with score and missing sections
    """
    
    # Check if student exists
    if student_id not in STUDENT_RESUMES:
        raise HTTPException(
            status_code=404,
            detail=f"Student {student_id} not found"
        )
    
    # Get student resume data
    resume_data = STUDENT_RESUMES[student_id]
    
    # Run Resume Readiness Agent
    resume_result = resume_readiness_agent(resume_data)
    
    # Validate result
    validation = validate_resume_result(resume_result)
    
    # Return resume analysis with validation
    return {
        "student_id": student_id,
        "resume_analysis": resume_result,
        "validation": validation,
        "message": "Resume readiness analysis completed successfully"
    }


@router.get("/resume-readiness")
def list_all_resume_readiness():
    """
    Get resume readiness analysis for all students.
    
    Returns:
        List of all student resume readiness scores
    """
    
    results = []
    
    for student_id in STUDENT_RESUMES:
        resume_data = STUDENT_RESUMES[student_id]
        
        resume_result = resume_readiness_agent(resume_data)
        
        results.append({
            "student_id": student_id,
            "resume_score": resume_result["resume_score"],
            "readiness_level": resume_result["readiness_level"],
            "sections_present": len(resume_result["sections_present"]),
            "sections_missing": len(resume_result["sections_missing"])
        })
    
    return {
        "total_students": len(results),
        "resume_readiness": results,
        "message": "All resume readiness scores retrieved"
    }