"""
Candidate Profile Routes
API endpoints for candidate profile evaluation
"""

from fastapi import APIRouter, HTTPException
from app.agents.candidate_profile_agent import candidate_profile_agent, validate_profile

router = APIRouter()

# Sample student data from CPIP_Seed_Data.json
SAMPLE_STUDENTS = {
    1: {
        "id": 1,
        "name": "Arathy Rajeev",
        "email": "arathy@gmail.com",
        "degree": "BBA",
        "cgpa": 7.0,
        "location": "Kochi",
        "target_role": "AI Engineer",
        "github_link": "https://github.com/arathy26",
        "linkedin_id": "https://www.linkedin.com/in/arathy-rajeev",
        "resume": "arathy_resume.pdf",
        "salary_expected": 500000
    },
    2: {
        "id": 2,
        "name": "Archana Rajeev",
        "email": "archana@gmail.com",
        "degree": "BBA",
        "cgpa": 8.0,
        "location": "Kochi",
        "target_role": "Backend Developer",
        "github_link": "https://github.com/archana",
        "linkedin_id": "https://www.linkedin.com/in/archana-rajeev",
        "resume": "archana_resume.pdf",
        "salary_expected": 600000
    },
    3: {
        "id": 3,
        "name": "Anamika P",
        "email": "anamika@gmail.com",
        "degree": "B.Tech",
        "cgpa": 8.5,
        "location": "Bangalore",
        "target_role": "Full Stack Developer",
        "github_link": "https://github.com/anamika",
        "linkedin_id": "https://www.linkedin.com/in/anamika-p",
        "resume": "anamika_resume.pdf",
        "salary_expected": 700000
    }
}


@router.get("/candidates/{student_id}")
def get_candidate_profile(student_id: int):
    """
    Get normalized candidate profile for a student.
    
    Args:
        student_id: ID of the student
        
    Returns:
        Normalized candidate profile
    """
    
    # Check if student exists
    if student_id not in SAMPLE_STUDENTS:
        raise HTTPException(
            status_code=404,
            detail=f"Student {student_id} not found"
        )
    
    # Get student data
    student_data = SAMPLE_STUDENTS[student_id]
    
    # Run Candidate Profile Agent
    profile = candidate_profile_agent(student_data)
    
    # Validate the profile
    validation = validate_profile(profile)
    
    # Return profile with validation status
    return {
        "candidate_profile": profile,
        "validation": validation,
        "message": "Candidate profile successfully generated"
    }


@router.get("/candidates")
def list_all_candidates():
    """
    Get list of all available candidates.
    
    Returns:
        List of all candidate profiles
    """
    
    profiles = []
    for student_id in SAMPLE_STUDENTS:
        student_data = SAMPLE_STUDENTS[student_id]
        profile = candidate_profile_agent(student_data)
        profiles.append(profile)
    
    return {
        "total_candidates": len(profiles),
        "candidates": profiles,
        "message": "All candidate profiles retrieved"
    }